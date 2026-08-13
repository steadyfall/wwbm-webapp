import random

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.shortcuts import redirect, render
from django.views.generic import View

from game.models import Level, Lifeline, Question, Session

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


class MainPage(View):
    def get(self, request, *args, **kwargs):
        return render(request, "mainPage.html")

    def post(self, request, *args, **kwargs):
        if "startPlay" not in tuple(self.request.POST.keys()):
            return redirect(self.request.get_full_path())
        if self.request.POST["startPlay"] == "yes":
            if self.request.user.is_authenticated:
                new_session = Session.objects.create(
                    session_user=self.request.user,
                )
                new_session.left_lifelines.set(
                    Lifeline.objects.values_list("id", flat=True)
                )
                return redirect("rules", session=new_session.session_id, permanent=True)
            else:
                return redirect("login")
        return redirect(self.request.get_full_path())


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
        sessionObj = Session.objects.filter(session_id=self.get_sessionId()).first()
        return sessionObj is None or self.request.user == sessionObj.session_user

    def get(self, request, *args, **kwargs):
        sessionId = self.get_sessionId()
        check = Session.objects.filter(session_id=sessionId).exists()
        if check:
            sessionObj = Session.objects.get(session_id=sessionId)
            if not sessionObj.agreedToRules and not sessionObj.gameOver:
                context = {
                    "title": "Rules (game about to begin)",
                    "lifelines": Lifeline.objects.all(),
                    "levels": Level.objects.all(),
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
        timer = (
            int(timeLeft)
            if (
                lifeline is not None
                and lifeline in (FIFTY50, AUDIENCE_POLL, EXPERT_ANSWER)
            )
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
            if (
                self.request.POST["lifelineSubmit"] == "yes"
                and self.request.POST["lifeline"] in LIFELINE_NAMES
            ):
                return render(
                    self.request,
                    "question.html",
                    self.context_creator(
                        lifeline=self.request.POST["lifeline"],
                        timeLeft=self.request.POST["timeLeftAfterLifeline"],
                    ),
                )
            else:
                return render(self.request, "question.html", self.context_creator())

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
            current_question = sessionObj.current_question
            optionText = current_question.correct_option.text
            option = (
                current_question.correct_option
                if userAnswer == optionText
                else current_question.incorrect_options.filter(text=userAnswer).first()
            )
            if option is None:
                messages.warning(request, "Invalid answer!")
                return redirect(self.request.get_full_path())
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
        if mode == "correct":
            title = "Correct answer!"
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
            title = "QUIT at the wrong time!"
            header = 'You just <span class="font-bold">QUIT</span> at the wrong time!'
            formatted_message = message.format(f"{total:,}")
        elif mode == "wrong":
            title = "Wrong answer!"
            header = 'You just <span class="font-bold">LOST</span> it ALL!'
            formatted_message = message.format(f"{total * 99:,}", f"{total:,}")
        context = {
            "title": title,
            "message": formatted_message,
            "mainMessage": header,
            "mode": mode,
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
        allSessions = [
            (
                f"$ {ses['score']:,}",
                ses["current_level__level_number"],
                ses["session_user__username"],
                ses["date_created"],
            )
            for ses in Session.objects.order_by("-score", "-date_created").values(
                "score",
                "current_level__level_number",
                "session_user__username",
                "date_created",
            )
        ]
        paginator = Paginator(allSessions, PAGINATE_NO)
        page = self.request.GET.get("page", 1)
        try:
            objects_list = paginator.page(page)
        except PageNotAnInteger:
            objects_list = paginator.page(1)
        except EmptyPage:
            objects_list = paginator.page(paginator.num_pages)
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
        allSessions = [
            (
                f"$ {ses.score:,}",
                ses.current_level.level_number,
                ses.date_created,
                ses.correct_count,
                ses.wrong_qn_id == default_wrong_qn_pk,
                ses.lifeline_count,
            )
            for ses in Session.objects.filter(session_user=self.request.user)
            .select_related("current_level", "wrong_qn")
            .annotate(
                correct_count=Count("correct_qns", distinct=True),
                lifeline_count=Count("used_lifelines", distinct=True),
            )
            .order_by("-score", "-date_created")
        ]
        paginator = Paginator(allSessions, PAGINATE_NO)
        page = self.request.GET.get("page", 1)
        try:
            objects_list = paginator.page(page)
        except PageNotAnInteger:
            objects_list = paginator.page(1)
        except EmptyPage:
            objects_list = paginator.page(paginator.num_pages)
        context = {
            "title": "Scoreboard",
            "heading": f'Scoreboard for <u><span class="text-info"><i>{self.request.user.username}</i></span></u>',
            "allSessions": objects_list,
        }
        return context

    def get(self, request, *args, **kwargs):
        return render(request, "scoreboard.html", self.context_creator())
