from django.shortcuts import render,redirect
from django.shortcuts import render,redirect,get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import auth
from WarehouseManagement.models import CustomUser,UserMember,Product,Cart,ShippingMethod, Order

from WarehouseManagement.models import ShippingMethod,AssignedOrder
from django.db import transaction
from django.contrib import messages
import random
import string
import re
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.http import FileResponse, Http404
import os
from django.contrib.auth.hashers import make_password,check_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse



def index(request):
    return render(request, 'home.html')

def loginpage(request):
    return render(request, 'login.html')

def signuppage(request):
    return render(request,'signup.html')

def logout(request):
    auth.logout(request)
    return render(request, 'login.html')

def client_signup(request):
    if request.method == 'POST':
        name = request.POST.get('cname')
        number = request.POST.get('cmobile_number')
        email = request.POST.get('cemail')
        image = request.FILES.get('cimage')
        usertype = request.POST.get('cuser_type')
        pancard = request.POST.get('cpan_card')
        address = request.POST.get('caddress')
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request,'user with the current email id already exists')
            return render(request,'signup.html')
        else:
            user = CustomUser.objects.create_user(email=email,first_name=name,username = email,user_type=usertype,is_active=False)
            user.save()
            members = UserMember(number =number,image=image,user_member=user,address=address,pancard=pancard)
            members.save()
            subject = 'Registration Confirmation'
            message = 'registration successfull ,wait for admin approval'
            send_mail(subject,"Hello " + name +' '+ message ,settings.EMAIL_HOST_USER,{email})
            messages.success(request, 'Customer registration successful. Please wait for admin approval.')
            return render(request, 'signup.html')
        

def delivery_signup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        number = request.POST.get('mobile_number')
        email = request.POST.get('email')
        image = request.FILES.get('image')
        usertype = request.POST.get('user_type')
        pancard = request.POST.get('pan_card')
        address = request.POST.get('address')
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request,'User with the current email id already exists')
            return render(request,'signup.html')
        else:
            user = CustomUser.objects.create_user(email=email,first_name=name,username=email,user_type=usertype,is_active=False)
            user.save()
            members = UserMember(number =number,image=image,user_member=user,address=address,pancard=pancard)
            members.save()
            subject = 'Registration Confirmation'
            message = 'registration successfull ,wait for admin approval'
            send_mail(subject,"Hello " + name +' '+ message ,settings.EMAIL_HOST_USER,{email})
            messages.success(request, 'Delivery Partner registration successful. Please wait for admin approval.')
            return render(request, 'signup.html')
        

def main_login(request):
    if request.method == 'POST':
        pending_users = CustomUser.objects.filter(is_active=False)
        pending_count = pending_users.count()
        username = request.POST.get('username')
        password = request.POST.get('password')
        usr = auth.authenticate(request, username=username, password=password)
        if usr is not None:
            if usr.is_superuser:
                auth.login(request, usr)
                total_products = Product.objects.count()
                total_delivery_members = CustomUser.objects.filter(user_type='2').count()
                total_customers = CustomUser.objects.filter(user_type='3').count()
                total_orders = AssignedOrder.objects.count()
                dispatched_orders = AssignedOrder.objects.exclude(dispatched_location=None).count()
                pending_orders = AssignedOrder.objects.filter(status='Pending').count()
                return render(request,'admin/home.html',{
                                                'pending_count': pending_count,'total_products': total_products,
                                                'total_delivery_members': total_delivery_members,
                                                'total_customers': total_customers,
                                                'total_orders': total_orders,
                                                'dispatched_orders': dispatched_orders,
                                                'pending_orders': pending_orders,})
            elif usr.user_type == '3':
                auth.login(request, usr)
                usr = UserMember.objects.get(user_member=request.user)
                cart_items_count = Cart.objects.filter(user_cart=request.user).count()
                return render(request,'customer/home.html',{'usr':usr,'cart_items_count': cart_items_count,})
            else:
                auth.login(request, usr)
                usr = UserMember.objects.get(user_member=request.user)
                delivered_orders = AssignedOrder.objects.filter(delivery_guy=request.user, status='Delivered')
                pending_orders = AssignedOrder.objects.filter(delivery_guy=request.user, status='Pending')
                
                total_assigned_orders = delivered_orders.count() + pending_orders.count()

                context = {
                    'delivered_orders': delivered_orders,
                    'pending_orders': pending_orders,
                    'total_assigned_orders': total_assigned_orders,
                    'usr':usr,
                    
                }

                return render(request, 'delivery/home.html', context)
                
        else:
            messages.error(request,'invalid credentials')
            return render(request,'login.html')


