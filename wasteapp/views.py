from django.shortcuts import render, redirect, get_object_or_404
from .models import Waste, Requirement, WasteRequest
from .forms import WasteForm
from django.db.models import Sum, Q
from django.db.models.functions import ExtractMonth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.core.paginator import Paginator
from .decorators import producer_required, consumer_required
from .models import Profile 
import json
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse

from .ai_matching import get_best_matches
# from .models import Waste

User = get_user_model()


# ── LANDING PAGE ─────────────────────────────────────────

def landing(request):
    return render(request, "landing.html")


# ── DASHBOARD ────────────────────────────────────────────

@login_required(login_url="login")
def dashboard(request):

    waste = Waste.objects.all()

    available_stock = Waste.objects.filter(status="produced", quantity__gt=0)

    requirements_list = Requirement.objects.all().order_by("-quantity")
    company_count = Profile.objects.filter(role="producer").count()

    paginator = Paginator(requirements_list, 5)
    page_number = request.GET.get("page")
    requirements = paginator.get_page(page_number)

    total = waste.aggregate(Sum("quantity"))["quantity__sum"] or 0

    recycled = WasteRequest.objects.filter(status="approved").aggregate(
    Sum("quantity")
)["quantity__sum"] or 0
    

    rate = round((recycled / total) * 100, 2) if total > 0 else 0

    waste_types = Waste.objects.values("waste_type").annotate(total=Sum("quantity"))

    waste_labels = json.dumps([w["waste_type"] or "Unknown" for w in waste_types])
    waste_values = json.dumps([w["total"] or 0 for w in waste_types])

    monthly = (
        Waste.objects.annotate(month=ExtractMonth("date"))
        .values("month")
        .annotate(total=Sum("quantity"))
        .order_by("month")
    )

    months = json.dumps([m["month"] or 0 for m in monthly])
    quantities = json.dumps([m["total"] or 0 for m in monthly])
    top_companies = (
        Waste.objects.values("company")
        .annotate(total=Sum("quantity"))
        .order_by("-total")[:5]
    )

    company_names = json.dumps([c["company"] or "Unknown" for c in top_companies])
    company_waste = json.dumps([c["total"] or 0 for c in top_companies])
    context = {
        "stock": available_stock,
        "requirements": requirements,
        "total": total,
        "recycled": recycled,
        "rate": rate,
        "waste_labels": waste_labels,
        "waste_values": waste_values,
        "months": months,
        "quantities": quantities,
        "company_names": company_names,
        "company_waste": company_waste,
        "company_count": company_count,
    }

    return render(request, "dashboard.html", context)


# ── PRODUCER PAGE ────────────────────────────────────────

@login_required(login_url="login")
@producer_required
def producer_page(request):

    # ✅ Latest first (IMPORTANT)
    my_waste = Waste.objects.filter(producer=request.user).order_by("-id")
    requests_list = WasteRequest.objects.filter(
        waste__producer=request.user
    ).order_by("-request_date")

    # ✅ PAGINATION (6 per page)
    waste_paginator = Paginator(my_waste, 6)
    request_paginator = Paginator(requests_list, 6)

    waste_page = request.GET.get("w_page")
    request_page = request.GET.get("r_page")

    waste_list = waste_paginator.get_page(waste_page)
    requests = request_paginator.get_page(request_page)

    pending_count = requests_list.filter(status="pending").count()

    context = {
        "waste_list": waste_list,
        "requests": requests,
        "pending_count": pending_count,
    }

    return render(request, "producer.html", context)

# ── CONSUMER PAGE ────────────────────────────────────────

@login_required(login_url="login")
@consumer_required
def consumer_page(request):

    search_query = request.GET.get("search", "")

    waste_data = Waste.objects.filter(status="produced", quantity__gt=0)

    if search_query:
        waste_data = waste_data.filter(
            Q(company__icontains=search_query)
            | Q(waste_type__icontains=search_query)
        )

    paginator = Paginator(waste_data, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "consumer.html",
        {"data": page_obj, "search_query": search_query},
    )


# ── ADD WASTE ────────────────────────────────────────────

