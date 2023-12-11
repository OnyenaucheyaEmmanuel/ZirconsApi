# myapp/models.py
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .paystack import Paystack
from .customuser import CustomUser

# models.py

from django.contrib.auth.models import AbstractUser
from django.db import models


class GymMembership(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, db_column='user_id')
    expiration_date = models.DateTimeField(null=True, blank=True)
    plan = models.CharField(max_length=20, default='')
    plan_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, null=True)

    def __str__(self):
        return f"{self.user.username}'s Gym Membership"

    def set_expiration_date(self, days):
        self.expiration_date = timezone.now() + timedelta(days=days)
        self.save()

    def send_expiration_email(self):
        three_days_from_now = timezone.now() + timedelta(days=3)
        if self.expiration_date and self.expiration_date <= three_days_from_now:
            subject = 'Gym Membership Expiration Reminder'
            message = f"Dear {self.user.first_name},\n\nYour gym membership is expiring on {self.expiration_date}. " \
                      f"Please renew your membership to continue enjoying our services.\n\nBest regards,\nThe Zircon Gym Team"
            from_email = 'ucheemma@swebslimited.com'
            to_email = [self.user.email]
            send_mail(subject, message, from_email, to_email, fail_silently=False)

    def set_plan_status(self):
        if self.expiration_date is not None and self.expiration_date > timezone.now():
            self.plan_status = True
        else:
            self.plan_status = False
        self.save()
        return self.plan_status

    def get_plan_status(self):
        return self.plan_status

    # @property
    # def user_id(self):
    #     return self.user.id if self.user else None

    @property
    def first_name(self):
        return self.user.first_name if self.user else None

    @property
    def last_name(self):
        return self.user.last_name if self.user else None


@receiver(post_save, sender=CustomUser)
def create_user_membership(sender, instance, created, **kwargs):
    if created:
        GymMembership.objects.create(user=instance)

class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(max_length=10, default='')
    last_name = models.CharField(max_length=10, default='')
    username = models.CharField(max_length=10, default='')
    amount = models.PositiveIntegerField()
    ref = models.CharField(max_length=5)
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_created',)

    def __str__(self):
        return f"Payment: {self.amount}"

    def save(self, *args, **kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            object_with_similar_ref = Payment.objects.filter(ref=ref)
            if not object_with_similar_ref:
                self.ref = ref
        super().save(*args, **kwargs)

    def amount_value(self):
        return int(self.amount) * 100

    def verify_payment(self):
        paystack = Paystack()
        status, result = paystack.verify_payment(self.ref, self.amount)
        if status:
            if result['amount'] / 100 == self.amount:
                self.verified = True
            self.save()
        if self.verified:
            return True
        return False

    # @property
    # def user_id(self):
    #     return self.user.id if self.user else None

    @property
    def username(self):
        return self.user.username if self.user else None
