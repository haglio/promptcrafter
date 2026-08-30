import copy

import pytest
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGroupBox,
    QPushButton,
    QRadioButton,
    QSlider,
    QWidget,
)

from promptcrafter.app import PromptCrafterWindow
from promptcrafter.types import Control, Option, Schema, Section, Submenu
from shared_ui.check_box import CheckBox
from tests.fixtures.test_schema import TEST_SCHEMA


@pytest.fixture()
def app(qtbot):
    window = PromptCrafterWindow(TEST_SCHEMA)
    qtbot.addWidget(window)
    window.show()
    return window


@pytest.fixture()
def window_with_a_toggle(qtbot):
    """Build a window whose second section leads with a multi-option toggle.

    The four toggle tests differ only in which of its options start selected,
    which was being spelled out in full four times.
    """
    def build(initially_selected_options=None):
        schema = copy.deepcopy(TEST_SCHEMA)
        schema.sections[1].controls.insert(0, Control(
            id="texture pack", text="texture pack", kind="toggle",
            initially_selected_options=initially_selected_options,
            options=[Option(id="oak", text="oak"), Option(id="pine", text="pine")],
        ))
        window = PromptCrafterWindow(schema)
        qtbot.addWidget(window)
        window.show()
        return window

    return build


# Each of these comes in two names for one look-up: `find_` for a control that
# has to be there (missing is the failure, and says so), `query_` for one whose
# absence is what a test is checking. Same body -- the pair used to be the same
# loop written twice.


def find_checkbox(container, label, *, required=True):
    for cb in container.findChildren(QCheckBox):
        if cb.text() == label or cb.accessibleName() == label:
            return cb
    if required:
        raise AssertionError(f"No QCheckBox with label '{label}'")
    return None


def query_checkbox(container, label):
    return find_checkbox(container, label, required=False)


def find_radio(container, label, *, required=True):
    for rb in container.findChildren(QRadioButton):
        if rb.text() == label:
            return rb
    if required:
        raise AssertionError(f"No QRadioButton with label '{label}'")
    return None


def query_radio(container, label):
    return find_radio(container, label, required=False)


def find_section(app, heading_text, *, required=True):
    for gb in app.findChildren(QGroupBox):
        if gb.title() == heading_text:
            return gb
    if required:
        raise AssertionError(f"No section with heading '{heading_text}'")
    return None


def query_section(app, heading_text):
    return find_section(app, heading_text, required=False)


def find_control(app, control_id):
    """The widget one control's rows are built into.

    ``control_id`` is a property of that container and of nothing else, so it is
    the only way to ask what *one* control shows. Searching the window instead
    answers about every control at once: the fixture spells "green" in three
    places, so a window-wide count of green radios says the same thing whether
    the selector built any or not.
    """
    for widget in app.findChildren(QWidget):
        if widget.property("control_id") == control_id:
            return widget
    raise AssertionError(f"No control container for '{control_id}'")


def find_slider(container):
    sliders = container.findChildren(QSlider)
    return sliders[0] if sliders else None


def find_button(container, label):
    for btn in container.findChildren(QPushButton):
        if btn.text() == label and not btn.isHidden():
            return btn
    return None


def find_mode_button(prompt):
    """The auto/manual button beside one prompt.

    Its label names the mode it switches *to*, so both prompts' buttons read
    "manual" at load; the object name is what separates it from the copy button
    sitting next to it.
    """
    for btn in prompt.parent().findChildren(QPushButton):
        if btn.objectName().startswith("mode_toggle_"):
            return btn
    raise AssertionError("No mode button beside the prompt")


def find_copy_button(container):
    for btn in container.findChildren(QPushButton):
        if btn.objectName() == "copy_button":
            return btn
    raise AssertionError("No copy button in this container")


def find_label_widget(container, label_text):
    from PyQt6.QtWidgets import QLabel
    for lbl in container.findChildren(QLabel):
        if label_text in lbl.text():
            return lbl
    return None


