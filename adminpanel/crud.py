"""Shared helpers for the admin panel's CRUD views."""

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

PAGINATE_NO = 12


def paginate(queryset, page, per_page=PAGINATE_NO):
    """Return the requested page, falling back to the first or last page."""
    paginator = Paginator(queryset, per_page)
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)


def build_breadcrumbs(items):
    """Return items enumerated as (number, item) pairs for the templates."""
    return [(number, item) for number, item in enumerate(items, start=1)]


def record_context(model, kwargs, **extra):
    """Return the shared context entries for a model-backed admin view."""
    context = {
        "recordVerboseName": model._meta.verbose_name,
        "recordVerboseNamePlural": model._meta.verbose_name_plural,
    }
    context.update(kwargs)
    context.update(extra)
    return context


def load_instance(model, pk):
    """Load a model instance by primary key, coercing numeric string pks."""
    return model.objects.get(pk=int(pk) if pk.isnumeric() else pk)


def get_record(model, pk):
    """Return the record for pk, falling back to the first record in the table."""
    if model.objects.filter(pk=pk).exists():
        return model.objects.get(pk=pk)
    return model.objects.all()[0]
