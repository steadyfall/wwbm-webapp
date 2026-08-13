from types import SimpleNamespace

import pytest

from game.lifelines import FIFTY50
from game.views import (
    build_option_values,
    get_question_timer,
    is_active_question_session,
)


@pytest.mark.parametrize(
    ("level", "expected_timer"),
    [(0, 5), (1, 20), (6, 40), (10, 50), (13, 60)],
)
def test_get_question_timer_uses_level_thresholds(level, expected_timer):
    assert get_question_timer(level) == expected_timer


def test_get_question_timer_preserves_time_remaining_after_lifeline():
    assert get_question_timer(1, lifeline=FIFTY50, time_left="7") == 7


def test_build_option_values_keeps_fifty_fifty_blanks():
    options, order = build_option_values(
        correct_option="Correct",
        incorrect_options=["Wrong 1", "Wrong 2", "Wrong 3"],
        selected_options=["Wrong 1", "Correct"],
    )

    assert set(options) == {"Wrong 1", "Correct", None}
    assert sorted(order) == [0, 1, 2, 3]


def test_active_question_session_requires_matching_playable_level():
    session = SimpleNamespace(
        agreed_to_rules=True,
        game_over=False,
        current_level=SimpleNamespace(level_number=1),
    )

    assert is_active_question_session(session, 1)
    assert not is_active_question_session(session, 2)
