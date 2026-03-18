import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wastenot_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from wasteapp.models import Waste

User = get_user_model()

# Get a producer
producer = User.objects.filter(profile__role='producer').first()

if producer:
    print(f"\n📊 CHECKING WASTE FOR PRODUCER: {producer.username}")
    print("=" * 60)
    
    # Check waste entries for this producer
    producer_waste = Waste.objects.filter(producer=producer)
    
    print(f"Total waste entries for {producer.username}: {producer_waste.count()}")
    print()
    
    for waste in producer_waste:
        print(f"  ✓ {waste.company:25} | {waste.waste_type:15} | {waste.quantity:5} kg | {waste.date}")
    
    print("\n" + "=" * 60)
    
    # Check ALL waste
    total_waste = Waste.objects.all().count()
    print(f"Total waste in database: {total_waste}")
    print()
    
    for waste in Waste.objects.all()[:5]:
        print(f"  - {waste.producer.username:20} -> {waste.company:25} | {waste.waste_type:15} | {waste.quantity:5} kg")
else:
    print("No producer found")