@login_required       
def add_products(request):
    return render(request,'admin/addproducts.html')

def get_total_products(request):
    total_products = Product.objects.count()
    return JsonResponse({'total_products': total_products})


def admin_home(request):
    total_products = Product.objects.count()
    total_delivery_members = CustomUser.objects.filter(user_type='2').count()
    total_customers = CustomUser.objects.filter(user_type='3').count()
    total_orders = AssignedOrder.objects.count()
    dispatched_orders = AssignedOrder.objects.exclude(dispatched_location=None).count()
    pending_orders = AssignedOrder.objects.filter(status='Pending').count()

    return render(request, 'admin/home.html', {
        'total_products': total_products,
        'total_delivery_members': total_delivery_members,
        'total_customers': total_customers,
        'total_orders': total_orders,
        'dispatched_orders': dispatched_orders,
        'pending_orders': pending_orders,
    })

def customer_home(request):
    cart_items_count = Cart.objects.filter(user_cart=request.user).count()
    return render(request, 'customer/home.html',{'cart_items_count': cart_items_count})

def delivery_home(request):
    delivered_orders = AssignedOrder.objects.filter(delivery_guy=request.user, status='Delivered')
    pending_orders = AssignedOrder.objects.filter(delivery_guy=request.user, status='Pending')
    total_assigned_orders = delivered_orders.count() + pending_orders.count()

    context = {
        'delivered_orders': delivered_orders,
        'pending_orders': pending_orders,
        'total_assigned_orders': total_assigned_orders,
    }

    return render(request, 'delivery/home.html', context)


@login_required
def create_product(request):
    if request.method == 'POST':
        product_name = request.POST.get('name')
        product_stock = request.POST.get('stock')
        product_price = request.POST.get('price')
        product_description = request.POST.get('description')
        product_specification = request.POST.get('specification')
        product_image = request.FILES.get('image')
        product = Product(product_name=product_name,product_stock=product_stock,product_price=product_price,product_description=product_description,product_specification=product_specification,product_image=product_image)
        product.save()
        messages.success(request, 'Product added successfully')
        return render(request,'admin/addproducts.html')



@login_required   
def manage_products(request):
    products = Product.objects.all()
    return render(request,'admin/manageproducts.html',{'products':products})




@login_required
def delete_product(request, pk):
    product = Product.objects.get(id=pk) 
    product.delete()
    messages.success(request, 'Product deleted successfully')
    return redirect('manage_products')

def edit_product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request,'admin/editproducts.html',{'product':product})


@login_required
def update_product(request, pk):
    if request.method == 'POST':
        product = Product.objects.get(id=pk)
        product.product_name = request.POST.get('product_name')
        product.product_stock = request.POST.get('product_stock')
        product.product_price = request.POST.get('product_price')
        product.product_description = request.POST.get('product_description')
        product.product_specification = request.POST.get('product_specification')
        if request.FILES.get('product_image'):
            product.product_image = request.FILES['product_image']
        product.save()
        messages.success(request,'Product updated')
        return redirect('manage_products')
    
    else:
        return render(request, 'admin/editproducts.html')

@login_required
def ClientDetails(request):
    customer = UserMember.objects.all()
    cart_items_count = Cart.objects.filter(user_cart=request.user).count()
    return render(request,'admin/clientdetails.html',{'customer':customer,'cart_items_count': cart_items_count})


@login_required 
def delete_customer(request,pk):
    customer = UserMember.objects.get(id=pk)
    customuser = CustomUser.objects.get(username=customer.user_member.username)
    customer.delete()
    customuser.delete()
    return redirect('ClientDetails')



@login_required
def DeliveryDetails(request):
    delivery = UserMember.objects.all()
    return render(request,'admin/deliverydetails.html',{'delivery':delivery})



@login_required
def delete_delivery(request,pk):
    delivery = UserMember.objects.get(id=pk)
    customuser = CustomUser.objects.get(username=delivery.user_member.username)
    delivery.delete()
    customuser.delete()
    return redirect('DeliveryDetails')

