"""The package's own import graph, as a number that can fail.

Length and coverage measure tidiness; neither says anything about coupling,
which is the property that actually decides whether this stays workable. So the
edges between these modules are written down here and checked, and adding one
means editing this file on purpose.

It has already earned it once. Consolidating the submenu key put a
`runtime -> state` edge in -- the pure renderer importing the module that
builds initial state, for a one-line string format. Acyclic, harmless, and
exactly the kind of edge nobody notices; the key moved to `types`, where both
sides already were.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

PACKAGE = pathlib.Path(__file__).resolve().parent.parent / "promptcrafter"

# Lower may not import higher, and equal may not import equal. Anything that
# would need to is telling you the layers are wrong, not that the rule is.
LAYERS = {
    "types": 0,        # dataclasses, literals, and how a submenu's state is keyed
    "paths": 0,        # filesystem, no schema knowledge
    "win32": 0,        # platform shims
    "kinds": 1,        # which control kinds mean what
    "toggle_state": 1,
    "process_name": 1,
    "schema": 1,       # the shipped config
    "style": 1,        # the stylesheet and the copy button's mark
    "state": 2,        # builds the state dict from a schema
    "runtime": 2,      # renders a prompt from schema plus state
    "transitions": 3,  # what a click does to the state
    "app": 4,          # widgets and wiring
    "__main__": 5,
    "__init__": 0,
}

# Every intra-package edge that exists. 21 of them.
EDGES = {
    ("__main__", "app"), ("__main__", "paths"), ("__main__", "process_name"),
    ("__main__", "schema"), ("__main__", "win32"),
    ("app", "kinds"), ("app", "paths"), ("app", "runtime"), ("app", "state"),
    ("app", "style"), ("app", "toggle_state"), ("app", "transitions"), ("app", "types"),
    ("kinds", "types"),
    ("process_name", "paths"),
    ("runtime", "kinds"), ("runtime", "toggle_state"), ("runtime", "types"),
    ("schema", "types"),
    ("state", "kinds"), ("state", "toggle_state"), ("state", "types"),
    ("style", "paths"),
    ("toggle_state", "types"),
    ("transitions", "runtime"), ("transitions", "toggle_state"), ("transitions", "types"),
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
    """Strictly-decreasing edges cannot close a loop; this says so out loud."""
    reachable = {m: {i for (e, i) in EDGES if e == m} for m in LAYERS}
    for start in LAYERS:
        seen, stack = set(), [start]
        while stack:
            for nxt in reachable[stack.pop()]:
                assert nxt != start, f"cycle through {start}"
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
