"""An id a schema points at that the schema does not hold.

Every failed lookup in the renderer answers with the empty string, so a mistyped
id reaches the prompt as silence: the text is shorter than it should be and
nothing anywhere says why, which leaves no way to tell a typo from a deliberate
blank (audit promptcrafter/all/design/016). Two answers, both here: the ids can
be checked before anything renders, and a lookup that fails at render time says
so once in the log.

Ids are the schema author's own vocabulary, so the whole-tree check below
reports counts and kinds only -- no id out of a schema reaches this file's
failure messages, which is what lets it run against a private one.
"""
from __future__ import annotations

import logging

import pytest

from promptcrafter import runtime
from promptcrafter.references import dangling_references, report_dangling_references
from promptcrafter.runtime import get_text_value
from promptcrafter.schema import schema as demo_schema
from promptcrafter.schema_overlay import load_schema
from promptcrafter.state import create_initial_state
from promptcrafter.types import (
    Control,
    DisabledOrHiddenBy,
    GlobalSubstitution,
    Option,
    Schema,
    Section,
    Submenu,
    SupplementedBy,
    TemplateText,
    TextRef,
    TextReference,
)


def _ref(kind, id_):
    return TextRef(ref=TextReference(kind=kind, id=id_))


def _schema(*, section_extra=None, control_extra=None, option_extra=None,
            section_text="plain"):
    """A one-control schema, with room to hang a reference off each level."""
    return Schema(sections=[
        Section(
            id="frame",
            text=section_text,
            controls=[
                Control(
                    id="tilt",
                    text="tilt",
                    kind="or",
                    options=[Option(id="left", text="left", **(option_extra or {}))],
                    **(control_extra or {}),
                ),
            ],
            **(section_extra or {}),
        ),
    ])


class TestWhatCountsAsDangling:

    def test_a_text_reference_to_a_control_that_is_not_there_is_named(self):
        schema = _schema(section_text=TemplateText(singular=["a ", _ref("control", "zoom")]))

        (dangling,) = dangling_references(schema)

        assert (dangling.kind, dangling.id) == ("control", "zoom")
        assert dangling.at == "section:frame"

    def test_a_condition_naming_a_control_that_is_not_there_is_named(self):
        schema = _schema(control_extra={
            "hidden_bys": [DisabledOrHiddenBy(control_id="zoom")]})

        assert [(d.kind, d.id) for d in dangling_references(schema)] == [("control", "zoom")]

    def test_a_condition_naming_an_option_that_is_not_there_is_named(self):
        schema = _schema(option_extra={
            "revealed_bys": [DisabledOrHiddenBy(option_id="right")]})

        assert [(d.kind, d.id) for d in dangling_references(schema)] == [("option", "right")]

    def test_a_supplement_s_own_text_is_walked_too(self):
        schema = _schema(control_extra={"supplemented_bys": [
            SupplementedBy(control_id="tilt", option_id="left",
                           supplemental_text=TemplateText(
                               singular=[_ref("option", "right")]))]})

        assert [(d.kind, d.id) for d in dangling_references(schema)] == [("option", "right")]

    def test_an_option_inside_a_submenu_is_a_real_option(self):
        """The renderer finds it, so a checker that did not would cry wolf."""
        schema = Schema(sections=[Section(id="frame", text="plain", controls=[
            Control(id="tilt", text="tilt", kind="or", options=[
                Option(id="left", text="left", submenu=Submenu(
                    kind="and-adv", options=[Option(id="slowly", text="slowly")])),
            ], hidden_bys=[DisabledOrHiddenBy(option_id="slowly")]),
        ])])

        assert dangling_references(schema) == []

    def test_a_schema_that_points_only_at_itself_is_clean(self):
        assert dangling_references(_schema()) == []

    def test_the_plural_half_of_a_template_is_walked_as_well(self):
        schema = _schema(section_text=TemplateText(
            singular=["one"], plural=[_ref("section", "frames")]))

        assert [(d.kind, d.id) for d in dangling_references(schema)] == [("section", "frames")]

    def test_an_option_s_own_control_text_is_walked(self):
        schema = _schema(option_extra={
            "custom_control_text": TemplateText(singular=[_ref("control", "zoom")])})

        assert [d.at for d in dangling_references(schema)] == ["option:left"]

    def test_a_substitution_s_two_halves_are_walked(self):
        schema = _schema(control_extra={"global_substitutions": [GlobalSubstitution(
            from_text=TemplateText(singular=[_ref("option", "right")]),
            to_text="left")]})

        assert [(d.kind, d.id) for d in dangling_references(schema)] == [("option", "right")]

    def test_an_opposite_condition_is_walked(self):
        schema = _schema(control_extra={
            "hidden_opposite_bys": [DisabledOrHiddenBy(control_id="zoom")]})

        assert [(d.kind, d.id) for d in dangling_references(schema)] == [("control", "zoom")]

    def test_a_submenu_option_s_own_references_are_walked(self):
        schema = Schema(sections=[Section(id="frame", text="plain", controls=[
            Control(id="tilt", text="tilt", kind="or", options=[
                Option(id="left", text="left", submenu=Submenu(
                    kind="and-adv", options=[Option(
                        id="slowly", text="slowly",
                        disabled_bys=[DisabledOrHiddenBy(option_id="right")])])),
            ]),
        ])])

        assert [d.at for d in dangling_references(schema)] == ["option:slowly"]