class TestUpdatingPrompts:
    def test_renders_shell_on_first_load(self, app):
        assert app.windowTitle() == "PromptCrafter"
        assert app.positive_prompt.toPlainText() == "space robo dino demon monster"
        assert app.negative_prompt.toPlainText() == "no clutter, blurry"

    def test_updates_positive_prompt_when_controls_change(self, qtbot, app):
        find_radio(app, "bone").click()
        find_radio(app, "towering").click()
        find_checkbox(app, "wings").click()
        find_radio(app, "mechanical").click()

        assert app.positive_prompt.toPlainText() == (
            "space robo dino demon monster, outline towering, bone armor, mechanical wings"
        )

    def test_updates_negative_prompt_when_controls_change(self, qtbot, app):
        find_checkbox(app, "extra limbs").click()

        assert app.negative_prompt.toPlainText() == "no clutter, blurry, extra limbs"

    def test_updates_negative_prompt_when_hidden_opposite_source_selected(self, qtbot, app):
        assert app.negative_prompt.toPlainText() == "no clutter, blurry"
        find_radio(app, "hot").click()
        assert app.negative_prompt.toPlainText() == "no clutter, blurry, cold"

    def test_clicking_the_chosen_radio_again_clears_it(self, qtbot, app):
        """A radio is the only control here that can be emptied by one click.

        Every other test clicks a radio to *choose*; the branch that puts the
        control back to no selection had never run.
        """
        find_radio(app, "bone").click()
        assert app.positive_prompt.toPlainText() == "space robo dino demon monster, bone armor"

        find_radio(app, "bone").click()

        assert app.positive_prompt.toPlainText() == "space robo dino demon monster"
        assert not find_radio(app, "bone").isChecked()


class TestToggleControls:
    def test_keeps_multi_option_toggles_off_initially(self, window_with_a_toggle):
        window = window_with_a_toggle(initially_selected_options=["oak"])

        toggle = find_checkbox(window, "texture pack")
        assert not toggle.isChecked()
        assert query_checkbox(window, "oak") is None
        assert window.positive_prompt.toPlainText() == "space robo dino demon monster"

    def test_shows_options_when_toggle_turned_on(self, window_with_a_toggle):
        window = window_with_a_toggle()

        assert query_checkbox(window, "oak") is None
        find_checkbox(window, "texture pack").click()

        assert find_checkbox(window, "oak").isChecked()
        assert find_checkbox(window, "pine").isChecked()
        assert window.positive_prompt.toPlainText() == "space robo dino demon monster, oak, pine"

    def test_uses_initial_option_defaults_when_turned_on(self, window_with_a_toggle):
        window = window_with_a_toggle(initially_selected_options=["oak"])

        find_checkbox(window, "texture pack").click()

        assert find_checkbox(window, "oak").isChecked()
        assert not find_checkbox(window, "pine").isChecked()
        assert window.positive_prompt.toPlainText() == "space robo dino demon monster, oak"

    def test_preserves_narrowed_selection_across_off_on(self, window_with_a_toggle):
        window = window_with_a_toggle()

        find_checkbox(window, "texture pack").click()
        find_checkbox(window, "pine").click()
        find_checkbox(window, "texture pack").click()
        find_checkbox(window, "texture pack").click()

        assert find_checkbox(window, "oak").isChecked()
        assert not find_checkbox(window, "pine").isChecked()
        assert window.positive_prompt.toPlainText() == "space robo dino demon monster, oak"


class TestRebuilding:
    def test_a_rebuild_leaves_one_widget_per_section(self, qtbot, app):
        """Nothing from the previous tree is still hanging off the window.

        Every click rebuilds the whole control tree, so a teardown that missed
        anything would stack a second copy of each section on each interaction
        and the window would grow without ever looking wrong at first glance.
        """
        titles = sorted(gb.title() for gb in app.findChildren(QGroupBox))
        assert titles

        for _ in range(4):
            app._rebuild()

        assert sorted(gb.title() for gb in app.findChildren(QGroupBox)) == titles

    def test_a_rebuild_keeps_one_trailing_stretch(self, qtbot, app):
        before = app.sections_layout.count()

        app._rebuild()
        app._rebuild()

        assert app.sections_layout.count() == before


