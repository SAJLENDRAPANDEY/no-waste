from django.shortcuts import render, redirect
from .models import Waste
from .forms import WasteForm
from django.db.models import Sum
from django.db.models.functions import ExtractMonth


def dashboard(request):

    waste = Waste.objects.all()

    # Recycling rate calculation
    total = sum(i.quantity for i in waste)
    recycled = sum(i.quantity for i in waste if i.status == "Recycled")

    rate = 0
    if total > 0:
        rate = (recycled / total) * 100

    # Waste type analytics
    plastic = sum(i.quantity for i in waste if i.waste_type == "Plastic")
    paper = sum(i.quantity for i in waste if i.waste_type == "Paper")
    metal = sum(i.quantity for i in waste if i.waste_type == "Metal")
    organic = sum(i.quantity for i in waste if i.waste_type == "Organic")

    # Monthly waste data (real-time)
    monthly = (
        Waste.objects
        .annotate(month=ExtractMonth('date'))
        .values('month')
        .annotate(total=Sum('quantity'))
        .order_by('month')
    )

    months = []
    quantities = []

    for m in monthly:
        months.append(m['month'])
        quantities.append(m['total'])

    context = {
        'waste': waste,
        'rate': round(rate,2),

        'plastic': plastic,
        'paper': paper,
        'metal': metal,
        'organic': organic,

        'months': months,
        'quantities': quantities
    }

    return render(request, "dashboard.html", context)


def add_waste(request):

    form = WasteForm()

    if request.method == "POST":
        form = WasteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')

    return render(request, 'add_waste.html', {'form': form})