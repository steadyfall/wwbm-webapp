import datetime

from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.admin.options import construct_change_message
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count, F, Max, Q
from django.db.models.functions import Length, Trim, TruncDate
from django.forms import ModelForm
from django.http import HttpResponseNotAllowed, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import View
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from game.models import Category, Lifeline, Option, Question, QuestionOrder, Session

from .crud import (
    PAGINATE_NO,
    build_breadcrumbs,
    get_record,
    load_instance,
    paginate,
    record_context,
)
from .forms import CategoryForm, LifelineForm, OptionForm, QuestionForm
from .mixins import SuperuserRequiredMixin
from .serializers import QuestionEncoder
from .viewsExtra import (
    daterange,
    get_content_type_for_model,
    log_addition,
    log_change,
    log_deletion,
    pk_checker,
    pretty_change_message,
    safe_object_delete_log,
    safe_pk_list_converter,
)

modelDict: dict[str, models.Model] = {
    "session": Session,
    "lifeline": Lifeline,
    "category": Category,
    "question": Question,
    "option": Option,
}
modelFormDict: dict[str, ModelForm] = {
    "session": Session,
    "lifeline": LifelineForm,
    "category": CategoryForm,
    "question": QuestionForm,
    "option": OptionForm,
}
allowedModelNames = tuple(modelDict.keys())
addressOfPages = {
    "adminMainPage": reverse_lazy("adminMainPage"),
    "test": reverse_lazy("test"),
    "adminListDB": lambda x: reverse_lazy("adminListDB", kwargs=x),
    "adminListLogs": reverse_lazy("adminListLogs"),
    "adminDBObject": lambda x: reverse_lazy("adminDBObject", kwargs=x),
    "adminDBObjectCreate": lambda x: reverse_lazy("adminDBObjectCreate", kwargs=x),
    "adminDBObjectDelete": lambda x: reverse_lazy("adminDBObjectDelete", kwargs=x),
    "adminDBObjectHistory": lambda x: reverse_lazy("adminDBObjectHistory", kwargs=x),
    "APIAccess": reverse_lazy("APIAccess"),
    "APIDocs": reverse_lazy("APIDocs"),
}

SITE_NAME = "AdminPanel"


# Test site


def testSite(request):
    return render(
        request,
        "adminpanel/index.html",
        {},
    )


# Production sites


class AdminViewBase(SuperuserRequiredMixin, LoginRequiredMixin, View):
    """Base view for admin panel pages that require a superuser login."""

    login_url = "adminLogin"
    raise_exception = False

    def redirect_back(self):
        """Redirect back to the previous page or the admin panel root."""
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER", "/admin/"))


class FormStateMixin:
    """Shared form-state handling for create and change views."""

    form_class = None
    initial = {}
    instance = None

    def get_initial(self):
        """Return the initial data to use for forms on this view."""
        return self.initial.copy()

    def get_instance(self):
        """Return the model instance bound to forms on this view."""
        return self.instance

    def get_form_class(self):
        """Return the form class to use."""
        return self.form_class

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {"initial": self.get_initial()}

        if self.request.method in ("POST", "PUT"):
            kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                }
            )
        if self.get_instance() is not None:
            kwargs["instance"] = self.get_instance()
        return kwargs

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def set_form_class(self, db):
        """Set the form class used by this view for the given model name."""
        self.form_class = modelFormDict[db]


