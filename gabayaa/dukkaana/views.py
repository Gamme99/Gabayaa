from django.shortcuts import render, redirect
from .models import Cloth, Shoe, Electronic
from .forms import ProductForm, ShoeForm, ClothForm, ElectronicForm
# Create your views here.

def base(request):
    return render(request, 'base.html', {})

def cloths(request):
    cloths = Cloth.objects.all()
    return render(request, 'cloths.html', {'cloths': cloths})

def shoes(request):
    shoes = Shoe.objects.all()
    return render(request, 'shoes.html', {'shoes': shoes})

def electronics(request):
    electronics = Electronic.objects.all()
    return render(request, 'electronics.html', {'electronics': electronics})

def renting(request):
    return render(request, 'renting.html', {})
def buying(request):
    return render(request, 'buying.html', {})
def manager(request):
    return render(request, 'manager.html', {})


def add_shoe(request):
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
    return render(request, 'add_shoe.html', context)


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
    return render(request, 'add_cloth.html', context)

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
    return render(request, 'add_electronic.html', context)