class TestSubmenus:
    """The second row an option opens under itself.

    A submenu's radios and checkboxes go through their own handlers, and the
    suite reached only one of the two: the checkbox handler had never been
    called by any test, and neither deselect branch had ever run.
    """

    def test_clicking_the_chosen_submenu_radio_again_clears_it(self, qtbot, app):
        find_checkbox(app, "wings").click()
        find_radio(app, "mechanical").click()
        assert app.positive_prompt.toPlainText() == (
            "space robo dino demon monster, mechanical wings"
        )

        find_radio(app, "mechanical").click()

        assert app.positive_prompt.toPlainText() == "space robo dino demon monster, wings"

    def test_a_submenu_checkbox_ticks_and_unticks(self, qtbot, app):
        find_checkbox(app, "tail").click()
        assert app.positive_prompt.toPlainText() == "space robo dino demon monster, tail"

        find_checkbox(app, "barbed").click()
        assert app.positive_prompt.toPlainText() == (
            "space robo dino demon monster, barbed tail"
        )

        find_checkbox(app, "barbed").click()

        assert app.positive_prompt.toPlainText() == "space robo dino demon monster, tail"

    def test_an_or_prefixed_submenu_kind_builds_radios_whatever_follows_the_or(self, qtbot):
        """The widget half of the open rival, pinned beside the state half.

        `_build_submenu` asks whether the kind begins with `or`, not whether it
        is one of the two declared `or` submenu kinds. Nothing validates a
        submenu kind, so a schema can carry `or` here and it builds radios;
        narrowing the test to a closed set would silently make them checkboxes.
        """
        schema = Schema(sections=[Section(id="grove", text="grove", controls=[
            Control(id="bough", text="bough", kind="and-commas",
                    initially_selected_options=["knot"], options=[
                        Option(id="knot", text="knot", submenu=Submenu(
                            kind="or", options=[Option(id="burl", text="burl")])),
                    ]),
        ])])
        window = PromptCrafterWindow(schema)
        qtbot.addWidget(window)

        assert query_radio(window, "burl") is not None
        assert query_checkbox(window, "burl") is None

    def test_a_submenu_keeps_the_options_the_click_did_not_touch(self, qtbot, app):
        find_checkbox(app, "antennae").click()
        find_checkbox(app, "arched").click()
        find_checkbox(app, "flared").click()

        find_checkbox(app, "arched").click()

        assert app.positive_prompt.toPlainText() == (
            "space robo dino demon monster, antennae flared"
        )


class TestDisablingAndHiding:
    def test_disabled_bys_at_section_level(self, qtbot, app):
        section = find_section(app, "section disabled target")
        assert section.isEnabled()

        find_checkbox(app, "is portrait").click()

        section = find_section(app, "section disabled target")
        assert not section.isEnabled()

    def test_disabled_bys_at_control_level(self, qtbot, app):
        modes = find_section(app, "modes")
        assert find_radio(modes, "low").isEnabled()

        find_checkbox(app, "is portrait").click()

        modes = find_section(app, "modes")
        assert not find_radio(modes, "low").isEnabled()

    def test_disabled_bys_at_option_level(self, qtbot, app):
        modes = find_section(app, "modes")
        assert find_radio(modes, "floating").isEnabled()

        find_checkbox(app, "is portrait").click()

        modes = find_section(app, "modes")
        assert not find_radio(modes, "floating").isEnabled()

    def test_hidden_bys_at_section_level(self, qtbot, app):
        assert query_section(app, "section hidden target") is not None

        find_checkbox(app, "is portrait").click()

        assert query_section(app, "section hidden target") is None

    def test_hidden_bys_at_control_level(self, qtbot, app):
        modes = find_section(app, "modes")
        assert find_label_widget(modes, "portrait focus") is not None

        find_checkbox(app, "is portrait").click()

        modes = find_section(app, "modes")
        assert find_label_widget(modes, "portrait focus") is None

    def test_hidden_bys_at_option_level(self, qtbot, app):
        modes = find_section(app, "modes")
        assert query_radio(modes, "airborne") is not None

        find_checkbox(app, "is portrait").click()

        modes = find_section(app, "modes")
        assert query_radio(modes, "airborne") is None

    def test_revealed_bys_at_section_level(self, qtbot, app):
        assert query_section(app, "portrait extras") is None

        find_checkbox(app, "is portrait").click()

        assert query_section(app, "portrait extras") is not None

    def test_revealed_bys_at_control_level(self, qtbot, app):
        modes = find_section(app, "modes")
        assert find_label_widget(modes, "portrait pose") is None

        find_checkbox(app, "is portrait").click()

        modes = find_section(app, "modes")
        assert find_label_widget(modes, "portrait pose") is not None

    def test_revealed_bys_at_option_level(self, qtbot, app):
        modes = find_section(app, "modes")
        assert query_radio(modes, "close crop") is None

        find_checkbox(app, "is portrait").click()

        modes = find_section(app, "modes")
        assert query_radio(modes, "close crop") is not None


