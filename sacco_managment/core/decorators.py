# core/decorators.py
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def staff_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account:staff_login')
        if request.user.role not in ['STAFF', 'ADMIN', 'SUPER_ADMIN']:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account:staff_login')
        if request.user.role not in ['ADMIN', 'SUPER_ADMIN']:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view