@login_required
@producer_required
def add_waste(request):

    form = WasteForm()

    if request.method == "POST":
        form = WasteForm(request.POST)

        if form.is_valid():
            waste = form.save(commit=False)
            waste.producer = request.user
            waste.status = "produced"
            waste.save()

            messages.success(request, "Waste added successfully!")
            return redirect("producer_page")

        else:
            messages.error(request, "Form invalid")

    return render(request, "add_waste.html", {"form": form})


# ── REQUEST WASTE ────────────────────────────────────────

@login_required
@consumer_required
def request_waste(request, id):

    waste = get_object_or_404(Waste, id=id)

    if request.method == "POST":

        quantity = request.POST.get("quantity")
        message = request.POST.get("message", "")

        if not quantity or int(quantity) <= 0:
            messages.error(request, "Invalid quantity")
            return redirect("request", id=id)

        if int(quantity) > waste.quantity:
            messages.error(request, f"Only {waste.quantity} available")
            return redirect("request", id=id)

        WasteRequest.objects.create(
            consumer=request.user,
            waste=waste,
            quantity=int(quantity),
            message=message,
            email=request.POST.get("email")
        )

        messages.success(request, "Request sent!")
        return redirect("consumer_page")

    return render(request, "request.html", {"waste": waste})


# ── APPROVE REQUEST ──────────────────────────────────────

from django.core.mail import EmailMultiAlternatives
from django.conf import settings

@login_required
@producer_required
def approve_request(request, id):

    req = get_object_or_404(WasteRequest, id=id)

    req.status = "approved"
    req.save()
    
    waste = req.waste
    waste.quantity -= req.quantity

    if waste.quantity <= 0:
        waste.status = "consumed"

    waste.save()

    # ✅ PROFESSIONAL EMAIL
    subject = "Your Waste Request Has Been Approved 🚚"

    text_content = f"""
Hello,

Good news! Your waste request has been approved.

Company: {waste.company}
Waste Type: {waste.waste_type}
Quantity: {req.quantity} kg

The company will now proceed with dispatch or further coordination.

Thank you for using Waste-Not.
"""

    html_content = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; background:#f4f4f4;">
      <div style="max-width:600px; margin:auto; background:#ffffff; border-radius:10px; overflow:hidden; border:1px solid #ddd;">
        
        <div style="background:#2a6049; color:white; padding:15px 20px;">
          <h2 style="margin:0;">Waste-Not Platform</h2>
          <p style="margin:0; font-size:13px;">Sustainable Waste Management</p>
        </div>

        <div style="padding:20px;">
          <h3 style="color:#2a6049;">Request Approved ✅</h3>
          <p>Your request has been successfully approved by the producer.</p>

          <table style="width:100%; border-collapse:collapse; margin-top:15px;">
            <tr>
              <td style="padding:8px; font-weight:bold;">Company</td>
              <td style="padding:8px;">{waste.company}</td>
            </tr>
            <tr>
              <td style="padding:8px; font-weight:bold;">Waste Type</td>
              <td style="padding:8px;">{waste.waste_type}</td>
            </tr>
            <tr>
              <td style="padding:8px; font-weight:bold;">Quantity</td>
              <td style="padding:8px;">{req.quantity} kg</td>
            </tr>
          </table>

          <p style="margin-top:15px;">
            🚚 <strong>Next Step:</strong> The company will now initiate dispatch or contact you for further details.
          </p>

          <p style="margin-top:20px; font-size:14px; color:#555;">
            Thank you for using <strong>Waste-Not</strong>. Together, we build a sustainable future ♻️
          </p>
        </div>

        <div style="background:#f0ede8; padding:12px; text-align:center; font-size:12px; color:#777;">
          Waste-Not Platform • Circular Economy Solution
        </div>

      </div>
    </div>
    """

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER,
        [req.email],
    )

    email.attach_alternative(html_content, "text/html")
    email.send()

    return redirect("producer_page")


# ── REJECT REQUEST ───────────────────────────────────────

from django.core.mail import EmailMultiAlternatives
from django.conf import settings

@login_required
@producer_required
def reject_request(request, id):

    req = get_object_or_404(WasteRequest, id=id)

    req.status = "rejected"
    req.save()

    waste = req.waste

    subject = "Update on Your Waste Request ❌"

    text_content = f"""
