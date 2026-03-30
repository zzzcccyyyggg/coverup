"""Static analysis utilities for Rust source code using tree-sitter.

This module provides functionality analogous to ``go_codeinfo.py`` (which targets
Go), but for Rust source files.  It powers the ``get_info`` tool function exposed
to the LLM when generating Rust tests and supplies additional helpers used by the
Rust backend for richer code context.
"""

import os
import re
import subprocess
import typing as T
from pathlib import Path


# ---------------------------------------------------------------------------
# tree-sitter bootstrap
# ---------------------------------------------------------------------------

_parser = None


def _ensure_parser():
    global _parser
    if _parser is not None:
        return _parser
    try:
        from tree_sitter import Parser  # type: ignore[import-not-found]
        from tree_sitter_languages import get_language  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(
            "Rust code analysis requires 'tree_sitter' and 'tree_sitter_languages' packages"
        ) from exc
    _parser = Parser()
    _parser.set_language(get_language("rust"))
    return _parser


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _node_text(node, source: bytes) -> str:
    """Extract the UTF-8 text of a tree-sitter node."""
    return source[node.start_byte:node.end_byte].decode("utf-8", errors="replace")


def _walk(node):
    """Yield *node* and all of its descendants (pre-order)."""
    yield node
    for child in node.children:
        yield from _walk(child)


def _iter_top_level(root):
    """Yield the immediate children of the root that are declaration items."""
    for child in root.children:
        yield child


# ---------------------------------------------------------------------------
# Symbol finders
# ---------------------------------------------------------------------------

def _find_function(root, source: bytes, name: str):
    """Find a top-level ``fn <name>(…)`` declaration."""
    for child in root.children:
        if child.type == "function_item":
            name_node = child.child_by_field_name("name")
            if name_node and _node_text(name_node, source) == name:
                return child
    return None


def _find_impl_method(root, source: bytes, type_name: str, method_name: str):
    """Find a method inside ``impl <type_name> { fn <method_name>... }``."""
    for child in root.children:
        if child.type == "impl_item":
            # Get the type this impl is for
            impl_type = child.child_by_field_name("type")
            if impl_type and type_name in _node_text(impl_type, source):
                body = child.child_by_field_name("body")
                if body:
                    for item in body.children:
                        if item.type == "function_item":
                            fn_name = item.child_by_field_name("name")
                            if fn_name and _node_text(fn_name, source) == method_name:
                                return item
    return None


def _find_struct(root, source: bytes, name: str):
    """Find a ``struct <name> { … }`` declaration."""
    for child in root.children:
        if child.type == "struct_item":
            name_node = child.child_by_field_name("name")
            if name_node and _node_text(name_node, source) == name:
                return child
    return None


def _find_enum(root, source: bytes, name: str):
    """Find an ``enum <name> { … }`` declaration."""
    for child in root.children:
        if child.type == "enum_item":
            name_node = child.child_by_field_name("name")
            if name_node and _node_text(name_node, source) == name:
                return child
    return None


def _find_trait(root, source: bytes, name: str):
    """Find a ``trait <name> { … }`` declaration."""
    for child in root.children:
        if child.type == "trait_item":
            name_node = child.child_by_field_name("name")
            if name_node and _node_text(name_node, source) == name:
                return child
    return None


def _find_impl_block(root, source: bytes, type_name: str):
    """Find the ``impl <type_name> { … }`` block."""
    for child in root.children:
        if child.type == "impl_item":
            impl_type = child.child_by_field_name("type")
            if impl_type and _node_text(impl_type, source).strip() == type_name:
                return child
    return None


def _find_const_or_static(root, source: bytes, name: str):
    """Find a top-level ``const`` or ``static`` declaration containing *name*."""
    for child in root.children:
        if child.type in ("const_item", "static_item"):
            name_node = child.child_by_field_name("name")
            if name_node and _node_text(name_node, source) == name:
                return child
    return None


