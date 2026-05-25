import random

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import View

from game.models import Level, Lifeline, Option, Question, Session

from .lifelines import (
    AUDIENCE_POLL,
    EXPERT_ANSWER,
    FIFTY50,
    LIFELINE_NAMES,
    audiencePoll,
    expertAnswer,
    fifty50,
)

# Testing pages


def pageChecker(request):
    if request.method == "POST":
        messages.success(request, "Account created!")
        print(request.POST)
    return render(
        request,
        "gameover.html",
        {
            "title": "title",
            "message": "formatted_message|",
            "mainMessage": "header",
            "mode": "finished",
        },
    )


def rules(request):
    context = {"lifelines": Lifeline.objects.all(), "levels": Level.objects.all()}
    return render(request, "rules.html", context)


def question(request):
    allOptions = [i.text for i in Question.objects.all()[345].incorrect_options.all()]
    allOptions.extend([Question.objects.all()[345].correct_option.text])
    random.shuffle(allOptions)
    p1 = allOptions[:2]
    p2 = allOptions[2:]

    context = {
        "question": Question.objects.all()[345].text,
        "options_part1": p1,
        "options_part2": p2,
    }
    return render(request, "question.html", context)


# Development pages

PAGINATE_NO = 12


def player_levels():
    return Level.objects.filter(level_number__range=(1, 15)).order_by("level_number")


def create_player_session(user):
    session = Session.objects.create(session_user=user)
    session.left_lifelines.set(Lifeline.objects.all())
    session.agreedToRules = True
    session.prev_level = Level.objects.get(level_number=-1)
    session.current_level = Level.objects.get(level_number=1)
    session.save(update_fields=["agreedToRules", "current_level", "prev_level"])
    return session


class MainPage(View):
    def get(self, request, *args, **kwargs):
        return render(request, "mainPage.html")

    def post(self, request, *args, **kwargs):
        if "startPlay" not in tuple(self.request.POST.keys()):
            return redirect(self.request.get_full_path())
        if self.request.POST["startPlay"] == "yes":
            return redirect("quiz_start")
        return redirect(self.request.get_full_path())