class AdminMainPage(AdminViewBase):
    def add_object_exists_to_logs(self, logs):
        logs_by_model = {}
        for log in logs:
            model = log.content_type.model_class()
            if model is not None:
                logs_by_model.setdefault(model, []).append(log)

        for model, model_logs in logs_by_model.items():
            object_ids = [log.object_id for log in model_logs]
            existing_ids = {
                str(pk)
                for pk in model.objects.filter(pk__in=object_ids).values_list(
                    "pk", flat=True
                )
            }
            for log in model_logs:
                log.object_exists = log.object_id in existing_ids

    def context_creater(self):
        recent_log = list(
            LogEntry.objects.select_related("content_type").order_by("-action_time")[
                :12
            ]
        )
        self.add_object_exists_to_logs(recent_log)
        total_question_count = Question.objects.count()
        daily_question_count = Question.objects.filter(
            date_added__gte=datetime.date.today()
        ).count()
        total_session_count = Session.objects.count()
        daily_session_count = Session.objects.filter(
            date_created__gte=datetime.date.today()
        ).count()
        top_30_highest_scores = list(
            Session.objects.order_by("-score", "-date_created").values_list(
                "score", flat=True
            )[:30]
        )
        highest_score = (
            f"{top_30_highest_scores[0]:,}" if top_30_highest_scores else "0"
        )
        total_user_count = User.objects.count()
        daily_user_count = User.objects.filter(
            date_joined__gte=datetime.date.today()
        ).count()
        categories = list(
            Category.objects.annotate(question_count=Count("all_questions"))
        )
        active_users_count = User.objects.filter(is_active=True).count()

        percent_of_daily_threshold = round(((daily_question_count) / 10) * 100)
        percent_of_active_users = (
            round((active_users_count / total_user_count) * 100)
            if total_user_count
            else 0
        )
        more_than_ten_sessions = daily_session_count / 10
        category_with_most_qs = max(
            categories,
            key=lambda category: category.question_count,
            default=None,
        )

        # Chart data
        (
            date_list,
            session_list,
            session_user_list,
            session_easy_list,
            session_medium_list,
            session_hard_list,
            score_list,
        ) = [[] for _ in range(7)]
        start_date = datetime.date.today() - datetime.timedelta(15)
        end_date = datetime.date.today() + datetime.timedelta(1)
        session_stats = {
            row["day"]: row
            for row in Session.objects.filter(
                date_created__date__gte=start_date,
                date_created__date__lt=end_date,
            )
            .annotate(day=TruncDate("date_created"))
            .values("day")
            .annotate(
                session_count=Count("pk"),
                session_user_count=Count("session_user", distinct=True),
                max_score=Max("score"),
            )
        }
        question_stats = {
            row["day"]: row
            for row in QuestionOrder.objects.filter(
                date_chosen__date__gte=start_date,
                date_chosen__date__lt=end_date,
            )
            .annotate(day=TruncDate("date_chosen"))
            .values("day")
            .annotate(
                easy_count=Count("pk", filter=Q(question__difficulty=Question.EASY)),
                medium_count=Count(
                    "pk", filter=Q(question__difficulty=Question.MEDIUM)
                ),
                hard_count=Count("pk", filter=Q(question__difficulty=Question.HARD)),
            )
        }
        for date in daterange(start_date, end_date):
            session_row = session_stats.get(date, {})
            question_row = question_stats.get(date, {})
            date_list.append(date.strftime("%d-%m"))
            session_list.append(session_row.get("session_count", 0))
            session_user_list.append(session_row.get("session_user_count", 0))
            session_easy_list.append(question_row.get("easy_count", 0))
            session_medium_list.append(question_row.get("medium_count", 0))
            session_hard_list.append(question_row.get("hard_count", 0))
            score_list.append(session_row.get("max_score") or 0)
        users_with_session_counts = list(
            User.objects.annotate(session_count=Count("initiated_sessions"))
        )
        active_users_labels = [user.username for user in users_with_session_counts]
        active_users_activity = [
            user.session_count for user in users_with_session_counts
        ]

        context = {
            "recent_log": recent_log,
            "total_question_count": total_question_count,
            "daily_question_count": daily_question_count,
            "total_session_count": total_session_count,
            "daily_session_count": daily_session_count,
            "top_30_highest_scores": top_30_highest_scores,
            "highest_score": highest_score,
            "total_user_count": total_user_count,
            "daily_user_count": daily_user_count,
            "total_category_count": f"{len(categories):,}",
            "active_users_count": active_users_count,
            "percent_of_daily_threshold": percent_of_daily_threshold,
            "percent_of_active_users": percent_of_active_users,
            "more_than_ten_sessions": more_than_ten_sessions,
            "category_with_most_qs": category_with_most_qs,
            "date_list": date_list,
            "session_list": session_list,
            "session_user_list": session_user_list,
            "session_easy_list": session_easy_list,
            "session_medium_list": session_medium_list,
            "session_hard_list": session_hard_list,
            "score_list": score_list,
            "active_users_labels": active_users_labels,
            "active_users_activity": active_users_activity,
        }
        breadcrumbs = [
            ["Admin", addressOfPages["adminMainPage"]],
            [[], []],
        ]
        context["breadcrumbs"] = build_breadcrumbs(breadcrumbs)
        context.update(self.kwargs)
        return context

    def get(self, request, *args, **kwargs):
        context = self.context_creater()
        return render(request, "adminpanel/index.html", context)


