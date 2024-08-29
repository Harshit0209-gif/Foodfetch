from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect,reverse
from myapp.models import Contact, Dish, Team, Category, Profile, Order
from django.http import HttpResponse, HttpResponseNotAllowed,JsonResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Order
from django.views.decorators.http import require_http_methods
from django_otp import devices_for_user
from django_otp.oath import TOTP
from django.core.mail import send_mail
import random
from myapp.models import Product
from .models import Cart, CartItem, Product

def generate_otp(length=6):
    # Define the characters to use for OTP generation
    characters = '0123456789'
    # Generate OTP by randomly selecting characters from the defined set
    otp = ''.join(random.choice(characters) for _ in range(length))
    return otp
def index(request):
    context ={}
    cats = Category.objects.all().order_by('name')
    context['categories'] = cats
    # print()
    dishes = []
    for cat in cats:
        dishes.append({
            'cat_id':cat.id,
            'cat_name':cat.name,
            'cat_img':cat.image,
            'items':list(cat.dish_set.all().values())
        })
    context['menu'] = dishes
    return render(request,'index.html', context)

def contact_us(request):
    context={}
    if request.method=="POST":
        name = request.POST.get("name")
        em = request.POST.get("email")
        sub = request.POST.get("subject")
        msz = request.POST.get("message")
        
        obj = Contact(name=name, email=em, subject=sub, message=msz)
        obj.save()
        context['message']=f"Dear {name}, Thanks for your time!"

    return render(request,'contact.html', context)

def about(request):
    return render(request,'about.html')

def team_members(request):
    context={}
    members = Team.objects.all().order_by('name')
    context['team_members'] = members
    return render(request,'team.html', context)




#cart and product
@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    product = get_object_or_404(Product, id=product_id)

    cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    cart_item.save()

    return redirect('cart_detail')

