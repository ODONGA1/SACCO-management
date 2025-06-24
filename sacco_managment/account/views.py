from django.shortcuts import render, redirect
from account.models import KYC, Account, AuditLog
from account.forms import KYCForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.forms import CreditCardForm
from core.models import CreditCard, Notification, Transaction
from django.contrib.auth import authenticate, login
from core.decorators import staff_required, admin_required
from .models import StaffPermission
from django.utils import timezone
from datetime import timedelta
from user_auths.models import User
from django.views.generic import FormView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.db.models import Count, Sum
from datetime import datetime, timedelta


@login_required
def account(request):
    if request.user.is_authenticated:
        try:
            kyc = KYC.objects.get(user=request.user)
        except KYC.DoesNotExist:
            messages.warning(request, "You need to submit your KYC")
            return redirect("account:kyc-reg")

        account = Account.objects.get(user=request.user)
    else:
        messages.warning(request, "You need to login to access the dashboard")
        return redirect("user_auths:login")

    context = {
        "kyc": kyc,
        "account": account,
    }
    return render(request, "account/account.html", context)


@login_required
def kyc_registration(request):
    user = request.user
    account = Account.objects.get(user=user)

    try:
        kyc = KYC.objects.get(user=user)
    except KYC.DoesNotExist:
        kyc = None

    if request.method == "POST":
        form = KYCForm(request.POST, request.FILES, instance=kyc)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = user
            new_form.account = account
            new_form.save()
            messages.success(
                request, "KYC Form submitted successfully, In review now.")
            return redirect("account:account")
    else:
        form = KYCForm(instance=kyc)
    context = {
        "account": account,
        "form": form,
        "kyc": kyc,
    }
    return render(request, "account/kyc-form.html", context)


@login_required
def dashboard(request):
    if request.user.is_authenticated:
        try:
            kyc = KYC.objects.get(user=request.user)
        except KYC.DoesNotExist:
            messages.warning(request, "You need to submit your KYC")
            return redirect("account:kyc-reg")

        recent_transfer = Transaction.objects.filter(
            sender=request.user, transaction_type="transfer", status="completed").order_by("-id")[:1]
        recent_received_transfer = Transaction.objects.filter(
            receiver=request.user, transaction_type="transfer").order_by("-id")[:1]

        sender_transaction = Transaction.objects.filter(
            sender=request.user, transaction_type="transfer").order_by("-id")
        receiver_transaction = Transaction.objects.filter(
            receiver=request.user, transaction_type="transfer").order_by("-id")

        request_sender_transaction = Transaction.objects.filter(
            sender=request.user, transaction_type="request")
        request_receiver_transaction = Transaction.objects.filter(
            receiver=request.user, transaction_type="request")

        withdrawal_transactions = Transaction.objects.filter(
            sender=request.user, transaction_type="withdrawal").order_by("-id")

        account = Account.objects.get(user=request.user)
        credit_card = CreditCard.objects.filter(
            user=request.user).order_by("-id")

        # Fetch notifications for the logged-in user
        notifications = Notification.objects.filter(user=request.user).order_by('-date')

        if request.method == "POST":
            form = CreditCardForm(request.POST)
            if form.is_valid():
                new_form = form.save(commit=False)
                new_form.user = request.user
                new_form.save()

                Notification.objects.create(
                    user=request.user,
                    notification_type="Added Credit Card"
                )

                messages.success(request, "Card Added Successfully.")
                return redirect("account:dashboard")
        else:
            form = CreditCardForm()

    else:
        messages.warning(request, "You need to login to access the dashboard")
        return redirect("user_auths:login")

    context = {
        "kyc": kyc,
        "account": account,
        "form": form,
        "credit_card": credit_card,
        "sender_transaction": sender_transaction,
        "receiver_transaction": receiver_transaction,
        "request_sender_transaction": request_sender_transaction,
        "request_receiver_transaction": request_receiver_transaction,
        "recent_transfer": recent_transfer,
        "recent_received_transfer": recent_received_transfer,
        "withdrawal_transactions": withdrawal_transactions,
        "notifications": notifications,  # Pass notifications to the template
    }
    return render(request, "account/dashboard.html", context)



@login_required
def all_credit_cards(request):
    cards = CreditCard.objects.filter(user=request.user)
    return render(request, "credit_card/all-card.html", {"credit_cards": cards})


@login_required
def mobile_money_deposit(request):
    if request.method == 'POST':
        form = MobileMoneyDepositForm(request.POST)
        if form.is_valid():
            # Initiate payment via Flutterwave/Yo! API
            # This is a simulation - replace with actual API call
            ref = f"MMD-{timezone.now().timestamp()}"
            
            # Create pending transaction
            transaction = Transaction.objects.create(
                user=request.user,
                amount=form.cleaned_data['amount'],
                transaction_type="mobile_money_deposit",
                status="pending",
                description=f"Mobile Money Deposit to {form.cleaned_data['phone_number']}"
            )
            
            MobileMoneyTransaction.objects.create(
                transaction=transaction,
                provider=form.cleaned_data['provider'],
                phone_number=form.cleaned_data['phone_number'],
                transaction_ref=ref
            )
            
            # Simulate API response
            return render(request, 'mobile_money/payment_prompt.html', {
                'phone': form.cleaned_data['phone_number'],
                'amount': form.cleaned_data['amount'],
                'ref': ref
            })
    else:
        form = MobileMoneyDepositForm()
    
    return render(request, 'mobile_money/deposit.html', {'form': form})

  
  
