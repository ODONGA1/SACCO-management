#reports/admin.py
from django.contrib import admin
from .models import FinancialReport
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'report_type', 'date_range', 'format', 'generated_at', 'download_link')
    list_filter = ('format', 'generated_at', 'report_type')
    search_fields = ('user__email', 'report_type')
    readonly_fields = ('generated_at', 'file')
    date_hierarchy = 'generated_at'
    list_per_page = 20
    
    def date_range(self, obj):
        return f"{obj.start_date} to {obj.end_date}"
    date_range.short_description = 'Date Range'
    
    def download_link(self, obj):
        if obj.file:
            return format_html(
                '<a href="{}" class="button" download>Download</a>',
                obj.file.url
            )
        return "-"
    download_link.short_description = 'Download'
    download_link.allow_tags = True
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(user=request.user)
        return qs
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('user', 'start_date', 'end_date', 'format')
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only on creation
            obj.user = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['delete_selected_reports']
    
    def delete_selected_reports(self, request, queryset):
        for report in queryset:
            report.file.delete(save=False)
            report.delete()
        self.message_user(request, "Selected reports deleted successfully")
    delete_selected_reports.short_description = "Delete selected reports"
