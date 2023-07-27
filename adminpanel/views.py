from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, HttpResponseRedirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy
from django.db.models import F
from django.db import models
from django.views.generic import View

from .mixins import SuperuserRequiredMixin
from .viewsExtra import (safe_object_delete, 
                         safe_pk_list_converter,
                         safe_object_delete_log)
from game.models import Session, Lifeline, Category, Question, Option

import operator

# Test site


def testSite(request):
    return render(
        request,
        "adminpanel/listdb.html",
        {
            "allRecords": Session.objects.all().annotate(
                key_primary=F(Session._meta.pk.name)
            ),
            "recordVerboseName": Session._meta.verbose_name,
            "recordVerboseNamePlural": Session._meta.verbose_name_plural,
            "lowerdb": "session",
        },
    )


# Production sites

modelDict: dict[str, models.Model] = {
    "session": Session,
    "lifeline": Lifeline,
    "category": Category,
    "question": Question,
    "option": Option,
}
allowedModelNames = tuple(modelDict.keys())
addressOfPages = dict(
    adminMainPage=reverse_lazy("adminMainPage"),
    test=reverse_lazy("test"),
    adminListDB=lambda x: reverse_lazy("adminListDB", kwargs=x),
    adminDBObject=lambda x: reverse_lazy("adminDBObject", kwargs=x),
    adminDBObjectCreate=lambda x: reverse_lazy("adminDBObjectCreate", kwargs=x),
    adminDBObjectDelete=lambda x: reverse_lazy("adminDBObjectDelete", kwargs=x),
)
after1stElement = operator.itemgetter(slice(1, None))

PAGINATE_NO = 12
SITE_NAME = "AdminPanel"


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
        breadcrumbs = [["Admin", addressOfPages["adminMainPage"]], [smallcaseDB.title()]]
        context["breadcrumbs"] = list(map(lambda x: (x[0], x[1]), list(enumerate(breadcrumbs, start=1))))
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
            and (
                set(safe_given_pk) - set(map(lambda y: y.key_primary, query))
                == set()
            )
        ) or (
            request.POST.get("admin-action") == "Delete all in view"
            and request.POST.get("allcheck")
            and given_pk
            and (
                set(safe_given_pk) - set(map(lambda y: y.key_primary, query))
                == set()
            )
            and len(set(safe_given_pk)) == PAGINATE_NO
        ):
            object_name = (
                model._meta.verbose_name
                if len(given_pk) == 1
                else model._meta.verbose_name_plural
            )
            action = list(map(lambda x: safe_object_delete_log(request, model, x), safe_given_pk))
            deleted = sum(list(map(lambda x: x[0], action)))
            messages.success(
                request,
                f"""Successfully deleted {len(action)} {object_name} and {deleted} objects related to it!""",
            )

        context = self.context_creator()
        return render(request, "adminpanel/listdb.html", context)
