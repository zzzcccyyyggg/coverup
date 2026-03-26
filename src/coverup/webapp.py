from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tarfile
import threading
import uuid
import zipfile

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .coverup import get_prompters

try:  # pragma: no cover - optional dependency import for request typing
    from fastapi import UploadFile as FastAPIUploadFile
except ImportError:  # pragma: no cover
    FastAPIUploadFile = Any


SUMMARY_PREFIX = "[CoverUp] Summary JSON: "
INITIAL_PREFIX = "[CoverUp] Initial coverage: "
FINAL_PREFIX = "[CoverUp] Final coverage: "
TRACE_PREFIX = "Trace log written to:"
PROMPT_OPTIONS = [
    {"value": "baseline", "label": "Baseline"},
    {"value": "advanced", "label": "Advanced"},
]
MODEL_OPTIONS = [
    {"value": "", "label": "Use environment default", "provider": "auto"},
    {"value": "gpt-4o", "label": "OpenAI / GPT-4o", "provider": "openai"},
    {"value": "gpt-4.1", "label": "OpenAI / GPT-4.1", "provider": "openai"},
    {"value": "deepseek/deepseek-chat", "label": "DeepSeek / Chat", "provider": "deepseek"},
    {
        "value": "anthropic/claude-3-5-sonnet-20241022",
        "label": "Anthropic / Claude 3.5 Sonnet",
        "provider": "anthropic",
    },
]
KEY_FAMILY_OPTIONS = [
    {"value": "auto", "label": "Auto-detect from model"},
    {"value": "openai", "label": "OpenAI key"},
    {"value": "anthropic", "label": "Anthropic key"},
    {"value": "deepseek", "label": "DeepSeek key"},
    {"value": "openrouter", "label": "OpenRouter key"},
]
KEY_ENV_VARS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _default_model() -> str:
    if "OPENAI_API_KEY" in os.environ:
        return "gpt-4o"
    if "ANTHROPIC_API_KEY" in os.environ:
        return "anthropic/claude-3-sonnet-20240229"
    if "AWS_ACCESS_KEY_ID" in os.environ:
        return "anthropic.claude-3-5-sonnet-20241022-v2:0"
    return ""


def _default_prompt(language: str) -> str:
    return "advanced"


def _infer_key_family(model: str) -> str:
    normalized = model.strip().lower()
    if not normalized:
        return "auto"
    if "deepseek" in normalized:
        return "deepseek"
    if normalized.startswith("anthropic") or "claude" in normalized:
        return "anthropic"
    if "openrouter" in normalized:
        return "openrouter"
    if normalized.startswith(("gpt-", "o1", "o3", "o4")):
        return "openai"
    return "auto"


def _resolve_key_env_var(key_family: str, model: str) -> str | None:
    if key_family != "auto":
        return KEY_ENV_VARS.get(key_family)
    inferred = _infer_key_family(model)
    return KEY_ENV_VARS.get(inferred)


def _repo_src_path() -> Path | None:
    repo_root = Path(__file__).resolve().parents[2]
    src_dir = repo_root / "src"
    if src_dir.is_dir() and (repo_root / "pyproject.toml").exists():
        return src_dir
    return None


def _read_log_tail(path: Path, limit: int = 24000) -> str:
    if not path.exists():
        return ""
    with path.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        handle.seek(max(size - limit, 0))
        data = handle.read().decode("utf-8", errors="replace")
    return data[-limit:]


def _safe_archive_target(base: Path, member_name: str) -> Path:
    target = (base / member_name).resolve()
    if base.resolve() not in target.parents and target != base.resolve():
        raise ValueError(f"Archive member escapes extraction root: {member_name}")
    return target


def _extract_archive(archive_path: Path, extract_dir: Path) -> None:
    if zipfile.is_zipfile(archive_path):
        with zipfile.ZipFile(archive_path) as archive:
            for member in archive.infolist():
                _safe_archive_target(extract_dir, member.filename)
            archive.extractall(extract_dir)
        return

    if tarfile.is_tarfile(archive_path):
        with tarfile.open(archive_path) as archive:
            for member in archive.getmembers():
                if member.issym() or member.islnk():
                    raise ValueError("Symbolic links are not allowed in uploaded archives")
                _safe_archive_target(extract_dir, member.name)
                archive.extract(member, extract_dir)
        return

    raise ValueError("Only .zip, .tar, .tar.gz, and .tgz archives are supported")


