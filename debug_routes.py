import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wastenot_project.settings')
django.setup()

from django.urls import get_resolver
from django.urls.resolvers import URLPattern

resolver = get_resolver()

print("=" * 70)
print("URL PATTERNS CONFIGURED")
print("=" * 70)

for pattern in resolver.url_patterns:
    if isinstance(pattern, URLPattern):
        print(f"✓ {str(pattern.pattern):30} -> {pattern.callback.__name__ if hasattr(pattern.callback, '__name__') else pattern.callback}")

print("\n" + "=" * 70)
print("ROUTES SUMMARY")
print("=" * 70)
print("Landing:    /")
print("Dashboard:  /dashboard/")
print("Producer:   /producer/")
print("Consumer:   /consumer/")
print("Add Waste:  /add-waste/")
print("Request:    /request/<id>/")
print("Login:      /login/")
print("Signup:     /signup/")
