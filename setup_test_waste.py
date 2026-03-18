import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wastenot_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from wasteapp.models import Waste

User = get_user_model()

# Get the producer
producer = User.objects.filter(profile__role='producer').first()

if producer:
    print(f"\n🔧 PREPARING FOR TESTING")
    print("=" * 70)
    print(f"Producer: {producer.username} (ID: {producer.id})")
    print()
    
    # Create a test waste entry
    waste = Waste.objects.create(
        producer=producer,
        company="Test Company",
        waste_type="Plastic",
        quantity=100,
        status="produced",
        location="Test Location",
        description="Test waste entry for verification"
    )
    
    print(f"✅ Created test waste entry:")
    print(f"   ID: {waste.id}")
    print(f"   Producer: {waste.producer.username}")
    print(f"   Company: {waste.company}")
    print(f"   Type: {waste.waste_type}")
    print(f"   Quantity: {waste.quantity} kg")
    print(f"   Date: {waste.date}")
    print()
    
    # Verify it shows up in producer's waste
    producer_waste = Waste.objects.filter(producer=producer)
    print(f"📊 Total waste for {producer.username}: {producer_waste.count()}")
    for w in producer_waste:
        print(f"   - {w.company} ({w.waste_type}) x {w.quantity}kg")
    
    print("\n✅ TEST READY - Try accessing /producer/ in your browser")
    print("=" * 70)