@login_required
def calendar(request):
    context = {
        "breadcrumb": {
            "parent": "Calendar",
            "child": "Calendar Basic"
        }
    }
    return render(request, 'calendar/calendar-basic.html', context)


@admin_required
def admin_dashboard(request):
    # Calculate time periods
    today = timezone.now().date()
    month_ago = today - timedelta(days=30)
    
    # Staff statistics
    total_staff = StaffPermission.objects.count()
    active_staff = StaffPermission.objects.filter(
        user__is_active=True
    ).count()
    
    # Financial statistics
    total_deposits = Account.objects.aggregate(
        total=Sum('account_balance') + Sum('mobile_money_balance')
    )['total'] or 0
    
    # Member growth
    member_growth = User.objects.filter(
        role='MEMBER',
        date_joined__gte=month_ago
    ).count()
    
    # System activities
    admin_actions = AuditLog.objects.filter(
        action__in=['USER_CREATE', 'USER_EDIT', 'KYC_APPROVE'],
        timestamp__gte=month_ago
    ).order_by('-timestamp')[:10]

    context = {
        'title': 'Admin Dashboard',
        'breadcrumb': {
            'parent': 'Dashboard',
            'child': 'Admin Portal'
        },
        'stats': {
            'total_staff': total_staff,
            'active_staff': active_staff,
            'total_deposits': total_deposits,
            'member_growth': member_growth,
        },
        'admin_actions': admin_actions,
        'current_date': today.strftime("%B %d, %Y"),
    }
    return render(request, 'account/admin/dashboard.html', context)

# STAFF
@staff_required
def staff_dashboard(request):
    # Calculate statistics
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    # Member statistics
    total_members = User.objects.filter(role='MEMBER').count()
    new_members_week = User.objects.filter(
        role='MEMBER', 
        date_joined__gte=week_ago
    ).count()
    
    # KYC statistics - fixed to use account relationship
    pending_kyc = Account.objects.filter(kyc_submitted=True, kyc_confirmed=False).count()
    approved_kyc = Account.objects.filter(kyc_confirmed=True).count()
    
    # Transaction statistics
    recent_transactions = Transaction.objects.select_related(
        'sender', 'receiver'
    ).order_by('-date')[:5]
    
    # Recent activities
    activities = AuditLog.objects.filter(
        timestamp__gte=week_ago
    ).order_by('-timestamp')[:10]

    context = {
        'title': 'Staff Dashboard',
        'breadcrumb': {
            'parent': 'Dashboard',
            'child': 'Staff Portal'
        },
        'stats': {
            'total_members': total_members,
            'new_members_week': new_members_week,
            'pending_kyc': pending_kyc,
            'approved_kyc': approved_kyc,
        },
        'recent_transactions': recent_transactions,
        'activities': activities,
        'current_date': today.strftime("%B %d, %Y"),
    }
    return render(request, 'account/staff/dashboard.html', context)
    

@staff_required
def user_profiles(request):
    accounts = Account.objects.filter(
        user__role='MEMBER'
    ).select_related('user')
    return render(request, 'account/staff/user_profiles.html', {
        'accounts': accounts
    })

@staff_required
def password_resets(request):
    # Placeholder - would integrate with actual password reset system
    return render(request, 'account/staff/password_resets.html', {
        'reset_requests': []
    })


@staff_required
def kyc_review(request):
    pending_kyc = KYC.objects.filter(kyc_confirmed=False).select_related('user', 'account')
    
    if request.method == 'POST':
        kyc_id = request.POST.get('kyc_id')
        action = request.POST.get('action')
        
        try:
            kyc = KYC.objects.get(id=kyc_id)
            if action == 'approve':
                kyc.account.kyc_confirmed = True
                kyc.account.save()
                messages.success(request, f"KYC for {kyc.user.username} approved.")
            elif action == 'reject':
                messages.info(request, f"KYC for {kyc.user.username} rejected.")
            return redirect('account:kyc_review')
        except KYC.DoesNotExist:
            messages.error(request, "KYC record not found.")
    
    return render(request, 'account/staff/kyc_review.html', {
        'pending_kyc': pending_kyc
    })
    
    

# staff functions
@admin_required
def add_staff(request):
    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create StaffPermission entry
            StaffPermission.objects.create(
                user=user,
                role=form.cleaned_data['role'],
                can_view_balances=form.cleaned_data['can_view_balances'],
                can_reset_passwords=form.cleaned_data['can_reset_passwords'],
                can_approve_loans=form.cleaned_data['can_approve_loans'],
                can_edit_kyc=form.cleaned_data['can_edit_kyc']
            )
            
            return redirect('account:manage_staff')
    else:
        form = StaffCreationForm()
    
    return render(request, 'account/admin/add_staff.html', {'form': form})

