# gym_booking/admin.py

from django.contrib import admin

from gym_booking.models import CustomUser  # Import your CustomUser model

from .models import GymMembership, Payment


class GymMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'plan_status', 'created_at', 'expiration_date']
    search_fields = ['user__username', 'plan']

    def get_custom_user_id(self, obj):
        return obj.user.user_id if obj.user else None

    get_custom_user_id.short_description = 'Custom User ID'


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'verified', 'ref', 'date_created']
    search_fields = ['user__username', 'amount']

    def get_custom_user_id(self, obj):
        return obj.user.user_id if obj.user else None

    get_custom_user_id.short_description = 'Custom User ID'


admin.site.register(GymMembership, GymMembershipAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(CustomUser)

