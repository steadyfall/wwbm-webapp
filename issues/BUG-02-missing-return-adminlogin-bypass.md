# Missing `return` in adminlogin — Superuser Redirect Broken

## Summary
`auth/views.py:85` calls `redirect("admin_page")` without `return`. The redirect return value is discarded and execution continues, so authenticated superusers see the admin login form instead of being redirected to the admin panel.

## Motivation
```python
def adminlogin(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            redirect("admin_page")   # ← return value discarded
        else:
            return redirect("mainpage")
    # Falls through to login form rendering
```
An already-authenticated superuser visiting `/auth/admin-login/` will see the login page rendered, not be redirected. This is a broken UX flow and could also confuse a re-authentication attempt.

## Scope
**Project:** Middleware

- Add `return` before `redirect("admin_page")` at `auth/views.py:85`
- Verify the named URL `"admin_page"` resolves correctly (or update to `"adminMainPage"` which is the correct URL name used elsewhere)

## Acceptance Criteria
- Authenticated superuser visiting `/auth/admin-login/` is redirected to the admin panel
- Non-superuser authenticated user is redirected to mainpage (already works)
- Unauthenticated user sees the login form (already works)

## Tests
- Unit test: authenticated superuser GET to adminlogin view → 302 redirect to admin panel
- Unit test: authenticated non-superuser GET to adminlogin view → 302 redirect to mainpage
- Unit test: unauthenticated GET to adminlogin view → 200 login form

## Notes
Also verify the URL name: the admin panel uses `"adminMainPage"` as its URL name (`adminpanel/urls.py`) but `adminlogin` redirects to `"admin_page"` — confirm these resolve to the same URL, or update the name.
