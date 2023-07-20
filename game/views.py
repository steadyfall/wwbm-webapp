from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages

from game.models import *
import random


# Testing pages


def pageChecker(request):
    if request.method == 'POST':
        messages.success(request, "Account created!")
        print(request.POST)
    return render(request, "about.html", {"lifelines": Lifeline.objects.all()})


def rules(request):
    context = {"lifelines": Lifeline.objects.all()}
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


class MainPage(View):
    def get(self, request, *args, **kwargs):
        return render(request, "mainPage.html")

    def post(self, request, *args, **kwargs):
        if "startPlay" not in tuple(self.request.POST.keys()):
            return redirect(self.request.get_full_path())
        if self.request.POST["startPlay"] == "yes":
            new_session = Session.objects.create(
                session_id=Session.get_unused_sessionId(),
                session_user=self.request.user,
            )
            return redirect("rules", session=new_session.session_id, permanent=True)
        return redirect(self.request.get_full_path())


class About(View):
    def get(self, request, *args, **kwargs):
        context = {"lifelines": Lifeline.objects.all()}
        return render(request, "about.html", context)
    

class Rules(View):
    def get_sessionId(self):
        return self.kwargs["session"]

    def get(self, request, *args, **kwargs):
        sessionId = self.get_sessionId()
        check = Session.objects.filter(session_id=sessionId).exists()
        if check:
            sessionObj = Session.objects.get(session_id=sessionId)
            if not sessionObj.agreedToRules and not sessionObj.gameOver:
                context = {"lifelines": Lifeline.objects.all()}
                return render(request, "rules.html", context)
        return redirect("mainpage", permanent=True)

    def post(self, request, *args, **kwargs):
        sessionId = self.get_sessionId()
        check = Session.objects.filter(session_id=sessionId).exists()
        if "agreed" not in tuple(self.request.POST.keys()):
            sessionObj.delete()
            return redirect("mainpage", permanent=True)
        if check:
            sessionObj = Session.objects.get(session_id=sessionId)
            if self.request.POST["agreed"] == "yes":
                sessionObj.agreedToRules = True
                sessionObj.prev_level = Level.objects.get(level_number=-1)
                sessionObj.current_level = Level.objects.get(level_number=1)
                sessionObj.save(
                    update_fields=["agreedToRules", "current_level", "prev_level"]
                )
                return redirect("question", session=sessionId, level=1, permanent=True)
            else:
                sessionObj.delete()
        return redirect("mainpage", permanent=True)


class QuestionInGame(View):
    def get_url_kwargs(self):
        """Order: Session, Level"""
        return (self.kwargs["session"], int(self.kwargs["level"]))

    def context_creator(self):
        def randomOptionsCreator(obj):
            optionsAsIs = [o.text for o in obj.incorrect_options.all()]
            optionsAsIs.extend([obj.correct_option.text])
            random.shuffle(optionsAsIs)
            orderAsIs = [0, 1, 2, 3]
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
        options, order = randomOptionsCreator(qn)
        context = dict(
            question=qn,
            total=total,
            forAmount=forAmount,
            timer=timeDecider(level),
            option1=options[order[0]],
            option2=options[order[1]],
            option3=options[order[2]],
            option4=options[order[3]],
        )
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
                    Session.set_question(sessionId)
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

        if "submit" not in tuple(self.request.POST.keys()) or (
            "userAnswer" not in tuple(self.request.POST.keys())
        ):
            messages.warning(request, "Choose an option!")
            return redirect(self.request.get_full_path())

        if self.request.POST["submit"] == "exit":
            sessionObj.gameOver = True
            sessionObj.save(update_fields=["gameOver"])
            return redirect("statusAfterQn", session=sessionId, level=level, status="quit", permanent=True)

        if self.request.POST["submit"] == "yes":
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
                return redirect(
                    "statusAfterQn",
                    session=sessionId,
                    level=level,
                    status="correct",
                    permanent=True,
                )
            else:
                sessionObj.gameOver = True
                sessionObj.wrong_qn = sessionObj.current_question
                sessionObj.score //= 100
                sessionObj.save(update_fields=["gameOver", "wrong_qn", "score"])
                return redirect(
                    "statusAfterQn", session=sessionId, level=level, status="incorrect", permanent=True
                )


class BetweenQuestion(View):
    def get_url_kwargs(self):
        """Order: Session, Level"""
        return (self.kwargs["session"], int(self.kwargs["level"]), self.kwargs["status"])

    def context_creator(self, message, mode="wrong"):
        sessionId, level, qStatus = self.get_url_kwargs()
        sessionObj = Session.objects.get(session_id=sessionId)
        total = sessionObj.score
        header, formatted_message, nextQ = "", "", False
        if mode == "correct":
            header = "You answered it correctly!"
            formatted_message = message.format(
                f"{Level.objects.get(level_number=level).money:,}", f"{total:,}"
            )
            nextQ = True
        elif mode == "over":
            header = "You have quit successfully!"
            formatted_message = message.format(
                f"{total:,}"
            )
        elif mode == "wrong":
            header = "You answered it wrong!"
            formatted_message = message.format(
                f"{total*99:,}", f"{total:,}"
            )
        context = dict(
            message=formatted_message,
            mainMessage=header,
            nextQ=nextQ,
        )
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
                    msg = """You just QUIT the game successfully, making your total earnings $<u style="color: blueviolet;">{}</u>!"""
                    return render(
                        request, "correct.html", self.context_creator(msg, "over")
                    )
                elif qStatus.lower() == "correct" and level_diff >= 2 and len(sessionObj.wrong_qn.text) == 4:
                    msg = """You just earned $<u style="color: blueviolet;">{}</u> to make your total earnings \
                    $<u style="color: blueviolet;">{}</u>!"""
                    return render(
                        request, "correct.html", self.context_creator(msg, "correct")
                    )
                elif qStatus.lower() == "incorrect" and sessionObj.gameOver and len(sessionObj.wrong_qn.text) > 4:
                    msg = """You just lost $<u class="text-light">{}</u> to make your final earnings $<u class="text-light">{}</u>!"""
                    return render(
                        request, "gameover.html", self.context_creator(msg)
                    )
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