def _find_type_alias(root, source: bytes, name: str):
    """Find a ``type <name> = ...;`` alias."""
    for child in root.children:
        if child.type == "type_item":
            name_node = child.child_by_field_name("name")
            if name_node and _node_text(name_node, source) == name:
                return child
    return None


def _find_mod(root, source: bytes, name: str):
    """Find a ``mod <name> { … }`` or ``mod <name>;`` declaration."""
    for child in root.children:
        if child.type == "mod_item":
            name_node = child.child_by_field_name("name")
            if name_node and _node_text(name_node, source) == name:
                return child
    return None


# ---------------------------------------------------------------------------
# Collecting impl methods for a type
# ---------------------------------------------------------------------------

def _collect_methods_for_type(
    source_dir: Path, type_name: str, *, exclude_file: Path | None = None
) -> list[str]:
    """Return source text of all method declarations for *type_name* in the crate."""
    parser = _ensure_parser()
    methods: list[str] = []
    for rs_file in sorted(source_dir.rglob("*.rs")):
        if exclude_file and rs_file.resolve() == exclude_file.resolve():
            continue
        try:
            src = rs_file.read_bytes()
        except OSError:
            continue
        tree = parser.parse(src)
        for child in tree.root_node.children:
            if child.type == "impl_item":
                impl_type = child.child_by_field_name("type")
                if impl_type and type_name in _node_text(impl_type, src):
                    body = child.child_by_field_name("body")
                    if body:
                        for item in body.children:
                            if item.type == "function_item":
                                methods.append(_node_text(item, src))
    return methods


# ---------------------------------------------------------------------------
# Public: get_info for Rust
# ---------------------------------------------------------------------------

def get_info_rust(
    file_path: Path,
    name: str,
    *,
    crate_root: Path | None = None,
    line: int = 0,
) -> str | None:
    """Return summarized information about Rust symbol *name*.

    Supports the following forms of *name*:
    - ``func_name``           – top-level function
    - ``TypeName``            – struct / enum / trait definition
    - ``TypeName::method``    – method on a type (via impl block)
    - ``module::Symbol``      – cross-module lookup (best-effort via ``cargo doc``)

    Returns a string suitable for inclusion in LLM context, or ``None`` if the
    symbol cannot be found.
    """
    parser = _ensure_parser()
    try:
        source = file_path.read_bytes()
    except OSError:
        return None

    tree = parser.parse(source)
    root = tree.root_node

    # Handle Rust's :: separator for Type::method
    parts = name.split("::")

    # ---- Case 1: simple name ----
    if len(parts) == 1:
        sym = parts[0]
        return _lookup_symbol(root, source, file_path, sym, crate_root)

    # ---- Case 2: Type::method or module::symbol ----
    if len(parts) == 2:
        type_or_mod, member = parts

        # Try as Type::method first
        node = _find_impl_method(root, source, type_or_mod, member)
        if node:
            return _format_rust_snippet(node, source, file_path)

        # Search crate for impl method
        if crate_root:
            result = _search_crate_method(crate_root, type_or_mod, member, exclude=file_path)
            if result:
                return result

        # Maybe it's module::symbol — try cargo doc
        return _try_rustdoc(name, crate_root or file_path.parent)

    # ---- Case 3: longer path (e.g., std::collections::HashMap) ----
    return _try_rustdoc(name, crate_root or file_path.parent)


def _lookup_symbol(root, source: bytes, file_path: Path, sym: str,
                   crate_root: Path | None) -> str | None:
    """Look up a simple (non-qualified) symbol name."""
    # function?
    node = _find_function(root, source, sym)
    if node:
        return _format_rust_snippet(node, source, file_path)

    # struct?
    node = _find_struct(root, source, sym)
    if node:
        return _format_rust_type_with_methods(node, source, file_path, sym)

    # enum?
    node = _find_enum(root, source, sym)
    if node:
        return _format_rust_type_with_methods(node, source, file_path, sym)

    # trait?
    node = _find_trait(root, source, sym)
    if node:
        return _format_rust_snippet(node, source, file_path)

    # const / static?
    node = _find_const_or_static(root, source, sym)
    if node:
        return _format_rust_snippet(node, source, file_path)

    # type alias?
    node = _find_type_alias(root, source, sym)
    if node:
        return _format_rust_snippet(node, source, file_path)

    # mod?
    node = _find_mod(root, source, sym)
    if node:
        return _format_rust_snippet(node, source, file_path)

    # search crate
    if crate_root:
        return _search_crate(crate_root, sym, exclude=file_path)

    return None


