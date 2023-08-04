from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def base(request):
    username = request.GET.get('username')
    return render(request, 'base.html', {'username': username})


@login_required(login_url="login")
def manager(request):
    if request.user.is_authenticated:
        return render(request, 'manager/manager.html', {})

    return redirect('login')


def logoutManager(request):
    logout(request)
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
        print("valid form ")
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            print("here")
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                print("user that logged in ", request.user)
                return redirect('manager')
            else:
                print("user is NONE")
    else:
        print("invlaid form ")

        form = AuthenticationForm()
        messages.error(request, 'Invalid form. Please correct the errors.')

    context = {'form': form}
    return render(request, 'manager/login.html', context)
