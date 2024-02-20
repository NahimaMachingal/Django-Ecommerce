from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product

# Create your views here.
def user_home(request):
    products = Product.objects.all().filter(is_available=True)

    context={
        'products' : products,

    }
    return render(request, 'customer/home.html',context)

def user_register(request):

    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST.get('email')
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']


        # Check if a user with the same email already exists
        if User.objects.filter(email=email).exists():
            return render(request, 'customer/userregister.html', {'error_message': 'User with this email already exists'})

        if password != confirm_password:
            return render(request, 'customer/userregister.html', {'error_message': 'passwords do not match'})
        
        myuser = User.objects.create_user(username=email, email=email, password=password)

        myuser.first_name = first_name
        myuser.last_name = last_name
        myuser.save()

        return redirect('login')

    return render(request,'customer/userregister.html')

def user_login(request):
    if 'email' in request.session:
        return redirect(user_home)
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Use Django's built-in authenticate function to check credentials
        user = authenticate(request, username=email, password=password)
        
        #replace these values with your predefined username and password
        if user is not None:
            # Valid credentials, log in the user
            login(request, user)
            request.session['email'] = email
            #successful login
            #you may want to set a session variable to track user's login status
            return redirect('user_home') # redirect to the home page
        else:
            # incorrect username or password
            error_message = 'Incorrect username or password'
            messages.error(request, error_message)
    return render(request,'customer/login.html')
# Clear messages stored in the session
    messages.clear(request)




