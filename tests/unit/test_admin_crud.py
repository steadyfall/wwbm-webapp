import pytest
from django.core.paginator import Page
from django.test import RequestFactory
from django.urls import reverse

from adminpanel.crud import (
    build_breadcrumbs,
    get_record,
    load_instance,
    paginate,
    record_context,
)
from adminpanel.views import AdminDBObjectChange, AdminDBObjectCreate
from game.models import Category


class TestPaginate:
    def test_returns_requested_page(self):
        page = paginate(list(range(30)), 2, per_page=10)

        assert isinstance(page, Page)
        assert page.number == 2
        assert list(page.object_list) == list(range(10, 20))

    def test_non_integer_page_falls_back_to_first(self):
        page = paginate(list(range(30)), "abc", per_page=10)

        assert page.number == 1

    def test_out_of_range_page_falls_back_to_last(self):
        page = paginate(list(range(30)), 99, per_page=10)

        assert page.number == 3


class TestBuildBreadcrumbs:
    def test_enumerates_items_starting_at_one(self):
        items = [["Admin", "/admin/"], ["Logs", "/admin/logs/"]]

        assert build_breadcrumbs(items) == [
            (1, ["Admin", "/admin/"]),
            (2, ["Logs", "/admin/logs/"]),
        ]


@pytest.mark.django_db
class TestRecordContext:
    def test_builds_verbose_names_and_merges_kwargs(self):
        context = record_context(Category, {"db": "category"}, allRecords=None)

        assert context["recordVerboseName"] == Category._meta.verbose_name
        assert context["recordVerboseNamePlural"] == Category._meta.verbose_name_plural
        assert context["db"] == "category"
        assert context["allRecords"] is None


@pytest.mark.django_db
class TestLoadInstance:
    def test_loads_instance_from_numeric_string_pk(self):
        category = Category.objects.create(name="General")

        assert load_instance(Category, str(category.pk)) == category


@pytest.mark.django_db
class TestGetRecord:
    def test_returns_record_when_pk_exists(self):
        category = Category.objects.create(name="General")

        assert get_record(Category, str(category.pk)) == category

    def test_falls_back_to_first_record_when_pk_missing(self):
        category = Category.objects.create(name="General")

        assert get_record(Category, 999) == category


@pytest.mark.django_db
class TestFormStateMixin:
    def test_create_form_kwargs_include_post_data_but_no_instance(self):
        view = AdminDBObjectCreate()
        view.request = RequestFactory().post(
            reverse("adminDBObjectCreate", kwargs={"db": "category"})
        )
        view.kwargs = {"db": "category"}
        view.set_form_class("category")

        form_kwargs = view.get_form_kwargs()

        assert form_kwargs["initial"] == {}
        assert "data" in form_kwargs
        assert "instance" not in form_kwargs

    def test_change_form_kwargs_include_bound_instance(self):
        category = Category.objects.create(name="General")
        view = AdminDBObjectChange()
        view.request = RequestFactory().get(
            reverse("adminDBObject", kwargs={"db": "category", "pk": category.pk})
        )
        view.kwargs = {"db": "category", "pk": str(category.pk)}
        view.set_form_state(Category, "category", str(category.pk))

        form_kwargs = view.get_form_kwargs()

        assert form_kwargs["instance"] == category
        assert "data" not in form_kwargs
