"""The private-schema overlay: what it reads, and what it does without one.

Every fixture here is fabricated. The overlay's whole reason for existing is
that a real schema may not enter this repo, so a test that made one "realistic"
would be the leak the feature exists to prevent.
"""
import json

import pytest

from promptcrafter import schema_overlay
from promptcrafter.schema import schema as demo_schema
from promptcrafter.schema_overlay import (
    OVERLAY_NAME,
    load_schema,
    overlay_path,
    schema_from_document,
)
from promptcrafter.state import create_initial_state
from promptcrafter.types import PluralText, TemplateText, TextRef

MINIMAL = {
    "sections": [
        {
            "id": "alpha",
            "text": {"singular": "alpha", "plural": "alphas"},
            "controls": [
                {
                    "id": "beta",
                    "text": {"singular": "beta", "plural": "betas"},
                    "kind": "or",
                    "options": [
                        {"id": "gamma", "text": {"singular": "gamma", "plural": "gammas"}},
                    ],
                },
            ],
        },
    ],
}


def _with_control(control):
    return {"sections": [{**MINIMAL["sections"][0], "controls": [control]}]}


def test_a_checkout_without_an_overlay_gets_the_demo_schema(monkeypatch, tmp_path):
    monkeypatch.setattr(schema_overlay, "project_root", lambda: tmp_path)
    assert not overlay_path().exists()
    assert load_schema() is demo_schema


def test_an_overlay_beside_the_checkout_wins(monkeypatch, tmp_path):
    (tmp_path / OVERLAY_NAME).write_text(json.dumps(MINIMAL), encoding="utf-8")
    monkeypatch.setattr(schema_overlay, "project_root", lambda: tmp_path)

    loaded = load_schema()

    assert loaded is not demo_schema
    assert [s.id for s in loaded.sections] == ["alpha"]


def test_a_directory_named_like_the_overlay_is_not_one(monkeypatch, tmp_path):
    """``is_file``, not ``exists``: a stray directory must not crash the launch."""
    (tmp_path / OVERLAY_NAME).mkdir()
    monkeypatch.setattr(schema_overlay, "project_root", lambda: tmp_path)

    assert load_schema() is demo_schema


def test_the_overlay_is_looked_for_in_this_checkout_not_the_primary(monkeypatch, tmp_path):
    """A worktree runs the tree under test, never the user's real schema."""
    monkeypatch.setattr(schema_overlay, "project_root", lambda: tmp_path)
    assert overlay_path() == tmp_path / OVERLAY_NAME


# --- the camelCase document, key by key ---

def test_a_bare_string_is_a_text_value():
    built = schema_from_document(
        _with_control({"id": "beta", "text": "beta", "kind": "or", "options": []})
    )
    assert built.sections[0].controls[0].text == "beta"


def test_singular_and_plural_strings_become_plural_text():
    text = schema_from_document(MINIMAL).sections[0].controls[0].text
    assert text == PluralText(singular="beta", plural="betas")


def test_a_lone_singular_repeats_as_the_plural():
    built = schema_from_document(
        _with_control({"id": "beta", "text": {"singular": "beta"}, "kind": "or", "options": []})
    )
    assert built.sections[0].controls[0].text == PluralText(singular="beta", plural="beta")


def test_a_list_of_parts_becomes_a_template_with_its_references():
    built = schema_from_document(
        _with_control({
            "id": "beta",
            "text": {
                "singular": ["a ", {"ref": {"kind": "control", "id": "delta"}}, " beta"],
                "plural": ["some betas"],
            },
            "kind": "or",
            "options": [],
        })
    )
    text = built.sections[0].controls[0].text
    assert isinstance(text, TemplateText)
    assert text.singular[0] == "a "
    assert isinstance(text.singular[1], TextRef)
    assert (text.singular[1].ref.kind, text.singular[1].ref.id) == ("control", "delta")
    assert text.plural == ["some betas"]


def test_a_template_without_a_plural_leaves_it_unset():
    built = schema_from_document(
        _with_control({
            "id": "beta", "text": {"singular": ["a beta"]}, "kind": "or", "options": [],
        })
    )
    assert built.sections[0].controls[0].text.plural is None


@pytest.mark.parametrize("bad", [42, None, ["beta"]])
def test_a_text_value_that_is_neither_string_nor_object_is_refused(bad):
    with pytest.raises(ValueError, match="string or an object"):
        schema_from_document(
            _with_control({"id": "beta", "text": bad, "kind": "or", "options": []})
        )


