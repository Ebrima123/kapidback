# kapidback

Django REST API for the Kapid Painting website: CMS content and a small CRM.
The frontend (website + `/admin` dashboard) lives in `kapidfront`.

## Setup

Requires Python 3.11+.

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env          # macOS/Linux: cp .env.example .env
python manage.py makemigrations cms crm
python manage.py migrate
python manage.py createsuperuser   # this is your dashboard login
python manage.py seed_demo         # optional demo services, projects, reviews, FAQs
python manage.py runserver 8000
```

SQLite is used by default. For Postgres set `DATABASE_URL=postgres://user:pass@host:5432/kapid`.

## API

| Area | Endpoint | Access |
| --- | --- | --- |
| Auth | `POST /api/auth/token/`, `POST /api/auth/token/refresh/`, `GET /api/auth/me/` | JWT |
| Public site | `GET /api/public/settings/ · services/ · services/<slug>/ · projects/ · projects/<slug>/ · testimonials/ · faqs/` | Anyone |
| Quote form | `POST /api/public/quote-request/` (creates a Lead, 10/hour per IP) | Anyone |
| CMS | `/api/cms/settings/`, `/api/cms/{services,projects,project-images,testimonials,faqs}/` | Staff |
| CRM | `/api/crm/{customers,leads,jobs,estimates,notes}/`, `/api/crm/dashboard/`, `POST /api/crm/leads/<id>/convert/` | Staff |

List endpoints support `?search=`, `?ordering=`, field filters (e.g. `?status=new`) and `?page=` / `?page_size=` (max 200).
The stock Django admin is still available at `/django-admin/` as a fallback.
