# reports/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from io import BytesIO
from reportlab.pdfgen import canvas
from openpyxl import Workbook
from core.models import Transaction
from .models import FinancialReport
from .forms import DateRangeForm

@login_required
def generate_report(request):
    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            format = form.cleaned_data['format']
            
            transactions = Transaction.objects.filter(
                user=request.user,
                date__range=[start_date, end_date]
            ).order_by('-date')

            if format == 'PDF':
                return generate_pdf_report(request, transactions, start_date, end_date)
            elif format == 'EXCEL':
                return generate_excel_report(request, transactions, start_date, end_date)
    
    else:
        form = DateRangeForm()
    
    return render(request, 'reports/generate_report.html', {'form': form})

def generate_pdf_report(request, transactions, start_date, end_date):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # PDF Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, f"Transaction Report: {start_date} to {end_date}")
    p.setFont("Helvetica", 12)

    # Column Headers
    y = 750
    p.drawString(100, y, "Date")
    p.drawString(200, y, "Description")
    p.drawString(400, y, "Amount")
    p.line(100, y - 10, 500, y - 10)  # Underline header

    y -= 30

    # Transactions Data
    for transaction in transactions:
        if y < 50:  # Create a new page if needed
            p.showPage()
            p.setFont("Helvetica", 12)
            y = 800

        p.drawString(100, y, str(transaction.date))
        p.drawString(200, y, transaction.description[:30])  # Truncate long descriptions
        p.drawString(400, y, f"${transaction.amount:.2f}")
        y -= 20

    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Transaction_Report_{start_date}_to_{end_date}.pdf"'
    
    return response

def generate_excel_report(request, transactions, start_date, end_date):
    wb = Workbook()
    ws = wb.active
    ws.title = "Transactions"

    # Headers
    headers = ["Date", "Description", "Amount"]
    ws.append(headers)

    # Transaction Data
    for transaction in transactions:
        ws.append([transaction.date, transaction.description, transaction.amount])

    # Save and return response
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Transaction_Report_{start_date}_to_{end_date}.xlsx"'

    return response