class QuizStart(View):
    def get(self, request, *args, **kwargs):
        context = {
            "title": "Start the Challenge | Trivivo",
            "lifelines": Lifeline.objects.all(),
            "levels": player_levels(),
        }
        return render(request, "quiz_start.html", context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = reverse("login")
            return redirect(f"{login_url}?next={reverse('quiz_start')}")
        if request.POST.get("startQuiz") != "yes":
            return redirect("quiz_start")
        session = create_player_session(request.user)
        return redirect("question", session=session.session_id, level=1)


class About(View):
    def get(self, request, *args, **kwargs):
        context = {
            "title": "About The Game",
            "lifelines": Lifeline.objects.all(),
            "levels": Level.objects.all(),
        }
        return render(request, "about.html", context)


class Rules(LoginRequiredMixin, UserPassesTestMixin, View):
    def get_sessionId(self):
        return self.kwargs["session"]

    def test_func(self):
        sessionId = self.get_sessionId()
        check = Session.objects.filter(session_id=sessionId).exists()
        if check:
            sessionObj = Session.objects.get(session_id=sessionId)
            if self.request.user == sessionObj.session_user:
                return True
        return False

    def get(self, request, *args, **kwargs):
        sessionId = self.get_sessionId()
        check = Session.objects.filter(session_id=sessionId).exists()
        if check:
            sessionObj = Session.objects.get(session_id=sessionId)
            if not sessionObj.agreedToRules and not sessionObj.gameOver:
                context = {
                    "title": "Rules (game about to begin)",
                    "lifelines": Lifeline.objects.all(),
                    "levels": player_levels(),
                }
                return render(request, "rules.html", context)
        return redirect("mainpage", permanent=True)

    def post(self, request, *args, **kwargs):
        sessionId = self.get_sessionId()
        check = Session.objects.filter(session_id=sessionId).exists()
        if not check:
            return redirect("mainpage", permanent=True)
        sessionObj = Session.objects.get(session_id=sessionId)
        if "agreed" not in tuple(self.request.POST.keys()):
            sessionObj.delete()
            return redirect("mainpage", permanent=True)
        if self.request.POST["agreed"] == "yes":
            sessionObj.agreedToRules = True
            sessionObj.prev_level = Level.objects.get(level_number=-1)
            sessionObj.current_level = Level.objects.get(level_number=1)
            sessionObj.save(
                update_fields=["agreedToRules", "current_level", "prev_level"]
            )
            return redirect("question", session=sessionId, level=1, permanent=True)
        sessionObj.delete()
        return redirect("mainpage", permanent=True)


class QuestionInGame(LoginRequiredMixin, UserPassesTestMixin, View):
    def get_url_kwargs(self):
        """Order: Session, Level"""
        return (self.kwargs["session"], int(self.kwargs["level"]))

    def test_func(self):
        sessionId, level = self.get_url_kwargs()
        check = Session.objects.filter(session_id=sessionId).exists()
        if check:
            sessionObj = Session.objects.get(session_id=sessionId)
            if self.request.user == sessionObj.session_user:
                return True
        return False

    def context_creator(self, lifeline=None, timeLeft=None):
        def randomOptionsCreator(obj, selected=None):
            if selected is None:
                optionsAsIs = [o.text for o in obj.incorrect_options.all()]
                optionsAsIs.extend([obj.correct_option.text])
                random.shuffle(optionsAsIs)
            else:
                optionsAsIs = list(selected)
                random.shuffle(optionsAsIs)
                optionsAsIs.extend([None, None])
            orderAsIs = list(range(4))
            random.shuffle(orderAsIs)
            return optionsAsIs, orderAsIs

        def timeDecider(level_number):
            if level_number >= 13:
                return 60
            elif level_number >= 10:
                return 50
            elif level_number >= 6:
                return 40
            elif level_number >= 1:
                return 20
            else:
                return 5

        sessionId, level = self.get_url_kwargs()
        sessionObj = Session.objects.get(session_id=sessionId)
        total = sessionObj.score
        forAmount = sessionObj.current_level.money
        qn = sessionObj.current_question
        options, order = (
            randomOptionsCreator(qn, fifty50(qn.pk, sessionId))
            if (lifeline is not None and lifeline == FIFTY50)
            else randomOptionsCreator(qn)
        )
        """TODO:
        Change int(timeleft) to int(timeLeft if timeLeft else 0) for better
        error handling when timer is not functional
        """
        try:
            retained_time = max(1, int(timeLeft))
        except (TypeError, ValueError):
            retained_time = timeDecider(level)
        timer = (
            retained_time
            if lifeline is not None
            and lifeline in (FIFTY50, AUDIENCE_POLL, EXPERT_ANSWER)
            else timeDecider(level)
        )
        fifty50Text = (
            "Kindly check your updated options."
            if (lifeline is not None and lifeline == FIFTY50)
            else None
        )
        expertAnswerText = (
            expertAnswer(qn.pk, sessionId)
            if (lifeline is not None and lifeline == EXPERT_ANSWER)
            else None
        )
        audiencePollText = (
            audiencePoll(qn.pk, sessionId)
            if (lifeline is not None and lifeline == AUDIENCE_POLL)
            else None
        )
        usedLifelineRecently = (
            True
            if (
                lifeline is not None
                and lifeline in (FIFTY50, AUDIENCE_POLL, EXPERT_ANSWER)
            )
            else None
        )
        context = {
            "title": f"WWBM - Question for $ {forAmount:,}",
            "session": sessionObj,
            "question": qn,
            "total": f"{total:,}",
            "forAmount": f"{forAmount:,}",
            "timer": timer,
            "option1": options[order[0]],
            "option2": options[order[1]],
            "option3": options[order[2]],
            "option4": options[order[3]],
            "expertAnswerText": expertAnswerText,
            "audiencePollText": audiencePollText,
            "fifty50Text": fifty50Text,
            "usedLifelineRecently": usedLifelineRecently,
            "options": [
                ("A", options[order[0]]),
                ("B", options[order[1]]),
                ("C", options[order[2]]),
                ("D", options[order[3]]),
            ],
            "levels": player_levels().order_by("-level_number"),
            "level_number": level,
        }
        return context

    def get(self, request, *args, **kwargs):
        sessionId, level = self.get_url_kwargs()
        check = Session.objects.filter(session_id=sessionId).exists()
        if check:
            sessionObj = Session.objects.get(session_id=sessionId)
            if (
                sessionObj.agreedToRules
                and not sessionObj.gameOver
                and (1 <= sessionObj.current_level.level_number <= 15)
                and sessionObj.current_level.level_number == level
            ):
                level_diff = (
                    sessionObj.current_level.level_number
                    - sessionObj.prev_level.level_number
                )
                if level_diff >= 2 or sessionObj.current_question.text == "None":
                    sessionObj.prev_level = Level.objects.get(
                        level_number=1 + sessionObj.prev_level.level_number
                    )
                    sessionObj.save(update_fields=["prev_level"])
                    if Session.set_question(sessionId) is None:
                        messages.error(
                            request,
                            "No questions are available for this level.",
                        )
                        return redirect("mainpage")
                return render(request, "question.html", self.context_creator())
        return redirect("mainpage", permanent=True)

    def post(self, request, *args, **kwargs):
        sessionId, level = self.get_url_kwargs()
        check = Session.objects.filter(session_id=sessionId).exists()
        if not check:
            return redirect("mainpage", permanent=True)
        sessionObj = Session.objects.get(session_id=sessionId)

        if (
            not (sessionObj.agreedToRules)
            or sessionObj.gameOver
            or not (1 <= sessionObj.current_level.level_number <= 15)
            or not (sessionObj.current_level.level_number == level)
        ):
            return redirect("mainpage", permanent=True)

        if "lifelineSubmit" in set(self.request.POST.keys()):
            lifeline = self.request.POST.get("lifeline")
            if (
                self.request.POST["lifelineSubmit"] == "yes"
                and lifeline in LIFELINE_NAMES
                and sessionObj.left_lifelines.filter(name=lifeline).exists()
            ):
                return render(
                    self.request,
                    "question.html",
                    self.context_creator(
                        lifeline=lifeline,
                        timeLeft=self.request.POST.get("timeLeftAfterLifeline"),
                    ),
                )
            else:
                messages.warning(request, "That lifeline is no longer available.")
                return render(self.request, "question.html", self.context_creator())

        if self.request.POST.get("timedOut") == "yes":
            sessionObj.gameOver = True
            sessionObj.wrong_qn = sessionObj.current_question
            sessionObj.score //= 100
            sessionObj.save(update_fields=["gameOver", "wrong_qn", "score"])
            return redirect(
                "statusAfterQn",
                session=sessionId,
                level=level,
                status="incorrect",
            )

        if "submitBtn" not in tuple(self.request.POST.keys()):
            messages.warning(request, "Invalid data!")
            return redirect(self.request.get_full_path())

        if self.request.POST["submitBtn"] == "exit":
            sessionObj.gameOver = True
            sessionObj.save(update_fields=["gameOver"])
            return redirect(
                "statusAfterQn",
                session=sessionId,
                level=level,
                status="quit",
                permanent=True,
            )

        if "userAnswer" not in tuple(self.request.POST.keys()):
            messages.warning(request, "Choose an option!")
            return redirect(self.request.get_full_path())

        if self.request.POST["submitBtn"] == "yes":
            userAnswer = self.request.POST["userAnswer"]
            optionText = sessionObj.current_question.correct_option.text
            option = Option.objects.get(text=userAnswer)
            option.hits.add(sessionObj.session_user)
            if userAnswer == optionText:
                sessionObj.score += sessionObj.current_level.money
                sessionObj.current_level = Level.objects.get(
                    level_number=1 + sessionObj.current_level.level_number
                )
                sessionObj.save(update_fields=["current_level", "score"])
                sessionObj.correct_qns.add(sessionObj.current_question)

                # Message to user after they have answered correctly and being redirected to next question
                if level == 15 and sessionObj.current_level.level_number == 16:
                    sessionObj.gameOver = True
                    sessionObj.save(update_fields=["gameOver"])
                    return redirect(
                        "statusAfterQn",
                        session=sessionId,
                        level=level,
                        status="correct",
                        permanent=True,
                    )
                msg = """You just earned <span class="font-bold">${}</span> \
                    to make your TOTAL earnings <span class="underline underline-offset-2">${}</span>!"""
                messages.success(
                    request,
                    msg.format(
                        f"{Level.objects.get(level_number=level).money:,}",
                        f"{sessionObj.score:,}",
                    ),
                )

                # Redirecting to next question
                return redirect(
                    "question",
                    session=sessionId,
                    level=sessionObj.current_level.level_number,
                    permanent=True,
                )

                # Previous method of going to intermediary page and giving option to user to quit
                """ return redirect(
                    "statusAfterQn",
                    session=sessionId,
                    level=level,
                    status="correct",
                    permanent=True,
                ) """
            else:
                sessionObj.gameOver = True
                sessionObj.wrong_qn = sessionObj.current_question
                sessionObj.score //= 100
                sessionObj.save(update_fields=["gameOver", "wrong_qn", "score"])
                return redirect(
                    "statusAfterQn",
                    session=sessionId,
                    level=level,
                    status="incorrect",
                    permanent=True,
                )


class BetweenQuestion(LoginRequiredMixin, UserPassesTestMixin, View):
    def get_url_kwargs(self):
        """Order: Session, Level"""
        return (
            self.kwargs["session"],
            int(self.kwargs["level"]),
            self.kwargs["status"],
        )

    def test_func(self):
        sessionId, level, qStatus = self.get_url_kwargs()
        check = Session.objects.filter(session_id=sessionId).exists()
        if check:
            sessionObj = Session.objects.get(session_id=sessionId)
            if self.request.user == sessionObj.session_user:
                return True
        return False

    def context_creator(self, message, mode="wrong"):
        sessionId, level, qStatus = self.get_url_kwargs()
        sessionObj = Session.objects.get(session_id=sessionId)
        total = sessionObj.score
        header, formatted_message = "", ""
        title = ""
        result_title = "Wrong Answer"
        if mode == "correct":
            title = "Correct answer!"
            result_title = "You Won" if sessionObj.current_level.level_number == 16 else "Correct Answer"
            header = 'You just <span class="font-bold">ANSWERED</span> it correctly!'
            formatted_message = (
                message.format(
                    f"{Level.objects.get(level_number=level).money:,}", f"{total:,}"
                )
                if sessionObj.current_level.level_number != 16
                else message.format(f"{total:,}")
            )
            mode = mode if sessionObj.current_level.level_number != 16 else "finished"
        elif mode == "over":
            title = "Voluntary Quit"
            result_title = "Voluntary Quit"
            header = "You walked away with your winnings."
            formatted_message = message.format(f"{total:,}")
        elif mode == "wrong":
            title = "Wrong Answer"
            result_title = "Wrong Answer"
            header = "That answer did not land."
            formatted_message = message.format(f"{total*99:,}", f"{total:,}")
        context = {
            "title": title,
            "message": formatted_message,
            "mainMessage": header,
            "mode": mode,
            "resultTitle": result_title,
        }
        return context

    def get(self, request, *args, **kwargs):
        sessionId, level, qStatus = self.get_url_kwargs()
        check = Session.objects.filter(session_id=sessionId).exists()
        if check:
            sessionObj = Session.objects.get(session_id=sessionId)
            if (
                sessionObj.agreedToRules
                and (1 <= sessionObj.current_level.level_number <= 16)
                and (0 <= sessionObj.current_level.level_number - level <= 1)
            ):
                level_diff = (
                    sessionObj.current_level.level_number
                    - sessionObj.prev_level.level_number
                )
                if (
                    qStatus.lower() == "quit"
                    and sessionObj.gameOver
                    and len(sessionObj.wrong_qn.text) == 4
                    and level_diff in (1, 2)
                ):
                    msg = """You just QUIT the game successfully, \
                        making your total earnings $<span class="font-bold underline underline-offset-2">{}</span>!"""
                    return render(
                        request, "gameover.html", self.context_creator(msg, "over")
                    )
                elif (
                    qStatus.lower() == "correct"
                    and level_diff >= 2
                    and len(sessionObj.wrong_qn.text) == 4
                ):
                    if level == 15 and sessionObj.current_level.level_number == 16:
                        msg = """You just <span class="font-bold">FINISHED</span> \
                            the game to make your total earnings $<span class="font-bold underline underline-offset-2">{}</span>!"""
                        return render(
                            request,
                            "gameover.html",
                            self.context_creator(msg, "correct"),
                        )
                    msg = """You just earned $<span class="font-bold">{}</span> \
                        to make your total earnings $<span class="font-bold underline underline-offset-2">{}</span>!"""
                    return render(
                        request, "gameover.html", self.context_creator(msg, "correct")
                    )
                elif (
                    qStatus.lower() == "incorrect"
                    and sessionObj.gameOver
                    and len(sessionObj.wrong_qn.text) > 4
                ):
                    msg = """You just lost $<span class="font-bold">{}</span> \
                          to make your final earnings $<span class="font-bold underline underline-offset-2">{}</span>!"""
                    return render(request, "gameover.html", self.context_creator(msg))
        return redirect("mainpage", permanent=True)

    def post(self, request, *args, **kwargs):
        sessionId, level, qStatus = self.get_url_kwargs()
        check = Session.objects.filter(session_id=sessionId).exists()

        if qStatus.lower() != "correct":
            return redirect("mainpage", permanent=True)

        if not check:
            return redirect("mainpage", permanent=True)
        sessionObj = Session.objects.get(session_id=sessionId)

        if (
            not sessionObj.agreedToRules
            and not (1 <= sessionObj.current_level.level_number <= 16)
            and not (0 <= sessionObj.current_level.level_number - level <= 1)
        ):
            return redirect("mainpage", permanent=True)

        if "nextQ" not in tuple(self.request.POST.keys()):
            messages.warning(request, "Choose an option!")
            return redirect(self.request.get_full_path())

        if self.request.POST["nextQ"] == "no":
            sessionObj.gameOver = True
            sessionObj.save(update_fields=["gameOver"])
            return redirect(
                "statusAfterQn",
                session=sessionId,
                level=level,
                status="quit",
                permanent=True,
            )

        if self.request.POST["nextQ"] == "yes":
            return redirect(
                "question",
                session=sessionId,
                level=sessionObj.current_level.level_number,
                permanent=True,
            )


class Leaderboard(View):
    def context_creator(self):
        sessions = Session.objects.select_related("current_level", "session_user").order_by(
            "-score", "-date_created"
        )
        paginator = Paginator(sessions, PAGINATE_NO)
        page = self.request.GET.get("page", 1)
        try:
            objects_list = paginator.page(page)
        except PageNotAnInteger:
            objects_list = paginator.page(1)
        except EmptyPage:
            objects_list = paginator.page(paginator.num_pages)
        for session in objects_list.object_list:
            session.level_reached = max(session.current_level.level_number - 1, 0)
        context = {
            "title": "WWBM Leaderboard",
            "heading": "Leaderboard",
            "allSessions": objects_list,
        }
        return context

    def get(self, request, *args, **kwargs):
        return render(request, "leaderboard.html", self.context_creator())


class ScoreBoard(LoginRequiredMixin, View):
    def context_creator(self):
        default_wrong_qn_pk = Question.get_default_pk()
        filters = {
            "date_played": self.request.GET.get("date_played", ""),
            "correct_questions": self.request.GET.get("correct_questions", ""),
            "used_lifelines": self.request.GET.get("used_lifelines", ""),
            "level_reached": self.request.GET.get("level_reached", ""),
            "minimum_score": self.request.GET.get("minimum_score", ""),
        }
        sessions = (
            Session.objects.filter(session_user=self.request.user)
            .select_related("current_level", "wrong_qn")
            .annotate(
                correct_count=Count("correct_qns", distinct=True),
                lifeline_count=Count("used_lifelines", distinct=True),
            )
        )
        if filters["date_played"]:
            sessions = sessions.filter(date_created__date=filters["date_played"])
        for name, lookup in (
            ("correct_questions", "correct_count"),
            ("used_lifelines", "lifeline_count"),
        ):
            if filters[name].isdigit():
                sessions = sessions.filter(**{lookup: int(filters[name])})
        if filters["level_reached"].isdigit():
            sessions = sessions.filter(
                current_level__level_number=int(filters["level_reached"]) + 1
            )
        if filters["minimum_score"].isdigit():
            sessions = sessions.filter(score__gte=int(filters["minimum_score"]))
        sessions = sessions.order_by("-score", "-date_created")
        paginator = Paginator(sessions, PAGINATE_NO)
        page = self.request.GET.get("page", 1)
        try:
            objects_list = paginator.page(page)
        except PageNotAnInteger:
            objects_list = paginator.page(1)
        except EmptyPage:
            objects_list = paginator.page(paginator.num_pages)
        for session in objects_list.object_list:
            session.level_reached = max(session.current_level.level_number - 1, 0)
            session.voluntary_quit = (
                session.gameOver and session.wrong_qn_id == default_wrong_qn_pk
            )
        page_query = self.request.GET.copy()
        page_query.pop("page", None)
        context = {
            "title": "Scoreboard",
            "heading": f"Dashboard for {self.request.user.username}",
            "allSessions": objects_list,
            "filters": filters,
            "level_choices": range(0, 16),
            "filter_query": page_query.urlencode(),
        }
        return context

    def get(self, request, *args, **kwargs):
        return render(request, "scoreboard.html", self.context_creator())
