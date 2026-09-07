"""What a control has picked, asked rather than type-tested.

``ControlState.selected_options`` was a `bool | str | list[str]` -- one field
carrying three meanings -- and every reader tested which of the three it had
been handed, 38 times across four modules, several of them re-testing inside a
comprehension that already knew. The three meanings are three types now, and
they answer the same questions as each other.
"""

from promptcrafter.types import ManyOf, OneOf, Switch


class TestASwitch:
    def test_it_has_a_selection_when_it_is_on(self):
        assert Switch(True).has_selection()
        assert not Switch(False).has_selection()

    def test_it_holds_no_option_ids_at_all(self):
        assert not Switch(True).contains("zeta")
        assert Switch(True).single_choice() == ""

    def test_it_answers_switched_on_with_its_own_state(self):
        assert Switch(True).is_switched_on()
        assert not Switch(False).is_switched_on()

    def test_a_rule_naming_no_option_reads_it_rather_than_the_enabled_flag(self):
        """A toggle assigned to directly is on whatever the flag beside it says."""
        assert Switch(True).is_engaged(enabled=False)
        assert not Switch(False).is_engaged(enabled=True)

    def test_nothing_that_names_an_option_moves_it(self):
        assert Switch(True).with_toggled("zeta") == Switch(True)
        assert Switch(True).without(lambda candidate: candidate == "zeta") == Switch(True)
        assert Switch(True).with_reach_of("zeta", ["zeta"]) == Switch(True)


class TestOneOf:
    def test_it_has_a_selection_when_something_is_chosen(self):
        assert OneOf("zeta").has_selection()
        assert not OneOf().has_selection()

    def test_it_contains_what_it_chose_and_nothing_else(self):
        assert OneOf("zeta").contains("zeta")
        assert not OneOf("zeta").contains("korth")

    def test_its_choice_is_its_single_choice(self):
        assert OneOf("zeta").single_choice() == "zeta"
        assert OneOf().single_choice() == ""

    def test_it_is_switched_on_by_existing(self):
        """A global selector holds one of these only while it is on -- off is a
        `Switch`, which is how "off" stays tellable from "on, nothing picked"."""
        assert OneOf().is_switched_on()

    def test_a_rule_naming_no_option_asks_whether_anything_is_chosen(self):
        assert OneOf("zeta").is_engaged(enabled=None)
        assert not OneOf().is_engaged(enabled=None)

    def test_a_rule_defers_to_the_enabled_flag_where_the_state_carries_one(self):
        assert not OneOf("zeta").is_engaged(enabled=False)

    def test_choosing_something_else_replaces_the_choice(self):
        assert OneOf("zeta").with_toggled("korth") == OneOf("korth")

    def test_choosing_what_is_already_chosen_empties_it(self):
        assert OneOf("zeta").with_toggled("zeta") == OneOf()

    def test_it_lets_go_of_a_choice_the_rule_reaches(self):
        assert OneOf("zeta").without(lambda candidate: candidate == "zeta") == OneOf()
        assert OneOf("zeta").without(lambda candidate: candidate == "korth") == OneOf("zeta")

    def test_a_reach_takes_the_id_itself_where_the_control_offers_it(self):
        assert OneOf().with_reach_of("zeta", ["korth zeta", "zeta"]) == OneOf("zeta")

    def test_a_reach_takes_the_first_offered_when_the_id_is_not_among_them(self):
        assert OneOf().with_reach_of("zeta", ["korth zeta", "zeta korth"]) == OneOf("korth zeta")

    def test_a_reach_that_finds_nothing_offered_leaves_it_alone(self):
        assert OneOf("korth").with_reach_of("zeta", []) == OneOf("korth")


class TestManyOf:
    def test_it_has_a_selection_when_anything_is_ticked(self):
        assert ManyOf(("zeta",)).has_selection()
        assert not ManyOf().has_selection()

    def test_it_contains_everything_it_holds(self):
        assert ManyOf(("zeta", "korth")).contains("korth")
        assert not ManyOf(("zeta",)).contains("korth")

    def test_it_has_no_single_choice(self):
        assert ManyOf(("zeta", "korth")).single_choice() == ""

    def test_it_is_switched_on_by_existing(self):
        assert ManyOf().is_switched_on()

    def test_a_rule_naming_no_option_defers_to_the_enabled_flag(self):
        assert not ManyOf(("zeta",)).is_engaged(enabled=False)
        assert ManyOf().is_engaged(enabled=True)

    def test_a_rule_falls_back_to_what_is_ticked_where_there_is_no_flag(self):
        assert ManyOf(("zeta",)).is_engaged(enabled=None)
        assert not ManyOf().is_engaged(enabled=None)

    def test_ticking_adds_and_ticking_again_takes_back_out(self):
        assert ManyOf(("zeta",)).with_toggled("korth") == ManyOf(("zeta", "korth"))
        assert ManyOf(("zeta", "korth")).with_toggled("zeta") == ManyOf(("korth",))

    def test_it_lets_go_of_everything_the_rule_reaches(self):
        assert ManyOf(("zeta", "korth")).without(
            lambda candidate: candidate.startswith("z")
        ) == ManyOf(("korth",))

    def test_a_reach_adds_what_is_offered_after_what_was_already_there(self):
        assert ManyOf(("korth",)).with_reach_of("zeta", ["zeta", "zeta korth"]) == ManyOf(
            ("korth", "zeta", "zeta korth")
        )

    def test_a_reach_never_repeats_something_already_ticked(self):
        assert ManyOf(("zeta",)).with_reach_of("zeta", ["zeta"]) == ManyOf(("zeta",))
