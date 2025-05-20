from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from ..user_form import CustomerForm, CustomerUpdateForm, LoginForm
from ..models import Customer, Product, Order, PromoCode
from django.contrib.auth import login
from .helper import superuser_required


def base(request):
    """
    Redirect to home page since we're using it as the landing page.
    """
    return redirect('')


# @login_required(login_url="login")
@superuser_required
def manager(request):
    """
    View for the manager dashboard.
    """
    try:
        if request.user.is_authenticated:
            context = {
                'total_products': Product.objects.count(),
                'total_customers': Customer.objects.count(),
                'total_orders': Order.objects.count(),
                'active_promos': PromoCode.objects.filter(is_active=True).count(),
                'recent_activities': []  # You can implement this later if needed
            }
            return render(request, 'auth/manager.html', context)
        return redirect('login')
    except Exception as e:
        return render(request, 'error.html', {
            'error_message': _('An error occurred while loading the manager dashboard.')
        })


def logoutManager(request):
    logout(request)
    request.session['cart'] = {}
    request.session['total_price'] = 0.00
    request.session['subtotal'] = 0.00
    request.session['promo_discount'] = 0.00
    request.session['total'] = 0.00
    request.session['discount'] = 0.00
    request.session['item_count'] = None
    return redirect("login")


def register(request):
    """
    View for manager registration.
    """
    try:
        if request.method == "POST":
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(
                    request, 'Registration successful. Please log in.')
                return redirect('login')
            else:
                messages.error(
                    request, 'Invalid form. Please correct the errors.')
        else:
            form = UserCreationForm()

        context = {'form': form}
        return render(request, 'auth/register.html', context)
    except Exception as e:
        return render(request, 'error.html', {
            'error_message': _('An error occurred during registration.')
        })


def loginManager(request):
    print("login manager --------------- ")
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            print("here")
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                print("user that logged in ", request.user)
                request.session['cart'] = {}
                request.session['total_price'] = 0.00
                request.session['subtotal'] = 0.00
                request.session['promo_discount'] = 0.00
                request.session['total'] = 0.00
                request.session['discount'] = 0.00
                request.session['item_count'] = None
                return redirect('manager')
            else:
                print("user is NONE")
        else:
            messages.error(request, 'Invalid form. Please correct the errors.')
    else:
        form = AuthenticationForm()

    context = {'form': form}
    return render(request, 'auth/login.html', context)


def login_customer(request):
    print("login customer --------------- ")

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect to a success page or home page
            # Replace 'home' with your actual home URL name
            return redirect('base')
        else:
            # print("Form Errors:", form.errors)  # Debugging line
            messages.error(request, 'Invalid form. Please correct the errors.')
    else:
        messages.error(request, 'method is not post')
        form = LoginForm()

    return render(request, 'auth/login.html', {'form': form})


def register_customer(request):
    form = CustomerForm()
    print("REGISTER CUS")
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Registration successful. Please log in.')

        print(form.errors)
    else:
        print("request method is get")
        initial_data = {
            'username': 'Galmo',
            'email': 'Galmo@example.com',
            'first_name': 'Galmo',
            'last_name': 'Said',
            'password1': 'Summer@23',
            'password2': 'Summer@23',
            'street_address': '123 main st',
            'city': 'Seattle',
            'state': 'WA',
            'zip_code': '98118',
            'phone_number': '0000000000',

        }
        form = CustomerForm(initial=initial_data)
    context = {'form': form}
    return render(request, 'customerAuthentication/register.html', context)


def update_customer(request, id):
    customer = get_object_or_404(Customer, id=id)

    if request.method == 'POST':
        form = CustomerUpdateForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            print(" update successfuly")
            messages.success(
                request, 'successfully update customer info')
    else:
        print("its get method")
        form = CustomerUpdateForm(instance=customer)

    context = {'form': form, 'customer': customer}
    return render(request, 'auth/update_customer.html', context)


def logout_customer(request):
    """
    View to handle customer logout.
    """
    logout(request)
    # Clear cart session data
    request.session['cart'] = {}
    request.session['total_price'] = 0.00
    request.session['subtotal'] = 0.00
    request.session['promo_discount'] = 0.00
    request.session['total'] = 0.00
    request.session['discount'] = 0.00
    request.session['item_count'] = None
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')
