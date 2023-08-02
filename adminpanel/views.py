from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse, reverse_lazy
from django.db.models import F
from django.db import models
from django.views.generic import View
from django.contrib.admin.options import construct_change_message
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.forms import modelform_factory
from django.contrib.admin.models import LogEntry


from .mixins import SuperuserRequiredMixin
from .forms import QuestionForm, OptionForm, LifelineForm, CategoryForm
from .viewsExtra import (
    pk_checker,
    safe_pk_list_converter,
    safe_object_delete_log,
    pretty_change_message,
    log_addition,
    log_change,
    log_deletion,
    daterange,
    get_content_type_for_model,
)
from game.models import Session, Lifeline, Category, Question, Option, QuestionOrder
import datetime

import operator


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
addressOfPages = dict(
    adminMainPage=reverse_lazy("adminMainPage"),
    test=reverse_lazy("test"),
    adminListDB=lambda x: reverse_lazy("adminListDB", kwargs=x),
    adminListLogs=reverse_lazy("adminListLogs"),
    adminDBObject=lambda x: reverse_lazy("adminDBObject", kwargs=x),
    adminDBObjectCreate=lambda x: reverse_lazy("adminDBObjectCreate", kwargs=x),
    adminDBObjectDelete=lambda x: reverse_lazy("adminDBObjectDelete", kwargs=x),
    adminDBObjectHistory=lambda x: reverse_lazy("adminDBObjectHistory", kwargs=x),
)
after1stElement = operator.itemgetter(slice(1, None))

PAGINATE_NO = 12
SITE_NAME = "AdminPanel"


# Test site


def testSite(request):
    return render(
        request,
        "adminpanel/index.html",
        {},
    )


# Production sites