class TestWhatTheAppSaysOnTheWayUp:

    def test_each_one_is_logged_with_where_it_was_found(self, caplog):
        schema = _schema(control_extra={
            "hidden_bys": [DisabledOrHiddenBy(control_id="zoom")]})

        with caplog.at_level(logging.WARNING, logger="promptcrafter.references"):
            found = report_dangling_references(schema)

        assert [(d.kind, d.id) for d in found] == [("control", "zoom")]
        assert "control:tilt" in caplog.text
        assert "zoom" in caplog.text

    def test_a_clean_schema_is_passed_over_in_silence(self, caplog):
        with caplog.at_level(logging.WARNING, logger="promptcrafter.references"):
            assert report_dangling_references(_schema()) == []

        assert caplog.records == []


class TestTheSchemasThisCheckoutCanLoad:

    def test_none_of_them_points_at_an_id_it_does_not_hold(self):
        for schema in (demo_schema, load_schema()):
            found = dangling_references(schema)
            kinds = sorted({d.kind for d in found})
            assert not found, f"{len(found)} unresolved reference(s), kinds: {kinds}"


class TestSayingSoAtRenderTime:
    """A private schema's typo cannot fail a suite that never sees it, so the
    renderer says so where it happens -- once per id, not once per rebuild."""

    @pytest.fixture(autouse=True)
    def _forget_earlier_warnings(self, monkeypatch):
        monkeypatch.setattr(runtime, "_UNRESOLVED_ALREADY_SAID", set())

    def test_an_unresolved_reference_is_logged_with_its_kind_and_id(self, caplog):
        schema = _schema(section_text=TemplateText(singular=[_ref("control", "zoom")]))
        state = create_initial_state(schema)

        with caplog.at_level(logging.WARNING, logger="promptcrafter.runtime"):
            rendered = get_text_value(schema.sections[0].text, False, schema, state)

        assert rendered == ""
        assert "control" in caplog.text
        assert "zoom" in caplog.text

    def test_the_same_missing_id_is_logged_once_however_often_it_renders(self, caplog):
        schema = _schema(section_text=TemplateText(singular=[_ref("control", "zoom")]))
        state = create_initial_state(schema)

        with caplog.at_level(logging.WARNING, logger="promptcrafter.runtime"):
            for _ in range(5):
                get_text_value(schema.sections[0].text, False, schema, state)

        assert len(caplog.records) == 1

    def test_a_reference_that_resolves_says_nothing(self, caplog):
        schema = _schema(section_text=TemplateText(singular=[_ref("control", "tilt")]))
        state = create_initial_state(schema)

        with caplog.at_level(logging.WARNING, logger="promptcrafter.runtime"):
            get_text_value(schema.sections[0].text, False, schema, state)

        assert caplog.records == []
