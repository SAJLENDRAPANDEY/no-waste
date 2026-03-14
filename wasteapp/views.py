from django.shortcuts import render, redirect, get_object_or_404
from .models import Waste
from .forms import WasteForm
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.conf import settings


# ---------------- DASHBOARD ----------------

def dashboard(request):
    waste           = Waste.objects.all()
    available_stock = Waste.objects.filter(status="Produced")

    total    = waste.aggregate(Sum('quantity'))['quantity__sum'] or 0
    recycled = waste.filter(status="Recycled").aggregate(Sum('quantity'))['quantity__sum'] or 0
    rate     = round((recycled / total) * 100, 2) if total > 0 else 0

    plastic = waste.filter(waste_type="Plastic").aggregate(Sum('quantity'))['quantity__sum'] or 0
    paper   = waste.filter(waste_type="Paper").aggregate(Sum('quantity'))['quantity__sum'] or 0
    metal   = waste.filter(waste_type="Metal").aggregate(Sum('quantity'))['quantity__sum'] or 0
    organic = waste.filter(waste_type="Organic").aggregate(Sum('quantity'))['quantity__sum'] or 0

    monthly = (
        Waste.objects
        .annotate(month=ExtractMonth('date'))
        .values('month')
        .annotate(total=Sum('quantity'))
        .order_by('month')
    )

    context = {
        'waste'     : waste,
        'stock'     : available_stock,
        'total'     : total,
        'recycled'  : recycled,
        'rate'      : rate,
        'plastic'   : plastic,
        'paper'     : paper,
        'metal'     : metal,
        'organic'   : organic,
        'months'    : [m['month'] for m in monthly],
        'quantities': [m['total'] for m in monthly],
    }

    return render(request, "dashboard.html", context)


# ---------------- ADD WASTE ----------------

def add_waste(request):
    form = WasteForm()

    if request.method == "POST":
        form = WasteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')

    return render(request, 'add_waste.html', {'form': form})


# ---------------- PRODUCER ----------------

@login_required
def producer_page(request):
    if request.method == "POST":
        company    = request.POST.get('company')
        waste_type = request.POST.get('waste_type')
        quantity   = request.POST.get('quantity')
        date       = request.POST.get('date')

        if company and waste_type and quantity and date:
            Waste.objects.create(
                producer   = request.user,
                company    = company,
                waste_type = waste_type,
                quantity   = quantity,
                date       = date,
                status     = "Produced"
            )
            return redirect('dashboard')

    return render(request, "producer.html")


# ---------------- CONSUMER ----------------

def consumer_page(request):
    waste_data = Waste.objects.filter(status="Produced")

    return render(request, "consumer.html", {
        "data": waste_data
    })


# ---------------- REQUEST WASTE ----------------

def request_waste(request, id):
    waste = get_object_or_404(Waste, id=id)

    if request.method == "POST":
        consumer_name  = request.POST.get('consumer_name')
        consumer_email = request.POST.get('consumer_email')
        quantity       = request.POST.get('quantity')
        message        = request.POST.get('message')

        # ✅ empty fields check
        if not all([consumer_name, consumer_email, quantity, message]):
            return render(request, "request.html", {
                'waste': waste,
                'error': 'Please fill in all fields'
            })

        # ✅ quantity validation
        if int(quantity) > waste.quantity:
            return render(request, "request.html", {
                'waste': waste,
                'error': f'Maximum available quantity is {waste.quantity} kg'
            })

        # ✅ Producer ko mail
        send_mail(
            subject        = f'New Waste Request from {consumer_name}',
            message        = f'''
Hello {waste.company},

You have received a new waste request.

Consumer Name  : {consumer_name}
Consumer Email : {consumer_email}
Waste Type     : {waste.waste_type}
Quantity Needed: {quantity} kg
Message        : {message}

Please respond to the consumer directly at: {consumer_email}
            ''',
            from_email     = settings.EMAIL_HOST_USER,
            recipient_list = [waste.producer.email],
            fail_silently  = False,
        )

        # ✅ Consumer ko Thank You mail
        send_mail(
            subject        = f'Thank You for Your Request – {waste.company}',
            message        = f'''
Dear {consumer_name},

Thank you for your interest in our waste materials.

We have received your request for {quantity} kg of {waste.waste_type}.
Our team will get back to you shortly.

Your Request Details:
- Waste Type : {waste.waste_type}
- Quantity   : {quantity} kg
- Message    : {message}

Best Regards,
{waste.company}
            ''',
            from_email     = settings.EMAIL_HOST_USER,
            recipient_list = [consumer_email],
            fail_silently  = False,
        )

        # ✅ redirect nahi — same page pe success message dikhe
        return render(request, "request.html", {
            'waste': waste,
            'sent' : True
        })

    return render(request, "request.html", {'waste': waste})