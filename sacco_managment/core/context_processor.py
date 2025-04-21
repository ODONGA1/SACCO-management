from core.models import Notification
from .models import Loan

def default(request):
    notifications = None

    if request.user.is_authenticated:  # ✅ Check if user is logged in
        if Notification.objects.filter(user=request.user).exists():  # ✅ Avoid errors if no notifications exist
            notifications = Notification.objects.filter(user=request.user).order_by("-date")[:10]

    return {
        "notifications": notifications,  
    }

def active_loan(request):
    if request.user.is_authenticated:
        active_loan = Loan.objects.filter(user=request.user, status='active').first()
        return {'active_loan': active_loan}
    return {}