class AdminMainPage(SuperuserRequiredMixin, LoginRequiredMixin, View):
    login_url = "admin_signin"
    raise_exception = True

    def context_creater(self):
        recent_log = list(LogEntry.objects.order_by("-action_time")[:12])
        total_question_count = Question.objects.all().count()
        daily_question_count = Question.objects.filter(
            date_added__gte=datetime.date.today()
        ).count()
        total_session_count = Session.objects.all().count()
        daily_session_count = Session.objects.filter(
            date_created__gte=datetime.date.today()
        ).count()
        top_30_highest_scores = list(
            map(
                lambda x: x.score,
                Session.objects.order_by("-score", "-date_created")[:30],
            )
        )
        highest_score = f"{top_30_highest_scores[0]:,}"
        total_user_count = User.objects.all().count()
        daily_user_count = User.objects.filter(
            date_joined__gte=datetime.date.today()
        ).count()
        total_category = Category.objects.all()
        active_users_count = User.objects.filter(is_active=True).count()

        percent_of_daily_threshold = round(((daily_question_count) / 10) * 100)
        percent_of_active_users = round((active_users_count / total_user_count) * 100)
        more_than_ten_sessions = daily_session_count / 10
        category_with_most_qs = sorted(
            list(map(lambda x: (x, x.all_questions.all().count()), total_category)),
            reverse=True,
            key=lambda y: y[1],
        )[0][0]

        # Chart data
        (
            date_list,
            session_list,
            session_user_list,
            session_easy_list,
            session_medium_list,
            session_hard_list,
            score_list,
        ) = [list() for _ in range(7)]
        start_date = datetime.date.today() - datetime.timedelta(15)
        end_date = datetime.date.today() + datetime.timedelta(1)
        for date in daterange(start_date, end_date):
            session_query = Session.objects.filter(date_created__gte=date).filter(
                date_created__lte=date + datetime.timedelta(1)
            )
            session_user_query = session_query.values("session_user").distinct()
            questionorder_dateQuery = QuestionOrder.objects.filter(
                date_chosen__gte=date
            ).filter(date_chosen__lte=date + datetime.timedelta(1))
            session_easy_query = questionorder_dateQuery.filter(
                question__difficulty=Question.EASY
            )
            session_medium_query = questionorder_dateQuery.filter(
                question__difficulty=Question.MEDIUM
            )
            session_hard_query = questionorder_dateQuery.filter(
                question__difficulty=Question.HARD
            )
            score_query = (
                Session.objects.filter(date_created__gte=date)
                .filter(date_created__lte=date + datetime.timedelta(1))
                .order_by("-score")
            )
            date_list.append(date.strftime("%d-%m"))
            session_list.append(session_query.count())
            session_user_list.append(session_user_query.count())
            session_easy_list.append(session_easy_query.count())
            session_medium_list.append(session_medium_query.count())
            session_hard_list.append(session_hard_query.count())
            score_list.append(score_query[0].score if score_query.exists() else 0)
        active_users_labels = [i.username for i in User.objects.all()]
        active_users_activity = [
            i.initiated_sessions.all().count() for i in User.objects.all()
        ]

        context = dict(
            recent_log=recent_log,
            total_question_count=total_question_count,
            daily_question_count=daily_question_count,
            total_session_count=total_session_count,
            daily_session_count=daily_session_count,
            top_30_highest_scores=top_30_highest_scores,
            highest_score=highest_score,
            total_user_count=total_user_count,
            daily_user_count=daily_user_count,
            total_category_count=f"{total_category.count():,}",
            active_users_count=active_users_count,
            percent_of_daily_threshold=percent_of_daily_threshold,
            percent_of_active_users=percent_of_active_users,
            more_than_ten_sessions=more_than_ten_sessions,
            category_with_most_qs=f"""\
                                <a style="text-decoration: none;" \
                                href="{reverse_lazy("adminDBObject", kwargs={'db':'category', 'pk':category_with_most_qs.pk})}" \
                                title="{category_with_most_qs.name}">\
                                This cat.</a>""",
            date_list=date_list,
            session_list=session_list,
            session_user_list=session_user_list,
            session_easy_list=session_easy_list,
            session_medium_list=session_medium_list,
            session_hard_list=session_hard_list,
            score_list=score_list,
            active_users_labels=active_users_labels,
            active_users_activity=active_users_activity,
        )
        breadcrumbs = [
            ["Admin", addressOfPages["adminMainPage"]],
            [[], []],
        ]
        context["breadcrumbs"] = list(
            map(lambda x: (x[0], x[1]), list(enumerate(breadcrumbs, start=1)))
        )
        context.update(self.kwargs)
        return context

    def get(self, request, *args, **kwargs):
        context = self.context_creater()
        return render(request, "adminpanel/index.html", context)


class AdminListDB(SuperuserRequiredMixin, LoginRequiredMixin, View):
    login_url = "adminLogin"
    raise_exception = True

    def get_url_kwargs(self):
        db = str(self.kwargs["db"])
        return db

    def context_creator(self):
        smallcaseDB = self.get_url_kwargs()
        model = modelDict[smallcaseDB]
        query = model.objects.all().annotate(key_primary=F(model._meta.pk.name))
        paginator = Paginator(query, PAGINATE_NO)
        page = self.request.GET.get("page", 1)
        try:
            objects_list = paginator.page(page)
        except PageNotAnInteger:
            objects_list = paginator.page(1)
        except EmptyPage:
            objects_list = paginator.page(paginator.num_pages)
        context = {
            "allRecords": objects_list,
            "recordVerboseName": model._meta.verbose_name,
            "recordVerboseNamePlural": model._meta.verbose_name_plural,
        }
        context.update(self.kwargs)
        context["title"] = SITE_NAME + " - " + context["recordVerboseName"]
        breadcrumbs = [
            ["Admin", addressOfPages["adminMainPage"]],
            [smallcaseDB.title()],
        ]
        context["breadcrumbs"] = list(
            map(lambda x: (x[0], x[1]), list(enumerate(breadcrumbs, start=1)))
        )
        return context

    def get(self, request, *args, **kwargs):
        smallcaseDB = self.get_url_kwargs()
        if smallcaseDB not in allowedModelNames:
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/admin/"))
        context = self.context_creator()
        return render(request, "adminpanel/listdb.html", context)

    def post(self, request, *args, **kwargs):
        smallcaseDB = self.get_url_kwargs()
        if (
            smallcaseDB not in allowedModelNames
            or request.POST.get("admin-action") == "-"
        ):
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/admin/"))

        model = modelDict[smallcaseDB]
        query = model.objects.all().annotate(key_primary=F(model._meta.pk.name))
        given_pk = request.POST.getlist("indcheck")
        safe_given_pk = safe_pk_list_converter(given_pk, model)
        if (
            request.POST.get("admin-action") == "Delete selected"
            and given_pk
            and (set(safe_given_pk) - set(map(lambda y: y.key_primary, query)) == set())
        ) or (
            request.POST.get("admin-action") == "Delete all in view"
            and request.POST.get("allcheck")
            and given_pk
            and (set(safe_given_pk) - set(map(lambda y: y.key_primary, query)) == set())
            and len(set(safe_given_pk)) == PAGINATE_NO
        ):
            object_name = (
                model._meta.verbose_name
                if len(given_pk) == 1
                else model._meta.verbose_name_plural
            )
            action = list(
                map(lambda x: safe_object_delete_log(request, model, x), safe_given_pk)
            )
            deleted = sum(list(map(lambda x: x[0], action)))
            messages.success(
                request,
                f"""Successfully deleted {len(action)} {object_name} and {deleted} objects related to it!""",
            )

        context = self.context_creator()
        return render(request, "adminpanel/listdb.html", context)