@login_required
def approve_disapprove_users(request):
    pending_users = CustomUser.objects.filter(is_active=False)
    approved_users = CustomUser.objects.filter(is_active=True)
    pending_count = pending_users.count()

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = get_object_or_404(CustomUser, id=user_id)

        if action == 'approve': 
            password = str(random.randint(100000, 999999))
            user.set_password(password)
            user.is_active = True
            user.save()

            subject = 'Registration Approved'
            message = f"Hello {user.username}, your username is {user.username} and your password is {password}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

            messages.success(request, 'Approved')
            return redirect('approve_disapprove_users')

        elif action == 'disapprove':
            user.delete()
            return redirect('approve_disapprove_users')

    return render(request, 'admin/approve.html', {'pending_users': pending_users, 'pending_count': pending_count, 'approved_users': approved_users})



def all_products(request):
    if request.user.is_authenticated:
        customer = UserMember.objects.get(user_member=request.user)
        products = Product.objects.all()
        cart_items_count = Cart.objects.filter(user_cart=request.user).count()
        return render(request,'customer/allproducts.html',{'products':products,'customer':customer,'cart_items_count': cart_items_count})



def add_to_cart(request, pk):
    pro = Product.objects.get(id=pk)
    cart_item, created = Cart.objects.get_or_create(user_cart=request.user,user_product=pro)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, 'Product Added To Cart')
    return redirect('cart_view')
    
    

def cart_remove(request, pk):   
    if request.user.is_authenticated:
        pro = Product.objects.get(id=pk)
        cart_item = Cart.objects.filter(user_cart=request.user, user_product=pro)
        if cart_item:
            cart_item.delete()
        return redirect('cart_view')    



def cart_view(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user_cart=request.user).select_related('user_product')
        total_price = sum(item.total_price() for item in cart_items)
        cart_items_count = Cart.objects.filter(user_cart=request.user).count()
        return render(request, 'customer/cart.html', {'cart': cart_items, 'total_price': total_price,'cart_items_count': cart_items_count})



def decrement(request,pk):
    if request.user.is_authenticated:
        cart_item = Cart.objects.get(user_product_id =pk, user_cart=request.user)
        cart_item.quantity -= 1
        cart_item.save()
        return redirect('cart_view')


def increment(request,pk):  
    if request.user.is_authenticated:
        cart_item = Cart.objects.get(user_product_id =pk, user_cart=request.user)
        cart_item.quantity += 1
        cart_item.save()
        return redirect('cart_view')
    



def generate_random_tracking_id(length=8):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))





def checkout_page(request):
    cart_items = Cart.objects.filter(user_cart=request.user).select_related('user_product')
    cart_items_count = Cart.objects.filter(user_cart=request.user).count()
    total_price = sum(item.total_price() for item in cart_items)
    shipping_methods = ShippingMethod.objects.all()
    return render(request, 'customer/checkout.html', {'cart_items': cart_items,'total_price': total_price,'shipping_methods': shipping_methods,'cart_items_count': cart_items_count})



def checkout(request):
    shipping_methods = ShippingMethod.objects.all()
    cart_items = Cart.objects.filter(user_cart=request.user).select_related('user_product')

    if request.method == 'POST':
        # Get data from the request
        shipping_method_id = request.POST['shipping_method']

        with transaction.atomic():
            # Create an Order for each item in the cart
            for item in cart_items:
                order = Order.objects.create(
                    user=request.user,
                    product=item.user_product,
                    quantity=item.quantity,
                    price=item.user_product.product_price,
                    shipping_method_id=shipping_method_id,
                    tracking_status='Pending', 
                )

                # Generate a random tracking id
                order.tracking_id = generate_random_tracking_id()
                order.save()

                # Send an email with tracking id to the customer
                send_tracking_email(request.user.email, order.tracking_id)

            # Clear the cart after placing the order
            Cart.objects.filter(user_cart=request.user).delete()

            return render(request, 'customer/order_placed.html', {'tracking_id': order.tracking_id})

    return render(request, 'customer/checkout.html', {'shipping_methods': shipping_methods, 'cart_items': cart_items})





def send_tracking_email(recipient, tracking_id):
    subject = 'Order Placed Successfully'
    message = f'Your order has been placed successfully. Your tracking ID is: {tracking_id}.'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient])



