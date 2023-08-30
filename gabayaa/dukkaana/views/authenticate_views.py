from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from ..user_form import CustomerForm, CustomerUpdateForm, LoginForm
from ..models import Customer
from django.contrib.auth import login


def base(request):
    username = request.user.username
    user_id = request.user.pk
    print("username: ", username)
    print("id: ", user_id)

    # if username == []:
    #     print("[]")
    # if username == {}:
    #     print("curly")
    # if username == "":
    #     print("empty string")
    # if username == None:
    #     print("none")

    return render(request, 'base.html', {'username': username})


@login_required(login_url="login")
def manager(request):
    if request.user.is_authenticated:
        return render(request, 'manager/manager.html', {})

    return redirect('login')


def logoutManager(request):
    logout(request)
    request.session['cart'] = {}
    request.session['total_price'] = 0.0
    return redirect("login")


def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Registration successful. Please log in.')
            # return redirect('login')
        else:
            messages.error(request, 'Invalid form. Please correct the errors.')
    else:
        print("request method is get")
    context = {'form': form}
    return render(request, 'manager/register.html', context)


def loginManager(request):
    if request.method == 'POST':
        # print("valid form ")
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
                request.session['total_price'] = 0.0
                return redirect('manager')
            else:
                print("user is NONE")
        else:
            messages.error(request, 'Invalid form. Please correct the errors.')

    else:
        print("invlaid form ")

        form = AuthenticationForm()
        messages.error(request, 'NOT a post method')

    context = {'form': form}
    return render(request, 'manager/login.html', context)


def login_customer(request):
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

    return render(request, 'customerAuthentication/login.html', {'form': form})


def register_customer(request):
    form = CustomerForm()

    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Registration successful. Please log in.')
            # return redirect('login')
        else:
            messages.error(
                request, ' this is Invalid form . Please correct the errors.')
            # print(form.errors)
    else:
        print("request method is get")
        initial_data = {
            'username': 'Galmo',
            'email': 'Galmo@example.com',
            'first_name': 'Galmo',
            'last_name': 'Said',
            'password1': 'Dikicha@23',
            'password2': 'Dikicha@23',
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
            # return redirect('customer_detail', id=id)
            messages.success(
                request, 'successfully update customer info')
    else:
        # If it's a GET request, create a form instance with the customer's data
        print("its get method")
        form = CustomerUpdateForm(instance=customer)

    context = {'form': form, 'customer': customer}
    return render(request, 'manager/update_customer.html', context)