class AdminDBObjectCreate(SuperuserRequiredMixin, LoginRequiredMixin, View):
    login_url = "adminLogin"
    raise_exception = True
    form_class = None
    initial = {}

    def get_url_kwargs(self):
        db = str(self.kwargs["db"])
        return db

    def get_initial(self):
        """Return the initial data to use for forms on this view."""
        return self.initial.copy()

    def get_form_class(self):
        """Return the form class to use."""
        return AdminDBObjectCreate.form_class

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
            "initial": self.get_initial(),
        }

        if self.request.method in ("POST", "PUT"):
            kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                }
            )
        return kwargs

    def context_creator(self):
        smallcaseDB = self.get_url_kwargs()
        model = modelDict[smallcaseDB]
        context = {
            "form": self.get_form(),
            "recordVerboseName": model._meta.verbose_name,
            "recordVerboseNamePlural": model._meta.verbose_name_plural,
        }
        context.update(self.kwargs)
        context["title"] = (
            SITE_NAME + " - Create " + context["recordVerboseName"].title()
        )
        breadcrumbs = [
            ["Admin", addressOfPages["adminMainPage"]],
            [smallcaseDB.title(), addressOfPages["adminListDB"]({"db": smallcaseDB})],
            [
                f"Create {smallcaseDB.title()}",
                addressOfPages["adminDBObjectCreate"]({"db": smallcaseDB}),
            ],
        ]
        context["breadcrumbs"] = list(
            map(lambda x: (x[0], x[1]), list(enumerate(breadcrumbs, start=1)))
        )
        return context

    def get(self, request, *args, **kwargs):
        smallcaseDB = self.get_url_kwargs()
        if smallcaseDB not in allowedModelNames or smallcaseDB in (
            "session",
            "lifeline",
        ):
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/admin/"))
        model = modelDict[smallcaseDB]
        setattr(AdminDBObjectCreate, "form_class", modelFormDict[smallcaseDB])
        context = self.context_creator()
        return render(request, "adminpanel/objectCreate.html", context)

    def post(self, request, *args, **kwargs):
        smallcaseDB = self.get_url_kwargs()
        if smallcaseDB not in allowedModelNames or smallcaseDB in (
            "session",
            "lifeline",
        ):
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/admin/"))
        if request.POST.get("cancel"):
            return redirect("adminListDB", db=smallcaseDB)
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


