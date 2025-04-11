from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils.timezone import now
from io import BytesIO
from reportlab.pdfgen import canvas
from openpyxl import Workbook
from core.models import Transaction
from .models import FinancialReport
from .forms import DateRangeForm

@login_required
def generate_report(request):
    """Handles report generation in PDF or Excel format."""
    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            report_format = form.cleaned_data['format']
            transactions = Transaction.objects.filter(
                user=request.user, date__range=[start_date, end_date]
            ).order_by('-date')
            
            if transactions.exists():
                report = FinancialReport.objects.create(
                    user=request.user,
                    report_type="Transaction Report",
                    start_date=start_date,
                    end_date=end_date,
                    format=report_format
                )
                
                if report_format == 'PDF':
                    return generate_pdf_report(transactions, start_date, end_date, report)
                elif report_format == 'EXCEL':
                    return generate_excel_report(transactions, start_date, end_date, report)
            else:
                messages.warning(request, "No transactions found for the selected date range.")
                return redirect('reports:generate_report')
    else:
        form = DateRangeForm()
    
    return render(request, 'reports/generate_report.html', {'form': form})


def generate_pdf_report(transactions, start_date, end_date, report):
    """Generates a PDF report for transactions."""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, 800, f"Transaction Report: {start_date} to {end_date}")
    pdf.setFont("Helvetica", 12)
    
    y = 750
    pdf.drawString(100, y, "Date")
    pdf.drawString(250, y, "Description")
    pdf.drawString(450, y, "Amount (UGX)")
    pdf.line(100, y - 10, 500, y - 10)
    y -= 30
    
    for transaction in transactions:
        if y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y = 800
        pdf.drawString(100, y, str(transaction.date))
        pdf.drawString(250, y, transaction.description[:30])
        pdf.drawString(450, y, f"{transaction.amount:.2f}")
        y -= 20
    
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    report.file.save(f"Transaction_Report_{start_date}_to_{end_date}.pdf", buffer)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Transaction_Report_{start_date}_to_{end_date}.pdf"'
    return response


def generate_excel_report(transactions, start_date, end_date, report):
    """Generates an Excel report for transactions."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Transactions"
    ws.append(["Date", "Description", "Amount ($)"])
    
    for transaction in transactions:
        ws.append([transaction.date, transaction.description, transaction.amount])
    
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    report.file.save(f"Transaction_Report_{start_date}_to_{end_date}.xlsx", buffer)
    
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Transaction_Report_{start_date}_to_{end_date}.xlsx"'
    return response


@login_required
def report_history(request):
    """Displays a user's report history."""
    reports = FinancialReport.objects.filter(user=request.user).order_by('-generated_at')
    return render(request, 'reports/history.html', {'reports': reports})


@login_required
def download_report(request, report_id):
    """Handles report file download."""
    report = get_object_or_404(FinancialReport, id=report_id, user=request.user)
    if report.file:
        response = HttpResponse(report.file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{report.file.name}"'
        return response
    messages.error(request, "Report file not found.")
    return redirect('reports:report_history')


@login_required
def delete_report(request, report_id):
    """Handles deletion of a report."""
    report = get_object_or_404(FinancialReport, id=report_id, user=request.user)
    if request.method == 'POST':
        report.file.delete(save=False)
        report.delete()
        messages.success(request, "Report deleted successfully.")
        return redirect('reports:report_history')
    return render(request, 'reports/confirm_delete.html', {'report': report})