@admin_required
def edit_staff(request, staff_id):
    staff_permission = get_object_or_404(StaffPermission, id=staff_id)
    
    if request.method == 'POST':
        form = StaffEditForm(request.POST, instance=staff_permission.user)
        if form.is_valid():
            form.save()
            
            # Update StaffPermission
            staff_permission.role = form.cleaned_data['role']
            staff_permission.can_view_balances = form.cleaned_data['can_view_balances']
            staff_permission.can_reset_passwords = form.cleaned_data['can_reset_passwords']
            staff_permission.can_approve_loans = form.cleaned_data['can_approve_loans']
            staff_permission.can_edit_kyc = form.cleaned_data['can_edit_kyc']
            staff_permission.save()
            
            return redirect('account:manage_staff')
    else:
        # Initialize form with existing data
        initial_data = {
            'role': staff_permission.role,
            'can_view_balances': staff_permission.can_view_balances,
            'can_reset_passwords': staff_permission.can_reset_passwords,
            'can_approve_loans': staff_permission.can_approve_loans,
            'can_edit_kyc': staff_permission.can_edit_kyc,
        }
        form = StaffEditForm(instance=staff_permission.user, initial=initial_data)
    
    return render(request, 'account/admin/edit_staff.html', {
        'form': form,
        'staff': staff_permission
    })

@admin_required
def activate_staff(request, staff_id):
    staff_permission = get_object_or_404(StaffPermission, id=staff_id)
    staff_permission.user.is_active = True
    staff_permission.user.save()
    return redirect('account:manage_staff')

@admin_required
def deactivate_staff(request, staff_id):
    staff_permission = get_object_or_404(StaffPermission, id=staff_id)
    staff_permission.user.is_active = False
    staff_permission.user.save()
    return redirect('account:manage_staff')



#manage staff
@admin_required
def manage_staff(request):
    staff_members = StaffPermission.objects.select_related('user').all()
    return render(request, 'account/admin/manage_staff.html', {
        'staff_members': staff_members
    })


# staff login
class StaffLoginView(FormView):
    template_name = 'registration/staff_login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('account:staff_dashboard')  # Default fallback
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        login_type = self.request.POST.get('login_type', 'staff')
        
        user = authenticate(self.request, username=username, password=password)
        
        if user is not None:
            # Check user role and login type match
            if login_type == 'admin' and user.role not in ['ADMIN', 'SUPER_ADMIN']:
                messages.error(self.request, "You don't have admin privileges")
                return self.form_invalid(form)
                
            if login_type == 'staff' and user.role not in ['STAFF', 'ADMIN', 'SUPER_ADMIN']:
                messages.error(self.request, "You don't have staff privileges")
                return self.form_invalid(form)
            
            login(self.request, user)
            
            # Redirect based on role
            if user.role in ['ADMIN', 'SUPER_ADMIN']:
                return redirect('account:admin_dashboard')
            elif user.role == 'STAFF':
                return redirect('account:staff_dashboard')
        
        messages.error(self.request, "Invalid username or password")
        return self.form_invalid(form)

# ADMIN

def staff_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user and user.role in ['STAFF', 'ADMIN', 'SUPER_ADMIN']:
            login(request, user)
            if user.role == 'STAFF':
                return redirect('staff_dashboard')
            elif user.role == 'ADMIN':
                return redirect('admin_dashboard')
            # SUPER_ADMIN uses Django admin
        else:
            messages.error(request, 'Invalid credentials or access rights')
    return render(request, 'account/staff_login.html')


@admin_required
def admin_dashboard(request):
    total_staff = StaffPermission.objects.count()
    
    # Placeholder values - integrate with actual models
    active_loans = 0
    total_deposits = Account.objects.aggregate(
        total=Sum('account_balance') + Sum('mobile_money_balance')
    )['total'] or 0
    
    # Staff activity (last active within 24 hours)
    staff_activity = StaffPermission.objects.filter(
        user__last_login__gte=timezone.now() - timedelta(days=1)
    ).order_by('-user__last_login')
    
    return render(request, 'account/admin/dashboard.html', {
        'total_staff': total_staff,
        'active_loans': active_loans,
        'total_deposits': total_deposits,
        'staff_activity': staff_activity
    })

@admin_required
def manage_staff(request):
    staff_members = StaffPermission.objects.select_related('user').all()
    return render(request, 'account/admin/manage_staff.html', {
        'staff_members': staff_members
    })

@admin_required
def financial_reports(request):
    # Placeholder - integrate with financial models
    return render(request, 'account/admin/financial_reports.html', {
        'reports': []
    })

@admin_required
def audit_logs(request):
    logs = AuditLog.objects.order_by('-timestamp')
    return render(request, 'account/admin/audit_logs.html', {
        'logs': logs
    })