class AdminDBObjectChange(SuperuserRequiredMixin, LoginRequiredMixin, View):
    login_url = "adminLogin"
    raise_exception = True
    form_class = None
    instance = None

    def get_url_kwargs(self):
        db, pk = str(self.kwargs["db"]), str(self.kwargs["pk"])
        return (db, pk)

    def get_instance(self):
        """Return the initial data to use for forms on this view."""
        return AdminDBObjectChange.instance

    def get_form_class(self):
        """Return the form class to use."""
        return AdminDBObjectCreate.form_class

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
            "instance": self.get_instance(),
        }

        if self.request.method in ("POST", "PUT"):
            kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                }
            )
        return kwargs

    def context_creator(self):
        smallcaseDB, pk = self.get_url_kwargs()
        model = modelDict[smallcaseDB]
        context = {
            "form": self.get_form(),
            "recordVerboseName": model._meta.verbose_name,
            "recordVerboseNamePlural": model._meta.verbose_name_plural,
        }
        context.update(self.kwargs)
        context["title"] = SITE_NAME + " - View " + context["recordVerboseName"].title()
        breadcrumbs = [
            ["Admin", addressOfPages["adminMainPage"]],
            [smallcaseDB.title(), addressOfPages["adminListDB"]({"db": smallcaseDB})],
            [
                f"View {smallcaseDB.title()}",
                addressOfPages["adminDBObject"]({"db": smallcaseDB, "pk": pk}),
            ],
        ]
        context["breadcrumbs"] = list(
            map(lambda x: (x[0], x[1]), list(enumerate(breadcrumbs, start=1)))
        )
        return context

    def get(self, request, *args, **kwargs):
        smallcaseDB, pk = self.get_url_kwargs()
        if smallcaseDB not in allowedModelNames or smallcaseDB in ("session"):
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/admin/"))
        model = modelDict[smallcaseDB]
        if not pk_checker(pk, model):
            return redirect("adminListDB", db=smallcaseDB)
        setattr(AdminDBObjectCreate, "form_class", modelFormDict[smallcaseDB])
        setattr(
            AdminDBObjectChange,
            "instance",
            model.objects.get(pk=int(pk) if pk.isnumeric() else pk),
        )
        context = self.context_creator()
        return render(request, "adminpanel/objectView.html", context)

    def post(self, request, *args, **kwargs):
        smallcaseDB, pk = self.get_url_kwargs()
        if smallcaseDB not in allowedModelNames or smallcaseDB in (
            "session",
            "lifeline",
        ):
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/admin/"))
        model = modelDict[smallcaseDB]
        if not pk_checker(pk, model):
            return redirect("adminListDB", db=smallcaseDB)

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
            return redirect("adminDBList", db=smallcaseDB)
        elif request.POST.get("save_continue"):
            return redirect("adminDBObject", db=smallcaseDB, pk=pk)

        if request.POST.get("delete"):
            return redirect("adminDBObjectDelete", db=smallcaseDB, pk=pk)

        return redirect("adminListDB", db=smallcaseDB)


class AdminDBObjectDelete(SuperuserRequiredMixin, LoginRequiredMixin, View):
    login_url = "adminLogin"
    raise_exception = True
    form_class = None
    instance = None

    def get_url_kwargs(self):
        db, pk = str(self.kwargs["db"]), str(self.kwargs["pk"])
        return (db, pk)

    def context_creator(self):
        smallcaseDB, pk = self.get_url_kwargs()
        model = modelDict[smallcaseDB]
        obj = model.objects.get(pk=pk)
        context = {
            "record": obj,
            "recordVerboseName": model._meta.verbose_name,
            "recordVerboseNamePlural": model._meta.verbose_name_plural,
        }
        context.update(self.kwargs)
        context["title"] = (
            SITE_NAME + " - Confirm deleting " + context["recordVerboseName"] + "?"
        )
        breadcrumbs = [
            ["Admin", addressOfPages["adminMainPage"]],
            [smallcaseDB.title(), addressOfPages["adminListDB"]({"db": smallcaseDB})],
            [
                f"View {smallcaseDB.title()}",
                addressOfPages["adminDBObject"]({"db": smallcaseDB, "pk": pk}),
            ],
            [
                f"Delete '{obj}'",
                addressOfPages["adminDBObjectDelete"]({"db": smallcaseDB, "pk": pk}),
            ],
        ]
        context["breadcrumbs"] = list(
            map(lambda x: (x[0], x[1]), list(enumerate(breadcrumbs, start=1)))
        )
        return context

    def get(self, request, *args, **kwargs):
        smallcaseDB, pk = self.get_url_kwargs()
        if smallcaseDB not in allowedModelNames or smallcaseDB in (
            "session",
            "lifeline",
        ):
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/admin/"))
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
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/admin/"))
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


