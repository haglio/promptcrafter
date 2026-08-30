from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from promptcrafter.paths import ensure_shared_ui_on_path

# shared_ui is imported via sys.path rather than installed; make it importable
# regardless of checkout depth (normal clone vs .claude/worktrees/<name>).
ensure_shared_ui_on_path()

from shared_ui.fonts import FONT_UI, SIZE_HEADING  # noqa: E402
from shared_ui.spacing import GAP_MEDIUM, GAP_SMALL  # noqa: E402
from shared_ui.check_box import CheckBox  # noqa: E402

from promptcrafter.kinds import is_or_prefixed_kind, is_radio_submenu_kind  # noqa: E402
from promptcrafter.runtime import (  # noqa: E402
    apply_substitutions,
    build_prompt,
    build_section_prompt,
    control_has_at_least_one_selected_option,
    find_section,
    get_active_substitutions,
    get_text_value,
    is_disabled,
    is_hidden,
    is_subject_plural,
)
from promptcrafter.state import create_initial_state, submenu_state_key  # noqa: E402
from promptcrafter.style import build_stylesheet, copy_button  # noqa: E402
from promptcrafter.toggle_state import is_toggle_enabled  # noqa: E402
from promptcrafter.transitions import (  # noqa: E402
    choose_global_selector_option,
    choose_option,
    set_control_weight,
    set_global_selector_enabled,
    set_section_weight,
    set_toggle_enabled,
    toggle_option,
)
from promptcrafter.types import (  # noqa: E402
    Control,
    ControlState,
    Option,
    PromptTarget,
    Schema,
    Section,
)


