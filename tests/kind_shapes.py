from __future__ import annotations

from promptcrafter.types import ManyOf, OneOf, Switch

SHAPES_BY_KIND = {
    "or": (OneOf,), "or-adv": (OneOf,), "or-adj": (OneOf,), "or-prefix": (OneOf,),
    "and-commas": (ManyOf,), "and-commas-adj": (ManyOf,), "and-commas-adv": (ManyOf,),
    "and-spaces-adj": (ManyOf,), "required": (ManyOf,), "hidden-opposite": (ManyOf,),
    "switch": (Switch, ManyOf), "global-selector": (Switch, OneOf),
}

KINDS_WHOSE_CONTROL_PICKS_ITS_SHAPE = frozenset(
    kind for kind, shapes in SHAPES_BY_KIND.items() if len(shapes) > 1)
