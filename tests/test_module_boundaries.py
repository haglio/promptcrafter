from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.repo_check

PACKAGE = pathlib.Path(__file__).resolve().parent.parent / "promptcrafter"

LAYERS = {
    "types": 0,
    "paths": 0,
    "win32": 0,
    "errors": 0,
    "kinds": 1,
    "references": 1,
    "switch_state": 1,
    "process_name": 1,
    "schema": 1,
    "schema_overlay": 2,
    "style": 1,
    "state": 2,
    "runtime": 2,
    "transitions": 3,
    "app": 4,
    "opening": 5,
    "__main__": 6,
    "__init__": 0,
}

EDGES = {
    ("__main__", "errors"), ("__main__", "opening"), ("__main__", "paths"),
    ("__main__", "process_name"), ("__main__", "win32"),
    ("opening", "app"), ("opening", "paths"), ("opening", "references"),
    ("opening", "schema_overlay"), ("opening", "win32"),
    ("app", "kinds"), ("app", "runtime"), ("app", "state"),
    ("app", "style"), ("app", "switch_state"), ("app", "transitions"), ("app", "types"),
    ("kinds", "types"),
    ("process_name", "paths"),
    ("references", "types"),
    ("runtime", "kinds"), ("runtime", "switch_state"), ("runtime", "types"),
    ("schema", "types"),
    ("schema_overlay", "paths"), ("schema_overlay", "schema"), ("schema_overlay", "types"),
    ("state", "kinds"), ("state", "switch_state"), ("state", "types"),
    ("switch_state", "types"),
    ("transitions", "runtime"), ("transitions", "switch_state"), ("transitions", "types"),
}


def _edges() -> set[tuple[str, str]]:
    found = set()
    for path in sorted(PACKAGE.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                parts = node.module.split(".")
                if parts[0] == "promptcrafter" and len(parts) > 1:
                    found.add((path.stem, parts[1]))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    parts = alias.name.split(".")
                    if parts[0] == "promptcrafter" and len(parts) > 1:
                        found.add((path.stem, parts[1]))
    return found


def test_every_module_is_placed_in_a_layer():
    assert {p.stem for p in PACKAGE.glob("*.py")} == set(LAYERS)


def test_the_edges_are_the_ones_written_down():
    actual = _edges()
    assert actual == EDGES, (
        f"{len(actual)} edges, {len(EDGES)} declared. "
        f"added: {sorted(actual - EDGES)}; gone: {sorted(EDGES - actual)}"
    )


@pytest.mark.parametrize(("importer", "imported"), sorted(EDGES))
def test_each_import_reaches_down_a_layer(importer, imported):
    assert LAYERS[importer] > LAYERS[imported], (
        f"{importer} (layer {LAYERS[importer]}) imports {imported} "
        f"(layer {LAYERS[imported]})"
    )


def test_the_layering_leaves_no_room_for_a_cycle():
    reachable = {m: {i for (e, i) in EDGES if e == m} for m in LAYERS}
    for start in LAYERS:
        seen, stack = set(), [start]
        while stack:
            for nxt in reachable[stack.pop()]:
                assert nxt != start, f"cycle through {start}"
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