# ---------------------------------------------------------------------------
# Intra-crate search
# ---------------------------------------------------------------------------

def _search_crate(source_dir: Path, name: str, *, exclude: Path | None = None) -> str | None:
    """Search all ``.rs`` files in the crate for *name*."""
    parser = _ensure_parser()
    for rs_file in sorted(source_dir.rglob("*.rs")):
        if exclude and rs_file.resolve() == exclude.resolve():
            continue
        try:
            src = rs_file.read_bytes()
        except OSError:
            continue
        tree = parser.parse(src)
        root = tree.root_node

        node = _find_function(root, src, name)
        if node:
            return _format_rust_snippet(node, src, rs_file)

        node = _find_struct(root, src, name)
        if node:
            return _format_rust_type_with_methods(node, src, rs_file, name)

        node = _find_enum(root, src, name)
        if node:
            return _format_rust_type_with_methods(node, src, rs_file, name)

        node = _find_trait(root, src, name)
        if node:
            return _format_rust_snippet(node, src, rs_file)

        node = _find_const_or_static(root, src, name)
        if node:
            return _format_rust_snippet(node, src, rs_file)

    return None


def _search_crate_method(
    source_dir: Path, type_name: str, method_name: str, *, exclude: Path | None = None
) -> str | None:
    """Search all ``.rs`` files for a method on *type_name*."""
    parser = _ensure_parser()
    for rs_file in sorted(source_dir.rglob("*.rs")):
        if exclude and rs_file.resolve() == exclude.resolve():
            continue
        try:
            src = rs_file.read_bytes()
        except OSError:
            continue
        tree = parser.parse(src)
        node = _find_impl_method(tree.root_node, src, type_name, method_name)
        if node:
            return _format_rust_snippet(node, src, rs_file)
    return None


# ---------------------------------------------------------------------------
# cargo doc fallback
# ---------------------------------------------------------------------------

def _try_rustdoc(name: str, cwd: Path) -> str | None:
    """Use ``cargo doc`` output or ``rustup doc`` as a fallback for external symbols.

    Since ``cargo doc`` generates HTML, we instead try to use ``rustc --explain``
    for error codes, or fall back to a simple ``cargo metadata`` based approach.
    For standard library types, we provide hardcoded signatures.
    """
    # For common std types, provide a quick answer
    std_docs = _get_std_doc(name)
    if std_docs:
        return std_docs

    # Try running `cargo doc --document-private-items` and searching
    # This is expensive; just return None for now and let the LLM
    # work with what it knows
    return None