def _detect_repo_root(extract_dir: Path) -> Path:
    visible_entries = [
        path for path in extract_dir.iterdir()
        if path.name != "__MACOSX" and not path.name.startswith(".")
    ]
    if len(visible_entries) == 1 and visible_entries[0].is_dir():
        return visible_entries[0]
    return extract_dir


def _normalize_hint(repo_root: Path, raw: str | None) -> Path | None:
    if not raw:
        return None
    candidate = (repo_root / raw).resolve()
    if repo_root.resolve() not in candidate.parents and candidate != repo_root.resolve():
        raise ValueError(f"Path escapes uploaded repository: {raw}")
    return candidate


def _preferred_candidate(candidates: list[Path], repo_root: Path) -> Path | None:
    if not candidates:
        return None

    def sort_key(path: Path) -> tuple[int, int, int, str]:
        parts = path.relative_to(repo_root).parts
        in_src = 0 if "src" in parts else 1
        in_pkg = 0 if "__init__.py" in {child.name for child in path.glob("__init__.py")} else 1
        return (in_src, in_pkg, len(parts), path.as_posix())

    return sorted({path.resolve() for path in candidates}, key=sort_key)[0]


def _detect_python_package_dir(repo_root: Path) -> Path:
    candidates: list[Path] = []

    for init_file in repo_root.rglob("__init__.py"):
        parts = init_file.relative_to(repo_root).parts
        if "tests" in parts or "test" in parts:
            continue
        candidates.append(init_file.parent)

    src_dir = repo_root / "src"
    if src_dir.is_dir():
        for child in src_dir.iterdir():
            if child.is_dir() and list(child.glob("*.py")):
                candidates.append(child)

    preferred = _preferred_candidate(candidates, repo_root)
    if preferred is not None:
        return preferred

    py_files = [
        path for path in repo_root.rglob("*.py")
        if "tests" not in path.relative_to(repo_root).parts
    ]
    if py_files:
        return py_files[0].parent.resolve()

    return repo_root


def _detect_tests_dir(repo_root: Path) -> Path:
    for rel in ("tests", "test"):
        candidate = repo_root / rel
        if candidate.is_dir():
            return candidate.resolve()

    candidate = repo_root / "tests"
    candidate.mkdir(parents=True, exist_ok=True)
    return candidate.resolve()


def _detect_go_package_dir(repo_root: Path) -> Path:
    if (repo_root / "go.mod").exists():
        return repo_root.resolve()

    go_mods = sorted(repo_root.rglob("go.mod"), key=lambda path: len(path.relative_to(repo_root).parts))
    if go_mods:
        return go_mods[0].parent.resolve()

    return repo_root.resolve()


def _detect_rust_package_dir(repo_root: Path) -> Path:
    if (repo_root / "Cargo.toml").exists():
        return repo_root.resolve()

    manifests = sorted(repo_root.rglob("Cargo.toml"), key=lambda path: len(path.relative_to(repo_root).parts))
    if manifests:
        return manifests[0].parent.resolve()

    return repo_root.resolve()


def _iter_generated_tests(repo_root: Path, language: str, prefix: str) -> list[Path]:
    if language == "python":
        paths = list(repo_root.rglob(f"test_{prefix}_*.py"))
    elif language == "go":
        paths = list(repo_root.rglob(f"{prefix}_*_test.go"))
    else:
        paths = list(repo_root.rglob(f"{prefix}_*_test.rs"))

    return sorted(path.resolve() for path in paths if path.is_file())


def _build_generated_zip(zip_path: Path, repo_root: Path, files: list[Path]) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, arcname=path.relative_to(repo_root).as_posix())


def _parse_coverup_log(log_path: Path) -> tuple[str | None, str | None, dict[str, Any] | None]:
    if not log_path.exists():
        return None, None, None

    initial_text: str | None = None
    final_text: str | None = None
    summary: dict[str, Any] | None = None
    fallback_counters: dict[str, int] | None = None
    fallback_cost: float | None = None

    fallback_coverages: list[str] = []

    full_text = log_path.read_text(encoding="utf-8", errors="replace")

    for line in full_text.splitlines():
        if line.startswith(INITIAL_PREFIX):
            initial_text = line[len(INITIAL_PREFIX):].strip()
        elif line.startswith(FINAL_PREFIX):
            final_text = line[len(FINAL_PREFIX):].strip()
        elif line.startswith(SUMMARY_PREFIX):
            payload = line[len(SUMMARY_PREFIX):].strip()
            try:
                summary = json.loads(payload)
            except json.JSONDecodeError:
                summary = None
        elif line.startswith("Measuring coverage..."):
            match = re.search(r"([0-9]+(?:\.[0-9]+)?%)\s*$", line)
            if match:
                fallback_coverages.append(match.group(1))

    progress_matches = re.findall(
        r"G=(\d+),\s*F=(\d+),\s*U=(\d+),\s*R=(\d+),\s*cost=~?\$([0-9]+(?:\.[0-9]+)?)",
        full_text,
    )
    if progress_matches:
        g, f, u, r, cost = progress_matches[-1]
        fallback_counters = {"G": int(g), "F": int(f), "U": int(u), "R": int(r)}
        fallback_cost = float(cost)

    if initial_text is None and fallback_coverages:
        initial_text = fallback_coverages[0]
    if final_text is None and len(fallback_coverages) > 1:
        final_text = fallback_coverages[-1]
    if summary is None and (fallback_counters is not None or initial_text or final_text):
        summary = {
            "initial_coverage": float(initial_text.rstrip("%")) if initial_text else None,
            "final_coverage": float(final_text.rstrip("%")) if final_text else None,
            "cost_usd": fallback_cost,
            "counters": fallback_counters or {},
        }

    return initial_text, final_text, summary


