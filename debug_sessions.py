import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wastenot_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session

User = get_user_model()

# Show all sessions and their users
sessions = Session.objects.all()
print(f"Total active sessions: {len(sessions)}\n")

for session in sessions:
    try:
        session_data = session.get_decoded()
        user_id = session_data.get('_auth_user_id')
        if user_id:
            user = User.objects.get(id=user_id)
            role = user.profile.role
            print(f"Session User: {user.username:20} | Role: {role}")
    except Exception as e:
        print(f"Error reading session: {e}")
