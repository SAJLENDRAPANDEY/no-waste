import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wastenot_project.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

users = User.objects.all()
for u in users:
    has_profile = hasattr(u, 'profile')
    role = u.profile.role if has_profile else "NO PROFILE"
    print(f"Username: {u.username:15} | Has Profile: {has_profile} | Role: {role}")
