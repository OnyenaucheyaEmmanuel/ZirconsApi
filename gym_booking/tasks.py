# # tasks.py
# from datetime import timedelta
# from django.utils import timezone
# from background_task import background

# from .models import GymMembership

# @background(schedule=timedelta(days=3))
# def send_expiration_email(user_id):
#     # Retrieve the user's gym membership
#     user_membership = GymMembership.objects.get(user_id=user_id)

#     send_email(user_membership.user.email, "Your membership is expiring soon!")

