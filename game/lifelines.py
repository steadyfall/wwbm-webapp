from game.models import *
import random, secrets

FIFTY50 = "Fifty-50"
AUDIENCE_POLL = "Audience Poll"
EXPERT_ANSWER = "Expert Answer"

mappedLifelines = [(2, FIFTY50), (3, AUDIENCE_POLL), (4, EXPERT_ANSWER)]
mappedLifelines = dict(tuple(map(lambda x: x[::-1], mappedLifelines)))


def general_procedure(lifeline_id, question_id, session_id):
    session = Session.objects.get(session_id=session_id)
    question = Question.objects.get(pk=question_id)
    lifeline = Lifeline.objects.get(pk=lifeline_id)
    session.lifeline_qns.add(question)
    session.left_lifelines.remove(lifeline)
    session.used_lifelines.add(lifeline)


def expertAnswer(question_id, session_id):
    general_procedure(mappedLifelines[EXPERT_ANSWER], question_id, session_id)
    question = Question.objects.get(pk=question_id)
    answer = f"The expert says that the answer would be <b>{question.correct_option.text}</b>."
    return answer


def fifty50(question_id, session_id):
    general_procedure(mappedLifelines[FIFTY50], question_id, session_id)
    question = Question.objects.get(pk=question_id)
    random_incorrect = secrets.choice(
        [o.text for o in question.incorrect_options.all()]
    )
    correct = question.correct_option.text
    newOptions = []
    newOptions.extend([random_incorrect, correct])
    random.shuffle(newOptions)
    return newOptions

def audiencePoll(question_id, session_id):
    general_procedure(mappedLifelines[AUDIENCE_POLL], question_id, session_id)
    question = Question.objects.get(pk=question_id)
    correct_answer = question.correct_option.text
    incorrectOptions = [o.text for o in question.incorrect_options.all()]

    percent = {}
    correct = random.randint(50, 100)
    percent[correct_answer] = correct
    for ioption in incorrectOptions:
        percent[ioption] = random.randint(1, correct - 1)
    percent_str = [
        f"<li><b>{x[0]}</b>: <i>{x[1]}</i>% of the audience thinks this is the correct answer.</li>"
        for x in random.sample(tuple(percent.items()), len(tuple(percent.items())))
    ]
    return "\n".join(percent_str)