class AdminListDB(AdminViewBase):
    def get_url_kwargs(self):
        return str(self.kwargs["db"])

    def context_creator(self):
        smallcaseDB = self.get_url_kwargs()
        model = modelDict[smallcaseDB]
        query = (
            model.objects.all()
            .annotate(key_primary=F(model._meta.pk.name))
            .order_by("-key_primary")
        )
        objects_list = paginate(query, self.request.GET.get("page", 1), PAGINATE_NO)
        context = record_context(model, self.kwargs, allRecords=objects_list)
        context["title"] = SITE_NAME + " - " + context["recordVerboseName"]
        context["breadcrumbs"] = build_breadcrumbs(
            [
                ["Admin", addressOfPages["adminMainPage"]],
                [smallcaseDB.title()],
            ]
        )
        return context

    def get(self, request, *args, **kwargs):
        smallcaseDB = self.get_url_kwargs()
        if smallcaseDB not in allowedModelNames:
            return self.redirect_back()
        context = self.context_creator()
        return render(request, "adminpanel/listdb.html", context)

    def is_bulk_delete_request(self, request, model, given_pk, safe_given_pk):
        """Return True when the request deletes a fully validated selection."""
        admin_action = request.POST.get("admin-action")
        if (
            admin_action not in ("Delete selected", "Delete all in view")
            or not given_pk
        ):
            return False
        valid_pks = set(
            model.objects.all()
            .annotate(key_primary=F(model._meta.pk.name))
            .values_list("key_primary", flat=True)
        )
        if set(safe_given_pk) - valid_pks:
            return False
        if admin_action == "Delete selected":
            return True
        return (
            bool(request.POST.get("allcheck"))
            and len(set(safe_given_pk)) == PAGINATE_NO
        )

    def post(self, request, *args, **kwargs):
        smallcaseDB = self.get_url_kwargs()
        if (
            smallcaseDB not in allowedModelNames
            or request.POST.get("admin-action") == "-"
        ):
            return self.redirect_back()

        model = modelDict[smallcaseDB]
        given_pk = request.POST.getlist("indcheck")
        safe_given_pk = safe_pk_list_converter(given_pk, model)
        if self.is_bulk_delete_request(request, model, given_pk, safe_given_pk):
            object_name = (
                model._meta.verbose_name
                if len(given_pk) == 1
                else model._meta.verbose_name_plural
            )
            action = [
                safe_object_delete_log(request, model, pk) for pk in safe_given_pk
            ]
            deleted = sum(result[0] for result in action)
            messages.success(
                request,
                f"""Successfully deleted {len(action)} {object_name} and {deleted} objects related to it!""",
            )

        context = self.context_creator()
        return render(request, "adminpanel/listdb.html", context)


class AdminDBObjectCreate(AdminViewBase, FormStateMixin):
    def get_url_kwargs(self):
        return str(self.kwargs["db"])

    def is_creatable(self, smallcaseDB):
        return smallcaseDB not in allowedModelNames or smallcaseDB in (
            "session",
            "lifeline",
        )

    def context_creator(self):
        smallcaseDB = self.get_url_kwargs()
        model = modelDict[smallcaseDB]
        context = record_context(model, self.kwargs, form=self.get_form())
        context["title"] = (
            SITE_NAME + " - Create " + context["recordVerboseName"].title()
        )
        context["breadcrumbs"] = build_breadcrumbs(
            [
                ["Admin", addressOfPages["adminMainPage"]],
                [
                    smallcaseDB.title(),
                    addressOfPages["adminListDB"]({"db": smallcaseDB}),
                ],
                [
                    f"Create {smallcaseDB.title()}",
                    addressOfPages["adminDBObjectCreate"]({"db": smallcaseDB}),
                ],
            ]
        )
        return context

    def get(self, request, *args, **kwargs):
        smallcaseDB = self.get_url_kwargs()
        if self.is_creatable(smallcaseDB):
            return self.redirect_back()
        self.set_form_class(smallcaseDB)
        context = self.context_creator()
        return render(request, "adminpanel/objectCreate.html", context)

    def post(self, request, *args, **kwargs):
        smallcaseDB = self.get_url_kwargs()
        if self.is_creatable(smallcaseDB):
            return self.redirect_back()
        if request.POST.get("cancel"):
            return redirect("adminListDB", db=smallcaseDB)
        self.set_form_class(smallcaseDB)
        form = self.get_form()
        if not form.is_valid():
            context = self.context_creator()
            return render(request, "adminpanel/objectCreate.html", context)
        if request.POST.get("create"):
            new_object = form.save()
            change_message = construct_change_message(form, None, "add")
            log_addition(request, new_object, change_message)
            messages.success(request, pretty_change_message(new_object))
            return redirect("adminDBObject", db=smallcaseDB, pk=new_object.pk)
        return redirect("adminListDB", db=smallcaseDB)