@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def assign_orders(request):
    # Get orders that are not assigned and not delivered
    
    orders_to_assign = Order.objects.filter(assigned_orders__isnull=True)

    if request.method == 'POST':
        # Handle form submission
        for order_id, delivery_guy_id in request.POST.items():
            if order_id.startswith('order_') and delivery_guy_id.isdigit():
                order_id = order_id.split('_')[1]
                order = Order.objects.get(pk=order_id)
                delivery_guy = CustomUser.objects.get(pk=delivery_guy_id)

                # Create AssignedOrder instance
                assigned_order = AssignedOrder.objects.create(order=order, delivery_guy=delivery_guy)

                # Update Order with the AssignedOrder instance
                order.assignedorder = assigned_order
                order.save()

        return redirect('assign_orders') 

    delivery_guys = CustomUser.objects.filter(user_type='2')

    return render(request, 'admin/assign_orders.html', {'orders_to_assign': orders_to_assign, 'delivery_guys': delivery_guys})




@user_passes_test(lambda u: u.user_type == '2', login_url='/login/')  
def delivery_guy_orders(request):
    delivery_guy = request.user
    assigned_orders = AssignedOrder.objects.filter(delivery_guy=delivery_guy)
    return render(request, 'delivery/delivery_guy_orders.html', {'assigned_orders': assigned_orders})


from datetime import datetime


@login_required
def update_order(request, assigned_order_id):
    assigned_order = get_object_or_404(AssignedOrder, id=assigned_order_id)

    if request.method == 'POST':
        # Handle form submission
        dispatched_location = request.POST.get('dispatched_location')
        transit_location = request.POST.get('transit_location')
        estimated_delivery_date = request.POST.get('estimated_delivery_date')
        status = request.POST.get('status')

        # Update AssignedOrder fields
        assigned_order.dispatched_location = dispatched_location
        assigned_order.transit_location = transit_location
        assigned_order.estimated_delivery_date = estimated_delivery_date
        assigned_order.status = status

        if status == 'Delivered':
            assigned_order.delivered_date = datetime.now()

        assigned_order.save()

        return redirect('delivery_guy_orders')

    # Handle GET request, display existing values
    return render(request, 'delivery/update_order.html', {'assigned_order': assigned_order})



from django.http import Http404

@login_required
def track_order(request):
    cart_items_count = Cart.objects.filter(user_cart=request.user).count()
    if request.method == 'POST':
        tracking_id = request.POST.get('tracking_id')
        


        try:
            order = get_object_or_404(Order, tracking_id=tracking_id)
            assigned_order = order.assigned_orders.first()  # Use the correct related_name

            pending_progress = 0
            dispatched_progress = 0
            transit_progress = 0
            delivered_progress = 0

            if assigned_order:
                if assigned_order.status == 'Pending':
                    pending_progress = 25
                elif assigned_order.status == 'Dispatched':
                    pending_progress = 25
                    dispatched_progress = 25
                elif assigned_order.status == 'In Transit':
                    pending_progress = 25
                    dispatched_progress = 25
                    transit_progress = 25
                elif assigned_order.status == 'Delivered':
                    pending_progress = 25
                    dispatched_progress = 25
                    transit_progress = 25
                    delivered_progress = 25

            return render(request, 'customer/track_order_result.html', {
                'order': order,
                'assigned_order': assigned_order,
                'pending_progress': pending_progress,
                'dispatched_progress': dispatched_progress,
                'transit_progress': transit_progress,
                'delivered_progress': delivered_progress,
                'cart_items_count': cart_items_count
            })
        except Http404:
            messages.error(request,'Invalid Tracking ID. Please check and try again.')
            return render(request, 'customer/track_order.html')

    return render(request, 'customer/track_order.html',{'cart_items_count': cart_items_count})


