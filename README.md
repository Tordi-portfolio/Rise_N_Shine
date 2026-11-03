# Rise 'N Shine Maid Services - Django website

## Run it
```
python -m venv venv
venv\Scripts\activate          (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Public pages
/  /services/  /about/  /areas/  /faq/  /quote/  /thank-you/

## Staff area (staff accounts only)
- /staff/login/                  Login page. Only accounts with is_staff can sign in.
- /staff/                        Dashboard (counts, needs-reply list, requests by service)
- /staff/responses/              All client responses: filter by status, search, paginate
- /staff/responses/<id>/         Full detail, set status, private notes, delete
- /staff/responses/export/       CSV export (respects current filters)
- /admin/                        Django admin (also staff only)

Security built in: staff-only login (non-staff are told "wrong username or password"),
5-failure lockout for 15 minutes per IP + username, 8-hour sessions that end when the
browser closes, CSRF on every form, POST-only logout and delete, honeypot on the quote form,
CSV formula-injection protection, noindex on staff pages.

Create more staff users: python manage.py createsuperuser, or in /admin/ tick "Staff status".

## Before going live
Set DJANGO_SECRET_KEY, DJANGO_DEBUG=0, DJANGO_ALLOWED_HOSTS=yourdomain.com and
DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com, then run collectstatic.
Edit business details in core/context_processors.py.
