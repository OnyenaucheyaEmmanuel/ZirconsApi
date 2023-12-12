# booking/admin.py
from django.contrib import admin

from .models import Payment


class PaymentAdmin(admin.ModelAdmin):
    list_display = ["id", 'first_name', 'last_name', 'email', 'players', 'team_name', 'phone', 'start_time', 'date', 'amount', "verified", "ref", "date_created",]
    search_fields = ['first_name', 'last_name', 'email', 'team_name', 'phone',]

admin.site.register(Payment, PaymentAdmin)