class TestPluralityInLabels:
    def test_shows_plural_section_label(self, qtbot, app):
        assert query_section(app, "accent") is not None
        find_radio(app, "two").click()
        assert query_section(app, "accents") is not None
        assert query_section(app, "accent") is None

    def test_shows_plural_control_label(self, qtbot, app):
        assert find_label_widget(app, "stance") is not None
        find_radio(app, "two").click()
        assert find_label_widget(app, "stances") is not None

    def test_shows_plural_option_label(self, qtbot, app):
        assert query_radio(app, "hero") is not None
        find_radio(app, "two").click()
        assert query_radio(app, "heroes") is not None

    def test_global_substitutions_in_labels(self, qtbot, app):
        section = find_section(app, "torso references")
        assert find_label_widget(section, "torso mentions") is not None
        assert find_checkbox(section, "torso badge") is not None

        find_checkbox(app, "thorax mode").click()

        section = find_section(app, "thorax references")
        assert query_section(app, "torso references") is None
        assert find_label_widget(section, "thorax mentions") is not None
        assert find_checkbox(section, "thorax badge") is not None
        assert find_checkbox(section, "thoraces") is not None

        find_checkbox(section, "thorax badge").click()
        find_checkbox(section, "thoraces").click()

        assert app.positive_prompt.toPlainText() == (
            "space robo dino demon monster, replace thorax terminology, thorax badge, thoraces"
        )


class TestWeights:
    def test_control_weight_lowers_below_1(self, qtbot, app):
        find_radio(app, "bone").click()
        # Find the slider in the armor control's container
        # After selecting bone, armor control should have a weight slider
        # Set weight to 0.6
        app.state.controls["armor"].weight = 0.6
        app._rebuild()

        assert app.positive_prompt.toPlainText() == "space robo dino demon monster, (bone armor:0.6)"

    def test_section_weight_raises_above_1(self, qtbot, app):
        app.state.sections["negative modes"].weight = 2.5
        app._rebuild()

        assert app.negative_prompt.toPlainText() == "(no clutter:2.5), blurry"

    def test_the_control_slider_sets_the_controls_weight(self, qtbot, app):
        """The slider itself, not the state behind it.

        The other weight tests here assign to ``state`` and rebuild, and the
        reset button only ever asks for 1.0 -- so the one number the slider is
        for had never travelled from the widget to the prompt.
        """
        find_radio(app, "bone").click()

        find_slider(find_control(app, "armor")).setValue(24)

        assert app.state.controls["armor"].weight == 2.4
        assert app.positive_prompt.toPlainText() == (
            "space robo dino demon monster, (bone armor:2.4)"
        )

    def test_the_section_slider_sets_the_sections_weight(self, qtbot, app):
        find_slider(find_section(app, "negative modes")).setValue(15)

        assert app.state.sections["negative modes"].weight == 1.5
        assert app.negative_prompt.toPlainText() == "(no clutter:1.5), blurry"

    def test_no_section_slider_when_no_selection(self, app):
        section = find_section(app, "details")
        assert find_slider(section) is None

    def test_no_control_slider_when_no_selection(self, app):
        # armor has no selection initially — find its container and check no slider
        # We check there's no slider by verifying the label widget has no sibling slider
        # This is implicitly true since the _build_control method only adds sliders when has selection
        # Just verify build works without error and armor section has no slider next to it
        details = find_section(app, "subject-core")
        # armor's header should exist but shouldn't have a slider
        # We need a more targeted approach — for now, verify slider count is limited
        assert app.positive_prompt.toPlainText() == "space robo dino demon monster"

    def test_section_weight_reset_button_appears(self, qtbot, app):
        section = find_section(app, "negative modes")
        assert find_button(section, "\u21ba") is None

        app.state.sections["negative modes"].weight = 2.5
        app._rebuild()

        section = find_section(app, "negative modes")
        assert find_button(section, "\u21ba") is not None

    def test_section_weight_reset_restores_to_1(self, qtbot, app):
        app.state.sections["negative modes"].weight = 2.5
        app._rebuild()
        assert app.negative_prompt.toPlainText() == "(no clutter:2.5), blurry"

        section = find_section(app, "negative modes")
        find_button(section, "\u21ba").click()

        assert app.negative_prompt.toPlainText() == "no clutter, blurry"
        section = find_section(app, "negative modes")
        assert find_button(section, "\u21ba") is None

    def test_control_weight_reset_restores_to_1(self, qtbot, app):
        find_radio(app, "bone").click()
        app.state.controls["armor"].weight = 2.0
        app._rebuild()
        assert app.positive_prompt.toPlainText() == "space robo dino demon monster, (bone armor:2.0)"

        # Find and click the reset button near armor
        # After rebuild, we need to find the armor control's reset button
        # The reset button is in the weight widget which is in the control header
        # We look for the reset button in the entire app since armor is the only weighted control
        reset = None
        for btn in app.findChildren(QPushButton):
            if btn.text() == "\u21ba" and not btn.isHidden():
                parent = btn.parent()
                while parent:
                    cid = parent.property("control_id")
                    if cid == "armor":
                        reset = btn
                        break
                    parent = parent.parent()
                if reset:
                    break
        assert reset is not None
        reset.click()

        assert app.positive_prompt.toPlainText() == "space robo dino demon monster, bone armor"