_COMMON_STD: dict[str, str] = {
    "Result": "enum Result<T, E> { Ok(T), Err(E) }",
    "Option": "enum Option<T> { Some(T), None }",
    "Vec": "pub struct Vec<T, A: Allocator = Global> { /* ... */ }",
    "String": "pub struct String { /* ... */ }",
    "HashMap": "pub struct HashMap<K, V, S = RandomState> { /* ... */ }",
    "Box": "pub struct Box<T: ?Sized, A: Allocator = Global>(/* ... */);",
    "Arc": "pub struct Arc<T: ?Sized, A: Allocator = Global> { /* ... */ }",
    "Rc": "pub struct Rc<T: ?Sized, A: Allocator = Global> { /* ... */ }",
    "Mutex": "pub struct Mutex<T: ?Sized> { /* ... */ }",
    "RwLock": "pub struct RwLock<T: ?Sized> { /* ... */ }",
    "Cell": "pub struct Cell<T: ?Sized> { /* ... */ }",
    "RefCell": "pub struct RefCell<T: ?Sized> { /* ... */ }",
    "Pin": "pub struct Pin<Ptr> { /* ... */ }",
    "Cow": "pub enum Cow<'a, B: ?Sized + ToOwned + 'a> { Borrowed(&'a B), Owned(<B as ToOwned>::Owned) }",
    "Iterator": "pub trait Iterator { type Item; fn next(&mut self) -> Option<Self::Item>; /* ... */ }",
    "Display": "pub trait Display { fn fmt(&self, f: &mut Formatter<'_>) -> Result; }",
    "Debug": "pub trait Debug { fn fmt(&self, f: &mut Formatter<'_>) -> Result; }",
    "Clone": "pub trait Clone: Sized { fn clone(&self) -> Self; }",
    "Default": "pub trait Default: Sized { fn default() -> Self; }",
    "From": "pub trait From<T>: Sized { fn from(value: T) -> Self; }",
    "Into": "pub trait Into<T>: Sized { fn into(self) -> T; }",
    "AsRef": "pub trait AsRef<T: ?Sized> { fn as_ref(&self) -> &T; }",
    "Deref": "pub trait Deref { type Target: ?Sized; fn deref(&self) -> &Self::Target; }",
    "Drop": "pub trait Drop { fn drop(&mut self); }",
    "Error": "pub trait Error: Debug + Display { fn source(&self) -> Option<&(dyn Error + 'static)>; }",
    "Read": "pub trait Read { fn read(&mut self, buf: &mut [u8]) -> io::Result<usize>; /* ... */ }",
    "Write": "pub trait Write { fn write(&mut self, buf: &[u8]) -> io::Result<usize>; fn flush(&mut self) -> io::Result<()>; /* ... */ }",
    "Serialize": "pub trait Serialize { fn serialize<S: Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error>; }",
    "Deserialize": "pub trait Deserialize<'de>: Sized { fn deserialize<D: Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error>; }",
}


def _get_std_doc(name: str) -> str | None:
    """Return documentation for common standard library types."""
    # Strip std:: prefix
    clean = name
    for prefix in ("std::", "core::", "alloc::", "collections::"):
        if clean.startswith(prefix):
            clean = clean[len(prefix):]

    # Try the last component
    parts = clean.split("::")
    last = parts[-1] if parts else clean

    doc = _COMMON_STD.get(last)
    if doc:
        return f"From Rust standard library:\n```rust\n{doc}\n```"
    return None


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _format_rust_snippet(node, source: bytes, file_path: Path) -> str:
    """Format a single tree-sitter node as a Rust code snippet."""
    text = _node_text(node, source)
    rel = file_path.name
    return f"in {rel}:\n```rust\n{text}\n```"


def _format_rust_type_with_methods(
    node, source: bytes, file_path: Path, type_name: str, *, max_methods: int = 10
) -> str:
    """Format a type definition together with a summary of its impl methods."""
    type_text = _node_text(node, source)
    result = f"in {file_path.name}:\n```rust\n{type_text}\n```"

    methods = _collect_methods_for_type(file_path.parent, type_name)
    if methods:
        shown = methods[:max_methods]
        sigs: list[str] = []
        for m in shown:
            # Extract just the signature (up to the opening brace)
            sig_line = m.split("{")[0].strip()
            if sig_line:
                sigs.append(sig_line)

        if sigs:
            result += "\n\nimpl methods:\n```rust\n" + "\n".join(sigs)
            if len(methods) > max_methods:
                result += f"\n// ... and {len(methods) - max_methods} more methods"
            result += "\n```"

    return result


# ---------------------------------------------------------------------------
# Control-flow analysis for branch inference
# ---------------------------------------------------------------------------