class PromptCrafterWindow(QMainWindow):
    def __init__(self, schema: Schema) -> None:
        super().__init__()
        self.schema = schema
        self.state = create_initial_state(schema)
        self.setWindowTitle("PromptCrafter")
        self.setStyleSheet(build_stylesheet())

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(0)

        # App header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        title = QLabel("PromptCrafter")
        title.setStyleSheet(f"font-size: 24pt; font-weight: bold; font-family: '{FONT_UI}';")
        header_layout.addWidget(title)
        header_layout.addStretch()
        root_layout.addWidget(header)
        root_layout.addSpacing(20)

        # Prompt areas
        self.positive_prompt = QPlainTextEdit()
        self.positive_prompt.setAccessibleName("Positive prompt")
        self.positive_prompt.setReadOnly(True)
        self.positive_prompt.setMinimumHeight(110)

        self.negative_prompt = QPlainTextEdit()
        self.negative_prompt.setAccessibleName("Negative prompt")
        self.negative_prompt.setReadOnly(True)
        self.negative_prompt.setMinimumHeight(72)

        pos_area = self._build_prompt_area("Positive prompt", self.positive_prompt, "positive")
        neg_area = self._build_prompt_area("Negative prompt", self.negative_prompt, "negative")
        root_layout.addWidget(pos_area)
        root_layout.addSpacing(12)
        root_layout.addWidget(neg_area)
        root_layout.addSpacing(16)

        # Scrollable sections area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        sections_container = QWidget()
        self.sections_layout = QVBoxLayout(sections_container)
        self.sections_layout.setSpacing(16)
        scroll.setWidget(sections_container)
        root_layout.addWidget(scroll)

        self._build_sections()
        self._refresh_prompts()

    def _build_prompt_area(self, label: str, text_edit: QPlainTextEdit, target: PromptTarget) -> QWidget:
        area = QWidget()
        area.setObjectName("prompt_area")
        layout = QVBoxLayout(area)
        layout.setContentsMargins(16, 12, 16, 16)

        # Header row: copy + mode toggle + label
        header = QWidget()
        hlayout = QHBoxLayout(header)
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.setSpacing(12)

        copy_btn = copy_button("Copy prompt")
        copy_btn.clicked.connect(lambda: self._copy_to_clipboard(text_edit.toPlainText()))
        hlayout.addWidget(copy_btn)

        mode = self.state.modes[target]
        mode_btn = QPushButton("manual" if mode == "auto" else "auto")
        mode_btn.setObjectName(f"mode_toggle_{mode}")
        mode_btn.setAccessibleName("manual" if mode == "auto" else "auto")
        mode_btn.clicked.connect(lambda: self._toggle_prompt_mode(target))
        hlayout.addWidget(mode_btn)

        lbl = QLabel(f"<b>{label}</b>")
        lbl.setStyleSheet(f"font-size: {SIZE_HEADING}pt;")
        hlayout.addWidget(lbl)
        hlayout.addStretch()

        layout.addWidget(header)
        layout.addWidget(text_edit)
        return area

    def _toggle_prompt_mode(self, target: PromptTarget) -> None:
        new_mode = "manual" if self.state.modes[target] == "auto" else "auto"
        self.state.modes[target] = new_mode
        prompt_widget = self.positive_prompt if target == "positive" else self.negative_prompt
        if new_mode == "auto":
            prompt_widget.setReadOnly(True)
            self._refresh_prompts()
        else:
            prompt_widget.setReadOnly(False)
        self._rebuild()

    def _copy_to_clipboard(self, text: str) -> None:
        cb = QApplication.clipboard()
        if cb:
            cb.setText(text)

    def _build_sections(self) -> None:
        while self.sections_layout.count():
            item = self.sections_layout.takeAt(0)
            # Hold the widget in a name across both calls. `setParent(None)`
            # leaves it with no C++ parent, so the only thing keeping it alive
            # is a Python reference; asking the layout item for it a second time
            # gets None back and `deleteLater` raises. That branch never ran
            # while a second list was holding those references, which is why the
            # list could not simply be deleted.
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        for section in self.schema.sections:
            section_widget = self._build_section(section)
            if section_widget:
                self.sections_layout.addWidget(section_widget)

        self.sections_layout.addStretch()

    def _build_section(self, section: Section) -> QGroupBox | None:
        if is_hidden(self.state, section.hidden_bys, section.revealed_bys):
            return None

        disabled = is_disabled(self.state, section.disabled_bys)
        plural = is_subject_plural(self.state)
        label = self._display_text(section.text, plural)

        group = QGroupBox(label)
        group.setProperty("section_id", section.id)
        layout = QVBoxLayout(group)
        layout.setSpacing(0)

        # Section header actions: copy button + weight slider (inside the groupbox)
        actions = QWidget()
        actions.setObjectName("section-header-actions")
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, GAP_MEDIUM)
        actions_layout.setSpacing(GAP_MEDIUM)

        copy_btn = copy_button("Copy section")
        copy_btn.clicked.connect(
            lambda sid=section.id: self._copy_section_prompt(sid)
        )
        actions_layout.addWidget(copy_btn)
        actions_layout.addStretch()

        if self._section_has_selection(section):
            weight_row = self._build_weight_widget(
                self.state.sections[section.id].weight,
                lambda w, sid=section.id: self._set_section_weight(sid, w),
            )
            actions_layout.addWidget(weight_row)

        layout.addWidget(actions)

        # Controls
        first_control = True
        prev_was_prefix = False
        for control in section.controls:
            control_widget = self._build_control(control, disabled)
            if control_widget:
                if not first_control and not prev_was_prefix:
                    divider = QWidget()
                    divider.setObjectName("control_divider")
                    divider.setFixedHeight(1)
                    layout.addSpacing(12)
                    layout.addWidget(divider)
                    layout.addSpacing(12)
                layout.addWidget(control_widget)
                first_control = False
            prev_was_prefix = control.kind == "or-prefix"

        if disabled:
            group.setEnabled(False)

        return group

    def _copy_section_prompt(self, section_id: str) -> None:
        section = find_section(self.schema, section_id)
        target = section.prompt_target if section and section.prompt_target else "positive"
        text = build_section_prompt(self.schema, self.state, target, section_id)
        self._copy_to_clipboard(text)

    def _build_control(self, control: Control, section_disabled: bool) -> QWidget | None:
        if control.kind == "hidden-opposite":
            return None
        if is_hidden(self.state, control.hidden_bys, control.revealed_bys):
            return None

        cs = self.state.controls.get(control.id)
        if not cs:
            return None

        disabled = section_disabled or is_disabled(self.state, control.disabled_bys)
        plural = is_subject_plural(self.state)
        label = self._display_text(control.text, plural)

        container = QWidget()
        container.setProperty("control_id", control.id)
        vlayout = QVBoxLayout(container)
        vlayout.setContentsMargins(0, 0, 0, 0)
        vlayout.setSpacing(GAP_SMALL)

        # Control header: label on left, weight on right
        header = QWidget()
        hlayout = QHBoxLayout(header)
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.setSpacing(GAP_MEDIUM)
        control_label = QLabel(f"<b>{label}</b>")
        hlayout.addWidget(control_label)
        hlayout.addStretch()

        if control.kind != "or-prefix" and control_has_at_least_one_selected_option(control, self.state):
            weight_row = self._build_weight_widget(
                cs.weight,
                lambda w, cid=control.id: self._set_control_weight(cid, w),
            )
            hlayout.addWidget(weight_row)

        vlayout.addWidget(header)

        # Control body
        if control.kind == "toggle":
            self._build_toggle_control(vlayout, control, cs, disabled)
        elif control.kind == "global-selector":
            self._build_global_selector_control(vlayout, control, cs, disabled)
        elif is_or_prefixed_kind(control.kind):
            self._build_radio_control(vlayout, control, cs, disabled)
        else:
            self._build_checkbox_control(vlayout, control, cs, disabled)

        return container

    def _build_toggle_control(
        self, layout: QVBoxLayout, control: Control, cs: ControlState, disabled: bool
    ) -> None:
        plural = is_subject_plural(self.state)
        label = self._display_text(control.text, plural)

        # Options row
        options_row = QWidget()
        options_layout = QHBoxLayout(options_row)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(20)
        options_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        toggle = QCheckBox()
        toggle.setObjectName("toggle_switch")
        toggle.setAccessibleName(label)
        toggle.setText(label)
        toggle.setChecked(is_toggle_enabled(cs))
        toggle.setEnabled(not disabled)
        toggle.clicked.connect(lambda checked, cid=control.id: self._on_toggle(cid, checked))
        options_layout.addWidget(toggle)

        layout.addWidget(options_row)

        # Multi-option toggles show options when enabled
        has_option_list = len(control.options) > 1 and isinstance(cs.selected_options, list)
        if is_toggle_enabled(cs) and has_option_list:
            opts_row = QWidget()
            opts_layout = QHBoxLayout(opts_row)
            opts_layout.setContentsMargins(0, 0, 0, 0)
            opts_layout.setSpacing(20)
            opts_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            for option in control.options:
                if is_hidden(self.state, option.hidden_bys, option.revealed_bys):
                    continue
                opt_disabled = disabled or is_disabled(self.state, option.disabled_bys)
                opt_label = self._display_text(option.text, plural)
                cb = CheckBox(opt_label)
                cb.setChecked(isinstance(cs.selected_options, list) and option.id in cs.selected_options)
                cb.setEnabled(not opt_disabled)
                cb.clicked.connect(
                    lambda _, cid=control.id, oid=option.id: self._on_checkbox(cid, oid)
                )
                opts_layout.addWidget(cb)

            layout.addWidget(opts_row)

    def _build_global_selector_control(
        self, layout: QVBoxLayout, control: Control, cs: ControlState, disabled: bool
    ) -> None:
        plural = is_subject_plural(self.state)
        label = self._display_text(control.text, plural)
        is_on = cs.selected_options is not False

        # Toggle row
        toggle_row = QWidget()
        toggle_layout = QHBoxLayout(toggle_row)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        toggle_layout.setSpacing(20)
        toggle_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        toggle = QCheckBox()
        toggle.setObjectName("toggle_switch")
        toggle.setAccessibleName(label)
        toggle.setText(label)
        toggle.setChecked(is_on)
        toggle.setEnabled(not disabled)
        toggle.clicked.connect(
            lambda checked, cid=control.id: self._on_global_selector_toggle(cid, checked)
        )
        toggle_layout.addWidget(toggle)
        layout.addWidget(toggle_row)

        if is_on:
            selected = cs.selected_options if isinstance(cs.selected_options, str) else ""
            opts_row = QWidget()
            opts_layout = QHBoxLayout(opts_row)
            opts_layout.setContentsMargins(0, 0, 0, 0)
            opts_layout.setSpacing(20)
            opts_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            for option in control.options:
                if is_hidden(self.state, option.hidden_bys, option.revealed_bys):
                    continue
                opt_disabled = disabled or is_disabled(self.state, option.disabled_bys)
                opt_label = self._display_text(option.text, plural)
                rb = QRadioButton(opt_label)
                rb.setChecked(selected == option.id)
                rb.setEnabled(not opt_disabled)
                rb.clicked.connect(
                    lambda _, cid=control.id, oid=option.id: self._on_global_selector_option(cid, oid)
                )
                opts_layout.addWidget(rb)

            layout.addWidget(opts_row)

    def _build_radio_control(
        self, layout: QVBoxLayout, control: Control, cs: ControlState, disabled: bool
    ) -> None:
        plural = is_subject_plural(self.state)
        selected = cs.selected_options if isinstance(cs.selected_options, str) else ""

        options_row = QWidget()
        options_layout = QHBoxLayout(options_row)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(20)
        options_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        for option in control.options:
            if is_hidden(self.state, option.hidden_bys, option.revealed_bys):
                continue
            opt_disabled = disabled or is_disabled(self.state, option.disabled_bys)
            opt_label = self._display_text(option.text, plural)

            # Each option + its submenu forms a vertical stack
            opt_stack = QWidget()
            stack_layout = QVBoxLayout(opt_stack)
            stack_layout.setContentsMargins(0, 0, 0, 0)
            stack_layout.setSpacing(GAP_SMALL)

            rb = QRadioButton(opt_label)
            rb.setAutoExclusive(False)
            rb.setChecked(selected == option.id)
            rb.setEnabled(not opt_disabled)
            rb.clicked.connect(
                lambda _, cid=control.id, oid=option.id: self._on_radio(cid, oid)
            )
            stack_layout.addWidget(rb)

            if selected == option.id and option.submenu:
                self._build_submenu(stack_layout, control.id, option, disabled)

            options_layout.addWidget(opt_stack)

        layout.addWidget(options_row)

    def _build_checkbox_control(
        self, layout: QVBoxLayout, control: Control, cs: ControlState, disabled: bool
    ) -> None:
        plural = is_subject_plural(self.state)

        options_row = QWidget()
        options_layout = QHBoxLayout(options_row)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(20)
        options_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        for option in control.options:
            if is_hidden(self.state, option.hidden_bys, option.revealed_bys):
                continue
            opt_disabled = disabled or is_disabled(self.state, option.disabled_bys)
            if control.kind == "required":
                opt_disabled = True
            opt_label = self._display_text(option.text, plural)

            # Each option + its submenu forms a vertical stack
            opt_stack = QWidget()
            stack_layout = QVBoxLayout(opt_stack)
            stack_layout.setContentsMargins(0, 0, 0, 0)
            stack_layout.setSpacing(GAP_SMALL)

            cb = CheckBox(opt_label)
            cb.setChecked(isinstance(cs.selected_options, list) and option.id in cs.selected_options)
            cb.setEnabled(not opt_disabled)
            cb.clicked.connect(
                lambda _, cid=control.id, oid=option.id: self._on_checkbox(cid, oid)
            )
            stack_layout.addWidget(cb)

            if isinstance(cs.selected_options, list) and option.id in cs.selected_options and option.submenu:
                self._build_submenu(stack_layout, control.id, option, disabled)

            options_layout.addWidget(opt_stack)

        layout.addWidget(options_row)

    def _build_submenu(
        self, layout: QVBoxLayout, parent_control_id: str, option: Option, disabled: bool
    ) -> None:
        if not option.submenu:
            return
        key = submenu_state_key(parent_control_id, option.id)
        submenu_state = self.state.controls.get(key)
        if not submenu_state:
            return
        plural = is_subject_plural(self.state)
        is_radio = is_radio_submenu_kind(option.submenu.kind)

        indent = QWidget()
        indent.setObjectName("submenu_indent")
        indent_layout = QVBoxLayout(indent)
        indent_layout.setContentsMargins(12, GAP_SMALL, 0, 0)
        indent_layout.setSpacing(GAP_SMALL)

        for child in option.submenu.options:
            if is_hidden(self.state, child.hidden_bys, child.revealed_bys):
                continue
            child_disabled = disabled or is_disabled(self.state, child.disabled_bys)
            child_label = self._display_text(child.text, plural)

            if is_radio:
                rb = QRadioButton(child_label)
                rb.setAutoExclusive(False)
                rb.setChecked(isinstance(submenu_state.selected_options, str) and submenu_state.selected_options == child.id)
                rb.setEnabled(not child_disabled)
                rb.clicked.connect(
                    lambda _, k=key, oid=child.id: self._on_radio(k, oid)
                )
                indent_layout.addWidget(rb)
            else:
                cb = CheckBox(child_label)
                cb.setChecked(isinstance(submenu_state.selected_options, list) and child.id in submenu_state.selected_options)
                cb.setEnabled(not child_disabled)
                cb.clicked.connect(
                    lambda _, k=key, oid=child.id: self._on_checkbox(k, oid)
                )
                indent_layout.addWidget(cb)

        layout.addWidget(indent)

    def _build_weight_widget(self, value: float, on_change) -> QWidget:
        container = QWidget()
        hlayout = QHBoxLayout(container)
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.setSpacing(6)

        reset_btn = QPushButton("\u21ba")
        reset_btn.setObjectName("weight_reset")
        reset_btn.setVisible(value != 1)
        reset_btn.clicked.connect(lambda: on_change(1.0))
        hlayout.addWidget(reset_btn)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(50)
        slider.setSingleStep(1)
        slider.setValue(int(value * 10))
        slider.setFixedWidth(120)
        slider.setAccessibleName("weight")
        slider.valueChanged.connect(lambda v: on_change(v / 10.0))
        hlayout.addWidget(slider)

        return container

    # --- State mutation handlers ---

    # Each one reads two ids off the widget that was clicked, hands them to the
    # rule in `transitions`, and rebuilds. The submenu radios and checkboxes go
    # through the same two as the top-level ones: submenu state lives in the
    # same flat dict under a composite key, so the rules never had to differ.

    def _on_radio(self, control_key: str, option_id: str) -> None:
        choose_option(self.state, control_key, option_id)
        self._rebuild()

    def _on_checkbox(self, control_key: str, option_id: str) -> None:
        toggle_option(self.state, control_key, option_id)
        self._rebuild()

    def _on_toggle(self, control_id: str, checked: bool) -> None:
        set_toggle_enabled(self.schema, self.state, control_id, checked)
        self._rebuild()

    def _on_global_selector_toggle(self, control_id: str, checked: bool) -> None:
        set_global_selector_enabled(self.schema, self.state, control_id, checked)
        self._rebuild()

    def _on_global_selector_option(self, control_id: str, option_id: str) -> None:
        choose_global_selector_option(self.schema, self.state, control_id, option_id)
        self._rebuild()

    def _set_section_weight(self, section_id: str, weight: float) -> None:
        set_section_weight(self.state, section_id, weight)
        self._rebuild()

    def _set_control_weight(self, control_id: str, weight: float) -> None:
        set_control_weight(self.state, control_id, weight)
        self._rebuild()

    # --- Helpers ---

    def _display_text(self, text, plural: bool) -> str:
        raw = get_text_value(text, plural, self.schema, self.state)
        subs = get_active_substitutions(self.schema, self.state)
        return apply_substitutions(raw, subs, self.schema, self.state) if subs else raw

    def _section_has_selection(self, section: Section) -> bool:
        return any(control_has_at_least_one_selected_option(c, self.state) for c in section.controls)

    def _rebuild(self) -> None:
        self._build_sections()
        self._refresh_prompts()

    def _refresh_prompts(self) -> None:
        if self.state.modes["positive"] == "auto":
            self.positive_prompt.setPlainText(build_prompt(self.schema, self.state, "positive"))
        if self.state.modes["negative"] == "auto":
            self.negative_prompt.setPlainText(build_prompt(self.schema, self.state, "negative"))
