from django.shortcuts import render,get_object_or_404
from sellerapp.models import User
from django.http import HttpResponseRedirect
from .models import *
from customerapp.models import product, customer
from django.contrib import messages  

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
            if request.method == "POST":

                address_id = request.POST.get("address")

                if not address_id:
                    messages.error(request, "Please select a delivery address.")
                    return HttpResponseRedirect("/checkout/")

                request.session["address_id"] = address_id

                return HttpResponseRedirect("/payment/")
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

    if "email" not in request.session:
        return HttpResponseRedirect("/seller/login/")

    uid = User.objects.get(email=request.session["email"])

    if uid.role != "customer":
        return HttpResponseRedirect("/seller/login/")

    cid = customer.objects.get(user_id=uid)

    # Selected Address
    address_id = request.session.get("address_id")

    if not address_id:
        messages.error(request, "Please select a delivery address.")
        return HttpResponseRedirect("/checkout/")

    address = get_object_or_404(Address, id=address_id, customer=cid)

    # Cart
    cart_obj, created = cart.objects.get_or_create(customer=cid)
    item = cartitem.objects.filter(cart=cart_obj)

    total_amount = 0

    for i in item:
        total_amount += i.product.product_price * i.qty

    discount = 65 if total_amount >= 100 else 0
    net_amount = total_amount - discount

    context = {
        "address": address,
        "item": item,
        "total_amount": total_amount,
        "discount": discount,
        "net_amount": net_amount,
    }

    return render(request, "customerapp/payment.html", context)

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

    if "email" not in request.session:
        return HttpResponseRedirect("/seller/login/")

    uid = User.objects.get(email=request.session["email"])

    if uid.role != "customer":
        return HttpResponseRedirect("/seller/login/")

    cid = customer.objects.get(user_id=uid)

    if request.method == "POST":

        fullname = request.POST["fullname"]
        mobile = request.POST["mobile"]
        house_no = request.POST["house_no"]
        area = request.POST["area"]
        landmark = request.POST["landmark"]
        city = request.POST["city"]
        state = request.POST["state"]
        pincode = request.POST["pincode"]
        address_type = request.POST["address_type"]

        is_default = request.POST.get("is_default")

        if is_default:
            Address.objects.filter(customer=cid).update(
                is_default=False
            )
        if Address.objects.filter(customer=cid).count() == 0:
            is_default = True
        else:
            is_default = bool(is_default)

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
            address_type=address_type,
            is_default=is_default
        )
        messages.success(request,"New Address Added Successfully.")
        return HttpResponseRedirect("/checkout/")

    addresses = Address.objects.filter(customer=cid)

    context = {
        "addresses": addresses,
        "cid": cid,
        "uid": uid,
    }

    return render(
        request,
        "customerapp/add_address.html",
        context
    )

def delete_address(request, pk):

    if "email" not in request.session:
        return HttpResponseRedirect("/seller/login/")

    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)

    address = get_object_or_404(
        Address,
        id=pk,
        customer=cid
    )

    address.delete()
    messages.success(request,"Address Deleted Successfully.")
    return HttpResponseRedirect("/checkout/")

def edit_address(request, pk):

    if "email" not in request.session:
        return HttpResponseRedirect("/seller/login/")

    uid = User.objects.get(email=request.session['email'])
    cid = customer.objects.get(user_id=uid)

    address = get_object_or_404(Address, id=pk, customer=cid)

    if request.method == "POST":

        address.fullname = request.POST['fullname']
        address.mobile = request.POST['mobile']
        address.house_no = request.POST['house_no']
        address.area = request.POST['area']
        address.landmark = request.POST['landmark']
        address.city = request.POST['city']
        address.state = request.POST['state']
        address.pincode = request.POST['pincode']
        address.address_type = request.POST['address_type']

        is_default = request.POST.get("is_default")

        if is_default:

            Address.objects.filter(customer=cid).update(
                is_default=False
            )

            address.is_default = True

        else:

            address.is_default = False

        address.save()
        messages.success(request,"Address Updated Successfully.")
        return HttpResponseRedirect("/checkout/")

    return render(request, "customerapp/edit_address.html", {
        "a": address
    })

def place_order(request):

    if "email" not in request.session:
        return HttpResponseRedirect("/seller/login/")

    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)

    if request.method == "POST":

        payment_method = request.POST.get("payment")

        address_id = request.session.get("address_id")

        if not address_id:
            messages.error(request, "Please select address.")
            return HttpResponseRedirect("/checkout/")

        address = get_object_or_404(Address, id=address_id)

        cart_obj = cart.objects.get(customer=cid)
        items = cartitem.objects.filter(cart=cart_obj)

        total = 0

        for i in items:
            total += i.product.product_price * i.qty

        discount = 65 if total >= 100 else 0

        final = total - discount

        order = Order.objects.create(
            customer=cid,
            address=address,
            payment_method=payment_method,
            total_amount=total,
            discount=discount,
            final_amount=final
        )

        for i in items:

            OrderItem.objects.create(
                order=order,
                product=i.product,
                quantity=i.qty,
                price=i.product.product_price,
                subtotal=i.product.product_price * i.qty
            )

        items.delete()

        if "address_id" in request.session:
            del request.session["address_id"]

        messages.success(request, "Order Placed Successfully.")

        return HttpResponseRedirect("/order_success/")

def order_success(request):

    if "email" not in request.session:
        return HttpResponseRedirect("/seller/login/")

    return render(request, "customerapp/order_success.html")

def orders(request):
    return render(request, "customerapp/orders.html")

def place_order(request):

    if request.method == "POST":

        if "email" not in request.session:
            return HttpResponseRedirect("/seller/login/")

        uid = User.objects.get(email=request.session["email"])
        cid = customer.objects.get(user_id=uid)

        address_id = request.session.get("address_id")

        if not address_id:
            messages.error(request,"Please select address.")
            return HttpResponseRedirect("/checkout/")

        address = Address.objects.get(
            id=address_id,
            customer=cid
        )

        cart_obj = cart.objects.get(customer=cid)
        items = cartitem.objects.filter(cart=cart_obj)

        total = 0

        for i in items:
            total += i.product.product_price * i.qty

        discount = 65 if total >= 100 else 0
        final = total - discount

        payment = request.POST.get("payment_method")

        if payment == "upi":
            payment = "UPI"

        elif payment == "card":
            payment = "CARD"

        else:
            payment = "COD"

        order = Order.objects.create(

            customer=cid,
            address=address,

            payment_method=payment,

            total_amount=total,
            discount=discount,
            final_amount=final,

            status="Pending"

        )

        for i in items:

            OrderItem.objects.create(

                order=order,

                product=i.product,

                quantity=i.qty,

                price=i.product.product_price,

                subtotal=i.product.product_price * i.qty

            )

        items.delete()

        if "address_id" in request.session:
            del request.session["address_id"]

        return HttpResponseRedirect("/order_success/")

    return HttpResponseRedirect("/payment/")