from django import forms
from .models import Waste

class WasteForm(forms.ModelForm):

    class Meta:
        model = Waste
        fields = [
            'company',
            'waste_type',
            'quantity',
            'date',
            'location',
            'description'
        ]