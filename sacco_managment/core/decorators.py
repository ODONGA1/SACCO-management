# core/decorators.py
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test

def role_required(*roles):
    def check_role(user):
        if not user.is_authenticated:
            return False
        return user.role in roles
    return user_passes_test(check_role, login_url='account:staff_login') 

staff_required = role_required('STAFF', 'ADMIN', 'SUPER_ADMIN')
admin_required = role_required('ADMIN', 'SUPER_ADMIN')
super_admin_required = role_required('SUPER_ADMIN')
