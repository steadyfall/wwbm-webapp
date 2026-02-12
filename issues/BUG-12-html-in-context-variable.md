# HTML Baked Into Context Variable in AdminMainPage

## Summary
`adminpanel/views.py:192-196` builds a raw HTML `<a>` tag with inline style and a dynamic URL and passes it as a context variable. This mixes presentation into business logic, bypasses Django's auto-escaping, and is untestable.

## Motivation
```python
# adminpanel/views.py:192-196
category_with_most_qs=f"""
    <a style="text-decoration: none;"
    href="{reverse_lazy("adminDBObject", kwargs={'db':'category', 'pk':category_with_most_qs.pk})}"
    title="{category_with_most_qs.name}">
    This cat.</a>""",
```

Issues:
1. **XSS risk**: if `category_with_most_qs.name` contains `"` or `>`, the `title=` attribute is injectable. Django's auto-escaping doesn't apply here because the string is already raw HTML.
2. **Untestable**: the context test would have to assert against a raw HTML string including a URL
3. **Wrong layer**: URL construction and link rendering belong in the template, not the view

## Scope
**Project:** Backend

- Change the context variable to pass the model object (or its `pk` and `name`) instead of an HTML string:
  ```python
  category_with_most_qs=category_with_most_qs,  # pass the object
  ```
- Update the corresponding template to render the link using `{% url %}` and `{{ category_with_most_qs.name }}` (both auto-escaped)

## Acceptance Criteria
- `category_with_most_qs` context variable is a model instance, not an HTML string
- The admin dashboard renders the same "category with most questions" link correctly
- A category name containing `<script>alert(1)</script>` is HTML-escaped in the rendered output

## Tests
- Unit test: `AdminMainPage` context contains a `Category` instance for `category_with_most_qs`, not a string
- Template test: XSS payload in category name is escaped in rendered HTML
