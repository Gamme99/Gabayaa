from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from ..user_form import CustomerForm, CustomerUpdateForm, LoginForm
from ..models import Customer, Product, Order, PromoCode
from .helper import superuser_required


# def base(request):
#     return redirect('home')


@superuser_required
def manager(request):
    try:
        context = {
            'total_products': Product.objects.count(),
            'total_customers': Customer.objects.count(),
            'total_orders': Order.objects.count(),
            'active_promos': PromoCode.objects.filter(is_active=True).count(),
            'recent_activities': []  # Optional
        }
        return render(request, 'manager/manager.html', context)
    except Exception as e:
        return render(request, 'error.html', {
            'error_message': _('An error occurred while loading the manager dashboard.')
        })


def login_view(request):
    """
    Unified login for both customers and managers.
    """
    form_class = LoginForm if request.method == 'POST' else AuthenticationForm
    form = form_class(request, data=request.POST or None)
    print("before condition")
    if request.method == 'POST' and form.is_valid():
        print("form is valid")
        user = form.get_user() if hasattr(form, 'get_user') else authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        print(f"user:  {user}")
        if user:
            login(request, user)
            request.session.update({
                'cart': {},
                'total_price': 0.00,
                'subtotal': 0.00,
                'promo_discount': 0.00,
                'total': 0.00,
                'discount': 0.00,
                'item_count': None,
            })

            return redirect('manager' if user.is_superuser or user.is_staff else 'home')
        messages.error(request, 'Invalid credentials.')
    elif request.method == 'POST':
        print("method is post but form is not valid")
        print(form.errors)
    elif form.is_valid():
        print("form is valid")

    return render(request, 'auth/login.html', {'form': form})


# def register_view(request):
#     """
#     Unified registration for customers (public) and managers (admin panel).
#     Use 'type' param to distinguish.
#     """
#     if request.GET.get('type') == 'manager':
#         form = UserCreationForm(request.POST or None)
#         template = 'manager/register.html'
#     else:
#         form = CustomerForm(request.POST or None, initial={
#             'username': 'Galmo',
#             'email': 'Galmo@example.com',
#             'first_name': 'Galmo',
#             'last_name': 'Said',
#             'password1': 'Summer@23',
#             'password2': 'Summer@23',
#             'street_address': '123 main st',
#             'city': 'Seattle',
#             'state': 'WA',
#             'zip_code': '98118',
#             'phone_number': '0000000000',
#         }) if request.method != 'POST' else CustomerForm(request.POST)
#         template = 'customerAuthentication/register.html'

#     if request.method == 'POST' and form.is_valid():
#         form.save()
#         messages.success(request, 'Registration successful. Please log in.')
#         return redirect('login')

#     return render(request, template, {'form': form})


def logout_view(request):
    """
    Unified logout for all users.
    """
    logout(request)
    request.session.update({
        'cart': {},
        'total_price': 0.00,
        'subtotal': 0.00,
        'promo_discount': 0.00,
        'total': 0.00,
        'discount': 0.00,
        'item_count': None,
    })
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login' if request.user.is_superuser else 'home')


def update_user(request, id):
    customer = get_object_or_404(Customer, id=id)
    form = CustomerUpdateForm(request.POST or None, instance=customer)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Successfully updated customer info.')

    return render(request, 'auth/update_user.html', {'form': form, 'customer': customer})


def password_reset(request):
    return redirect('home')