@dataclass
class JobRecord:
    id: str
    archive_name: str
    language: str
    model: str
    prompt: str
    key_family: str
    max_attempts: int
    prefix: str
    api_key: str = field(repr=False, default="")
    package_dir_hint: str = ""
    tests_dir_hint: str = ""
    created_at: str = field(default_factory=_utc_now)
    updated_at: str = field(default_factory=_utc_now)
    status: str = "queued"
    message: str = "Uploaded and waiting to start."
    error: str | None = None
    return_code: int | None = None
    repo_root: str | None = None
    package_dir: str | None = None
    tests_dir: str | None = None
    initial_coverage_text: str | None = None
    final_coverage_text: str | None = None
    summary: dict[str, Any] | None = None
    generated_tests: list[str] = field(default_factory=list)
    generated_zip_name: str | None = None
    trace_log: str | None = None
    log_path: str | None = None
    job_dir: Path = field(repr=False, default=Path("."))
    archive_path: Path = field(repr=False, default=Path("."))
    extract_dir: Path = field(repr=False, default=Path("."))


class JobManager:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir.resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._jobs: dict[str, JobRecord] = {}
        self._lock = threading.Lock()

    def create_job(
        self,
        *,
        archive_name: str,
        archive_bytes: bytes,
        language: str,
        model: str,
        prompt: str,
        key_family: str,
        api_key: str,
        max_attempts: int,
        package_dir_hint: str,
        tests_dir_hint: str,
        prefix: str = "coverup",
    ) -> JobRecord:
        job_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
        job_dir = self.data_dir / job_id
        extract_dir = job_dir / "repo"
        job_dir.mkdir(parents=True, exist_ok=True)
        extract_dir.mkdir(parents=True, exist_ok=True)

        safe_name = Path(archive_name or "repository.zip").name
        archive_path = job_dir / safe_name
        archive_path.write_bytes(archive_bytes)
        _extract_archive(archive_path, extract_dir)
        repo_root = _detect_repo_root(extract_dir)

        job = JobRecord(
            id=job_id,
            archive_name=safe_name,
            language=language,
            model=model.strip(),
            prompt=prompt.strip() or _default_prompt(language),
            key_family=key_family.strip() or "auto",
            max_attempts=max(1, int(max_attempts)),
            prefix=prefix,
            api_key=api_key,
            package_dir_hint=package_dir_hint.strip(),
            tests_dir_hint=tests_dir_hint.strip(),
            repo_root=repo_root.as_posix(),
            log_path=(job_dir / "coverup.stdout.log").as_posix(),
            trace_log=(job_dir / "trace.jsonl").as_posix(),
            job_dir=job_dir,
            archive_path=archive_path,
            extract_dir=extract_dir,
        )

        with self._lock:
            self._jobs[job_id] = job

        thread = threading.Thread(target=self._run_job, args=(job_id,), daemon=True)
        thread.start()
        return job

    def list_jobs(self) -> list[dict[str, Any]]:
        with self._lock:
            jobs = list(self._jobs.values())
        jobs.sort(key=lambda item: item.created_at, reverse=True)
        return [self._serialize_job(job) for job in jobs]

    def get_job(self, job_id: str) -> JobRecord | None:
        with self._lock:
            return self._jobs.get(job_id)

    def serialize_job(self, job_id: str) -> dict[str, Any]:
        job = self.get_job(job_id)
        if job is None:
            raise KeyError(job_id)
        return self._serialize_job(job)

    def _set_job_fields(self, job: JobRecord, **changes: Any) -> None:
        with self._lock:
            for key, value in changes.items():
                setattr(job, key, value)
            job.updated_at = _utc_now()

    def _serialize_job(self, job: JobRecord) -> dict[str, Any]:
        payload = asdict(job)
        payload.pop("job_dir", None)
        payload.pop("archive_path", None)
        payload.pop("extract_dir", None)
        payload.pop("api_key", None)
        payload["download_url"] = (
            f"/api/jobs/{job.id}/download" if job.generated_zip_name else None
        )
        payload["log_tail"] = _read_log_tail(Path(job.log_path)) if job.log_path else ""
        return payload

    def _resolve_project_layout(self, job: JobRecord) -> tuple[Path, Path | None]:
        repo_root = Path(job.repo_root).resolve()

        package_dir = _normalize_hint(repo_root, job.package_dir_hint)
        tests_dir = _normalize_hint(repo_root, job.tests_dir_hint)

        if job.language == "python":
            package_dir = package_dir or _detect_python_package_dir(repo_root)
            tests_dir = tests_dir or _detect_tests_dir(repo_root)
        elif job.language == "go":
            package_dir = package_dir or _detect_go_package_dir(repo_root)
            tests_dir = None
        else:
            package_dir = package_dir or _detect_rust_package_dir(repo_root)
            tests_dir = None

        return package_dir.resolve(), tests_dir.resolve() if tests_dir else None

    def _build_command(self, job: JobRecord, package_dir: Path, tests_dir: Path | None) -> list[str]:
        cmd = [
            sys.executable,
            "-c",
            "import sys, coverup; sys.exit(coverup.main())",
            "--language",
            job.language,
            "--package-dir",
            package_dir.as_posix(),
            "--max-attempts",
            str(job.max_attempts),
            "--trace-log",
            Path(job.trace_log).as_posix(),
            "--log-file",
            (job.job_dir / "coverup-run").as_posix(),
            "--prefix",
            job.prefix,
        ]

        if job.model:
            cmd.extend(["--model", job.model])
        if job.prompt:
            cmd.extend(["--prompt", job.prompt])
        if tests_dir is not None:
            cmd.extend(["--tests-dir", tests_dir.as_posix()])

        return cmd

    def _child_env(self, job: JobRecord) -> dict[str, str]:
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        src_dir = _repo_src_path()
        if src_dir is not None:
            pythonpath = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = (
                src_dir.as_posix() if not pythonpath else f"{src_dir.as_posix()}:{pythonpath}"
            )
        if job.api_key:
            env_var = _resolve_key_env_var(job.key_family, job.model)
            if env_var is not None:
                env[env_var] = job.api_key
        return env

    def _run_job(self, job_id: str) -> None:
        job = self.get_job(job_id)
        if job is None:
            return

        try:
            package_dir, tests_dir = self._resolve_project_layout(job)
            repo_root = Path(job.repo_root).resolve()
            before_files = set(_iter_generated_tests(repo_root, job.language, job.prefix))

            self._set_job_fields(
                job,
                status="running",
                message="Running CoverUp against the uploaded repository.",
                package_dir=package_dir.as_posix(),
                tests_dir=tests_dir.as_posix() if tests_dir else None,
            )

            cmd = self._build_command(job, package_dir, tests_dir)
            log_path = Path(job.log_path)

            with log_path.open("w", encoding="utf-8", errors="replace") as log_handle:
                process = subprocess.Popen(
                    cmd,
                    cwd=repo_root,
                    stdout=log_handle,
                    stderr=subprocess.STDOUT,
                    env=self._child_env(job),
                )
                return_code = process.wait()

            initial_text, final_text, summary = _parse_coverup_log(log_path)
            after_files = set(_iter_generated_tests(repo_root, job.language, job.prefix))
            generated_files = sorted(after_files - before_files)

            generated_zip_name: str | None = None
            if generated_files:
                generated_zip = job.job_dir / "generated-tests.zip"
                _build_generated_zip(generated_zip, repo_root, generated_files)
                generated_zip_name = generated_zip.name

            status = "finished" if return_code == 0 else "failed"
            message = (
                "Run completed. Review the coverage delta and download the generated tests."
                if status == "finished"
                else "Run failed. Check the log tail below for the failure point."
            )
            error = None
            if status == "failed":
                error = f"CoverUp exited with code {return_code}"

            if summary is not None:
                (job.job_dir / "summary.json").write_text(
                    json.dumps(summary, indent=2, sort_keys=True),
                    encoding="utf-8",
                )

            self._set_job_fields(
                job,
                status=status,
                message=message,
                return_code=return_code,
                error=error,
                initial_coverage_text=initial_text,
                final_coverage_text=final_text,
                summary=summary,
                generated_tests=[
                    path.relative_to(repo_root).as_posix() for path in generated_files
                ],
                generated_zip_name=generated_zip_name,
                api_key="",
            )
        except Exception as exc:  # pragma: no cover - best-effort UI surface
            self._set_job_fields(
                job,
                status="failed",
                message="The web job could not be prepared or executed.",
                error=str(exc),
                api_key="",
            )