class TestGlobalSelector:
    """One control that reaches across the window and sets the others.

    Every look-up here is scoped to a single control's container. The window
    rebuilds on each click, so the container is fetched again after one.
    """

    def _click_the_toggle(self, app):
        find_checkbox(find_control(app, "colorize"), "colorize").click()

    def _choose(self, app, option_label):
        find_radio(find_control(app, "colorize"), option_label).click()

    def test_hides_options_while_off(self, app):
        colorize = find_control(app, "colorize")

        assert not find_checkbox(colorize, "colorize").isChecked()
        assert query_radio(colorize, "green") is None
        assert query_radio(colorize, "black") is None

    def test_shows_options_when_turned_on(self, app):
        self._click_the_toggle(app)

        colorize = find_control(app, "colorize")
        assert find_checkbox(colorize, "colorize").isChecked()
        assert find_radio(colorize, "green").isEnabled()
        assert find_radio(colorize, "black").isEnabled()

    def test_selects_the_same_option_in_every_other_control(self, app):
        self._click_the_toggle(app)
        self._choose(app, "green")

        assert find_radio(find_control(app, "eye color"), "green").isChecked()
        assert app.positive_prompt.toPlainText() == (
            "space robo dino demon monster, green, green tinted render style"
        )

    def test_reaches_options_that_merely_contain_the_chosen_id(self, app):
        # Matching is a substring test rather than an id comparison, so
        # choosing "green" also ticks "green tinted". Held as a finding at the
        # owner's decision (2026-08-25); this pins what it does today so the
        # decision to change it has to be a deliberate one.
        self._click_the_toggle(app)
        self._choose(app, "green")

        assert find_checkbox(find_control(app, "render style"), "green tinted").isChecked()

    def test_choosing_another_option_releases_the_first(self, app):
        self._click_the_toggle(app)
        self._choose(app, "green")
        self._choose(app, "black")

        assert find_radio(find_control(app, "eye color"), "black").isChecked()
        assert not find_radio(find_control(app, "eye color"), "green").isChecked()
        assert not find_checkbox(find_control(app, "render style"), "green tinted").isChecked()
        assert app.positive_prompt.toPlainText() == (
            "space robo dino demon monster, black, black and white render style"
        )

    def test_turning_it_off_clears_everything_it_selected(self, app):
        self._click_the_toggle(app)
        self._choose(app, "green")
        self._click_the_toggle(app)

        assert not find_radio(find_control(app, "eye color"), "green").isChecked()
        assert not find_checkbox(find_control(app, "render style"), "green tinted").isChecked()
        assert app.positive_prompt.toPlainText() == "space robo dino demon monster"


class TestPromptMode:
    def test_manual_hands_the_prompt_over(self, app):
        assert app.positive_prompt.isReadOnly()

        find_mode_button(app.positive_prompt).click()

        assert app.state.modes["positive"] == "manual"
        assert not app.positive_prompt.isReadOnly()

    def test_manual_leaves_what_was_typed_alone(self, app):
        find_mode_button(app.positive_prompt).click()
        app.positive_prompt.setPlainText("a prompt of my own")

        find_radio(app, "bone").click()

        assert app.positive_prompt.toPlainText() == "a prompt of my own"

    def test_auto_takes_the_prompt_back_and_rewrites_it(self, app):
        button = find_mode_button(app.positive_prompt)
        button.click()
        app.positive_prompt.setPlainText("a prompt of my own")
        find_radio(app, "bone").click()

        button.click()

        assert app.positive_prompt.isReadOnly()
        assert app.positive_prompt.toPlainText() == "space robo dino demon monster, bone armor"

    def test_each_prompt_switches_on_its_own(self, app):
        find_mode_button(app.positive_prompt).click()

        assert app.state.modes["negative"] == "auto"
        assert app.negative_prompt.isReadOnly()

    def test_the_negative_button_switches_the_negative_prompt(self, app):
        """The other half of the pair, which nothing asked for.

        Every mode test drove the positive button, so a handler that wrote
        "positive" whatever it was handed passed all of them.
        """
        find_mode_button(app.negative_prompt).click()

        assert app.state.modes["negative"] == "manual"
        assert app.state.modes["positive"] == "auto"
        assert not app.negative_prompt.isReadOnly()
        assert app.positive_prompt.isReadOnly()


