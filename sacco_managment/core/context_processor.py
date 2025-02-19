from core.models import Notification

def default(request):
    notifications = None

    if request.user.is_authenticated:  # ✅ Check if user is logged in
        if Notification.objects.filter(user=request.user).exists():  # ✅ Avoid errors if no notifications exist
            notifications = Notification.objects.filter(user=request.user).order_by("-date")[:10]

    return {
        "notifications": notifications,  
    }