def test_a_text_object_without_a_singular_is_refused():
    with pytest.raises(ValueError, match="needs a"):
        schema_from_document(
            _with_control({"id": "beta", "text": {"plural": "betas"}, "kind": "or", "options": []})
        )


def test_a_template_part_that_is_neither_text_nor_a_ref_is_refused():
    with pytest.raises(ValueError, match="must be a string"):
        schema_from_document(
            _with_control({
                "id": "beta", "text": {"singular": [42]}, "kind": "or", "options": [],
            })
        )


def test_camel_case_keys_arrive_as_the_snake_case_fields():
    built = schema_from_document({
        "sections": [{
            "id": "alpha",
            "text": "alpha",
            "promptTarget": "negative",
            "controls": [{
                "id": "beta",
                "text": "beta",
                "kind": "and-commas",
                "customText": "betaing",
                "initiallySelectedOptions": ["gamma"],
                "globalSubstitutions": [{"from": "gamma", "to": "delta"}],
                "hiddenOppositeBys": [{"controlId": "epsilon"}],
                "revealedBys": [{"controlId": "zeta"}],
                "options": [{
                    "id": "gamma",
                    "text": "gamma",
                    "customControlText": "gammaing",
                    "hiddenBys": [{"optionId": "eta"}],
                    "disabledBys": [{"controlId": "theta", "optionId": "iota"}],
                    "supplementedBys": [
                        {"optionId": "kappa", "supplementalText": "kappaish", "side": "adj"},
                    ],
                    "submenu": {
                        "kind": "and-adj",
                        "options": [{"id": "lambda", "text": "lambda"}],
                    },
                }],
            }],
        }],
    })
    section = built.sections[0]
    control = section.controls[0]
    option = control.options[0]

    assert section.prompt_target == "negative"
    assert control.custom_text == "betaing"
    assert control.initially_selected_options == ["gamma"]
    assert control.global_substitutions[0].from_text == "gamma"
    assert control.global_substitutions[0].to_text == "delta"
    assert control.global_substitutions[0].from_plural is None
    assert control.hidden_opposite_bys[0].control_id == "epsilon"
    assert control.revealed_bys[0].control_id == "zeta"
    assert option.custom_control_text == "gammaing"
    assert option.hidden_bys[0].option_id == "eta"
    assert option.disabled_bys[0].control_id == "theta"
    assert option.disabled_bys[0].option_id == "iota"
    assert option.supplemented_bys[0].supplemental_text == "kappaish"
    assert option.supplemented_bys[0].side == "adj"
    assert option.supplemented_bys[0].option_id == "kappa"
    assert option.submenu.kind == "and-adj"
    assert option.submenu.options[0].id == "lambda"


def test_a_plural_substitution_carries_both_halves():
    built = schema_from_document(
        _with_control({
            "id": "beta", "text": "beta", "kind": "or", "options": [],
            "globalSubstitutions": [{
                "from": "gamma", "to": "delta",
                "fromPlural": "gammas", "toPlural": "deltas",
            }],
        })
    )
    substitution = built.sections[0].controls[0].global_substitutions[0]
    assert substitution.from_plural == "gammas"
    assert substitution.to_plural == "deltas"


def test_absent_condition_lists_arrive_empty_not_missing():
    control = schema_from_document(MINIMAL).sections[0].controls[0]
    assert control.hidden_bys == []
    assert control.revealed_bys == []
    assert control.disabled_bys == []
    assert control.supplemented_bys == []
    assert control.global_substitutions == []
    assert control.hidden_opposite_bys == []
    assert control.custom_text is None
    assert control.initially_selected_options is None


def test_a_submenu_nests_to_any_depth():
    built = schema_from_document(
        _with_control({
            "id": "beta", "text": "beta", "kind": "and-commas",
            "options": [{
                "id": "gamma", "text": "gamma",
                "submenu": {"kind": "and-adj", "options": [{
                    "id": "delta", "text": "delta",
                    "submenu": {
                        "kind": "and-adv",
                        "options": [{"id": "epsilon", "text": "epsilon"}],
                    },
                }]},
            }],
        })
    )
    inner = built.sections[0].controls[0].options[0].submenu.options[0].submenu
    assert inner.kind == "and-adv"
    assert inner.options[0].id == "epsilon"


def test_a_built_schema_can_open_the_app_state():
    """The point of the loader: what it returns is what the rest of the app takes."""
    state = create_initial_state(schema_from_document(MINIMAL))
    assert state.controls["beta"].selected_options == ""
    assert list(state.sections) == ["alpha"]
