from django.contrib import admin
# from .models import Profile
from .models import Waste, Requirement, WasteRequest,Profile
admin.site.register(Waste)
admin.site.register(Requirement)
admin.site.register(WasteRequest)
# admin.site.register(Profile)
# from .models import Users

admin.site.register(Profile)

