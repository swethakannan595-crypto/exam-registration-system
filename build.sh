
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate

python manage.py shell -c "import os; from django.contrib.auth import get_user_model; User = get_user_model(); student, _ = User.objects.get_or_create(username='student'); student.set_password(os.environ['DEMO_STUDENT_PASSWORD']); student.is_staff = False; student.is_superuser = False; student.save(); admin, _ = User.objects.get_or_create(username='admin'); admin.set_password(os.environ['DEMO_ADMIN_PASSWORD']); admin.is_staff = True; admin.is_superuser = True; admin.save()"
