import asyncio
import json

import argparse
import os
import subprocess
import sys
import typing as T

from datetime import datetime
from pathlib import Path

from . import llm
from .languages.base import LanguageBackend
from .languages.go_backend import GoBackend
from .languages.python_backend import PythonBackend
from .languages.rust_backend import RustBackend
from .segment import CodeSegment
from .prompt.prompter import Prompter
from .version import __version__
from .utils import format_branches, summary_coverage
from .python_support import get_required_modules
from .diagnostic_ir import DiagnosticIR, DiagnosticIRBuilder, Phase
from .agents.memory import ReflectiveMemory, SuccessLevel
from .agents.repair import RepairOrchestrator
from .agents.planner import UCBPlanner
from .agents.trace import TraceLogger
from .agents.blocker import extract_blockers, format_blockers_for_prompt


def get_prompters() -> dict[str, T.Callable[[T.Any], Prompter]]:
    # in the future, we may dynamically load based on file names.

    from .prompt.gpt_v1 import GptV1Prompter
    from .prompt.gpt_v2 import GptV2Prompter
    from .prompt.gpt_v2_ablated import GptV2AblatedPrompter
    from .prompt.claude import ClaudePrompter
    from .prompt.gpt_go_v1 import GoGptV1Prompter
    from .prompt.gpt_rust_v1 import RustGptV1Prompter

    return {
        "gpt-v1": GptV1Prompter,
        "gpt-v2": GptV2Prompter,
        "gpt-v2-no-coverage": lambda cmd_args: GptV2AblatedPrompter(cmd_args, with_coverage=False),
        "gpt-v2-no-code-context": lambda cmd_args: GptV2AblatedPrompter(cmd_args, with_get_info=False, with_imports=False),
        "gpt-v2-no-error-fixing": lambda cmd_args: GptV2AblatedPrompter(cmd_args, with_error_fixing=False),
        "gpt-v2-ablated": \
            lambda cmd_args: GptV2AblatedPrompter(cmd_args,
                with_coverage=False, with_get_info=False, with_imports=False, with_error_fixing=False),
        "claude": ClaudePrompter,
        "gpt-go-v1": GoGptV1Prompter,
        "gpt-rust-v1": RustGptV1Prompter,
    }


prompter_registry = get_prompters()


