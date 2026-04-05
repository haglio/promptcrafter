import copy

from promptcrafter.runtime import build_prompt
from promptcrafter.state import create_initial_state
from promptcrafter.types import Control, GlobalSubstitution, Option, PluralText, SupplementedBy
from tests.fixtures.test_schema import TEST_SCHEMA


class TestControlKinds:
    def test_renders_or_control_kind(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["alignment"].selected_options = "hero"

        assert build_prompt(TEST_SCHEMA, state, "positive") == "space robo dino demon monster, hero"

    def test_renders_or_prefix_control_kind(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["element prefix"].selected_options = "void"
        state.controls["armor"].selected_options = "chrome"

        prompt = build_prompt(TEST_SCHEMA, state, "positive")
        assert "void chrome armor" in prompt
        assert "void," not in prompt

    def test_renders_or_adv_control_kind(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["movement"].selected_options = "swiftly"

        assert build_prompt(TEST_SCHEMA, state, "positive") == "space robo dino demon monster, movement swiftly"

    def test_renders_or_adj_control_kind(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["armor"].selected_options = "chrome"

        assert build_prompt(TEST_SCHEMA, state, "positive") == "space robo dino demon monster, chrome armor"

    def test_renders_and_commas_control_kind(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["appendages"].selected_options = ["wings", "horns"]

        assert build_prompt(TEST_SCHEMA, state, "positive") == "space robo dino demon monster, wings, horns"

    def test_renders_and_commas_adv_control_kind(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["stance"].selected_options = ["lunging", "three-quarter"]

        assert build_prompt(TEST_SCHEMA, state, "positive") == (
            "space robo dino demon monster, stance lunging, stance three-quarter"
        )

    def test_renders_and_commas_adj_control_kind(self):
        schema = copy.deepcopy(TEST_SCHEMA)
        schema.sections[1].controls.insert(5, Control(
            id="material vibe",
            text="material vibe",
            kind="and-commas-adj",
            options=[
                Option(id="crystalline", text="crystalline"),
                Option(id="molten", text="molten"),
            ],
        ))

        state = create_initial_state(schema)
        state.controls["material vibe"].selected_options = ["crystalline", "molten"]

        assert "crystalline material vibe, molten material vibe" in build_prompt(schema, state, "positive")

    def test_renders_and_spaces_adj_control_kind(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["render style"].selected_options = ["cinematic", "volumetric"]

        assert build_prompt(TEST_SCHEMA, state, "positive") == (
            "space robo dino demon monster, cinematic volumetric render style"
        )

    def test_renders_global_selector_control_kind(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["colorize"].selected_options = "green"

        assert build_prompt(TEST_SCHEMA, state, "positive") == "space robo dino demon monster"

    def test_initializes_global_selector_as_off(self):
        state = create_initial_state(TEST_SCHEMA)

        assert state.controls["colorize"].selected_options is False

    def test_renders_hidden_opposite_when_linked_option_active(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["temperature"].selected_options = "hot"

        assert build_prompt(TEST_SCHEMA, state, "negative") == "no clutter, blurry, cold"

    def test_does_not_render_multi_option_toggles_just_because_they_have_defaults(self):
        schema = copy.deepcopy(TEST_SCHEMA)
        schema.sections[1].controls.insert(0, Control(
            id="texture pack",
            text="texture pack",
            kind="toggle",
            initially_selected_options=["oak", "pine"],
            options=[
                Option(id="oak", text="oak"),
                Option(id="pine", text="pine"),
            ],
        ))

        state = create_initial_state(schema)

        assert build_prompt(schema, state, "positive") == "space robo dino demon monster"
        assert state.controls["texture pack"].enabled is False
        assert state.controls["texture pack"].selected_options == ["oak", "pine"]

    def test_renders_required_with_all_selected_options(self):
        schema = copy.deepcopy(TEST_SCHEMA)
        schema.sections[0].controls.insert(1, Control(
            id="subject base",
            text="subject base",
            kind="required",
            options=[
                Option(id="hero", text="hero"),
                Option(id="villain", text="villain"),
            ],
        ))

        state = create_initial_state(schema)

        assert build_prompt(schema, state, "positive") == "space robo dino demon monster, hero, villain"

    def test_global_substitutions_for_toggles_without_options(self):
        schema = copy.deepcopy(TEST_SCHEMA)
        schema.sections[1].controls.insert(0, Control(
            id="thorax mode lite",
            text="replace torso terminology",
            kind="toggle",
            global_substitutions=[GlobalSubstitution(from_text="torso", to_text="thorax")],
            options=[],
        ))
        schema.sections[1].controls.insert(1, Control(
            id="torso mention",
            text="torso mention",
            kind="and-commas",
            options=[Option(id="torso badge", text="torso badge")],
        ))

        state = create_initial_state(schema)
        state.controls["thorax mode lite"].selected_options = True
        state.controls["torso mention"].selected_options = ["torso badge"]

        assert build_prompt(schema, state, "positive") == "space robo dino demon monster, thorax badge"

    def test_renders_control_text_for_toggles_without_options_when_enabled(self):
        schema = copy.deepcopy(TEST_SCHEMA)
        schema.sections[1].controls.insert(0, Control(
            id="safety mode",
            text="safety mode",
            custom_text="keep safe",
            kind="toggle",
            options=[],
        ))

        state = create_initial_state(schema)
        state.controls["safety mode"].selected_options = True

        assert build_prompt(schema, state, "positive") == "space robo dino demon monster, keep safe"


class TestControlCustomText:
    def test_renders_custom_text_for_or_adv(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["silhouette"].selected_options = "towering"

        assert build_prompt(TEST_SCHEMA, state, "positive") == "space robo dino demon monster, outline towering"

    def test_renders_custom_text_for_or_adj(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["surface treatment"].selected_options = "runed"

        assert build_prompt(TEST_SCHEMA, state, "positive") == "space robo dino demon monster, runed plating"

    def test_renders_custom_text_for_and_commas_adv(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["sitting on"].selected_options = ["etchings", "glow"]

        assert build_prompt(TEST_SCHEMA, state, "positive") == (
            "space robo dino demon monster, alighting upon etchings, alighting upon glow"
        )

    def test_renders_custom_text_for_and_commas_adj(self):
        schema = copy.deepcopy(TEST_SCHEMA)
        schema.sections[1].controls.insert(5, Control(
            id="surface mood",
            text="surface mood",
            custom_text="finish",
            kind="and-commas-adj",
            options=[
                Option(id="gleaming", text="gleaming"),
                Option(id="weathered", text="weathered"),
            ],
        ))

        state = create_initial_state(schema)
        state.controls["surface mood"].selected_options = ["gleaming", "weathered"]

        assert "gleaming finish, weathered finish" in build_prompt(schema, state, "positive")

    def test_renders_custom_text_for_and_spaces_adj(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["finish profile"].selected_options = ["matte", "pearlescent"]

        assert build_prompt(TEST_SCHEMA, state, "positive") == "space robo dino demon monster, matte pearlescent finish"


class TestOptionCustomControlText:
    def test_options_can_override_control_text(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["silhouette"].selected_options = "lanky"

        assert build_prompt(TEST_SCHEMA, state, "positive") == "space robo dino demon monster, frame lanky"


class TestSupplements:
    def test_options_apply_adv_supplements(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["element prefix"].selected_options = "nebula"
        state.controls["surface treatment"].selected_options = "runed"

        assert "runed plating within nebula" in build_prompt(TEST_SCHEMA, state, "positive")

    def test_controls_apply_adv_supplements(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["element prefix"].selected_options = "nebula"
        state.controls["armor"].selected_options = "chrome"

        assert "chrome armor elemental" in build_prompt(TEST_SCHEMA, state, "positive")

    def test_options_apply_adj_supplements(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["element prefix"].selected_options = "plasma"
        state.controls["surface treatment"].selected_options = "runed"

        assert "plasma runed plating" in build_prompt(TEST_SCHEMA, state, "positive")

    def test_controls_apply_adj_supplements(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["movement"].selected_options = "heavily"
        state.controls["armor"].selected_options = "chrome"

        assert "moving chrome armor" in build_prompt(TEST_SCHEMA, state, "positive")


class TestSubmenuKinds:
    def test_renders_or_adj_submenu(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["appendages"].selected_options = ["wings"]
        state.controls["appendages__wings__submenu"].selected_options = "mechanical"

        assert build_prompt(TEST_SCHEMA, state, "positive") == "space robo dino demon monster, mechanical wings"

    def test_renders_or_adv_submenu(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["appendages"].selected_options = ["horns"]
        state.controls["appendages__horns__submenu"].selected_options = "wishily"

        assert build_prompt(TEST_SCHEMA, state, "positive") == "space robo dino demon monster, horns wishily"

    def test_renders_and_adj_submenu(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["appendages"].selected_options = ["tail"]
        state.controls["appendages__tail__submenu"].selected_options = ["barbed", "segmented"]

        assert build_prompt(TEST_SCHEMA, state, "positive") == "space robo dino demon monster, barbed segmented tail"

    def test_renders_and_adv_submenu(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["appendages"].selected_options = ["antennae"]
        state.controls["appendages__antennae__submenu"].selected_options = ["arched", "flared"]

        assert build_prompt(TEST_SCHEMA, state, "positive") == "space robo dino demon monster, antennae arched flared"


class TestWeights:
    def test_applies_control_weight(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["alignment"].selected_options = "hero"
        state.controls["alignment"].weight = 3

        assert build_prompt(TEST_SCHEMA, state, "positive") == "space robo dino demon monster, (hero:3.0)"

    def test_applies_section_weight(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["alignment"].selected_options = "hero"
        state.sections["subject-core"].weight = 5

        assert "(space robo dino demon monster, hero:5.0)" in build_prompt(TEST_SCHEMA, state, "positive")

    def test_control_weight_overrides_section_weight(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["alignment"].selected_options = "hero"
        state.sections["subject-core"].weight = 5
        state.controls["alignment"].weight = 3
        state.controls["silhouette"].selected_options = "towering"

        prompt = build_prompt(TEST_SCHEMA, state, "positive")
        assert "(space robo dino demon monster:5.0), (hero:3.0), (outline towering:5.0)" in prompt


class TestNegativePrompt:
    def test_builds_negative_prompt_independently(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["neg-quality"].selected_options = ["blurry", "extra limbs"]

        assert build_prompt(TEST_SCHEMA, state, "negative") == "no clutter, blurry, extra limbs"

    def test_does_not_render_hidden_opposite_when_linked_option_inactive(self):
        state = create_initial_state(TEST_SCHEMA)

        assert build_prompt(TEST_SCHEMA, state, "negative") == "no clutter, blurry"


class TestRevealedBys:
    def test_does_not_render_revealed_items_until_trigger_active(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["portrait lighting"].selected_options = "rim-lit"
        state.controls["portrait pose"].selected_options = "close crop"

        assert build_prompt(TEST_SCHEMA, state, "positive") == "space robo dino demon monster"

    def test_renders_revealed_items_when_trigger_active(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["is portrait"].selected_options = True
        state.controls["portrait lighting"].selected_options = "rim-lit"
        state.controls["portrait pose"].selected_options = "close crop"

        assert build_prompt(TEST_SCHEMA, state, "positive") == (
            "space robo dino demon monster, portrait, close crop, rim-lit portrait lighting"
        )


class TestPlurality:
    def test_uses_plural_text_at_control_level(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["count"].selected_options = "two"
        state.controls["stance"].selected_options = ["lunging"]

        prompt = build_prompt(TEST_SCHEMA, state, "positive")
        assert "stances lunging" in prompt
        assert "stance lunging" not in prompt

    def test_uses_plural_text_at_option_level(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["count"].selected_options = "two"
        state.controls["alignment"].selected_options = "hero"

        prompt = build_prompt(TEST_SCHEMA, state, "positive")
        assert "heroes" in prompt
        assert "hero," not in prompt

    def test_uses_custom_plural_text_at_control_level(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["count"].selected_options = "two"
        state.controls["finish profile"].selected_options = ["matte", "pearlescent"]

        assert "matte pearlescent finishes" in build_prompt(TEST_SCHEMA, state, "positive")

    def test_uses_plural_supplemental_text(self):
        schema = copy.deepcopy(TEST_SCHEMA)
        armor = None
        for section in schema.sections:
            for control in section.controls:
                if control.id == "armor":
                    armor = control
                    break
        assert armor is not None

        armor.supplemented_bys = [
            SupplementedBy(
                control_id="movement",
                supplemental_text=PluralText(singular="storm", plural="storms"),
                side="adj",
            ),
        ]

        state = create_initial_state(schema)
        state.controls["count"].selected_options = "two"
        state.controls["movement"].selected_options = "heavily"
        state.controls["armor"].selected_options = "chrome"

        assert "storms chrome armor" in build_prompt(schema, state, "positive")

    def test_applies_global_substitutions_for_singular_and_plural(self):
        state = create_initial_state(TEST_SCHEMA)
        state.controls["portrait focus"].selected_options = ["torso", "torso side profile", "torsos"]
        state.controls["thorax mode"].selected_options = True

        prompt = build_prompt(TEST_SCHEMA, state, "positive")
        assert "thorax, thorax side profile, thoraces" in prompt
        assert "torso" not in prompt
        assert "torsos" not in prompt
