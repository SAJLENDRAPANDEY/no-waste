def calculate_score(waste, required_qty, user_location=None):
    score = 0

    # 🔹 1. Quantity Match (50)
    if waste.quantity >= required_qty:
        score += 50
    else:
        score += (waste.quantity / required_qty) * 50

    # 🔹 2. Waste Type Match (30)
    score += 30  # already filtered

    # 🔹 3. Location Match (IMPORTANT 🔥)
    if user_location and waste.location:
        if user_location.lower() in waste.location.lower():
            score += 20
        else:
            score += 5

    # 🔹 4. Company Priority (optional smart logic)
    if "green" in waste.company.lower():
        score += 5

    return round(score, 2)


def get_best_matches(waste_queryset, waste_type, quantity, user_location=None):

    # 🔍 FILTER
    filtered = waste_queryset.filter(
        waste_type__iexact=waste_type,
        status="produced",
        quantity__gt=0
    )

    results = []

    for waste in filtered:
        score = calculate_score(waste, quantity, user_location)

        results.append({
            "id": waste.id,
            "company": waste.company,
            "quantity": waste.quantity,
            "location": waste.location,
            "score": score
        })

    # 🔥 SORTING
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results[:5]