@login_required
def remove_from_cart(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    cart_item.delete()
    return redirect('cart_detail')

@login_required
def cart_detail(request):
    cart = get_object_or_404(Cart, user=request.user)
    return render(request, 'myapp/cart_detail.html', {'cart': cart})

def product_list(request):
    dishes = Product.objects.all()  # Assuming your Product model is used for dishes
    return render(request, 'myapp/all_dishes.html', {'dishes': dishes})

def product_detail(request, product_id):
    dish = get_object_or_404(Product, id=product_id)
    return render(request, 'myapp/dish.html', {'dish': dish})


def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    
    # Calculate total price
    total_price = sum(item.quantity * item.product.discounted_price for item in cart_items)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart_detail.html', context)


def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.quantity * item.product.discounted_price for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart.html', context)





def all_dishes(request):
    context={}
    dishes = Dish.objects.all()
    if "q" in request.GET:
        id = request.GET.get("q")
        dishes = Dish.objects.filter(category__id=id)
        context['dish_category'] = Category.objects.get(id=id).name 

    context['dishes'] = dishes
    return render(request,'all_dishes.html', context)

def register(request):
    context = {}
    if request.method == "POST":
        # Fetch data from HTML form
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('pass')
        contact = request.POST.get('number')
        
        check = User.objects.filter(username=email)
        if len(check) == 0:
            # Generate OTP (you can generate it here or keep it as before)
            otp = generate_otp() # Example OTP
            send_mail(
                'OTP Verification',
                f'Your OTP is: {otp}',
                'from@example.com',
                [email],
                fail_silently=False,
            )
            
            # Store OTP in session
            request.session['otp'] = otp
            request.session['name'] = name
            request.session['email'] = email
            request.session['password'] = password
            request.session['contact'] = contact
            
            return redirect('verify_otp')
        else:
            context['error'] = f"A User with this email already exists"

    return render(request, 'register.html', context)

def verify_otp(request):
    context = {}
    if request.method == "POST":
        # Fetch OTP from HTML form
        otp_entered = request.POST.get('otp')
        # Retrieve OTP from session
        otp_sent = request.session.get('otp')

        email = request.session.get('email')
        name = request.session.get('name')
        password = request.session.get('password')
        contact = request.session.get('contact')

        if otp_entered == otp_sent:
            # If OTP matches, clear session and proceed with registration
            del request.session['otp']
            del request.session['email']
            del request.session['name']
            del request.session['password']
            del request.session['contact']
            
            # Create user and profile objects
            user = User.objects.create_user(email, email, password)
            user.first_name = name
            user.save()

            profile = Profile(user=user, contact_number=contact)
            profile.save()
            
            return redirect('login')
        else:
            context['error'] = "Invalid OTP. Please try again."

    return render(request, 'verify_otp.html', context)

def check_user_exists(request):
    email = request.GET.get('usern')
    check = User.objects.filter(username=email)
    if len(check)==0:
        return JsonResponse({'status':0,'message':'Not Exist'})
    else:
        return JsonResponse({'status':1,'message':'A user with this email already exists!'})

def signin(request):
    context={}
    if request.method=="POST":
        email = request.POST.get('email')
        passw = request.POST.get('password')

        check_user = authenticate(username=email, password=passw)
        if check_user:
            login(request, check_user)
            if check_user.is_superuser or check_user.is_staff:
                return HttpResponseRedirect('/admin')
            return HttpResponseRedirect('/dashboard')
        else:
            context.update({'message':'Invalid Login Details!','class':'alert-danger'})

    return render(request,'login.html', context)

def dashboard(request):
    context={}
    login_user = get_object_or_404(User, id = request.user.id)
    #fetch login user's details
    profile = Profile.objects.get(user__id=request.user.id)
    context['profile'] = profile

    #update profile
    if "update_profile" in request.POST:
        print("file=",request.FILES)
        name = request.POST.get('name')
        contact = request.POST.get('contact_number')
        add = request.POST.get('address')
       

        profile.user.first_name = name 
        profile.user.save()
        profile.contact_number = contact 
        profile.address = add 

        if "profile_pic" in request.FILES:
            pic = request.FILES['profile_pic']
            profile.profile_pic = pic
        profile.save()
        context['status'] = 'Profile updated successfully!'
    
    #Change Password 
    if "change_pass" in request.POST:
        c_password = request.POST.get('current_password')
        n_password = request.POST.get('new_password')

        check = login_user.check_password(c_password)
        if check==True:
            login_user.set_password(n_password)
            login_user.save()
            login(request, login_user)
            context['status'] = 'Password Updated Successfully!' 
        else:
            context['status'] = 'Current Password Incorrect!'

    #My Orders 
    orders = Order.objects.filter(customer__user__id=request.user.id).order_by('-id')
    context['orders']=orders    
    return render(request, 'dashboard.html', context)

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

@login_required
def single_dish(request, id):
    context={}
    dish = get_object_or_404(Dish, id=id)

    if request.user.is_authenticated:
        cust = get_object_or_404(Profile, user__id = request.user.id)
        order = Order(customer=cust, item=dish)
        order.save()
        inv = f'INV0000-{order.id}'

        paypal_dict = {
            'business':settings.PAYPAL_RECEIVER_EMAIL,
            'amount':dish.discounted_price,
            'item_name':dish.name,
            'user_id':request.user.id,
            'invoice':inv,
            'notify_url':'http://{}{}'.format(settings.HOST, reverse('paypal-ipn')),
            'return_url':'http://{}{}'.format(settings.HOST,reverse('payment_done')),
            'cancel_url':'http://{}{}'.format(settings.HOST,reverse('payment_cancel')),
        }

        order.invoice_id = inv 
        order.save()
        request.session['order_id'] = order.id

        form = PayPalPaymentsForm(initial=paypal_dict)
        context.update({'dish':dish, 'form':form})

    return render(request,'dish.html', context)


def payment_done(request):
    pid = request.GET.get('PayerID')
    if pid is None:
        pid = 'TRFWVUMS9AZSE'

    order_id = request.session.get('order_id')
    order_obj = Order.objects.get(id=order_id)
    order_obj.status = True
    order_obj.payer_id = pid
    order_obj.save()
    
    return redirect('add_address')

def successful_payment(request):
    # Process successful payment logic
    # ...
    return redirect('add_address')

def add_address_view(request):
    return render(request, 'add_address.html')

def confirmation(request):
    return render(request, 'confirmation.html')

def delivery_updates(request):
    return render(request, 'delivery.html')


def payment_cancel(request):
    ## remove comment to delete cancelled order
    # order_id = request.session.get('order_id')
    # Order.objects.get(id=order_id).delete()

    return render(request, 'payment_failed.html') 
def payment_done(request):
    ## remove comment to delete cancelled order
    # order_id = request.session.get('order_id')
    # Order.objects.get(id=order_id).delete()

    return render(request, 'payment_successfull.html') 

@require_POST
def address(request):
    # Handle the POST request data
    address = request.POST.get('address')  # Assuming the address is sent via POST data
    # Perform further processing, such as saving the address to the database, etc.

    # Return a JSON response indicating success or any additional data
    return JsonResponse({'message': 'Address received successfully'})


def accept_order(request, order_id):
    order = Order.objects.get(pk=order_id)
    order.status = 'accepted'
    order.save()
    return HttpResponse('Order accepted successfully')

def reject_order(request, order_id):
    order = Order.objects.get(pk=order_id)
    order.status = 'rejected'
    order.save()
    return HttpResponse('Order rejected successfully')