class AdminDBObjectChange(AdminViewBase, FormStateMixin):
    def get_url_kwargs(self):
        db, pk = str(self.kwargs["db"]), str(self.kwargs["pk"])
        return (db, pk)

    def context_creator(self):
        smallcaseDB, pk = self.get_url_kwargs()
        model = modelDict[smallcaseDB]
        context = record_context(model, self.kwargs, form=self.get_form())
        context["title"] = SITE_NAME + " - View " + context["recordVerboseName"].title()
        context["breadcrumbs"] = build_breadcrumbs(
            [
                ["Admin", addressOfPages["adminMainPage"]],
                [
                    smallcaseDB.title(),
                    addressOfPages["adminListDB"]({"db": smallcaseDB}),
                ],
                [
                    f"View {smallcaseDB.title()}",
                    addressOfPages["adminDBObject"]({"db": smallcaseDB, "pk": pk}),
                ],
            ]
        )
        return context

    def set_form_state(self, model, smallcaseDB, pk):
        self.set_form_class(smallcaseDB)
        self.instance = load_instance(model, pk)

    def get(self, request, *args, **kwargs):
        smallcaseDB, pk = self.get_url_kwargs()
        if smallcaseDB not in allowedModelNames or smallcaseDB == "session":
            return self.redirect_back()
        model = modelDict[smallcaseDB]
        if not pk_checker(pk, model):
            return redirect("adminListDB", db=smallcaseDB)
        self.set_form_state(model, smallcaseDB, pk)
        context = self.context_creator()
        return render(request, "adminpanel/objectView.html", context)

    def post(self, request, *args, **kwargs):
        smallcaseDB, pk = self.get_url_kwargs()
        if smallcaseDB not in allowedModelNames or smallcaseDB in (
            "session",
            "lifeline",
        ):
            return self.redirect_back()
        model = modelDict[smallcaseDB]
        if not pk_checker(pk, model):
            return redirect("adminListDB", db=smallcaseDB)
        self.set_form_state(model, smallcaseDB, pk)

        if request.POST.get("cancel"):
            return redirect("adminListDB", db=smallcaseDB)

        form = self.get_form()
        if not form.is_valid():
            messages.warning(request, "Kindly check your input before submitting.")
            context = self.context_creator()
            return render(request, "adminpanel/objectView.html", context)

        if (request.POST.get("save") or request.POST.get("save_continue")) and (
            len(form.changed_data) != 0
        ):
            saved_object = form.save()
            change_message = construct_change_message(form, None, False)
            log_change(request, saved_object, change_message)
            pretty_msg = pretty_change_message(saved_object)
            messages.success(request, pretty_msg)
        if request.POST.get("save"):
            return redirect("adminListDB", db=smallcaseDB)
        elif request.POST.get("save_continue"):
            return redirect("adminDBObject", db=smallcaseDB, pk=pk)

        if request.POST.get("delete"):
            return redirect("adminDBObjectDelete", db=smallcaseDB, pk=pk)

        return redirect("adminListDB", db=smallcaseDB)


