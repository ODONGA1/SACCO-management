from django.contrib import admin
from .models import Account, KYC, StaffPermission 
from import_export.admin import ImportExportModelAdmin

from account.models import Account, KYC
from user_auths.models import User

# Unregister the User model if already registered elsewhere
admin.site.unregister(User)

# Custom admin for Account model
class AccountAdminModel(ImportExportModelAdmin):
    list_editable = ['account_status', 'account_balance', 'kyc_submitted', 'kyc_confirmed'] 
    list_display = ['user', 'account_number', 'account_status', 'account_balance', 'kyc_submitted', 'kyc_confirmed'] 
    list_filter = ['account_status']

# Custom admin for KYC model
class KYCAdmin(ImportExportModelAdmin):
    search_fields = ["full_name"]
    list_display = ['user', 'full_name', 'gender', 'identity_type', 'date_of_birth'] 

# Custom admin for User model
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active')
    actions = ['activate_staff']

    def activate_staff(self, request, queryset):
        updated = queryset.filter(role='STAFF').update(is_active=True)
        self.message_user(request, f"{updated} staff account(s) activated.")
        
        
class StaffPermissionAdmin(ImportExportModelAdmin):
    list_display = ('user', 'role', 'can_view_balances', 'can_reset_passwords')
    list_filter = ('role',)
    search_fields = ('user__username',)
    
    

# Register Account and KYC models
admin.site.register(StaffPermission, StaffPermissionAdmin)
admin.site.register(Account, AccountAdminModel)
admin.site.register(KYC, KYCAdmin)