def parse_args(args=None):
    ap = argparse.ArgumentParser(prog='CoverUp',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument('source_files', type=Path, nargs='*',
                    help='only process certain source file(s)')

    def Path_existing_dir(value):
        path_dir = Path(value).resolve()
        if not path_dir.is_dir(): raise argparse.ArgumentTypeError(f"\"{value}\" must be a directory")
        return path_dir

    ap.add_argument('--tests-dir', type=lambda value: Path(value).resolve(), default=None,
                    help='directory where tests reside')

    g = ap.add_mutually_exclusive_group(required=False)
    g.add_argument('--package-dir', type=Path_existing_dir,
                    help='directory with the package sources (e.g., src/flask)')
    g.add_argument('--source-dir', type=Path_existing_dir, dest='package_dir', help=argparse.SUPPRESS)

    ap.add_argument('--language', type=str, choices=['python', 'go', 'rust'], default='python',
                    help='target language for coverage improvement')

    ap.add_argument('--checkpoint', type=Path, 
                    help=f'path to save progress to (and to resume it from)')
    ap.add_argument('--no-checkpoint', action='store_const', const=None, dest='checkpoint', default=argparse.SUPPRESS,
                    help='disable checkpoint')  
    # default 
    def default_model():
        if 'OPENAI_API_KEY' in os.environ:
            return "gpt-4o"
        if 'ANTHROPIC_API_KEY' in os.environ:
            return "anthropic/claude-3-sonnet-20240229"
        if 'AWS_ACCESS_KEY_ID' in os.environ:
            return "anthropic.claude-3-5-sonnet-20241022-v2:0"

    ap.add_argument('--model', type=str, default=default_model(),
                    help='OpenAI model to use')

    ap.add_argument('--prompt', '--prompt-family', type=str,
                    choices=list(prompter_registry.keys()),
                    default='gpt-v2',
                    help='Prompt style to use')

    ap.add_argument('--ollama-api-base', type=str, default="http://localhost:11434",
                    help='"api_base" setting for Ollama models')

    ap.add_argument('--bedrock-anthropic-version', type=str, default="bedrock-2023-05-31",
                    help='"anthropic_version" setting for bedrock Anthropic models')

    ap.add_argument('--model-temperature', type=float, default=0,
                    help='Model "temperature" to use')

    ap.add_argument('--line-limit', type=int, default=50,
                    help='attempt to keep code segment(s) at or below this limit')

    ap.add_argument('--rate-limit', type=int,
                    help='max. tokens/minute to send in prompts')

    ap.add_argument('--max-attempts', type=int, default=3,
                    help='max. number of prompt attempts for a code segment')

    ap.add_argument('--max-backoff', type=int, default=64,
                    help='max. number of seconds for backoff interval')

    ap.add_argument('--dry-run', default=False,
                    action=argparse.BooleanOptionalAction,
                    help=f'whether to actually prompt the model; used for testing')

    ap.add_argument('--show-details', default=False,
                    action=argparse.BooleanOptionalAction,
                    help=f'show details of lines/branches after each response')

    ap.add_argument('--log-file', default=f"coverup-log",
                    help='log file to use')

    ap.add_argument('--pytest-args', type=str, default='',
                    help='extra arguments to pass to pytest')
    ap.add_argument('--go-test-args', type=str, default='',
                    help='extra arguments to pass to go test')

    ap.add_argument('--install-missing-modules', default=False,
                    action=argparse.BooleanOptionalAction,
                    help='attempt to install any missing modules')

    ap.add_argument('--prefix', type=str, default='coverup',
                    help='prefix to use for test file names')

    ap.add_argument('--write-requirements-to', type=Path,
                    help='append the name of any missing modules to the given file')

    ap.add_argument('--repeat-tests', type=int, default=5,
                    help='number of times to repeat test execution to help detect flaky tests')
    ap.add_argument('--no-repeat-tests', action='store_const', const=0, dest='repeat_tests', help=argparse.SUPPRESS)

    ap.add_argument('--disable-polluting', default=False,
                    action=argparse.BooleanOptionalAction,
                    help='look for tests causing others to fail and disable them')

    ap.add_argument('--disable-failing', default=False,
                    action=argparse.BooleanOptionalAction,
                    help='look for failing tests and disable them')

    ap.add_argument('--prompt-for-tests', default=True,
                    action=argparse.BooleanOptionalAction,
                    help='prompt LLM for new tests')

    ap.add_argument('--isolate-tests', default=True,
                    action=argparse.BooleanOptionalAction,
                    help='run tests in isolation (to work around any state pollution) when measuring suite coverage')

    ap.add_argument('--debug', '-d', default=False,
                    action=argparse.BooleanOptionalAction,
                    help='print out debugging messages.')

    ap.add_argument('--add-to-pythonpath', default=True,
                    action=argparse.BooleanOptionalAction,
                    help='add (parent of) source directory to PYTHONPATH')

    ap.add_argument('--branch-coverage', default=True,
                    action=argparse.BooleanOptionalAction,
                    help=argparse.SUPPRESS)

    ap.add_argument('--skip-suite-measurement', default=False,
                    action=argparse.BooleanOptionalAction,
                    help='skip running the existing test suite for baseline/final coverage')

    ap.add_argument('--continue-on-failure', default=False,
                    action=argparse.BooleanOptionalAction,
                    help='do not abort CoverUp when the test suite returns a non-zero exit code; continue processing')

    def positive_int(value):
        ivalue = int(value)
        if ivalue < 0: raise argparse.ArgumentTypeError("must be a number >= 0")
        return ivalue

    ap.add_argument('--max-concurrency', type=positive_int, default=15,
                    help='maximum number of parallel requests; 0 means unlimited')

    ap.add_argument('--save-coverage-to', type=Path_existing_dir,
                    help='save each new test\'s coverage to given directory')

    # ── CoverAgent-ML ablation flags ──
    ap.add_argument('--no-agent-memory', default=False,
                    action='store_true',
                    help='disable ReflectiveMemory (ablation)')
    ap.add_argument('--no-agent-repair', default=False,
                    action='store_true',
                    help='disable tool-first RepairOrchestrator (ablation)')
    ap.add_argument('--no-agent-planner', default=False,
                    action='store_true',
                    help='disable UCB Planner (ablation)')
    ap.add_argument('--no-agent-blocker', default=False,
                    action='store_true',
                    help='disable Coverage Blocker Explanation (ablation)')
    ap.add_argument('--trace-log', type=str, default=None,
                    help='path for JSONL trace log (enables TraceLogger)')

    ap.add_argument('--version', action='version',
                    version=f"%(prog)s v{__version__} (Python {'.'.join(map(str, sys.version_info[:3]))})")

    args = ap.parse_args(args)

    if not args.model:
        ap.error('Specify the model to use with --model')

    if args.tests_dir is None:
        args.tests_dir = Path('tests').resolve()
    else:
        args.tests_dir = args.tests_dir.resolve()

    if args.disable_failing and args.disable_polluting:
        ap.error('Specify only one of --disable-failing and --disable-polluting')

    args.language = args.language.lower()

    if args.language == 'python':
        for i in range(len(args.source_files)):
            if not args.source_files[i].is_file() or args.source_files[i].suffix != '.py':
                ap.error(f'All source files given must be Python sources; offending file: "{args.source_files[i]}".')

            args.source_files[i] = args.source_files[i].resolve()

        if args.package_dir:
            args.src_base_dir = args.package_dir.parent
            if not list(args.package_dir.glob("*.py")):
                sources = sorted(args.package_dir.glob("**/*.py"), key=lambda p: len(p.parts))
                suggestion = sources[0].parent if sources else None

                try:
                    args.package_dir = args.package_dir.relative_to(Path.cwd())
                    suggestion = suggestion.relative_to(Path.cwd()) if suggestion else None
                except ValueError:
                    pass

                ap.error(f'No Python sources found in "{args.package_dir}"' +
                         (f'; did you mean "{suggestion}"?' if suggestion else '.'))

        elif args.source_files:
            if len({p.parent for p in args.source_files}) > 1:
                ap.error('All source files must be in the same directory unless --package-dir is given.')

            args.src_base_dir = args.source_files[0].parent
        else:
            ap.error('Specify either --package-dir or a file name')

        if not args.tests_dir.exists():
            ap.error(f'Directory "{args.tests_dir}" does not exist. Please specify the correct one or create it.')

    elif args.language == 'go':
        if args.source_files:
            ap.error('Specifying individual source files is not supported for Go projects; use --package-dir.')

        if not args.package_dir:
            ap.error('Go support requires --package-dir pointing to the module root.')

        args.src_base_dir = args.package_dir
        args.tests_dir = args.package_dir
        # Branch coverage is now inferred via control-flow analysis in go_codeinfo
        args.branch_coverage = True
        args.install_missing_modules = False
        args.add_to_pythonpath = False

        if args.disable_polluting or args.disable_failing:
            ap.error('Go backend does not support --disable-polluting or --disable-failing yet.')

        if args.prompt == 'gpt-v2' and '--prompt' not in sys.argv:
            args.prompt = 'gpt-go-v1'

    elif args.language == 'rust':
        if args.source_files:
            ap.error('Specifying individual source files is not supported for Rust projects; use --package-dir.')

        if not args.package_dir:
            ap.error('Rust support requires --package-dir pointing to the crate root (containing Cargo.toml).')

        args.src_base_dir = args.package_dir
        args.tests_dir = args.package_dir
        args.branch_coverage = True
        args.install_missing_modules = False
        args.add_to_pythonpath = False

        if args.disable_polluting or args.disable_failing:
            ap.error('Rust backend does not support --disable-polluting or --disable-failing yet.')

        if args.prompt == 'gpt-v2' and '--prompt' not in sys.argv:
            args.prompt = 'gpt-rust-v1'

    else:
        ap.error(f'Unsupported language "{args.language}"')

    return args


def add_to_pythonpath(dir: Path) -> None:
    from .python_support import add_to_pythonpath as _add

    _add(dir)


log_file = None
def log_write(args: argparse.Namespace, seg: CodeSegment, m: str) -> None:
    """Writes to the log file, opening it first if necessary."""

    global log_file
    if not log_file:
        log_file = open(args.log_file, "a", buffering=1)    # 1 = line buffered

    log_file.write(f"---- {datetime.now().isoformat(timespec='seconds')} {seg} ----\n{m}\n")


def check_whole_suite(args: argparse.Namespace) -> None:
    """Check whole suite and disable any polluting/failing tests."""
    import pytest_cleanslate.reduce as reduce

    pytest_args = (*(("--count", str(args.repeat_tests)) if args.repeat_tests else ()), *args.pytest_args.split())

    while True:
        print("Checking test suite...  ", end='', flush=True)
        try:
            results = reduce.run_pytest(args.tests_dir,
                                        pytest_args=(*pytest_args, *(('-x',) if args.disable_polluting else ())),
                                        trace=args.debug)
            if not results.get_first_failed():
                print("tests ok!")
                return

        except subprocess.CalledProcessError as e:
            print(str(e) + "\n" + str(e.stdout, 'UTF-8', errors='ignore'))
            sys.exit(1)

        if args.disable_failing:
            failed = list(results.get_failed())
            print(f"{len(failed)} test(s)/module(s) failed, disabling...")
            to_disable = {Path(reduce.get_module(t)) for t in failed}

        else:
            try:
                reduction = reduce.reduce(tests_path=args.tests_dir, results=results,
                                          pytest_args=pytest_args, trace=args.debug)
            except subprocess.CalledProcessError as e:
                print(str(e) + "\n" + str(e.stdout, 'UTF-8', errors='ignore'))
                sys.exit(1)

            if 'error' in reduction:
                sys.exit(1)

            # FIXME add check for disabling too much
            # FIXME could just disable individual tests rather than always entire modules
            to_disable = {Path(reduce.get_module(m)) for m in (reduction['modules'] + reduction['tests'])}

        for t in to_disable:
            print(f"Disabling {t}")
            t.rename(t.parent / ("disabled_" + t.name))

PROGRESS_COUNTERS=['G', 'F', 'U', 'R']  # good, failed, useless, retry
class Progress:
    """Tracks progress, showing a tqdm-based bar."""

    def __init__(self, total, initial):
        import tqdm
        from collections import OrderedDict

        self._bar = tqdm.tqdm(total=total, initial=initial)

        self._postfix = OrderedDict()
        for p in [*PROGRESS_COUNTERS, 'cost']:
            self._postfix[p] = ''  # to establish order

        self._bar.set_postfix(ordered_dict=self._postfix)

    def update_cost(self, cost: float):
        self._postfix['cost'] = f'~${cost:.02f}'
        self._bar.set_postfix(ordered_dict=self._postfix)

    def update_counters(self, counters: dict):
        """Updates the counters display."""
        for k in counters:
            self._postfix[k] = counters[k]

        self._bar.set_postfix(ordered_dict=self._postfix)

    def signal_one_completed(self):
        """Signals an item completed."""
        self._bar.update()

    def close(self):
        """Closes the underlying tqdm bar."""
        self._bar.close()


class State:
    def __init__(self, initial_coverage: dict):
        """Initializes the CoverUp state."""
        from collections import defaultdict

        self._done : T.Dict[Path, T.Set[T.Tuple[int, int]]] = defaultdict(set)
        self._coverage = initial_coverage
        self._cost = 0.0
        self._counters = {k:0 for k in PROGRESS_COUNTERS}
        self._final_coverage: dict|None = None
        self._bar: Progress|None = None


    def get_initial_coverage(self) -> dict:
        """Returns the coverage initially measured."""
        return self._coverage


    def set_final_coverage(self, cov: dict) -> None:
        """Adds the final coverage obtained, so it can be saved in a checkpoint."""
        self._final_coverage = cov


    def set_progress_bar(self, bar: Progress):
        """Specifies a progress bar to update."""
        self._bar = bar
        if bar is not None:
            self._bar.update_cost(self._cost)
            self._bar.update_counters(self._counters)


    def add_cost(self, cost: float) -> None:
        self._cost += cost
        if self._bar:
            self._bar.update_cost(self._cost)


    def inc_counter(self, key: str):
        """Increments a progress counter."""
        self._counters[key] += 1

        if self._bar:
            self._bar.update_counters(self._counters)


    def mark_done(self, seg: CodeSegment):
        """Marks a segment done."""
        self._done[seg.path].add((seg.begin, seg.end))


    def is_done(self, seg: CodeSegment):
        """Returns whether a segment is done."""
        return (seg.begin, seg.end) in self._done[seg.path]


    @staticmethod
    def load_checkpoint(ckpt_file: Path):   # -> State
        """Loads state from a checkpoint."""
        try:
            with ckpt_file.open("r") as f:
                ckpt = json.load(f)
                if ckpt['version'] != 2: return None
                assert 'done' in ckpt
                assert 'cost' in ckpt
                assert 'counters' in ckpt
                assert 'coverage' in ckpt, "coverage information missing in checkpoint"

                state = State(ckpt['coverage'])
                state._cost = ckpt['cost']
                state._counters = ckpt['counters']
                for filename, done_list in ckpt['done'].items():
                    state._done[Path(filename).resolve()] = set(tuple(d) for d in done_list)
                return state

        except FileNotFoundError:
            return None


    def save_checkpoint(self, ckpt_file: Path):
        """Saves this state to a checkpoint file."""
        ckpt = {
            'version': 2,
            'done': {str(k):list(v) for k,v in self._done.items() if len(v)}, # cannot serialize 'Path' or 'set' as-is
            'cost': self._cost,
            'counters': self._counters,
            'coverage': self._coverage,
            **({'final_coverage': self._final_coverage} if self._final_coverage else {})
            # FIXME save missing modules
        }

        with ckpt_file.open("w") as f:
            json.dump(ckpt, f)


def extract_python(response: str) -> str:
    # This regex accepts a truncated code block... this seems fine since we'll try it anyway
    m = re.search(r'```python\n(.*?)(?:```|\Z)', response, re.DOTALL)
    if not m: raise RuntimeError(f"Unable to extract Python code from response {response}")
    return m.group(1)


# ── CoverAgent-ML shared instances ──────────────────────────────────────

state: State
memory: T.Optional[ReflectiveMemory] = None
repair_orchestrator: T.Optional[RepairOrchestrator] = None
planner: T.Optional[UCBPlanner] = None
trace_logger: T.Optional[TraceLogger] = None
use_blocker: bool = True


async def improve_coverage(
    args: argparse.Namespace,
    backend: LanguageBackend,
    chatter: llm.Chatter,
    prompter: Prompter,
    seg: CodeSegment
) -> bool:
    """Works to improve coverage for a code segment.

    CoverAgent-ML enhanced loop:
    1. Inject reflective memory lessons into initial prompt
    2. On compile/run failure → classify into DiagnosticIR
    3. Try tool-first repair *before* falling back to LLM
    4. Record failure in reflective memory
    5. Update UCB planner with reward signal
    """
    global memory, repair_orchestrator, planner, trace_logger, use_blocker

    messages = prompter.initial_prompt(seg)

    # ── Inject coverage blocker analysis into the conversation ──
    if use_blocker:
        try:
            blockers = extract_blockers(
                seg.path, seg.missing_lines, seg.missing_branches,
                seg.executed_lines, backend.language_id,
            )
            blocker_text = format_blockers_for_prompt(blockers)
            if blocker_text:
                from .prompt.prompter import mk_message
                messages.append(mk_message(blocker_text, role="user"))
                log_write(args, seg, f"[BLOCKER] Injected {len(blockers)} blocker(s)")
        except Exception as e:
            log_write(args, seg, f"[BLOCKER] Extraction failed: {e}")

    # ── Inject memory lessons into the conversation ──
    if memory:
        lessons = memory.format_for_prompt(backend.language_id)
        if lessons:
            from .prompt.prompter import mk_message
            messages.append(mk_message(lessons, role="user"))
            log_write(args, seg, f"[MEMORY] Injected {memory.size} lessons")

    attempts = 0
    tool_repair_used = 0  # counter for logging

    if args.dry_run:
        return True

    while True:
        attempts += 1
        if (attempts > args.max_attempts):
            log_write(args, seg, "Too many attempts, giving up")
            break

        if not (response := await chatter.chat(messages, ctx=seg)):
            log_write(args, seg, "giving up")
            break

        response_message = response["choices"][0]["message"]
        messages.append(response_message)

        if not (last_test := backend.extract_test_code(response_message['content'])):
            log_write(args, seg, "No test code in model response, giving up")
            break

        log_cb = lambda message: log_write(args, seg, message)

        if not backend.handle_missing_dependencies(seg, last_test, log_cb):
            return False

        try:
            coverage = await backend.measure_test_coverage(
                seg,
                last_test,
                isolate_tests=args.isolate_tests,
                branch_coverage=args.branch_coverage,
                log_write=log_cb,
            )

        except subprocess.TimeoutExpired:
            log_write(args, seg, "measure_coverage timed out")
            # Record timeout in DiagnosticIR + memory
            ir = (
                DiagnosticIRBuilder(language=backend.language_id, phase=Phase.RUN.value)
                .timeout()
                .tool(backend._default_tool_name())
                .message("Test execution timed out")
                .build()
            )
            if memory:
                memory.record(ir, action="timeout", level=SuccessLevel.NONE)
            if planner:
                planner.update(seg.identify(), ir)
            if trace_logger:
                trace_logger.log_attempt(
                    seg_id=seg.identify(), attempt=attempts,
                    action="llm", ir=ir, outcome="timeout",
                    tool_fixes=[],
                    memory_injected=memory is not None,
                    extra={"blocker_injected": use_blocker},
                )
            return True

        except subprocess.CalledProcessError as e:
            state.inc_counter('F')
            raw_output = str(e.stdout, 'UTF-8', errors='ignore') if e.stdout else str(e)

            # ── DiagnosticIR classification ──
            ir = backend.classify_error(raw_output, phase=Phase.COMPILE.value)
            if memory:
                memory.record(ir, action=f"llm_{ir.error_category}",
                              level=SuccessLevel.NONE)
            if planner:
                planner.update(seg.identify(), ir)
            if trace_logger:
                trace_logger.log_attempt(
                    seg_id=seg.identify(), attempt=attempts,
                    action="llm", ir=ir, outcome="F",
                    tool_fixes=[],
                    memory_injected=memory is not None,
                    extra={"blocker_injected": use_blocker},
                )

            log_write(args, seg,
                f"[DIAG] {ir.short_summary()} "
                f"(category={ir.error_category}, code={ir.error_code})")

            # ── Phase 1: tool-first repair ──
            patched, fix_names = (
                repair_orchestrator.try_tool_repair(last_test, ir, backend)
                if repair_orchestrator else (last_test, [])
            )
            if fix_names:
                tool_repair_used += 1
                log_write(args, seg,
                    f"[REPAIR] Tool-first fixes applied: {fix_names}")
                last_test = patched
                # Re-verify the patched code without an LLM call
                try:
                    coverage = await backend.measure_test_coverage(
                        seg,
                        last_test,
                        isolate_tests=args.isolate_tests,
                        branch_coverage=args.branch_coverage,
                        log_write=log_cb,
                    )
                    # If we get here, the tool repair succeeded!
                    log_write(args, seg,
                        f"[REPAIR] Tool repair succeeded — skipping LLM error prompt")
                    # Don't record here — fall through to coverage check
                    # which will record FULL (G) or PARTIAL (U) correctly
                except subprocess.CalledProcessError:
                    # Tool repair didn't fully fix it — fall back to LLM
                    log_write(args, seg,
                        f"[REPAIR] Tool repair partial — falling back to LLM")
                    error = backend.format_test_error(raw_output)
                    # Add memory-based hint to error prompt
                    if memory:
                        memory_hint = memory.format_entry_for_error(ir)
                        if memory_hint:
                            error = error + "\n\n" + memory_hint
                    if not (prompts := prompter.error_prompt(seg, error)):
                        log_write(args, seg, "Test failed:\n\n" + error)
                        break
                    messages.extend(prompts)
                    continue
                except subprocess.TimeoutExpired:
                    return True
            else:
                # ── Phase 2: LLM fallback ──
                error = backend.format_test_error(raw_output)
                # Add memory-based hint
                memory_hint = memory.format_entry_for_error(ir) if memory else None
                if memory_hint:
                    error = error + "\n\n" + memory_hint
                log_write(args, seg, f"[DEBUG] test FAILED (exit {e.returncode}). "
                           f"Formatted error sent to LLM ({len(error)} chars):\n{error}\n")
                if not (prompts := prompter.error_prompt(seg, error)):
                    log_write(args, seg, "Test failed:\n\n" + error)
                    break
                messages.extend(prompts)
                continue

        except RuntimeError as e:
            state.inc_counter('F')
            error = str(e)
            ir = (
                DiagnosticIRBuilder(language=backend.language_id, phase=Phase.COMPILE.value)
                .fail()
                .tool(backend._default_tool_name())
                .error("unknown", "", error)
                .build()
            )
            if memory:
                memory.record(ir, action="runtime_error", level=SuccessLevel.NONE)
            if trace_logger:
                trace_logger.log_attempt(
                    seg_id=seg.identify(), attempt=attempts,
                    action="llm", ir=ir, outcome="F",
                    tool_fixes=[],
                    memory_injected=memory is not None,
                    extra={"blocker_injected": use_blocker},
                )
            log_write(args, seg, f"[DEBUG] test size limit exceeded: {error}")
            if not (prompts := prompter.error_prompt(seg, error)):
                log_write(args, seg, "Test too large:\n\n" + error)
                break

            messages.extend(prompts)
            continue

        result = coverage['files'].get(seg.filename, None)
        if result is None:
            # Debug: log available keys to diagnose key mismatch
            available_keys = list(coverage['files'].keys())[:10]
            log_write(args, seg, f"[DEBUG] coverage key mismatch! "
                       f"seg.filename={seg.filename!r} not in coverage files. "
                       f"Available keys (first 10): {available_keys}")
        new_lines = set(result['executed_lines']) if result else set()
        new_branches = set(tuple(b) for b in result['executed_branches']) if (result and \
                                                                              'executed_branches' in result) \
                       else set()
        gained_lines = seg.missing_lines.intersection(new_lines)
        gained_branches = seg.missing_branches.intersection(new_branches)

        log_write(args, seg, f"[DEBUG] coverage check: "
                   f"seg.missing_lines={sorted(seg.missing_lines)}, "
                   f"new_executed={sorted(new_lines)[:20]}{'...' if len(new_lines)>20 else ''}, "
                   f"total_new_lines={len(new_lines)}, "
                   f"target_in_new={sorted(seg.missing_lines.intersection(new_lines))}, "
                   f"gained_lines={sorted(gained_lines)}, "
                   f"gained_branches={sorted(gained_branches)}")

        if args.show_details:
            print(seg.identify())
            print(f"Originally missing: {sorted(seg.missing_lines)}")
            print(f"                    {list(format_branches(seg.missing_branches))}")
            print(f"Gained:             {sorted(gained_lines)}")
            print(f"                    {list(format_branches(gained_branches))}")

        if not gained_lines and not gained_branches:
            state.inc_counter('U')
            # Record as useless (ok but no coverage gain)
            ir = (
                DiagnosticIRBuilder(language=backend.language_id, phase=Phase.COVERAGE.value)
                .ok()
                .tool(backend._default_tool_name())
                .message("Test compiled and ran but gained no new coverage")
                .coverage_delta(0.0, 0.0)
                .build()
            )
            if planner:
                planner.update(seg.identify(), ir)
            if memory:
                memory.record(ir, action="llm", level=SuccessLevel.PARTIAL)
            if trace_logger:
                trace_logger.log_attempt(
                    seg_id=seg.identify(), attempt=attempts,
                    action="llm", ir=ir, outcome="U",
                    tool_fixes=[],
                    memory_injected=memory is not None,
                    extra={"blocker_injected": use_blocker},
                )
            log_write(args, seg, f"[DEBUG] USELESS: test compiled & ran but gained no coverage. "
                       f"This usually means the test doesn't exercise the target lines/branches.")

            # ── Re-inject blocker analysis for missing_coverage_prompt ──
            if use_blocker:
                try:
                    blockers = extract_blockers(
                        seg.path, seg.missing_lines, seg.missing_branches,
                        seg.executed_lines, backend.language_id,
                    )
                    blocker_text = format_blockers_for_prompt(blockers)
                except Exception:
                    blocker_text = ""
            else:
                blocker_text = ""

            if not (prompts := prompter.missing_coverage_prompt(seg, seg.missing_lines, seg.missing_branches)):
                log_write(args, seg, "Test doesn't improve coverage")
                break

            if blocker_text:
                from .prompt.prompter import mk_message
                # Insert blocker BEFORE the missing_coverage prompt
                # so LLM sees "why not reached" before "what to cover"
                prompts.insert(0, mk_message(blocker_text, role="user"))

            messages.extend(prompts)
            continue

        asked = {'lines': sorted(seg.missing_lines), 'branches': sorted(seg.missing_branches)}
        gained = {'lines': sorted(gained_lines), 'branches': sorted(gained_branches)}

        new_test_path = backend.save_successful_test(seg, last_test, asked, gained)
        log_write(args, seg, f"Saved as {new_test_path}\n")
        state.inc_counter('G')

        # Record success in DiagnosticIR + memory + planner
        delta_l = len(gained_lines) / max(len(seg.missing_lines), 1)
        delta_b = len(gained_branches) / max(len(seg.missing_branches), 1) if seg.missing_branches else 0.0
        ir = (
            DiagnosticIRBuilder(language=backend.language_id, phase=Phase.COVERAGE.value)
            .ok()
            .tool(backend._default_tool_name())
            .message(f"Gained {len(gained_lines)} lines, {len(gained_branches)} branches")
            .coverage_delta(delta_l, delta_b)
            .build()
        )
        if memory:
            action = f"tool_repair+llm" if tool_repair_used > 0 else "llm"
            memory.record(ir, action=action, level=SuccessLevel.FULL)
        if planner:
            planner.update(seg.identify(), ir)
        if trace_logger:
            trace_logger.log_attempt(
                seg_id=seg.identify(), attempt=attempts,
                action="tool_repair+llm" if tool_repair_used > 0 else "llm",
                ir=ir, outcome="G",
                tool_fixes=[],
                memory_injected=memory is not None,
                extra={"blocker_injected": use_blocker},
            )

        if tool_repair_used > 0:
            log_write(args, seg,
                f"[AGENT] Tool repairs used: {tool_repair_used} in this segment")

        if args.save_coverage_to:
            target_path = Path(new_test_path)
            with (args.save_coverage_to / (target_path.stem + ".json")).open("w") as f:
                json.dump(coverage, f)

        # TODO re-add segment with remaining missing coverage?
        break

    return True # finished


def main():
    global state, memory, repair_orchestrator, planner, trace_logger, use_blocker
    args = parse_args()

    # ── CoverAgent-ML: initialise agent modules (respecting ablation flags) ──
    memory = ReflectiveMemory() if not args.no_agent_memory else None
    repair_orchestrator = RepairOrchestrator() if not args.no_agent_repair else None
    # Planner is initialised later (after we know segment count) for size-adaptive tuning
    planner = None  # set below after segment counting
    _planner_enabled = not args.no_agent_planner
    trace_logger = TraceLogger(args.trace_log) if args.trace_log else None
    use_blocker = not args.no_agent_blocker

    backend_map: dict[str, type[LanguageBackend]] = {
        'python': PythonBackend,
        'go': GoBackend,
        'rust': RustBackend,
    }

    backend = backend_map[args.language](args)

    try:
        backend.prepare_environment()
    except RuntimeError as exc:
        print(str(exc))
        return 1

    if args.prompt_for_tests:
        try:
            chatter = llm.Chatter(model=args.model)
            chatter.set_log_msg(lambda ctx, msg: log_write(args, ctx, msg))
            chatter.set_log_json(lambda ctx, j: log_write(args, ctx, json.dumps(j, indent=2)))
            chatter.set_signal_retry(lambda: state.inc_counter('R'))

            chatter.set_model_temperature(args.model_temperature)
            chatter.set_max_backoff(args.max_backoff)

            if args.rate_limit:
                chatter.set_token_rate_limit((args.rate_limit, 60))

            extra_request_pars = {}
            if "ollama" in args.model:
                extra_request_pars['api_base'] = args.ollama_api_base
            if args.model.startswith("bedrock/anthropic"):
                extra_request_pars['anthropic_version'] = args.bedrock_anthropic_version
            chatter.set_extra_request_pars(extra_request_pars)

            prompter = prompter_registry[args.prompt](cmd_args=args)
            for f in prompter.get_functions():
                chatter.add_function(f)

        except llm.ChatterError as e:
            print(e)
            return 1

        log_write(args, 'startup', f"Command: {' '.join(sys.argv)}")

        # --- (1) load or measure initial coverage, figure out segmentation ---

        if args.checkpoint and (state := State.load_checkpoint(args.checkpoint)):
            print("Continuing from checkpoint;  coverage: ", end='', flush=True)
            coverage = state.get_initial_coverage()
        else:
            if args.skip_suite_measurement:
                print("Skipping initial coverage measurement; using synthetic zero coverage.")
                coverage = backend.initial_empty_coverage()
                state = State(coverage)
            else:
                if args.language == 'python' and (args.disable_polluting or args.disable_failing):
                    # check and clean up suite before measuring coverage
                    check_whole_suite(args)

                try:
                    print("Measuring coverage...  ", end='', flush=True)
                    coverage = backend.measure_suite_coverage(
                        pytest_args=args.pytest_args,
                        isolate_tests=args.isolate_tests,
                        branch_coverage=args.branch_coverage,
                        trace=(print if args.debug else None),
                        raise_on_failure=not args.continue_on_failure,
                    )
                    state = State(coverage)

                except subprocess.CalledProcessError as e:
                    print("Error measuring coverage:\n" + str(e.stdout, 'UTF-8', errors='ignore'))
                    return 1

        print(summary_coverage(coverage, args.source_files))
        # TODO also show running coverage estimate

        chatter.set_add_cost(state.add_cost)

        segments = sorted(backend.get_missing_coverage(state.get_initial_coverage(), line_limit=args.line_limit),
                          key=lambda seg: seg.missing_count(), reverse=True)

        # save initial coverage so we don't have to redo it next time
        if args.checkpoint:
            state.save_checkpoint(args.checkpoint)

        # --- (2) prompt for tests ---

        print(f"Prompting {args.model} for tests to increase coverage...")
        print("(in the following, G=good, F=failed, U=useless and R=retry)")

        async def work_segment(seg: CodeSegment) -> None:
            if await improve_coverage(args, backend, chatter, prompter, seg):
                # Only mark done if was able to complete (True return),
                # so that it can be retried after installing any missing modules
                state.mark_done(seg)
                if planner:
                    planner.mark_completed(seg.identify())

            if args.checkpoint:
                state.save_checkpoint(args.checkpoint)
            progress.signal_one_completed()

        # Build segment lookup: seg.identify() → seg
        seg_lookup: dict[str, CodeSegment] = {}
        worklist = []
        seg_done_count = 0
        for seg in segments:
            if not seg.path.is_relative_to(args.src_base_dir):
                continue

            if args.source_files and seg.path not in args.source_files:
                continue

            if state.is_done(seg):
                seg_done_count += 1
            else:
                seg_id = seg.identify()
                seg_lookup[seg_id] = seg
                worklist.append(seg)  # store segments, not coroutines

        # ── Size-adaptive planner initialisation ──
        num_segments = len(worklist)
        if _planner_enabled:
            if num_segments < 20:
                # Small project: less exploration, more passes (conservative)
                planner = UCBPlanner(c=0.8, min_passes=2)
            elif num_segments > 80:
                # Large project: more exploration, benefit from learning
                planner = UCBPlanner(c=2.0, min_passes=2)
            else:
                # Medium project: defaults
                planner = UCBPlanner(c=1.5, min_passes=2)
            print(f"[CoverAgent-ML] Planner: c={planner.c}, "
                  f"min_passes={planner.min_passes}, segments={num_segments}")

        # Register arms after planner is created
        for seg in worklist:
            if planner:
                planner.add_arm(
                    seg.identify(),
                    missing_lines=len(seg.missing_lines),
                    missing_branches=len(seg.missing_branches),
                )

        progress = Progress(total=len(seg_lookup)+seg_done_count, initial=seg_done_count)
        state.set_progress_bar(progress)

        async def run_it():
            concurrency = args.max_concurrency or len(seg_lookup) or 1

            if planner and not args.no_agent_planner:
                # ── Batch-wave loop driven by planner.select_batch() ──
                # Each wave: planner picks top-k segments, we run them
                # concurrently, then planner re-scores for the next wave.
                semaphore = asyncio.Semaphore(concurrency)
                while planner.has_active_arms():
                    batch_ids = planner.select_batch(k=concurrency)
                    if not batch_ids:
                        break

                    async def sem_work(s):
                        async with semaphore:
                            await work_segment(s)

                    batch_coros = []
                    for sid in batch_ids:
                        seg = seg_lookup.get(sid)
                        if seg and not state.is_done(seg):
                            batch_coros.append(sem_work(seg))
                    if not batch_coros:
                        break
                    await asyncio.gather(*batch_coros)
            else:
                # ── Baseline: schedule all segments at once ──
                if concurrency < len(worklist):
                    semaphore = asyncio.Semaphore(concurrency)

                    async def sem_coro(s):
                        async with semaphore:
                            await work_segment(s)

                    await asyncio.gather(*(sem_coro(s) for s in worklist))
                else:
                    await asyncio.gather(*(work_segment(s) for s in worklist))

        try:
            asyncio.run(run_it())
        except KeyboardInterrupt:
            print("Interrupted.")
            if args.checkpoint:
                state.save_checkpoint(args.checkpoint)
            return 1
        finally:
            # Suppress noisy "Fatal error on SSL transport" messages that
            # Python 3.10 asyncio spews when the event loop closes while
            # httpx/litellm still have open SSL connections.  These are
            # harmless but alarming-looking.
            import logging
            logging.getLogger("asyncio").setLevel(logging.CRITICAL)

        progress.close()

        # ── CoverAgent-ML: print agent statistics ──
        if memory and memory.size > 0:
            print(f"\n[CoverAgent-ML] Memory: {memory.size} lessons recorded")
            stats = memory.get_stats()
            if stats:
                print(f"  Error categories: {stats}")
        if planner:
            gs = planner.get_global_stats()
            print(f"  Planner: {gs['total_pulls']} pulls across {gs['num_arms']} arms")
        if trace_logger:
            trace_logger.close()
            print(f"  Trace log written to: {args.trace_log}")

    # --- (3) clean up resulting test suite ---

    if args.language == 'python' and (args.disable_polluting or args.disable_failing):
        check_whole_suite(args)

    # --- (4) show final coverage

    if args.prompt_for_tests and not args.skip_suite_measurement:
        try:
            print("Measuring coverage...  ", end='', flush=True)
            coverage = backend.measure_suite_coverage(
                pytest_args=args.pytest_args,
                isolate_tests=args.isolate_tests,
                branch_coverage=args.branch_coverage,
                trace=(print if args.debug else None),
                raise_on_failure=not args.continue_on_failure,
            )

        except subprocess.CalledProcessError as e:
            print("Error measuring coverage:\n" + str(e.stdout, 'UTF-8', errors='ignore'))
            return 1

        print(summary_coverage(coverage, args.source_files))

    # --- (5) save state and show missing modules, if appropriate

        if args.checkpoint:
            state.set_final_coverage(coverage)
            state.save_checkpoint(args.checkpoint)

        if not args.install_missing_modules and (required := get_required_modules()):
            print(f"Some modules seem to be missing:  {', '.join(str(m) for m in required)}")
            if args.write_requirements_to:
                with args.write_requirements_to.open("a") as f:
                    for module in required:
                        f.write(f"{module}\n")
    elif args.prompt_for_tests and args.skip_suite_measurement:
        print("Skipping final coverage measurement due to --skip-suite-measurement.")

    return 0