class AdminDBObjectDelete(AdminViewBase):
    def get_url_kwargs(self):
        db, pk = str(self.kwargs["db"]), str(self.kwargs["pk"])
        return (db, pk)

    def context_creator(self):
        smallcaseDB, pk = self.get_url_kwargs()
        model = modelDict[smallcaseDB]
        obj = load_instance(model, pk)
        context = record_context(model, self.kwargs, record=obj)
        context["title"] = (
            SITE_NAME + " - Confirm deleting " + context["recordVerboseName"] + "?"
        )
        context["breadcrumbs"] = build_breadcrumbs(
            [
                ["Admin", addressOfPages["adminMainPage"]],
                [
                    smallcaseDB.title(),
                    addressOfPages["adminListDB"]({"db": smallcaseDB}),
                ],
                [
                    f"View {smallcaseDB.title()}",
                    addressOfPages["adminDBObject"]({"db": smallcaseDB, "pk": pk}),
                ],
                [
                    f"Delete '{obj}'",
                    addressOfPages["adminDBObjectDelete"](
                        {"db": smallcaseDB, "pk": pk}
                    ),
                ],
            ]
        )
        return context

    def get(self, request, *args, **kwargs):
        smallcaseDB, pk = self.get_url_kwargs()
        if smallcaseDB not in allowedModelNames or smallcaseDB in (
            "session",
            "lifeline",
        ):
            return self.redirect_back()
        model = modelDict[smallcaseDB]
        if not pk_checker(pk, model):
            return redirect("adminListDB", db=smallcaseDB)
        context = self.context_creator()
        return render(request, "adminpanel/objectDelete.html", context)

    def post(self, request, *args, **kwargs):
        smallcaseDB, pk = self.get_url_kwargs()
        if smallcaseDB not in allowedModelNames or smallcaseDB in (
            "session",
            "lifeline",
        ):
            return self.redirect_back()
        model = modelDict[smallcaseDB]
        if not pk_checker(pk, model):
            return redirect("adminListDB", db=smallcaseDB)
        if request.POST.get("yes") and not request.POST.get("no"):
            object_given = model.objects.get(pk=pk)
            object_name = object_given._meta.verbose_name
            log_deletion(request, object_given, str(object_given))
            pretty_msg = pretty_change_message(object_given)
            deleted = object_given.delete()[0]
            messages.success(
                request,
                pretty_msg
                + f"""\nSuccessfully deleted 1 {object_name} and {deleted} objects related to it!""",
            )
        return redirect("adminListDB", db=smallcaseDB)


class AdminDBObjectHistory(AdminViewBase):
    def get_url_kwargs(self):
        db, pk = str(self.kwargs["db"]), str(self.kwargs["pk"])
        return (db, pk)

    def context_creator(self):
        smallcaseDB, pk = self.get_url_kwargs()
        model = modelDict[smallcaseDB]

        obj = get_record(model, pk)

        query = LogEntry.objects.filter(
            content_type_id=get_content_type_for_model(obj).pk, object_id=pk
        ).order_by("-action_time")

        objects_list = (
            paginate(query, self.request.GET.get("page", 1), PAGINATE_NO)
            if query.exists()
            else None
        )

        context = record_context(
            model,
            self.kwargs,
            record=obj,
            query=objects_list,
            object_name=objects_list[0].object_repr if objects_list else str(obj),
        )
        context["title"] = (
            SITE_NAME + " - " + "History of " + f'"{context["object_name"]}"'
        )
        context["breadcrumbs"] = build_breadcrumbs(
            [
                ["Admin", addressOfPages["adminMainPage"]],
                [
                    smallcaseDB.title(),
                    addressOfPages["adminListDB"]({"db": smallcaseDB}),
                ],
                [
                    f"View {smallcaseDB.title()}",
                    addressOfPages["adminDBObject"]({"db": smallcaseDB, "pk": pk}),
                ],
                [
                    f"History of '{obj}'",
                    addressOfPages["adminDBObjectHistory"](
                        {"db": smallcaseDB, "pk": pk}
                    ),
                ],
            ]
        )
        return context

    def get(self, request, *args, **kwargs):
        smallcaseDB, pk = self.get_url_kwargs()
        if smallcaseDB not in allowedModelNames:
            return self.redirect_back()
        model = modelDict[smallcaseDB]
        if not pk_checker(pk, model):
            return redirect("adminListDB", db=smallcaseDB)
        context = self.context_creator()
        return render(request, "adminpanel/objectHistory.html", context)


class ShowLogDB(AdminViewBase):
    def context_creator(self):
        objects_list = paginate(
            LogEntry.objects.order_by("-action_time"),
            self.request.GET.get("page", 1),
            PAGINATE_NO,
        )
        context = {"allRecords": objects_list}
        context.update(self.kwargs)
        context["title"] = SITE_NAME + " - " + "Changelog"
        context["breadcrumbs"] = build_breadcrumbs(
            [
                ["Admin", addressOfPages["adminMainPage"]],
                ["Logs", addressOfPages["adminListLogs"]],
            ]
        )
        return context

    def get(self, request, *args, **kwargs):
        context = self.context_creator()
        return render(request, "adminpanel/listlog.html", context)


