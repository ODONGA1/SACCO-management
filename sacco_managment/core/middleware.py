# core/middleware.py
import re
from .models import AuditLog

class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_paths = [
            re.compile(r'^/static/'),
            re.compile(r'^/staff/dashboard/$'),
        ]

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated and request.user.role != 'MEMBER':
            if not any(p.match(request.path) for p in self.exempt_paths):
                AuditLog.objects.create(
                    user=request.user,
                    action='ACTION',
                    details=f"Accessed {request.path}",
                    ip_address=self.get_client_ip(request)
                )
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')