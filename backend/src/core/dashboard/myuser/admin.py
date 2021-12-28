from django.contrib import admin
from core.dashboard.myuser.models import Profile


admin.site.register(Profile, admin.ModelAdmin)

