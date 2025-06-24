from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils.timezone import now
from io import BytesIO
from reportlab.pdfgen import canvas
from openpyxl import Workbook
import csv
from core.models import Transaction
from .models import FinancialReport
from .forms import DateRangeForm

@login_required
def generate_report(request):
    """Handles report generation in PDF, Excel or CSV format."""
    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            report_format = form.cleaned_data['format']
            
            # Get transactions within date range
            transactions = Transaction.objects.filter(
                user=request.user, 
                date__range=[start_date, end_date]
            ).order_by('-date')
            
            if transactions.exists():
                # Generate report based on format
                if report_format == 'PDF':
                    return generate_pdf_report(request, transactions, start_date, end_date)
                elif report_format == 'EXCEL':
                    return generate_excel_report(request, transactions, start_date, end_date)
                elif report_format == 'CSV':
                    return generate_csv_report(request, transactions, start_date, end_date)
            else:
                messages.warning(request, "No transactions found for the selected date range.")
                return redirect('reports:generate_report')
    else:
        form = DateRangeForm()
    
    return render(request, 'reports/generate_report.html', {'form': form})

def generate_pdf_report(request, transactions, start_date, end_date):
    """Generates a PDF report for transactions."""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    
    # Set up document
    pdf.setTitle(f"Transaction Report: {start_date} to {end_date}")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, 800, f"Transaction Report")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 780, f"Period: {start_date} to {end_date}")
    pdf.drawString(100, 760, f"Generated For: {request.user.get_full_name() or request.user.username}")
    pdf.drawString(100, 740, f"Generated On: {now().strftime('%Y-%m-%d %H:%M')}")
    
    # Table headers
    y = 700
    headers = ["Date", "Transaction Type", "Amount (UGX)", "Status", "Description"]
    col_positions = [100, 180, 280, 380, 480]
    
    for i, header in enumerate(headers):
        pdf.drawString(col_positions[i], y, header)
    
    pdf.line(100, y - 10, 550, y - 10)
    y -= 30
    
    # Transaction rows
    for transaction in transactions:
        if y < 100:  # New page if running out of space
            pdf.showPage()
            y = 800
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(100, y, "Transaction Report (Continued)")
            y -= 50
            pdf.setFont("Helvetica", 12)
        
        row = [
            transaction.date.strftime('%Y-%m-%d'),
            transaction.get_transaction_type_display(),
            f"{transaction.amount:,.2f}",
            transaction.get_status_display(),
            transaction.description[:50]  # Truncate long descriptions
        ]
        
        for i, value in enumerate(row):
            pdf.drawString(col_positions[i], y, str(value))
        
        y -= 20
    
    # Save the PDF
    pdf.save()
    buffer.seek(0)
    
    # Create and save report record
    report = FinancialReport.objects.create(
        user=request.user,
        report_type="Transaction Report",
        start_date=start_date,
        end_date=end_date,
        format='PDF'
    )
    report.file.save(f"Transaction_Report_{start_date}_to_{end_date}.pdf", buffer)
    
    # Return response
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Transaction_Report_{start_date}_to_{end_date}.pdf"'
    return response

def generate_excel_report(request, transactions, start_date, end_date):
    """Generates an Excel report for transactions."""
    buffer = BytesIO()
    wb = Workbook()
    ws = wb.active
    ws.title = "Transactions"
    
    # Add header
    ws.append(["Transaction Report"])
    ws.append([f"Period: {start_date} to {end_date}"])
    ws.append([f"Generated For: {request.user.get_full_name() or request.user.username}"])
    ws.append([f"Generated On: {now().strftime('%Y-%m-%d %H:%M')}"])
    ws.append([])  # Empty row
    
    # Add headers
    headers = ["Date", "Transaction ID", "Type", "Amount (UGX)", "Status", "Description"]
    ws.append(headers)
    
    # Add data
    for transaction in transactions:
        ws.append([
            transaction.date,
            transaction.transaction_id,
            transaction.get_transaction_type_display(),
            transaction.amount,
            transaction.get_status_display(),
            transaction.description
        ])
    
    # Save to buffer
    wb.save(buffer)
    buffer.seek(0)
    
    # Create and save report record
    report = FinancialReport.objects.create(
        user=request.user,
        report_type="Transaction Report",
        start_date=start_date,
        end_date=end_date,
        format='EXCEL'
    )
    report.file.save(f"Transaction_Report_{start_date}_to_{end_date}.xlsx", buffer)
    
    # Return response
    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="Transaction_Report_{start_date}_to_{end_date}.xlsx"'
    return response

def generate_csv_report(request, transactions, start_date, end_date):
    """Generates a CSV report for transactions."""
    buffer = StringIO()
    writer = csv.writer(buffer)
    
    # Write header
    writer.writerow(["Transaction Report"])
    writer.writerow([f"Period: {start_date} to {end_date}"])
    writer.writerow([f"Generated For: {request.user.get_full_name() or request.user.username}"])
    writer.writerow([f"Generated On: {now().strftime('%Y-%m-%d %H:%M')}"])
    writer.writerow([])  # Empty row
    
    # Write headers
    headers = ["Date", "Transaction ID", "Type", "Amount (UGX)", "Status", "Description"]
    writer.writerow(headers)
    
    # Write data
    for transaction in transactions:
        writer.writerow([
            transaction.date.strftime('%Y-%m-%d'),
            transaction.transaction_id,
            transaction.get_transaction_type_display(),
            transaction.amount,
            transaction.get_status_display(),
            transaction.description
        ])
    
    # Convert to bytes
    csv_content = buffer.getvalue()
    buffer.close()
    csv_bytes = BytesIO(csv_content.encode('utf-8'))
    
    # Create and save report record
    report = FinancialReport.objects.create(
        user=request.user,
        report_type="Transaction Report",
        start_date=start_date,
        end_date=end_date,
        format='CSV'
    )
    report.file.save(f"Transaction_Report_{start_date}_to_{end_date}.csv", csv_bytes)
    
    # Return response
    response = HttpResponse(csv_bytes.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="Transaction_Report_{start_date}_to_{end_date}.csv"'
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
        response['Content-Disposition'] = f'attachment; filename="{report.file.name.split("/")[-1]}"'
        return response
    messages.error(request, "Report file not found.")
    return redirect('reports:report_history')

@login_required
def delete_report(request, report_id):
    """Handles deletion of a report."""
    report = get_object_or_404(FinancialReport, id=report_id, user=request.user)
    if request.method == 'POST':
        report.file.delete()  # Delete the file
        report.delete()       # Delete the database record
        messages.success(request, "Report deleted successfully.")
        return redirect('reports:report_history')
    return render(request, 'reports/confirm_delete.html', {'report': report})