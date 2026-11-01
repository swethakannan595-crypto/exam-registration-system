# Online Examination Registration System (Django)

Individual focus: **exam registration and result access**, with an interactive student dashboard.

## Run it
```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations exams
python manage.py migrate
python manage.py seed_demo          # optional demo data
python manage.py runserver
```
Open http://127.0.0.1:8000/ - demo logins: `student / student123`, `admin / admin123` (admin panel at /admin/).

## Features
- Student sign-up / login, profile
- Browse exams with live search and filters, seat meter, deadline and seat-limit checks
- One-click registration with confirmation dialog, cancel before deadline
- Printable hall ticket with unique ticket number
- Results: only published results visible, grade and pass/fail, printable result sheet
- Dashboard: animated stats, next-exam countdown, Chart.js score chart (bar/line toggle), pass/fail doughnut
- Admin: create exams, enter marks, bulk publish/unpublish results

## Structure
- `examsite/` settings and root URLs
- `exams/` models, views, forms, admin, templates, `seed_demo` command
- `static/` CSS and JS
