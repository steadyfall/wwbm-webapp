import os
import re

import pytest
from django.contrib.auth.models import User
from playwright.sync_api import Page, expect

from game.models import Level, Lifeline, Option, Question

# Playwright manages an event loop while Django's live test server seeds its sync DB.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture
def player_data(transactional_db):
    user = User.objects.create_user(username="player", password="securePass1")
    amounts = [
        100,
        200,
        300,
        500,
        1_000,
        2_000,
        4_000,
        8_000,
        16_000,
        32_000,
        64_000,
        125_000,
        250_000,
        500_000,
        1_000_000,
    ]
    Level.objects.update_or_create(level_number=-1, defaults={"money": 0})
    Level.objects.update_or_create(level_number=0, defaults={"money": 0})
    for number, amount in enumerate(amounts, start=1):
        Level.objects.update_or_create(level_number=number, defaults={"money": amount})
    Level.objects.update_or_create(level_number=16, defaults={"money": 0})

    for name, description in (
        ("Fifty-50", "Remove two incorrect answers."),
        ("Audience Poll", "See what the audience chose."),
        ("Expert Answer", "Ask an expert for their pick."),
    ):
        Lifeline.objects.create(name=name, description=description)

    for number in range(1, 16):
        if number <= 5:
            difficulty = Question.EASY
        elif number <= 10:
            difficulty = Question.MEDIUM
        else:
            difficulty = Question.HARD
        correct = Option.objects.create(text=f"Correct answer {number}")
        question = Question.objects.create(
            who_added=user,
            text=f"Question number {number}?",
            correct_option=correct,
            difficulty=difficulty,
        )
        question.incorrect_options.set(
            [Option.objects.create(text=f"Wrong {number}-{index}") for index in range(3)]
        )
    return user


def log_in(page: Page, base_url: str) -> None:
    page.goto(f"{base_url}/auth/login/")
    page.get_by_label("Username").fill("player")
    page.get_by_label("Password").fill("securePass1")
    page.get_by_role("button", name="Log in").click()


def begin_game(page: Page) -> None:
    expect(page.get_by_role("heading", name="Ready for the hot seat?")).to_be_visible()
    page.get_by_role("button", name="Start the quiz").click()
    expect(page.locator(".question-box")).to_be_visible()


@pytest.mark.parametrize("viewport_width", [390, 900, 1024])
@pytest.mark.django_db(transaction=True)
def test_compact_timed_game_places_question_before_prize_ladder(
    page: Page, live_server, player_data, viewport_width
):
    page.set_viewport_size({"width": viewport_width, "height": 900})
    log_in(page, live_server.url)
    page.goto(f"{live_server.url}/quiz/")
    begin_game(page)

    board = page.locator(".game-board").bounding_box()
    ladder = page.locator(".ladder").bounding_box()

    assert board is not None and ladder is not None
    assert board["y"] < ladder["y"]
    assert page.evaluate(
        "document.documentElement.scrollWidth <= document.documentElement.clientWidth"
    )


@pytest.mark.django_db(transaction=True)
def test_wrong_answer_journey(page: Page, live_server, player_data):
    page.goto(live_server.url)
    expect(page.get_by_role("heading", name=re.compile("Think fast"))).to_be_visible()
    page.get_by_role("link", name="Take the hot seat").click()
    expect(page.get_by_role("heading", name="Ready for the hot seat?")).to_be_visible()

    page.get_by_role("link", name="Log in to start").click()
    page.get_by_label("Username").fill("player")
    page.get_by_label("Password").fill("securePass1")
    page.get_by_role("button", name="Log in").click()
    begin_game(page)

    page.get_by_role("button", name="Use a lifeline").click()
    expect(page.get_by_role("dialog", name="Choose a lifeline")).to_be_visible()
    page.get_by_role("button", name="Cancel").click()
    expect(page.get_by_role("button", name="Use a lifeline")).to_be_enabled()
    page.get_by_role("button", name="Use a lifeline").click()
    page.get_by_role("button", name="Use lifeline", exact=True).click()
    expect(page.locator(".feedback")).to_be_visible()

    page.locator(".option").filter(has_not_text="Correct answer").first.click()
    page.get_by_role("button", name="Lock answer").click()
    expect(page.get_by_role("heading", name="Wrong Answer")).to_be_visible()
    page.get_by_role("link", name="View leaderboard").click()
    expect(page.get_by_role("heading", name="Leaderboard")).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_voluntary_quit_and_logout_journey(page: Page, live_server, player_data):
    page.goto(live_server.url)
    page.get_by_role("link", name="Log in").click()
    page.get_by_label("Username").fill("player")
    page.get_by_label("Password").fill("securePass1")
    page.get_by_role("button", name="Log in").click()
    page.get_by_role("link", name="Take the hot seat").click()
    begin_game(page)

    page.get_by_role("button", name="Walk away").click()
    expect(page.get_by_role("heading", name="Voluntary Quit")).to_be_visible()
    page.get_by_role("link", name="View leaderboard").click()
    expect(page.get_by_role("heading", name="Leaderboard")).to_be_visible()
    page.get_by_role("link", name="Log out").click()
    expect(page.get_by_role("heading", name=re.compile("Think fast"))).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_win_all_fifteen_questions_journey(page: Page, live_server, player_data):
    log_in(page, live_server.url)
    page.get_by_role("link", name="Take the hot seat").click()
    begin_game(page)
    expected_times = {1: "20", 6: "40", 10: "50", 13: "60"}

    for level in range(1, 16):
        if level in expected_times:
            expect(page.locator("#time-left")).to_have_text(expected_times[level])
        page.locator(".option").filter(has_text="Correct answer").click()
        page.get_by_role("button", name="Lock answer").click()

    expect(page.get_by_role("heading", name="You Won")).to_be_visible()
    page.get_by_role("link", name="View leaderboard").click()
    expect(page.get_by_role("heading", name="Leaderboard")).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_dashboard_exposes_game_filters(page: Page, live_server, player_data):
    log_in(page, live_server.url)
    page.get_by_role("link", name="Dashboard").click()
    expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()
    expect(page.get_by_label("Date played")).to_be_visible()
    expect(page.get_by_label("Correct questions")).to_be_visible()
    expect(page.get_by_label("Used lifelines")).to_be_visible()
    expect(page.get_by_label("Level reached")).to_be_visible()
    expect(page.get_by_label("Minimum score")).to_be_visible()