def create_app(data_dir: str | Path | None = None):
    try:
        from fastapi import FastAPI, File, Form, HTTPException
        from fastapi.responses import FileResponse
        from fastapi.staticfiles import StaticFiles
    except ImportError as exc:  # pragma: no cover - import guard for optional deps
        raise RuntimeError(
            "CoverUp Web UI requires optional web dependencies. "
            "Install them with `pip install .[web]`."
        ) from exc

    app = FastAPI(title="CoverUp Studio", version="0.1.0")
    resolved_data_dir = Path(data_dir).resolve() if data_dir is not None else (Path.cwd() / ".coverup-web").resolve()
    app.state.manager = JobManager(resolved_data_dir)

    @app.get("/api/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/options")
    def options() -> dict[str, Any]:
        return {
            "languages": ["python", "go", "rust"],
            "prompts": PROMPT_OPTIONS,
            "defaultPromptByLanguage": {"python": "advanced", "go": "advanced", "rust": "advanced"},
            "models": MODEL_OPTIONS,
            "keyFamilies": KEY_FAMILY_OPTIONS,
            "defaultModel": _default_model(),
        }

    @app.get("/api/jobs")
    def list_jobs() -> list[dict[str, Any]]:
        return app.state.manager.list_jobs()

    @app.get("/api/jobs/{job_id}")
    def get_job(job_id: str) -> dict[str, Any]:
        try:
            return app.state.manager.serialize_job(job_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Unknown job id") from exc

    @app.get("/api/jobs/{job_id}/download")
    def download_generated_tests(job_id: str):
        job = app.state.manager.get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Unknown job id")
        if not job.generated_zip_name:
            raise HTTPException(status_code=404, detail="No generated tests available for download")

        generated_zip = job.job_dir / job.generated_zip_name
        return FileResponse(
            generated_zip,
            media_type="application/zip",
            filename=f"{job.id}-generated-tests.zip",
        )

    @app.post("/api/jobs")
    async def create_job(
        archive: FastAPIUploadFile = File(...),
        language: str = Form("python"),
        model: str = Form(""),
        prompt: str = Form(""),
        key_family: str = Form("auto"),
        api_key: str = Form(""),
        max_attempts: int = Form(3),
        package_dir: str = Form(""),
        tests_dir: str = Form(""),
    ) -> dict[str, Any]:
        language = language.strip().lower()
        if language not in {"python", "go", "rust"}:
            raise HTTPException(status_code=400, detail="Unsupported language")

        archive_name = archive.filename or ""
        if not archive_name:
            raise HTTPException(status_code=400, detail="Repository archive is required")

        try:
            archive_bytes = await archive.read()
            job = app.state.manager.create_job(
                archive_name=archive_name,
                archive_bytes=archive_bytes,
                language=language,
                model=model,
                prompt=prompt,
                key_family=key_family,
                api_key=api_key.strip(),
                max_attempts=max_attempts,
                package_dir_hint=package_dir,
                tests_dir_hint=tests_dir,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except (tarfile.TarError, zipfile.BadZipFile) as exc:
            raise HTTPException(status_code=400, detail="Invalid repository archive") from exc

        return app.state.manager.serialize_job(job.id)

    webui_dir = Path(__file__).resolve().parent / "webui"
    app.mount("/", StaticFiles(directory=webui_dir.as_posix(), html=True), name="webui")
    return app


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="coverup-web",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    ap.add_argument("--host", default="127.0.0.1", help="host interface to bind")
    ap.add_argument("--port", type=int, default=8000, help="port to listen on")
    ap.add_argument(
        "--data-dir",
        type=lambda value: Path(value).resolve(),
        default=(Path.cwd() / ".coverup-web").resolve(),
        help="directory used to store uploaded repositories and run artifacts",
    )
    args = ap.parse_args(argv)

    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover - optional dependency guard
        print(
            "CoverUp Web UI requires optional web dependencies. "
            "Install them with `pip install .[web]`.",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

    app = create_app(data_dir=args.data_dir)
    uvicorn.run(app, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