@login_required
def get_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    assigned_order = order.assigned_orders.last()

    # Define checkpoint colors and values based on the order status
    checkpoints = {
        'Pending': {'color': '#CCCCCC', 'progress': 0, 'label': 'Pending', 'location': ''},
        'Dispatched': {'color': '#FFD700', 'progress': 25, 'label': 'Dispatched', 'location': assigned_order.dispatched_location if assigned_order else ''},
        'In Transit': {'color': '#87CEEB', 'progress': 50, 'label': 'In Transit', 'location': assigned_order.transit_location if assigned_order else ''},
        'Delivered': {'color': '#32CD32', 'progress': 100, 'label': 'Delivered', 'location': ''},
    }

    # Get the current status and return corresponding colors and values
    status = assigned_order.status if assigned_order else 'Pending'
    status_info = checkpoints.get(status, checkpoints['Pending'])

    # If the order is not pending, set pending progress to 0
    pending_progress = 0 if status != 'Pending' else status_info['progress']

    # If the order is pending, adjust pending progress based on other bars
    if status == 'Pending':
        dispatched_progress = checkpoints['Dispatched']['progress'] if assigned_order else 0
        transit_progress = checkpoints['In Transit']['progress'] if assigned_order else 0
        delivered_progress = checkpoints['Delivered']['progress'] if assigned_order else 0

        # Ensure each bar has equal width
        total_progress = dispatched_progress + transit_progress + delivered_progress
        progress_factor = 25  # Equal width for each bar
        pending_progress = min(pending_progress, total_progress)
        dispatched_progress = min(dispatched_progress, progress_factor)
        transit_progress = min(transit_progress, progress_factor)
        delivered_progress = min(delivered_progress, progress_factor)

    status_data = {
        'checkpoints': [
            {'color': checkpoints['Pending']['color'], 'progress': pending_progress, 'label': checkpoints['Pending']['label'], 'location': checkpoints['Pending']['location']},
            {'color': checkpoints['Dispatched']['color'], 'progress': dispatched_progress, 'label': checkpoints['Dispatched']['label'], 'location': checkpoints['Dispatched']['location']},
            {'color': checkpoints['In Transit']['color'], 'progress': transit_progress, 'label': checkpoints['In Transit']['label'], 'location': checkpoints['In Transit']['location']},
            {'color': checkpoints['Delivered']['color'], 'progress': delivered_progress, 'label': checkpoints['Delivered']['label'], 'location': checkpoints['Delivered']['location']},
        ],
    }

    return JsonResponse(status_data)


