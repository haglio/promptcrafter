"""The questions the four modules ask about a control's kind.

`ControlKind` is a twelve-member string `Literal`, and until now four modules
each answered "is this a radio kind?" for themselves -- three of them with
`kind.startswith("or")` and the fourth with an explicit set. The two are not the
same question, and neither is the submenu test that looks almost identical to
them, so all three keep a name here rather than being collapsed into whichever
one was written most often.

Nothing validates a kind at any layer: `Literal` is erased at runtime, the
dataclasses have no `__post_init__`, and there is no type checker in the gate.
A kind outside the twelve reaches every one of these predicates unchecked.
"""

from __future__ import annotations

from promptcrafter.types import ControlKind, SubmenuKind

# The four control kinds that hold one selection rather than a list.
RADIO_CONTROL_KINDS: frozenset[ControlKind] = frozenset({"or", "or-adv", "or-adj", "or-prefix"})

# The two submenu kinds that do. `or` and `or-prefix` are control kinds only and
# never appear on a Submenu, which is why the prefix test below happens to give
# the right answer when it is pointed at one.
RADIO_SUBMENU_KINDS: frozenset[SubmenuKind] = frozenset({"or-adv", "or-adj"})

# The submenu kinds whose modifier follows the option text instead of preceding
# it. Note this cuts across the previous set rather than agreeing with it.
ADVERB_SUBMENU_KINDS: frozenset[SubmenuKind] = frozenset({"or-adv", "and-adv"})


def is_radio_kind(kind: str) -> bool:
    """The closed rival: `kind` is one of the four enumerated radio kinds.

    Agrees with :func:`is_or_prefixed_kind` on every one of the twelve declared
    `ControlKind` members -- they part company only on a string that merely
    begins with `or`, such as a thirteenth kind named `or-suffix`. This one
    leaves such a kind out until somebody adds it to the set above.

    Which of the two is right is the owner's to say; `tests/test_kinds.py` holds
    the evidence and will red if a thirteenth `or-*` kind is declared without
    the question being answered.
    """
    return kind in RADIO_CONTROL_KINDS


def is_or_prefixed_kind(kind: str) -> bool:
    """The open rival: `kind` merely begins with `or`.

    Same answers as :func:`is_radio_kind` on everything that exists today (see
    that docstring). This one takes a future `or-*` kind in with no edit here,
    which is convenient if every `or-*` kind is single-select by construction
    and silent on the day one is not.
    """
    return kind.startswith("or")


def is_radio_submenu_kind(kind: str) -> bool:
    """A submenu rendered as radios rather than checkboxes -- an arity question.

    Decides the submenu's state shape (a string, not a list) and its widget
    class. Not the same question as :func:`is_adverb_submenu_kind`, which the
    identical-looking test beside it in the renderer is asking.
    """
    return kind in RADIO_SUBMENU_KINDS


def is_adverb_submenu_kind(kind: str) -> bool:
    """A submenu whose text goes after the option's -- a word-order question.

    Cuts across :func:`is_radio_submenu_kind` rather than agreeing with it: of
    the four submenu kinds the two answer the same for `or-adv` and `and-adj`
    and differently for the other two. Collapsing them would be wrong.
    """
    return kind in ADVERB_SUBMENU_KINDS
