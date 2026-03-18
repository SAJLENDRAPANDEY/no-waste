import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wastenot_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

# Get test users
producer = User.objects.filter(profile__role='producer').first()
consumer = User.objects.filter(profile__role='consumer').first()

print("\n" + "=" * 70)
print("TESTING ROUTES")
print("=" * 70)

client = Client()

# Test as consumer
print(f"\n🔵 LOGGED IN AS: {consumer.username} (CONSUMER)")
client.login(username=consumer.username, password="test")

routes = [
    ("/", "Landing Page"),
    ("/dashboard/", "Dashboard"),
    ("/producer/", "Producer Page"),
    ("/consumer/", "Consumer Page"),
    ("/add-waste/", "Add Waste (PRODUCER ONLY)"),
    ("/consumer/request/1/", "Request Waste (CONSUMER ACTION)"),
]

for route, desc in routes:
    try:
        response = client.get(route, follow=True)
        status = f"✓ {response.status_code}"
        if response.redirect_chain:
            redirects = " -> ".join([r[0] for r in response.redirect_chain])
            status += f" (redirected to: {redirects})"
        print(f"  {route:25} {status:30} [{desc}]")
    except Exception as e:
        print(f"  {route:25} ✗ ERROR: {str(e)[:40]}")

# Test as producer
client.logout()
print(f"\n🟢 LOGGED IN AS: {producer.username} (PRODUCER)")
client.login(username=producer.username, password="test")

for route, desc in routes:
    try:
        response = client.get(route, follow=True)
        status = f"✓ {response.status_code}"
        if response.redirect_chain:
            redirects = " -> ".join([r[0] for r in response.redirect_chain])
            status += f" (redirected to: {redirects})"
        print(f"  {route:25} {status:30} [{desc}]")
    except Exception as e:
        print(f"  {route:25} ✗ ERROR: {str(e)[:40]}")

print("\n" + "=" * 70)
