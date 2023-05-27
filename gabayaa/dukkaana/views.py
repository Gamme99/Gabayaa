from django.shortcuts import render, redirect
from .models import Cloth, Shoe, Electronic
from .forms import ProductForm, ShoeForm, ClothForm, ElectronicForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.backends.db import SessionStore
from django.contrib import messages

# Create your views here.

def base(request):
    username = request.GET.get('username')
    return render(request, 'base.html', {'username': username})

def cloths(request):
    # cloths = Cloth.objects.all()
    products = Cloth.objects.all()
    return render(request, 'view/products.html', {'products': products})

def shoes(request):
    # shoes = Shoe.objects.all()
    products = Shoe.objects.all()
    return render(request, 'view/products.html', {'products': products})

def electronics(request):
    # electronics = Electronic.objects.all()
    products = Electronic.objects.all()
    return render(request, 'view/products.html', {'products': products})

def renting(request):
    return render(request, 'renting.html', {})
def buying(request):
    return render(request, 'buying.html', {})

# @login_required(login_url="/login")
# @login_required
def manager(request):
    try:
        if request.session['managerLogin']:
            username = request.session['username']
            print("username that is authenticated:", username)
            return render(request, 'manager/manager.html', {'username': username, 'user': request.user})
    except KeyError:
        pass
    return redirect('login')
 
def logoutManager(request):

    request.session['username'] = None
    request.session['managerLogin'] = False
    logout(request) 
    return redirect("login")

def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. Please log in.')
            # return redirect('login')  
        else:
            messages.error(request, 'Invalid form. Please correct the errors.')
    else:
        print("request method is get")
    context = {'form': form}
    return render(request, 'manager/register.html', context)

def login(request):
    if request.method == 'POST':
        print("valid form ")
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                request.session['managerLogin'] = True
                # session = SessionStore(request.session.session_key)
                request.session['username'] = username
                # session['username'] = username
                # session['username'] = username
                # session.save()


                print("username in login: ", username)
                
                # messages.success(request, f"{username}' ")
                # return redirect('manager') 
                messages.success(request, 'Registration successful. Please log in.')
                return render(request, 'manager/manager.html', {'username':username})
    else:
        print("invlaid form ")
        form = AuthenticationForm()
        messages.error(request, 'Invalid form. Please correct the errors.')
    
    context = {'form': form}
    return render(request, 'manager/login.html', context)
# @login_required(login_url="/login")
def add_shoe(request):

    try:
        print ("out here")
        if request.session['managerLogin']:
            print("down here:", request.session['managerLogin'])
            message = None
            
            form = ShoeForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                message = "successfully added shoe!"
                return redirect('manager')    
            else:
                # Handle invalid shoe form
                message = "Shoe form is invalid! Please correct the errors in the form."
                # print(form.errors)
            form = ShoeForm()

            context = {'form': form, 'message': message}
            return render(request, 'forms/add_shoe.html', context)
    except KeyError:
        pass
    return redirect('login')


def add_cloth(request):
    message = None
   
    form = ClothForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        # Handle successful cloth creation
        return redirect('manager')  
    else:
        # Handle invalid cloth form
        message = "Cloth form is invalid! Please correct the errors in the form."
       
    form = ClothForm()
    context = {'form': form, 'message': message}
    return render(request, 'forms/add_cloth.html', context)

def add_electronic(request):
    form = ElectronicForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        # Handle successful electronic creation
        return redirect('manager')  
    else:
        # Handle invalid electronic form
        message = "Electronic form is invalid! Please correct the errors in the form."

    form = ElectronicForm()
    context = {'form': form, 'message': message}
    return render(request, 'forms/add_electronic.html', context)

