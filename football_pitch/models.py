# booking/models.py
import secrets
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models

from .paystack import Paystack

# class PitchBooking(models.Model):
#     first_name = models.CharField(max_length=20)
#     last_name = models.CharField(max_length=20)
#     email = models.EmailField()
#     phone = models.IntegerField(max_length=11)
#     team_name = models.CharField(max_length=20)
#     date = models.DateField()
#     start_time = models.TimeField()
#     minutes = models.IntegerField(max_length=10)

#     @property
#     def first_name(self):
#         return self.first_name
#     @property
#     def last_name(self):
#         return self.last_name
#     @property
#     def team_name(self):
#         return self.team_name
#     @property
#     def date(self):
#         return self.date

#     @property
#     def start_time(self):
#         return self.start_time
#     @property
#     def minutes(self):
#         return self.minutes +"minutes"





class Payment(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField()
    phone = models.IntegerField()
    team_name = models.CharField(max_length=20)
    amount = models.PositiveIntegerField()
    date = models.DateField()
    start_time = models.TimeField()
    players = models.PositiveIntegerField()
    ref = models.CharField(max_length=5)
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
        # You need to define an 'amount' field in your model for this method to work correctly.
        # Assuming you add an 'amount' field, the implementation can be like this:
        return int(self.amount) * 100

    def verify_payment(self):
        # Assuming you have a Paystack class that contains the 'verify_payment' method.
        paystack = Paystack()
        status, result = paystack.verify_payment(self.ref, self.amount)
        if status:
            if result['amount'] / 100 == self.amount:
                self.verified = True
            self.save()
        return self.verified
    
 

    # def is_time_slot_available(self):
    #     end_time = int(self.start_time + timedelta(minutes=int(self.minutes)))
    #     conflicting_bookings = Payment.objects.filter(
    #         date=self.date,
    #         start_time__lt=end_time,
    #         end_time__gt=self.start_time
    #     )

    #     if conflicting_bookings.exists():
    #         raise ValidationError('The selected time slot is already booked.')

    # @property
    # def minutes_formatted(self):
    #     return f"{int(self.minutes)} minutes"

    # def save(self, *args, **kwargs):
    #     self.is_time_slot_available()  # Check availability before saving
    #     super().save(*args, **kwargs)



    # The following properties are redundant, as they already exist as model fields.

    # @property
    # def first_name(self):
    #     return self.user.first_name

    # @property
    # def last_name(self):
    #     return self.user.last_name

    # @property
    # def team_name(self):
    #     return self.team_name

    # @property
    # def date(self):
    #     return self.date

    # @property
    # def start_time(self):
    #     return self.start_time

    # @property
    # def minutes(self):
    #     return str(self.minutes) + " minutes"
