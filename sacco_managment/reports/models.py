from django.db import models
from django.contrib.auth import get_user_model
from core.models import Transaction

User = get_user_model()

class FinancialReport(models.Model):
    REPORT_FORMATS = (
        ('PDF', 'PDF'),
        ('EXCEL', 'Excel'),
    )

    REPORT_TYPES = (
        ('TRANSACTION', 'Transaction Report'),
        ('SUMMARY', 'Financial Summary'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="financial_reports")
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, default='TRANSACTION')
    start_date = models.DateField()
    end_date = models.DateField()
    format = models.CharField(max_length=10, choices=REPORT_FORMATS)
    generated_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='reports/', blank=True, null=True)
    transactions = models.ManyToManyField(Transaction, related_name="reports")

    class Meta:
        ordering = ['-generated_at']
        verbose_name = "Financial Report"
        verbose_name_plural = "Financial Reports"

    def __str__(self):
        return f"{self.user.email} - {self.get_report_type_display()} ({self.start_date} to {self.end_date})"
