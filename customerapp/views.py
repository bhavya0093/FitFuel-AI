from django.shortcuts import render,get_object_or_404,redirect
from sellerapp.models import User
from django.http import HttpResponseRedirect 
from .models import *
from customerapp.models import product, customer
from django.contrib import messages
import uuid
from .models import UserHealthProfile
import math
from django.db.models import Q
from django.urls import reverse


def customer_dashboard(request):

    if "email" in request.session:

        uid = User.objects.get(email=request.session["email"])
        cid = customer.objects.get(user_id=uid)
        # ==========================
        # Cart Summary
        # ==========================

        cart_obj = cart.objects.filter(customer=cid).first()

        cart_items = []

        cart_count = 0

        cart_protein = 0

        cart_calories = 0

        if cart_obj:

            cart_items = cartitem.objects.filter(cart=cart_obj)

            cart_count = cart_items.count()

            for item in cart_items:

                cart_protein += item.product.protein * item.qty

                cart_calories += item.product.calories * item.qty
        try:
            health = UserHealthProfile.objects.get(customer=cid)
        except UserHealthProfile.DoesNotExist:
            health = None
        categories = Category.objects.all()

        selected_category = request.GET.get("category")

        profile = UserHealthProfile.objects.filter(customer=cid).first()

        pid = product.objects.all()

        selected_category_obj = None
        category_sections = []

        if selected_category:
            pid = pid.filter(product_category_id=selected_category)
            try:
                selected_category_obj = Category.objects.get(id=selected_category)
            except Category.DoesNotExist:
                pass
        else:
            for cat in categories:
                cat_products = product.objects.filter(product_category=cat)[:6]
                if cat_products.exists():
                    category_sections.append({
                        "category": cat,
                        "products": cat_products
                    })

            ai_products = []

        try:
            hp = cid.health_profile

            ai_products = product.objects.filter(
                diet_type=hp.diet_type,
                goal_type=hp.goal
            ).order_by(
                "-protein",
                "product_price"
            )[:4]

        except UserHealthProfile.DoesNotExist:
                hp = None

                ai_products = product.objects.filter(
                    is_ai_recommended=True
                )[:4]
        recommended_product = ai_products[0] if ai_products else None
        for p in ai_products:

            score = 50

            if hp:

                if hp.goal == p.goal_type:
                    score += 20

                if hp.diet_type == p.diet_type:
                    score += 15

            if p.protein >= 25:
                score += 10

            elif p.protein >= 15:
                score += 5

            if p.rating >= 4.5:
                score += 5

            if score > 99:
                score = 99

            p.ai_match = score

            reasons = []

            if hp:

                if hp.goal == p.goal_type:
                    reasons.append(f"Perfect for {hp.goal}")

                if hp.diet_type == p.diet_type:
                    reasons.append(f"{hp.diet_type} Friendly")

                if p.protein >= 25:
                    reasons.append(f"High Protein ({p.protein}g)")

                if p.sugar <= 5:
                    reasons.append("Low Sugar")

                if p.fiber >= 5:
                    reasons.append("High Fiber")

            p.ai_reasons = reasons[:4]

        active_page = request.GET.get("active_page") or "home"

        context = {
            "uid": uid,
            "cid": cid,
            "pid": pid,
            "categories": categories,
            "selected_category": selected_category,
            "selected_category_obj": selected_category_obj,
            "category_sections": category_sections,
            "orders": orders,
            "active_page": active_page,
            "health": health,
            "health_profile": profile,
            "ai_products": ai_products,
            "recommended_product": recommended_product,
            "cart_count": cart_count,
            "cart_protein": round(cart_protein,1),
            "cart_calories": int(cart_calories),
        }

        return render(request, "customerapp/customer_dashboard.html", context)

    return HttpResponseRedirect("/seller/login/")

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
                "active_page": "profile",
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

                discount = 65 if total_amount >= 100 else 0
                net_amount = total_amount - discount
            
            context = {
                'item' : item,
                'total_amount' : total_amount,
                'discount': discount,
                'net_amount': net_amount,
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

    if not item.exists():
        messages.error(request,"Your cart is empty.")
        return redirect("view_cart")

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

    next_url = request.GET.get("next") or request.POST.get("next") or "/checkout/"

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
        return HttpResponseRedirect(next_url)

    addresses = Address.objects.filter(customer=cid)

    context = {
        "addresses": addresses,
        "cid": cid,
        "uid": uid,
        "next_url": next_url,
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

    next_url = request.GET.get("next") or "/checkout/"

    address.delete()
    messages.success(request,"Address Deleted Successfully.")
    return HttpResponseRedirect(next_url)

def edit_address(request, pk):

    if "email" not in request.session:
        return HttpResponseRedirect("/seller/login/")

    uid = User.objects.get(email=request.session['email'])
    cid = customer.objects.get(user_id=uid)

    address = get_object_or_404(Address, id=pk, customer=cid)

    next_url = request.GET.get("next") or request.POST.get("next") or "/checkout/"

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
        return HttpResponseRedirect(next_url)

    return render(request, "customerapp/edit_address.html", {
        "a": address,
        "next_url": next_url,
    })

def place_order(request):

    if "email" not in request.session:
        return HttpResponseRedirect("/seller/login/")

    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)

    if not cartitem.objects.filter(cart__customer=cid).exists():

        messages.error(request,"Your cart is empty.")

        return redirect("view_cart")

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
        Payment.objects.create(
            order=order,
            payment_id="PAY" + uuid.uuid4().hex[:10].upper(),
            transaction_id=uuid.uuid4().hex[:16].upper(),
            amount=final,
            method=payment_method,
            status="Pending" if payment_method == "COD" else "Paid"
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

def orders(request):

    if "email" not in request.session:
        return HttpResponseRedirect("/seller/login/")

    uid = User.objects.get(email=request.session["email"])

    if uid.role != "customer":
        return HttpResponseRedirect("/seller/login/")

    cid = customer.objects.get(user_id=uid)

    orders = Order.objects.filter(
        customer=cid
    ).order_by("-order_date")[:5]

    print("Orders =>", orders)
    print("Count =>", orders.count())

    context = {
        "orders": orders
    }

    return render(
        request,
        "customerapp/orders.html",
        context
    )

def order_success(request):

    if "email" not in request.session:
        return HttpResponseRedirect("/seller/login/")

    return render(
        request,
        "customerapp/order_success.html"
    )   

def order_details(request, pk):

    if "email" not in request.session:
        return HttpResponseRedirect("/seller/login/")

    uid = User.objects.get(email=request.session["email"])

    if uid.role != "customer":
        return HttpResponseRedirect("/seller/login/")

    cid = customer.objects.get(user_id=uid)

    order = get_object_or_404(
        Order,
        id=pk,
        customer=cid
    )

    context = {
        "order": order
    }

    return render(
        request,
        "customerapp/order_details.html",
        context
    )

def cancel_order(request, pk):

    if "email" not in request.session:
        return HttpResponseRedirect("/seller/login/")

    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)

    order = get_object_or_404(
        Order,
        id=pk,
        customer=cid
    )

    if order.status != "Pending":
        messages.error(request, "This order cannot be cancelled.")
        return redirect("orders")

    order.status = "Cancelled"
    order.save()

    messages.success(request, "Order Cancelled Successfully.")

    return redirect("orders")



def profile(request):
    if "email" not in request.session:
        return redirect("login")
    
    # Redirect to the main dashboard with the profile page activated
    return redirect(reverse("customer_dashboard") + "?active_page=profile")

def save_health_profile(request):

    if "email" not in request.session:
        return redirect("login")

    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)

    if request.method == "POST":

        age = int(request.POST["age"])
        gender = request.POST["gender"]

        height = float(request.POST["height"])
        weight = float(request.POST["weight"])

        activity = request.POST["activity_level"]
        goal = request.POST["goal"]
        diet = request.POST["diet_type"]

        # ==========================
        # BMI
        # ==========================

        bmi = round(weight / ((height / 100) ** 2), 2)

        # ==========================
        # BMR
        # ==========================

        if gender == "Male":

            bmr = (
                10 * weight +
                6.25 * height -
                5 * age +
                5
            )

        else:

            bmr = (
                10 * weight +
                6.25 * height -
                5 * age -
                161
            )

        # ==========================
        # TDEE
        # ==========================

        activity_factor = {

            "Sedentary":1.2,
            "Light":1.375,
            "Moderate":1.55,
            "Active":1.725,
            "Very Active":1.9,

        }

        tdee = bmr * activity_factor.get(activity,1.2)

        # ==========================
        # Calories
        # ==========================

        if goal == "Weight Loss":

            calories = int(tdee - 500)

        elif goal == "Muscle Gain":

            calories = int(tdee + 300)

        else:

            calories = int(tdee)

        # ==========================
        # Macronutrients
        # ==========================

        protein = round(weight * 2,1)

        fat = round(weight * 0.8,1)

        carbs = round(
            (
                calories -
                (protein * 4 + fat * 9)
            ) / 4,
            1
        )

        water = round(weight * 0.035,1)

        profile, created = UserHealthProfile.objects.get_or_create(
            customer=cid
        )

        profile.age = age
        profile.gender = gender
        profile.height = height
        profile.weight = weight

        profile.activity_level = activity

        profile.goal = goal

        profile.diet_type = diet

        profile.bmi = bmi

        profile.daily_calories = calories

        profile.protein_goal = protein

        profile.carbs_goal = carbs

        profile.fat_goal = fat

        profile.water_goal = water

        profile.save()

        messages.success(
            request,
            "Health Profile Saved Successfully"
        )

    return redirect(
        reverse("customer_dashboard") +
        "?active_page=profile"
    )

def get_ai_recommendations(health_profile):

    products = product.objects.all()

    # Goal Based
    if health_profile.goal == "Muscle Gain":
        products = products.filter(
            protein__gte=20
        ).order_by("-protein")

    elif health_profile.goal == "Weight Loss":
        products = products.filter(
            calories__lte=250,
            sugar__lte=10
        ).order_by("-protein")

    elif health_profile.goal == "Maintenance":
        products = products.order_by("-is_featured")

    # Diet Type
    if health_profile.diet_type == "Veg":
        products = products.filter(
            diet_type="Veg"
        )

    elif health_profile.diet_type == "Vegan":
        products = products.filter(
            diet_type="Vegan"
        )

    return products[:8]

def ai_assessment(request):
    if "email" not in request.session:
        return redirect("login")

    return redirect(reverse("customer_dashboard") + "?active_page=assessment")