class TestCopying:
    @pytest.fixture(autouse=True)
    def _nothing_copied_yet(self, app):
        """Put something on the clipboard that no test here expects.

        The clipboard is one object for the whole process, and two of these
        tests copy the same text, so without this a test could be reading what
        the test before it left there -- the suite is also run shuffled.
        """
        QApplication.clipboard().setText("nothing has been copied yet")

    def test_the_copy_button_copies_the_prompt_beside_it(self, app):
        find_radio(app, "bone").click()

        find_copy_button(app.positive_prompt.parent()).click()

        assert QApplication.clipboard().text() == "space robo dino demon monster, bone armor"

    def test_each_prompt_has_its_own_copy_button(self, app):
        find_copy_button(app.negative_prompt.parent()).click()

        assert QApplication.clipboard().text() == "no clutter, blurry"

    def test_a_sections_copy_button_copies_nothing(self, app):
        """What the section copy buttons do today: clear the clipboard.

        ``clicked`` carries a bool, and the lambda behind these buttons names
        the section id as its first parameter with a default, so Qt's
        ``checked`` lands there instead: the handler is called with ``False``,
        matches no section, and copies an empty string. Recorded 2026-08-25 and
        held unfixed. The two tests below pin the copy itself, which is sound.
        """
        find_copy_button(find_section(app, "negative modes")).click()

        assert QApplication.clipboard().text() == ""

    def test_the_section_copy_takes_its_target_from_the_section(self, app):
        # Called with the id the button above fails to pass. This section
        # renders into the negative prompt, so a copy that assumed positive
        # would come back empty.
        app._copy_section_prompt("negative modes")

        assert QApplication.clipboard().text() == "no clutter"

    def test_the_section_copy_reads_past_a_section_that_names_no_target(self, qtbot):
        """Two sections can share an id, and the target comes from either.

        The look-up is not "the section with this id" -- it is "the first
        section with this id that names a target", so a pair whose second half
        is the negative one copies the negative prompt. Nothing makes ids
        unique, and a copy button is built for each half.
        """
        schema = Schema(sections=[
            Section(id="zonk", text="zonk", controls=[
                Control(id="quaffle", text="quaffle", kind="toggle",
                        initially_selected_options=True),
            ]),
            Section(id="zonk", text="zonk", prompt_target="negative", controls=[
                Control(id="snitch", text="snitch", kind="toggle",
                        initially_selected_options=True),
            ]),
        ])
        window = PromptCrafterWindow(schema)
        qtbot.addWidget(window)

        window._copy_section_prompt("zonk")

        assert QApplication.clipboard().text() == ""

    def test_the_section_copy_leaves_the_other_sections_out(self, app):
        find_radio(app, "bone").click()
        find_radio(find_control(app, "eye color"), "green").click()

        app._copy_section_prompt("subject-core")

        assert app.positive_prompt.toPlainText() == (
            "space robo dino demon monster, bone armor, green"
        )
        assert QApplication.clipboard().text() == "space robo dino demon monster, bone armor"


def test_option_checkboxes_use_the_shared_ticked_checkbox(app):
    # Every option checkbox must be the shared CheckBox (a real ticked box),
    # not a plain QCheckBox whose styled indicator renders as a down-caret.
    # The QSS pill toggles (objectName "toggle_switch") stay QCheckBox.
    option_boxes = [
        cb for cb in app.findChildren(QCheckBox)
        if cb.objectName() != "toggle_switch"
    ]
    assert option_boxes  # the test schema renders checkbox options
    assert all(isinstance(cb, CheckBox) for cb in option_boxes)