def find_control_flow_nodes(root):
    """Yield control-flow nodes from the AST."""
    for node in _walk(root):
        if node.type in (
            "if_expression",
            "match_expression",
            "while_expression",
            "loop_expression",
            "for_expression",
            "if_let_expression",
        ):
            yield node


def infer_branches(
    path: Path,
    executed_lines: set[int],
    missing_lines: set[int],
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """Infer executed and missing branches from control-flow + line coverage.

    Returns ``(executed_branches, missing_branches)`` where each branch is
    ``(from_line, to_line)`` with ``to_line == 0`` meaning "exit".
    """
    parser = _ensure_parser()
    try:
        source = path.read_bytes()
    except OSError:
        return [], []

    tree = parser.parse(source)
    executed_branches: list[tuple[int, int]] = []
    missing_branches: list[tuple[int, int]] = []

    for node in find_control_flow_nodes(tree.root_node):
        if node.type in ("if_expression", "if_let_expression"):
            _analyze_if(node, source, executed_lines, missing_lines,
                        executed_branches, missing_branches)
        elif node.type == "match_expression":
            _analyze_match(node, source, executed_lines, missing_lines,
                           executed_branches, missing_branches)

    return executed_branches, missing_branches


def _first_body_line_of_block(block_node) -> int | None:
    """Return the first meaningful line inside a block node."""
    for child in block_node.children:
        if child.type not in ("{", "}", "comment", "line_comment", "block_comment"):
            return child.start_point[0] + 1
    return None


def _analyze_if(node, source, executed_lines, missing_lines, exec_br, miss_br):
    """Analyze an if / if-else / if let expression to detect branch coverage."""
    cond_line = node.start_point[0] + 1

    consequence = node.child_by_field_name("consequence")
    alternative = node.child_by_field_name("alternative")

    if consequence:
        first_line = _first_body_line_of_block(consequence)
        if first_line:
            branch = (cond_line, first_line)
            if first_line in executed_lines:
                exec_br.append(branch)
            elif first_line in missing_lines:
                miss_br.append(branch)

    if alternative:
        # alternative may be another if_expression (else if) or a block
        if alternative.type in ("if_expression", "if_let_expression"):
            first_line = alternative.start_point[0] + 1
        else:
            first_line = _first_body_line_of_block(alternative)
        if first_line:
            branch = (cond_line, first_line)
            if first_line in executed_lines:
                exec_br.append(branch)
            elif first_line in missing_lines:
                miss_br.append(branch)


def _analyze_match(node, source, executed_lines, missing_lines, exec_br, miss_br):
    """Analyze match arms for branch coverage."""
    match_line = node.start_point[0] + 1

    body = node.child_by_field_name("body")
    if not body:
        return

    for child in body.children:
        if child.type == "match_arm":
            # The body of a match arm
            value = child.child_by_field_name("value")
            if value:
                first_line = value.start_point[0] + 1
                branch = (match_line, first_line)
                if first_line in executed_lines:
                    exec_br.append(branch)
                elif first_line in missing_lines:
                    miss_br.append(branch)


# ---------------------------------------------------------------------------
# Extract impl type name (for receiver context)
# ---------------------------------------------------------------------------

def extract_impl_type(node, source: bytes) -> str | None:
    """Given an impl_item node, return the implementing type name."""
    if node.type != "impl_item":
        return None
    impl_type = node.child_by_field_name("type")
    if impl_type:
        text = _node_text(impl_type, source).strip()
        # Remove generic parameters for simple name lookup
        match = re.match(r'(\w+)', text)
        return match.group(1) if match else text
    return None


def find_type_definition(root, source: bytes, type_name: str) -> str | None:
    """Find and return the source text of a type definition (struct/enum/trait)."""
    node = _find_struct(root, source, type_name)
    if node:
        return _node_text(node, source)
    node = _find_enum(root, source, type_name)
    if node:
        return _node_text(node, source)
    node = _find_trait(root, source, type_name)
    if node:
        return _node_text(node, source)
    return None
