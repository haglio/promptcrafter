from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
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

from promptcrafter.runtime import (
    apply_substitutions,
    build_prompt,
    control_has_at_least_one_selected_option,
    get_active_substitutions,
    get_text_value,
    is_disabled,
    is_hidden,
    is_subject_plural,
)
from promptcrafter.state import create_initial_state
from promptcrafter.toggle_state import (
    get_toggle_selections_for_next_state,
    is_toggle_enabled,
)
from promptcrafter.types import (
    Control,
    ControlState,
    Option,
    Schema,
    Section,
    State,
)


class PromptCrafterWindow(QMainWindow):
    def __init__(self, schema: Schema) -> None:
        super().__init__()
        self.schema = schema
        self.state = create_initial_state(schema)
        self.setWindowTitle("PromptCrafter")

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # Prompt areas
        prompt_area = QWidget()
        prompt_layout = QVBoxLayout(prompt_area)
        self.positive_prompt = QPlainTextEdit()
        self.positive_prompt.setAccessibleName("Positive prompt")
        self.positive_prompt.setReadOnly(True)
        prompt_layout.addWidget(self.positive_prompt)

        self.negative_prompt = QPlainTextEdit()
        self.negative_prompt.setAccessibleName("Negative prompt")
        self.negative_prompt.setReadOnly(True)
        prompt_layout.addWidget(self.negative_prompt)
        root_layout.addWidget(prompt_area)

        # Scrollable sections area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        sections_container = QWidget()
        self.sections_layout = QVBoxLayout(sections_container)
        scroll.setWidget(sections_container)
        root_layout.addWidget(scroll)

        # Track widgets for rebuilds
        self._section_widgets: list[QGroupBox] = []
        self._build_sections()
        self._refresh_prompts()

    def _build_sections(self) -> None:
        for w in self._section_widgets:
            self.sections_layout.removeWidget(w)
            w.setParent(None)
            w.deleteLater()
        self._section_widgets.clear()
        # Remove the trailing stretch if present
        while self.sections_layout.count():
            item = self.sections_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
                item.widget().deleteLater()

        for section in self.schema.sections:
            section_widget = self._build_section(section)
            if section_widget:
                self.sections_layout.addWidget(section_widget)
                self._section_widgets.append(section_widget)

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

        # Section weight slider
        if self._section_has_selection(section):
            weight_row = self._build_weight_widget(
                self.state.sections[section.id].weight,
                lambda w, sid=section.id: self._set_section_weight(sid, w),
            )
            layout.addWidget(weight_row)

        for control in section.controls:
            control_widget = self._build_control(control, disabled)
            if control_widget:
                layout.addWidget(control_widget)

        if disabled:
            group.setEnabled(False)

        return group

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
        vlayout.setContentsMargins(4, 2, 4, 2)

        # Control header with label
        header = QWidget()
        hlayout = QHBoxLayout(header)
        hlayout.setContentsMargins(0, 0, 0, 0)
        control_label = QLabel(f"<b>{label}</b>")
        hlayout.addWidget(control_label)
        hlayout.addStretch()

        # Control weight slider (only if has selection and not or-prefix)
        if control.kind != "or-prefix" and self._control_has_selection(control):
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
        elif control.kind.startswith("or"):
            self._build_radio_control(vlayout, control, cs, disabled)
        else:
            self._build_checkbox_control(vlayout, control, cs, disabled)

        return container

    def _build_toggle_control(
        self, layout: QVBoxLayout, control: Control, cs: ControlState, disabled: bool
    ) -> None:
        plural = is_subject_plural(self.state)
        label = self._display_text(control.text, plural)

        toggle = QCheckBox()
        toggle.setAccessibleName(label)
        toggle.setText(label)
        toggle.setChecked(is_toggle_enabled(cs))
        toggle.setEnabled(not disabled)
        toggle.clicked.connect(lambda checked, cid=control.id: self._on_toggle(cid, checked))
        layout.addWidget(toggle)

        # Multi-option toggles show options when enabled
        has_option_list = len(control.options) > 1 and isinstance(cs.selected_options, list)
        if is_toggle_enabled(cs) and has_option_list:
            for option in control.options:
                if is_hidden(self.state, option.hidden_bys, option.revealed_bys):
                    continue
                opt_disabled = disabled or is_disabled(self.state, option.disabled_bys)
                opt_label = self._display_text(option.text, plural)
                cb = QCheckBox(opt_label)
                cb.setChecked(isinstance(cs.selected_options, list) and option.id in cs.selected_options)
                cb.setEnabled(not opt_disabled)
                cb.clicked.connect(
                    lambda _, cid=control.id, oid=option.id: self._on_toggle_check(cid, oid)
                )
                layout.addWidget(cb)

    def _build_global_selector_control(
        self, layout: QVBoxLayout, control: Control, cs: ControlState, disabled: bool
    ) -> None:
        plural = is_subject_plural(self.state)
        label = self._display_text(control.text, plural)
        is_on = cs.selected_options is not False

        toggle = QCheckBox()
        toggle.setAccessibleName(label)
        toggle.setText(label)
        toggle.setChecked(is_on)
        toggle.setEnabled(not disabled)
        toggle.clicked.connect(
            lambda checked, cid=control.id: self._on_global_selector_toggle(cid, checked)
        )
        layout.addWidget(toggle)

        if is_on:
            selected = cs.selected_options if isinstance(cs.selected_options, str) else ""
            group = QButtonGroup(layout.parentWidget())
            group.setExclusive(False)
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
                layout.addWidget(rb)

    def _build_radio_control(
        self, layout: QVBoxLayout, control: Control, cs: ControlState, disabled: bool
    ) -> None:
        plural = is_subject_plural(self.state)
        selected = cs.selected_options if isinstance(cs.selected_options, str) else ""

        for option in control.options:
            if is_hidden(self.state, option.hidden_bys, option.revealed_bys):
                continue
            opt_disabled = disabled or is_disabled(self.state, option.disabled_bys)
            opt_label = self._display_text(option.text, plural)
            rb = QRadioButton(opt_label)
            rb.setAutoExclusive(False)
            rb.setChecked(selected == option.id)
            rb.setEnabled(not opt_disabled)
            rb.clicked.connect(
                lambda _, cid=control.id, oid=option.id: self._on_radio(cid, oid)
            )
            layout.addWidget(rb)

            # Submenu
            if selected == option.id and option.submenu:
                self._build_submenu(layout, control.id, option, disabled)

    def _build_checkbox_control(
        self, layout: QVBoxLayout, control: Control, cs: ControlState, disabled: bool
    ) -> None:
        plural = is_subject_plural(self.state)

        for option in control.options:
            if is_hidden(self.state, option.hidden_bys, option.revealed_bys):
                continue
            opt_disabled = disabled or is_disabled(self.state, option.disabled_bys)
            if control.kind == "required":
                opt_disabled = True
            opt_label = self._display_text(option.text, plural)
            cb = QCheckBox(opt_label)
            cb.setChecked(isinstance(cs.selected_options, list) and option.id in cs.selected_options)
            cb.setEnabled(not opt_disabled)
            cb.clicked.connect(
                lambda _, cid=control.id, oid=option.id: self._on_checkbox(cid, oid)
            )
            layout.addWidget(cb)

            # Submenu
            if isinstance(cs.selected_options, list) and option.id in cs.selected_options and option.submenu:
                self._build_submenu(layout, control.id, option, disabled)

    def _build_submenu(
        self, layout: QVBoxLayout, parent_control_id: str, option: Option, disabled: bool
    ) -> None:
        if not option.submenu:
            return
        key = f"{parent_control_id}__{option.id}__submenu"
        submenu_state = self.state.controls.get(key)
        if not submenu_state:
            return
        plural = is_subject_plural(self.state)
        is_radio = option.submenu.kind.startswith("or")

        indent = QWidget()
        indent_layout = QVBoxLayout(indent)
        indent_layout.setContentsMargins(20, 0, 0, 0)

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
                    lambda _, k=key, oid=child.id: self._on_submenu_radio(k, oid)
                )
                indent_layout.addWidget(rb)
            else:
                cb = QCheckBox(child_label)
                cb.setChecked(isinstance(submenu_state.selected_options, list) and child.id in submenu_state.selected_options)
                cb.setEnabled(not child_disabled)
                cb.clicked.connect(
                    lambda _, k=key, oid=child.id: self._on_submenu_checkbox(k, oid)
                )
                indent_layout.addWidget(cb)

        layout.addWidget(indent)

    def _build_weight_widget(self, value: float, on_change) -> QWidget:
        container = QWidget()
        hlayout = QHBoxLayout(container)
        hlayout.setContentsMargins(0, 0, 0, 0)

        reset_btn = QPushButton("\u21ba")
        reset_btn.setVisible(value != 1)
        reset_btn.clicked.connect(lambda: on_change(1.0))
        hlayout.addWidget(reset_btn)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(50)
        slider.setSingleStep(1)
        slider.setValue(int(value * 10))
        slider.setAccessibleName("weight")
        slider.valueChanged.connect(lambda v: on_change(v / 10.0))
        hlayout.addWidget(slider)

        return container

    # --- State mutation handlers ---

    def _on_radio(self, control_id: str, option_id: str) -> None:
        cs = self.state.controls.get(control_id)
        if not cs:
            return
        if cs.selected_options == option_id:
            cs.selected_options = ""
        else:
            cs.selected_options = option_id
        self._rebuild()

    def _on_checkbox(self, control_id: str, option_id: str) -> None:
        cs = self.state.controls.get(control_id)
        if not cs or not isinstance(cs.selected_options, list):
            return
        if option_id in cs.selected_options:
            cs.selected_options = [o for o in cs.selected_options if o != option_id]
        else:
            cs.selected_options = [*cs.selected_options, option_id]
        self._rebuild()

    def _on_toggle(self, control_id: str, checked: bool) -> None:
        cs = self.state.controls.get(control_id)
        if not cs:
            return
        control = self._find_schema_control(control_id)
        if not control:
            return
        cs.selected_options = get_toggle_selections_for_next_state(control, cs, checked)
        cs.enabled = checked
        self._rebuild()

    def _on_toggle_check(self, control_id: str, option_id: str) -> None:
        self._on_checkbox(control_id, option_id)

    def _on_global_selector_toggle(self, control_id: str, checked: bool) -> None:
        cs = self.state.controls.get(control_id)
        if not cs:
            return
        previous = cs.selected_options if isinstance(cs.selected_options, str) else ""
        cs.selected_options = "" if checked else False
        if not checked and previous:
            self._clear_global_selector_matches(previous)
        self._rebuild()

    def _on_global_selector_option(self, control_id: str, option_id: str) -> None:
        cs = self.state.controls.get(control_id)
        if not cs:
            return
        previous = cs.selected_options if isinstance(cs.selected_options, str) else ""

        # Clear previous matches
        if previous and previous != option_id:
            self._clear_global_selector_matches(previous)

        cs.selected_options = option_id

        # Apply new matches
        if option_id:
            self._apply_global_selector_matches(control_id, option_id)
        self._rebuild()

    def _clear_global_selector_matches(self, option_id: str) -> None:
        for section in self.schema.sections:
            for control in section.controls:
                if control.kind == "global-selector":
                    continue
                cs = self.state.controls.get(control.id)
                if not cs:
                    continue
                if isinstance(cs.selected_options, str):
                    if cs.selected_options == option_id or option_id in cs.selected_options:
                        cs.selected_options = ""
                elif isinstance(cs.selected_options, list):
                    filtered = [s for s in cs.selected_options if s != option_id and option_id not in s]
                    if len(filtered) != len(cs.selected_options):
                        cs.selected_options = filtered

    def _apply_global_selector_matches(self, source_control_id: str, option_id: str) -> None:
        for section in self.schema.sections:
            for control in section.controls:
                if control.id == source_control_id:
                    continue
                cs = self.state.controls.get(control.id)
                if not cs:
                    continue
                if isinstance(cs.selected_options, str):
                    match = next(
                        (o for o in control.options if o.id == option_id or option_id in o.id),
                        None,
                    )
                    if match:
                        cs.selected_options = match.id
                elif isinstance(cs.selected_options, list):
                    matching = [o.id for o in control.options if o.id == option_id or option_id in o.id]
                    if matching:
                        cs.selected_options = list(set(cs.selected_options) | set(matching))

    def _on_submenu_radio(self, key: str, option_id: str) -> None:
        cs = self.state.controls.get(key)
        if not cs:
            return
        if cs.selected_options == option_id:
            cs.selected_options = ""
        else:
            cs.selected_options = option_id
        self._rebuild()

    def _on_submenu_checkbox(self, key: str, option_id: str) -> None:
        cs = self.state.controls.get(key)
        if not cs or not isinstance(cs.selected_options, list):
            return
        if option_id in cs.selected_options:
            cs.selected_options = [o for o in cs.selected_options if o != option_id]
        else:
            cs.selected_options = [*cs.selected_options, option_id]
        self._rebuild()

    def _set_section_weight(self, section_id: str, weight: float) -> None:
        self.state.sections[section_id].weight = weight
        self._rebuild()

    def _set_control_weight(self, control_id: str, weight: float) -> None:
        cs = self.state.controls.get(control_id)
        if cs:
            cs.weight = weight
        self._rebuild()

    # --- Helpers ---

    def _find_schema_control(self, control_id: str) -> Control | None:
        for section in self.schema.sections:
            for control in section.controls:
                if control.id == control_id:
                    return control
        return None

    def _display_text(self, text, plural: bool) -> str:
        raw = get_text_value(text, plural, self.schema, self.state)
        subs = get_active_substitutions(self.schema, self.state)
        return apply_substitutions(raw, subs, self.schema, self.state) if subs else raw

    def _section_has_selection(self, section: Section) -> bool:
        return any(control_has_at_least_one_selected_option(c, self.state) for c in section.controls)

    def _control_has_selection(self, control: Control) -> bool:
        return control_has_at_least_one_selected_option(control, self.state)

    def _rebuild(self) -> None:
        self._build_sections()
        self._refresh_prompts()

    def _refresh_prompts(self) -> None:
        if self.state.positive_mode == "auto":
            self.positive_prompt.setPlainText(build_prompt(self.schema, self.state, "positive"))
        if self.state.negative_mode == "auto":
            self.negative_prompt.setPlainText(build_prompt(self.schema, self.state, "negative"))