Hello,

We regret to inform you that your waste request could not be approved at this time.

Company: {waste.company}
Waste Type: {waste.waste_type}
Quantity Requested: {req.quantity} kg

This may be due to availability issues or other operational constraints.

You may explore other available listings on the platform.

Thank you for using Waste-Not.
"""

    html_content = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; background:#f4f4f4;">
      <div style="max-width:600px; margin:auto; background:#ffffff; border-radius:10px; overflow:hidden; border:1px solid #ddd;">
        
        <div style="background:#b03a2e; color:white; padding:15px 20px;">
          <h2 style="margin:0;">Waste-Not Platform</h2>
          <p style="margin:0; font-size:13px;">Request Update</p>
        </div>

        <div style="padding:20px;">
          <h3 style="color:#b03a2e;">Request Not Approved ❌</h3>

          <p>
            Thank you for your interest. Unfortunately, your request could not be approved at this time.
          </p>

          <table style="width:100%; border-collapse:collapse; margin-top:15px;">
            <tr>
              <td style="padding:8px; font-weight:bold;">Company</td>
              <td style="padding:8px;">{waste.company}</td>
            </tr>
            <tr>
              <td style="padding:8px; font-weight:bold;">Waste Type</td>
              <td style="padding:8px;">{waste.waste_type}</td>
            </tr>
            <tr>
              <td style="padding:8px; font-weight:bold;">Requested Quantity</td>
              <td style="padding:8px;">{req.quantity} kg</td>
            </tr>
          </table>

          <p style="margin-top:15px;">
            ⚠️ This may be due to limited availability, request mismatch, or operational constraints.
          </p>

          <p style="margin-top:10px;">
            🔎 We encourage you to explore other available waste listings on the platform.
          </p>

          <p style="margin-top:20px; font-size:14px; color:#555;">
            Thank you for using <strong>Waste-Not</strong>. We appreciate your commitment to sustainability ♻️
          </p>
        </div>

        <div style="background:#f0ede8; padding:12px; text-align:center; font-size:12px; color:#777;">
          Waste-Not Platform • Circular Economy Solution
        </div>

      </div>
    </div>
    """

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER,
        [req.email],   # ✅ form wala email use karo
    )

    email.attach_alternative(html_content, "text/html")
    email.send()

    return redirect("producer_page")

# ── ADD REQUIREMENT ──────────────────────────────────────

@login_required
def add_requirement(request):

    if request.method == "POST":

        Requirement.objects.create(
            company=request.POST.get("company"),
            waste_type=request.POST.get("waste_type"),
            quantity=int(request.POST.get("quantity")),
            location=request.POST.get("location"),
        )

        return redirect("dashboard")

    return render(request, "add_requirement.html")


# ── PROFILE ──────────────────────────────────────────────

@login_required
def profile(request):
    return render(request, "profile.html", {"profile": request.user.profile})


# ── SIGNUP ───────────────────────────────────────────────

def signup(request):

    error = None

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")
        role = request.POST.get("role")

        if password != confirm:
            error = "Passwords do not match"

        elif User.objects.filter(username=username).exists():
            error = "Username exists"

        elif User.objects.filter(email=email).exists():
            error = "Email exists"

        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )

            user.refresh_from_db()
            user.profile.role = role
            user.profile.save()

            messages.success(request, "Account created!")
            return redirect("login")

    return render(request, "signup.html", {"error": error})


# ── LOGIN ────────────────────────────────────────────────

def login_view(request):

    error = None

    if request.method == "POST":

        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )

        if user:
            login(request, user)

            if user.profile.role == "producer":
                return redirect("producer_page")
            else:
                return redirect("consumer_page")

        else:
            error = "Invalid credentials"

    return render(request, "login.html", {"error": error})





def smart_match_api(request):
    error=None
    waste_type = request.GET.get("waste_type")
    quantity = int(request.GET.get("quantity", 0))
    location = request.GET.get("location", "")

    results = get_best_matches(
        Waste.objects.all(),
        waste_type,
        quantity,
        location
    )

    return render(request, "smart_match.html", {"error": error})
    return JsonResponse(results, safe=False)