class APIAccess(AdminViewBase):
    def context_creator(self, request):
        token, created = Token.objects.get_or_create(user=request.user)
        context = {}
        context.update(self.kwargs)
        context["token"] = token.key
        context["created"] = token.created
        context["title"] = SITE_NAME + " - " + "API Token"
        context["breadcrumbs"] = build_breadcrumbs(
            [
                ["Admin", addressOfPages["adminMainPage"]],
                ["API Access", addressOfPages["APIAccess"]],
            ]
        )
        return context

    def get(self, request, *args, **kwargs):
        context = self.context_creator(request)
        return render(request, "adminpanel/apiaccess.html", context)


class APIDocs(AdminViewBase):
    def context_creator(self, request):
        context = {}
        context.update(self.kwargs)
        context["title"] = SITE_NAME + " - " + "API Docs"
        context["breadcrumbs"] = build_breadcrumbs(
            [
                ["Admin", addressOfPages["adminMainPage"]],
                ["API Docs", addressOfPages["APIDocs"]],
            ]
        )
        return context

    def get(self, request, *args, **kwargs):
        context = self.context_creator(request)
        return render(request, "adminpanel/apidocs.html", context)


class GetQuestion(AdminViewBase):
    def get(self, request, *args, **kwargs):
        response = {}
        count = self.request.GET.get("count")
        count = int(count) if count and count.isdigit() else 1
        if count > 5:
            response["error"] = "Cannot request more than 5 objects."
            return JsonResponse(response, safe=False, encoder=QuestionEncoder)
        response["data"] = list(Question.objects.order_by("?")[:count])
        return JsonResponse(response, safe=False, encoder=QuestionEncoder)

    def post(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(["GET", "PUT", "DELETE"])


class AddQuestion(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    statuses = {
        # status code : status message
        0: "Error.",
        1: "OK.",
        2: "Rate limited.",
        3: "Invalid/missing data.",
        4: "Invalid/missing parameters.",
        5: "Validate data in parameters before sending another request.",
    }

    def get(self, request, *args, **kwargs):
        return JsonResponse({"error": "GET request not allowed."})

    def post(self, request, *args, **kwargs):
        final = {}
        result = {}
        add_questions = []

        def checkQuestion(obj):
            def checkCategory(c):
                if isinstance(c, str):
                    lookup = Category.objects.filter(name__icontains=c.strip())
                    if lookup.count() > 1:
                        return lookup.annotate(length_name=Length("name")).order_by(
                            "length_name"
                        )[0]
                    elif lookup.count() == 1:
                        return lookup[0]
                return Category.objects.get(pk=Category.get_default_pk())

            def checkQuestionText(qn):
                if isinstance(qn, str):
                    lookup = Question.objects.annotate(trimmed_text=Trim("text"))
                    lookup = lookup.filter(trimmed_text__iexact=qn.strip())
                    if lookup.count() == 0:
                        return qn
                return False

            def checkDifficulty(diff):
                difficulties = ("Easy", "Medium", "Hard")
                db_difficulties = (Question.EASY, Question.MEDIUM, Question.HARD)
                lower_difficulties = [difficulty.lower() for difficulty in difficulties]
                mapped_difficulties = dict(
                    zip(lower_difficulties, db_difficulties, strict=True)
                )
                if isinstance(diff, str):
                    if diff.lower() in lower_difficulties:
                        return mapped_difficulties[diff.lower()]
                return False

            def checkOption(opt):
                lookup = Option.objects.annotate(trimmed_text=Trim("text"))
                if isinstance(opt, str) or isinstance(opt, int):
                    lookup = lookup.filter(
                        trimmed_text__iexact=opt if isinstance(opt, str) else str(opt)
                    )
                    if lookup.count() == 1:
                        return lookup[0]
                    elif lookup.count() == 0:
                        new_option = Option.objects.create(text=opt)
                        return new_option
                return False

            queryResult = {}
            if not isinstance(obj, dict):
                queryResult["status_code"] = 3
                queryResult["status_message"] = self.statuses[
                    queryResult["status_code"]
                ]
                return queryResult

            keys = tuple(obj.keys())
            if (
                "difficulty" not in keys
                or "question" not in keys
                or "correct_answer" not in keys
                or "incorrect_answers" not in keys
            ):
                queryResult["status_code"] = 4
                queryResult["status_message"] = self.statuses[
                    queryResult["status_code"]
                ]
                return queryResult

            cat = obj["category"] if "category" in keys else None
            if isinstance(cat, list):
                cat = list(set(cat))
                if len(cat) > 0:
                    for i in range(len(cat)):
                        individual_cat = cat[i]
                        converted = checkCategory(individual_cat)
                        cat[i] = (
                            Category.objects.get(pk=Category.get_default_pk())
                            if not converted
                            else converted
                        )
                else:
                    cat = [Category.objects.get(pk=Category.get_default_pk())]
                cat = list(set(cat))
            elif isinstance(cat, str):
                cat = [checkCategory(cat)]
            else:
                cat = checkCategory(cat)

            qn = checkQuestionText(obj["question"])
            difficulty = checkDifficulty(obj["difficulty"])
            correct_option = checkOption(obj["correct_answer"])

            incorrect_options = (
                obj["incorrect_answers"]
                if isinstance(obj["incorrect_answers"], list)
                else False
            )
            if incorrect_options:
                incorrect_options = list(set(incorrect_options))
                if len(incorrect_options) == 3:
                    for i in range(len(incorrect_options)):
                        individual_option = incorrect_options[i]
                        converted = checkOption(individual_option)
                        if converted:
                            incorrect_options[i] = converted
                        else:
                            incorrect_options = False
                            break
                else:
                    incorrect_options = False

            if qn and correct_option and incorrect_options and difficulty:
                queryResult["status_code"] = 1
                queryResult["status_message"] = self.statuses[
                    queryResult["status_code"]
                ]
                add_questions.append(
                    (
                        {
                            "text": qn,
                            "difficulty": difficulty,
                            "correct_option": correct_option,
                        },
                        cat,
                        incorrect_options,
                    )
                )
                return queryResult
            else:
                queryResult["status_code"] = 5
                queryResult["status_message"] = self.statuses[
                    queryResult["status_code"]
                ]
                return queryResult

        def updateM2Mfields(obj: Question, cat, opt):
            obj.falls_under.set(cat)
            obj.incorrect_options.set(opt)

        received_json_data = request.data
        if not isinstance(received_json_data, list):
            final["success"] = 0
            result["status_code"] = 3
            result["status_message"] = self.statuses[result["status_code"]]
            final["errors"] = result
            return JsonResponse(final, safe=False, encoder=QuestionEncoder, status=400)

        count = len(received_json_data)
        if count == 0:
            final["success"] = 0
            result["status_code"] = 3
            result["status_message"] = self.statuses[result["status_code"]]
            final["errors"] = result
            return JsonResponse(final, safe=False, encoder=QuestionEncoder, status=400)

        for idx in range(len(received_json_data)):
            received_json_data[idx] = checkQuestion(received_json_data[idx])

        status_codes_after_action = [res["status_code"] for res in received_json_data]
        if len(set(status_codes_after_action)) >= 1 and 1 not in set(
            status_codes_after_action
        ):
            final["success"] = 0
            unique_status_codes = [
                {"status_code": code, "status_message": self.statuses[code]}
                for code in set(status_codes_after_action)
            ]
            final["errors"] = unique_status_codes
            return JsonResponse(final, safe=False, encoder=QuestionEncoder, status=409)

        final["success"] = 1
        result["status_code"] = 1
        result["status_message"] = f"OK. Added {len(received_json_data)} questions."
        final["messages"] = result
        created_questions = Question.objects.bulk_create(
            [
                Question(
                    who_added=Token.objects.get(
                        key=request.headers["Authorization"].split().pop()
                    ).user,
                    question_type=Question.MULTIPLE,
                    **create_data[0],
                )
                for create_data in add_questions
            ]
        )
        _ = list(
            map(
                lambda q, data: updateM2Mfields(q, data[1], data[2]),
                created_questions,
                add_questions,
            ),
        )
        return JsonResponse(final, safe=False, encoder=QuestionEncoder, status=201)
