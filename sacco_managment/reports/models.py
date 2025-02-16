# reports/models.py
from django.db import models
from django.contrib.auth import get_user_model
from core.models import Transaction

User = get_user_model()

class FinancialReport(models.Model):
    REPORT_FORMATS = (
        ('PDF', 'PDF'),
        ('EXCEL', 'Excel'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    format = models.CharField(max_length=10, choices=REPORT_FORMATS)
    generated_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='reports/')
    transactions = models.ManyToManyField(Transaction)

    def __str__(self):
        return f"{self.user.email} - {self.report_type} Report"