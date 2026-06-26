from django.shortcuts import render,get_object_or_404
from sellerapp.models import User
from django.http import HttpResponseRedirect
from .models import *
from customerapp.models import product, customer  

def customer_dashboard(request):

    if "email" in request.session:

        uid = User.objects.get(email=request.session['email'])
        cid = customer.objects.get(user_id=uid)
        pid = product.objects.all()

        context = {
            "uid": uid,
            "cid": cid,
            "pid": pid,
        }

        return render(request,"customerapp/customer_dashboard.html",context)
    
    return HttpResponseRedirect("/seller/login")
def logout(request):
    request.session.flush()
    return HttpResponseRedirect("/seller/login/")

def edit_profile(request):
    if "email" in request.session:
        uid = User.objects.get(email = request.session['email'])

        if uid.role == "customer":
            cid = customer.objects.get(user_id=uid)

            cid.firstname = request.POST['firstname']
            cid.lastname = request.POST['lastname']
            cid.contectno = request.POST['contectno']
            if "pic" in request.FILES:
                cid.pic = request.FILES['pic']
            
            cid.save()

            context = {
                "uid": uid,
                "cid": cid,
                "pid": product.objects.all(),
            }

            return render(request, "customerapp/customer_dashboard.html", context)

def show_product(request):

    if "email" in request.session:

        uid = User.objects.get(email=request.session['email'])
        cid = customer.objects.get(user_id=uid)

        products = product.objects.all()

        return render(request, "customerapp/index.html", {
            "cid": cid,
            "products": products
        })
    
    else:
        return HttpResponseRedirect("/seller/login")
    
def add_to_cart(request,pk):
    uid = User.objects.get(email = request.session['email'])
    if uid.role == "customer":
        cid = customer.objects.get(user_id = uid)
        products = get_object_or_404(product, id=pk)

        Cart_obj,is_created = cart.objects.get_or_create(customer = cid)

        print("------> Cart customer ::",Cart_obj)
        print("------> Cart customer status ::",is_created) 

        cartItemData,is_created = cartitem.objects.get_or_create(
            cart=Cart_obj,
            product=products,
            defaults={'qty':1}
        )

        if not is_created:
            cartItemData.qty += 1
            cartItemData.save()

        return HttpResponseRedirect("/view_cart/")

    
def view_cart(request):
    if "email" in request.session:
        uid = User.objects.get(email=request.session['email'])

        if uid.role == "customer":
            cid = customer.objects.get(user_id=uid)
            Cart_obj, created = cart.objects.get_or_create(customer=cid)
            item = cartitem.objects.filter(cart=Cart_obj)

            total_amount = 0

            for i in item:
                total_amount += i.product.product_price * i.qty

            # Coupon Logic
            if total_amount >= 100:
                discount = 65
            else:
                discount = 0

            net_amount = total_amount - discount

            if total_amount < 100:
                remaining_amount = 100 - total_amount
            else:
                remaining_amount = 0

            context = {
                'item': item,
                'total_amount': total_amount,
                'discount': discount,
                'net_amount': net_amount,
                'remaining_amount': remaining_amount,
            }
            return render(request, "customerapp/cart.html", context)

def checkout(request):
    if "email" in request.session:
        uid = User.objects.get(email = request.session['email'])
        if uid.role == "customer":
            cid = customer.objects.get(user_id = uid)
            Cart_obj, created = cart.objects.get_or_create(customer = cid)
            item = cartitem.objects.filter(cart=Cart_obj)
            addresses = Address.objects.filter(customer=cid)
            total_amount = 0
            for i in item:
                total_amount += i.product.product_price * i.qty

            context = {
                'item' : item,
                'total_amount' : total_amount,
                'net_amount' : total_amount - 65 ,
                "addresses": addresses,
            }
        return render(request,"customerapp/check_out.html",context)

def payment(request):
    return render(request,"customerapp/payment.html")

def increase_qty(request,pk):
    if "email" in request.session:
        uid = User.objects.get(email = request.session['email'])
        if uid.role == "customer":
            cid = customer.objects.get(user_id = uid)
            cart_obj, created = cart.objects.get_or_create(customer = cid)
            cart_item = get_object_or_404(cartitem, id=pk, cart=cart_obj)

            cart_item.qty += 1
            cart_item.save()
    
    return HttpResponseRedirect("/view_cart/")

def decrease_qty(request, pk):
    if "email" in request.session:
        uid = User.objects.get(email=request.session['email'])
        if uid.role == "customer":
            cid = customer.objects.get(user_id=uid)
            Cart_obj, created = cart.objects.get_or_create(customer=cid)
            cart_item = get_object_or_404(cartitem, id=pk, cart=Cart_obj)

            if cart_item.qty > 1:
                cart_item.qty -= 1
                cart_item.save()
            else:
                cart_item.delete()

    return HttpResponseRedirect("/view_cart/")

def add_address(request):
    if "email" in request.session:
        return HttpResponseRedirect("/seller/login/")
    
    uid = User.objects.get(email=request.session['email'])
    
    if uid.role == "customer":
        cid = customer.objects.get(user_id=uid)
        if request.method == "POST":
            fullname = request.POST['fullname']
            mobile = request.POST['mobile']
            house_no = request.POST['house_no']
            area = request.POST['area']
            landmark = request.POST['landmark']
            city = request.POST['city']
            state = request.POST['state']
            pincode = request.POST['pincode']
            address_type = request.POST['address_type']

            Address.objects.create(
                customer=cid,
                fullname=fullname,
                mobile=mobile,
                house_no=house_no,
                area=area,
                landmark=landmark,
                city=city,
                state=state,
                pincode=pincode,
                address_type=address_type
            )
        addresses = Address.objects.filter(customer=cid)

        context = {
            'addresses': addresses,
        }
        return render(request, "customerapp/address.html", context)