@login_required
def update_delivery_status(request, assigned_order_id):
    assigned_order = get_object_or_404(AssignedOrder, id=assigned_order_id)

    # Check if the assigned order is delivered
    if assigned_order.status == 'Delivered':
        # Update the Order model's tracking_status
        assigned_order.order.tracking_status = 'Delivered'
        assigned_order.order.save()

        return JsonResponse({'status': 'success', 'tracking_status': 'Delivered'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Product is not delivered yet.'})
    


@login_required
def order_details(request):
    # Retrieve all orders with related information
    orders = Order.objects.select_related('user', 'product').all()

    context = {
        'orders': orders,
    }

    return render(request, 'admin/order_details.html', context)




def all_orders(request):
    orders = Order.objects.all()
    order_data = []

    for order in orders:
        assigned_order = order.assigned_orders.last()
        checkpoints = get_checkpoint_data(assigned_order)
        order_data.append({'order': order, 'assigned_order': assigned_order, 'checkpoints': checkpoints})

    context = {'orders_data': order_data}
    return render(request, 'admin/all_orders.html', context)




def get_checkpoint_data(assigned_order):
    checkpoints = {
        'Pending': {'color': '#CCCCCC', 'progress': 0, 'label': 'Pending', 'location': ''},
        'Dispatched': {'color': '#FFD700', 'progress': 25, 'label': 'Dispatched', 'location': assigned_order.dispatched_location if assigned_order else ''},
        'In Transit': {'color': '#87CEEB', 'progress': 50, 'label': 'In Transit', 'location': assigned_order.transit_location if assigned_order else ''},
        'Delivered': {'color': '#32CD32', 'progress': 100, 'label': 'Delivered', 'location': assigned_order.delivered_date.strftime('%Y-%m-%d %H:%M:%S') if assigned_order and assigned_order.delivered_date else ''},
    }

    dispatched_progress = transit_progress = delivered_progress = 0

    if assigned_order:
        dispatched_progress = checkpoints['Dispatched']['progress']
        transit_progress = checkpoints['In Transit']['progress']
        delivered_progress = checkpoints['Delivered']['progress']

    status = assigned_order.status if assigned_order else 'Pending'
    status_info = checkpoints.get(status, checkpoints['Pending'])

    pending_progress = 0 if status != 'Pending' else status_info['progress']

    if status == 'Pending':
        total_progress = dispatched_progress + transit_progress + delivered_progress
        progress_factor = 25
        pending_progress = min(pending_progress, total_progress)
        dispatched_progress = min(dispatched_progress, progress_factor)
        transit_progress = min(transit_progress, progress_factor)
        delivered_progress = min(delivered_progress, progress_factor)

    return [
        {'color': checkpoints['Pending']['color'], 'progress': pending_progress, 'label': checkpoints['Pending']['label'], 'location': checkpoints['Pending']['location']},
        {'color': checkpoints['Dispatched']['color'], 'progress': dispatched_progress, 'label': checkpoints['Dispatched']['label'], 'location': checkpoints['Dispatched']['location']},
        {'color': checkpoints['In Transit']['color'], 'progress': transit_progress, 'label': checkpoints['In Transit']['label'], 'location': checkpoints['In Transit']['location']},
        {'color': checkpoints['Delivered']['color'], 'progress': delivered_progress, 'label': checkpoints['Delivered']['label'], 'location': checkpoints['Delivered']['location']},
    ]


@login_required
def customer_password(request):
    cart_items_count = Cart.objects.filter(user_cart=request.user).count()
    return render(request, 'customer/reset_passwords.html',{'cart_items_count': cart_items_count})


@login_required
def reset_password_customer(request):
    if request.method == 'POST':
        current_password = request.POST['current']
        new_password = request.POST['passwd']
        confirm_password = request.POST['cpasswd']

        current_user = request.user
        user = CustomUser.objects.get(username=current_user)

        if not check_password(current_password, user.password):
            messages.error(request, 'Current password is incorrect!')
            return redirect('reset_password_customer')

        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters long!')
            return redirect('reset_password_customer')

        if not re.search(r'\d', new_password):
            messages.error(request, 'Password must contain at least one number!')
            return redirect('reset_password_customer')

        if not re.search(r'[A-Z]', new_password):
            messages.error(request, 'Password must contain at least one capital letter!')
            return redirect('reset_password_customer')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            messages.error(request, 'Password must contain at least one special character!')
            return redirect('reset_password_customer')

        if new_password == confirm_password:
            user.password = make_password(new_password)
            user.save()
            messages.success(request, 'Password reset successfully!')
            return redirect('loginpage')
        else:
            messages.error(request, 'Passwords do not match!')
    return render(request, 'customer/reset_passwords.html')



@login_required
def delivery_password(request):
    return render(request, 'delivery/reset_password.html')


@login_required
def reset_password_delivery(request):
    if request.method == 'POST':
        current_password = request.POST['current']
        new_password = request.POST['passwd']
        confirm_password = request.POST['cpasswd']

        current_user = request.user
        user = CustomUser.objects.get(username=current_user)

        if not check_password(current_password, user.password):
            messages.error(request, 'Current password is incorrect!')
            return redirect('reset_password_customer')

        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters long!')
            return redirect('reset_password_customer')

        if not re.search(r'\d', new_password):
            messages.error(request, 'Password must contain at least one number!')
            return redirect('reset_password_customer')

        if not re.search(r'[A-Z]', new_password):
            messages.error(request, 'Password must contain at least one capital letter!')
            return redirect('reset_password_customer')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            messages.error(request, 'Password must contain at least one special character!')
            return redirect('reset_password_customer')

        if new_password == confirm_password:
            user.password = make_password(new_password)
            user.save()
            messages.success(request, 'Password reset successfully!')
            return redirect('loginpage')
        else:
            messages.error(request, 'Passwords do not match!')
    return render(request, 'delivery/reset_password.html')



@login_required
def edit_profile(request):
    
    user = request.user
    user_member, created = UserMember.objects.get_or_create(user_member=user)
    cart_items_count = Cart.objects.filter(user_cart=request.user).count()

    if request.method == 'POST':
        # Handle form submission for editing UserMember information
        user_member.number = request.POST.get('number')
        user_member.address = request.POST.get('address')
        user_member.pancard = request.POST.get('pancard')

        # Handle profile image upload if provided
        if 'image' in request.FILES:
            user_member.image = request.FILES['image']

        
        user.first_name = request.POST.get('name')
        new_email = request.POST.get('email')
        user.email = new_email
        user.username = new_email

        user.save()
        user_member.save()

    context = {
        'user': user,
        'user_member': user_member,
        'cart_items_count': cart_items_count
    }

    return render(request, 'customer/customer_profile.html', context)



@login_required
def edit_profile_delivery(request):
    user = request.user
    user_member, created = UserMember.objects.get_or_create(user_member=user)

    if request.method == 'POST':
        # Handle form submission for editing UserMember information
        user_member.number = request.POST.get('number')
        user_member.address = request.POST.get('address')
        user_member.pancard = request.POST.get('pancard')

        # Handle profile image upload if provided
        if 'image' in request.FILES:
            user_member.image = request.FILES['image']

        # Handle additional fields like name
        user.first_name = request.POST.get('name')
        new_email = request.POST.get('email')
        user.email = new_email
        user.username = new_email

        user.save()
        user_member.save()

    context = {
        'user': user,
        'user_member': user_member,
    }

    return render(request, 'delivery/delivery_profile.html', context)