class AdminDBObjectHistory(SuperuserRequiredMixin, LoginRequiredMixin, View):
    login_url = "adminLogin"
    raise_exception = False

    def get_url_kwargs(self):
        db, pk = str(self.kwargs["db"]), str(self.kwargs["pk"])
        return (db, pk)

    def context_creator(self):
        smallcaseDB, pk = self.get_url_kwargs()
        model = modelDict[smallcaseDB]

        obj = model.objects.all()[0]
        if model.objects.filter(pk=pk).exists():
            obj = model.objects.get(pk=pk)

        query = LogEntry.objects.filter(
            content_type_id=get_content_type_for_model(obj).pk, object_id=pk
        ).order_by("-action_time")

        if query.exists():
            paginator = Paginator(query, PAGINATE_NO)
            page = self.request.GET.get("page", 1)
            try:
                objects_list = paginator.page(page)
            except PageNotAnInteger:
                objects_list = paginator.page(1)
            except EmptyPage:
                objects_list = paginator.page(paginator.num_pages)
        else:
            objects_list = None

        context = dict(
            record=obj,
            recordVerboseName=model._meta.verbose_name,
            recordVerboseNamePlural=model._meta.verbose_name_plural,
            query=objects_list,
            object_name=query[0].object_repr if query.exists() else str(obj),
        )
        context.update(self.kwargs)
        context["title"] = (
            SITE_NAME + " - " + "History of " + f'"{context["object_name"]}"'
        )
        breadcrumbs = [
            ["Admin", addressOfPages["adminMainPage"]],
            [smallcaseDB.title(), addressOfPages["adminListDB"]({"db": smallcaseDB})],
            [
                f"View {smallcaseDB.title()}",
                addressOfPages["adminDBObject"]({"db": smallcaseDB, "pk": pk}),
            ],
            [
                f"History of '{obj}'",
                addressOfPages["adminDBObjectHistory"]({"db": smallcaseDB, "pk": pk}),
            ],
        ]
        context["breadcrumbs"] = list(
            map(lambda x: (x[0], x[1]), list(enumerate(breadcrumbs, start=1)))
        )
        return context

    def get(self, request, *args, **kwargs):
        smallcaseDB, pk = self.get_url_kwargs()
        if smallcaseDB not in allowedModelNames:
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/admin/"))
        model = modelDict[smallcaseDB]
        if not pk_checker(pk, model):
            return redirect("adminListDB", db=smallcaseDB)
        context = self.context_creator()
        return render(request, "adminpanel/objectHistory.html", context)


class ShowLogDB(SuperuserRequiredMixin, LoginRequiredMixin, View):
    login_url = "adminLogin"
    raise_exception = True

    def context_creator(self):
        paginator = Paginator(LogEntry.objects.order_by("-action_time"), PAGINATE_NO)
        page = self.request.GET.get("page", 1)
        try:
            objects_list = paginator.page(page)
        except PageNotAnInteger:
            objects_list = paginator.page(1)
        except EmptyPage:
            objects_list = paginator.page(paginator.num_pages)
        context = dict(
            allRecords=objects_list,
        )
        context.update(self.kwargs)
        context["title"] = SITE_NAME + " - " + "Changelog"
        breadcrumbs = [
            ["Admin", addressOfPages["adminMainPage"]],
            ["Logs", addressOfPages["adminListLogs"]],
        ]
        context["breadcrumbs"] = list(
            map(lambda x: (x[0], x[1]), list(enumerate(breadcrumbs, start=1)))
        )
        return context

    def get(self, request, *args, **kwargs):
        context = self.context_creator()
        return render(request, "adminpanel/listlog.html", context)
