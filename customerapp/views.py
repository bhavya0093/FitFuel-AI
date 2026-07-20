from urllib import request
import random
from django.shortcuts import render,get_object_or_404,redirect
from sellerapp.models import User
from django.http import HttpResponseRedirect ,HttpResponse
from .models import *
from customerapp.models import product, customer
from django.contrib import messages
import uuid
from .models import UserHealthProfile
import math
from django.db.models import Q,Avg
from django.urls import reverse
from django.utils import timezone
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.http import JsonResponse
from .services import model
from .prompts import product_chat_prompt
from datetime import timedelta
from .utils import check_user_achievements



def customer_dashboard(request):

    if "email" in request.session:

        uid = User.objects.get(email=request.session["email"])
        cid = customer.objects.get(user_id=uid)
        wallet, created = Wallet.objects.get_or_create(
                                customer=cid
                            )
        # ==========================
        # Cart Summary
        # ==========================

        cart_obj = cart.objects.filter(customer=cid).first()
        price = request.GET.get("price")
        protein = request.GET.get("protein")
        
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

        # Calculate dynamic goal status based on logged intake + consumed meals + cart items
        import datetime
        from django.utils import timezone
        today = timezone.now().date()
        today_logs = ProgressLog.objects.filter(customer=cid, created_at=today)
        logged_calories = sum(log.calories for log in today_logs)
        logged_protein = sum(log.protein for log in today_logs)
        logged_water = sum(log.water for log in today_logs)

        # Calculate consumed meals from the Meal Planner (DailyMealLog)
        today_meals = DailyMealLog.objects.filter(customer=cid, log_date=today, consumed=True)
        meal_calories = sum(m.calories for m in today_meals)
        meal_protein = sum(m.protein for m in today_meals)

        # Combine manually logged intake and consumed meals
        actual_calories = logged_calories + meal_calories
        actual_protein = logged_protein + meal_protein

        current_calories = actual_calories if actual_calories > 0 else int(cart_calories)
        current_protein = actual_protein if actual_protein > 0 else round(cart_protein, 1)
        current_water = logged_water

        goal_calories = health.daily_calories if health else 2000
        goal_protein = health.protein_goal if health else 150
        goal_water = health.water_goal if health else 3.0

        cal_pct = min(100, round((current_calories / goal_calories) * 100)) if goal_calories > 0 else 0
        prot_pct = min(100, round((current_protein / goal_protein) * 100)) if goal_protein > 0 else 0
        water_pct = min(100, round((current_water / goal_water) * 100)) if goal_water > 0 else 0
        
        try:
            match_score = min(100, round((cal_pct + prot_pct + water_pct) / 3))
        except Exception:
            match_score = 0
        categories = Category.objects.all()

        selected_category = request.GET.get("category")
        search = request.GET.get("search")

        diet = request.GET.get("diet")
        goal = request.GET.get("goal")
        brand = request.GET.get("brand")
        sort = request.GET.get("sort")
        
        profile = UserHealthProfile.objects.filter(customer=cid).first()

        pid = product.objects.all()
        if search:
            pid = pid.filter(
                Q(product_name__icontains=search) |

                Q(brand__icontains=search) |

                Q(description__icontains=search)

            )
        if diet:
            pid = pid.filter(diet_type=diet)

        if goal:
            pid = pid.filter(goal_type=goal)
        
        if brand:
            pid = pid.filter(brand__iexact=brand)
        
        if price:
            pid = pid.filter(product_price__lte=price)
            
        if protein:
            pid = pid.filter(
                protein__gte=protein
            )

        if sort == "latest":
            pid = pid.order_by("-created_at")

        elif sort == "low":
            pid = pid.order_by("product_price")

        elif sort == "high":
            pid = pid.order_by("-product_price")

        elif sort == "protein":
            pid = pid.order_by("-protein")

        elif sort == "rating":
            pid = pid.order_by("-rating")

        elif sort == "popular":
            pid = pid.order_by("-total_sold")

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

                cat_products = pid.filter(
                    product_category=cat
                )[:6]

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

        # Get featured product
        featured_product = product.objects.filter(is_featured=True).first()
        if not featured_product:
            featured_product = product.objects.order_by("-rating", "-product_price").first()

        featured_tags = []
        featured_original_price = 0
        if featured_product:
            if featured_product.ai_tags:
                featured_tags = [tag.strip() for tag in featured_product.ai_tags.split(",") if tag.strip()]
            else:
                featured_tags = ["High Protein", "Low Sugar", "Fast Recovery"]
            if featured_product.discount > 0:
                featured_original_price = int(featured_product.product_price * 100 / (100 - featured_product.discount))
            else:
                featured_original_price = featured_product.product_price

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
        if active_page == "assessment" and cid.subscription_plan == "Free":
            return redirect("subscription_plans")


        unread_notifications = Notification.objects.filter(
                                customer=cid,
                                is_read=False
                            ).count()
        notifications = Notification.objects.filter(
                            customer=cid
                        ).order_by("-created_at")[:5]

        orders = Order.objects.filter(customer=cid).order_by("-order_date")

        total_amount = sum(i.product.product_price * i.qty for i in cart_items) if cart_items else 0
        discount = 65 if total_amount >= 100 else 0

        # Auto-apply FITFUEL10 if no coupon is set in session
        coupon_id = request.session.get("coupon_id")
        if not coupon_id:
            try:
                default_coupon = Coupon.objects.filter(code="FITFUEL10", is_active=True).first()
                if default_coupon:
                    request.session["coupon_id"] = default_coupon.id
                    coupon_id = default_coupon.id
            except Exception:
                pass

        coupon_discount = 0
        coupon = None
        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id, is_active=True)
                if total_amount >= coupon.minimum_amount:
                    coupon_discount = (total_amount * coupon.discount) // 100
                    if coupon_discount > coupon.maximum_discount:
                        coupon_discount = coupon.maximum_discount
            except Coupon.DoesNotExist:
                pass

        net_amount = total_amount - discount - coupon_discount
        remaining_amount = 100 - total_amount if total_amount < 100 else 0

        import datetime
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        delivery_date = "Tomorrow, " + tomorrow.strftime("%d %b")

        # Achievements & Leaderboard Integration
        achievements = UserAchievement.objects.filter(
            customer=cid
        ).order_by("-unlocked_at")

        total_badges = achievements.count()

        gold_badges = achievements.filter(
            badge="🏆"
        ).count()

        protein_badges = achievements.filter(
            title__icontains="Protein"
        ).count()

        latest_badge = achievements.first()

        game, created = UserGamification.objects.get_or_create(customer=cid)
        level = game.level
        current_xp = game.xp
        next_level_xp = level * 100
        remaining_xp = next_level_xp - current_xp
        xp_progress = round((current_xp / next_level_xp) * 100) if next_level_xp > 0 else 0
        streak_pct = min(int(game.streak * 100 / 7), 100) if game.streak else 0

        leaderboard_qs = UserGamification.objects.select_related(
            "customer",
            "customer__user_id"
        ).order_by(
            "-xp",
            "-level"
        )

        rank = 1
        for user in leaderboard_qs:
            user.rank = rank
            rank += 1

        my_rank = None
        for user in leaderboard_qs:
            if user.customer == cid:
                my_rank = user.rank
                break

        progress_logs = ProgressLog.objects.filter(customer=cid).order_by("-created_at")
        chart_logs = list(ProgressLog.objects.filter(customer=cid).order_by("-created_at")[:7])
        chart_logs.reverse()

        wishlist_pids = set(Wishlist.objects.filter(customer=cid).values_list("product_id", flat=True))

        context = {
            "game": game,
            "streak_pct": streak_pct,
            "cal_pct": cal_pct,
            "prot_pct": prot_pct,
            "water_pct": water_pct,
            "current_calories": current_calories,
            "current_protein": current_protein,
            "current_water": current_water,
            "match_score": match_score,
            "total_users_count": 15000 + customer.objects.count(),
            "total_products_count": 240 + product.objects.count(),
            "total_meal_plans_count": 500 + customer.objects.count() * 10,
            "ai_accuracy": 97,
            "uid": uid,
            "cid": cid,
            "wishlist_pids": wishlist_pids,
            "wishlist_count": cid.wishlist_count,
            "pid": pid,
            "progress_logs": progress_logs,
            "chart_logs": chart_logs,
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
            "featured_product": featured_product,
            "featured_tags": featured_tags,
            "featured_original_price": featured_original_price,
            "cart_count": cart_count,
            "cart_protein": round(cart_protein,1),
            "cart_calories": int(cart_calories),
            "item": cart_items,
            "total_amount": total_amount,
            "discount": discount,
            "coupon": coupon,
            "coupon_discount": coupon_discount,
            "delivery_date": delivery_date,
            "net_amount": net_amount,
            "remaining_amount": remaining_amount,
            "search": search,
            "diet": diet,
            "goal": goal,
            "brand": brand,
            "price": price,
            "protein": protein,
            "sort": sort,
            "unread_notifications": unread_notifications,
            "notifications": notifications,
            "wallet": wallet,
            # Achievements & Leaderboard Context
            "achievements": achievements,
            "total_badges": total_badges,
            "gold_badges": gold_badges,
            "protein_badges": protein_badges,
            "latest_badge": latest_badge,
            "level": level,
            "current_xp": current_xp,
            "next_level_xp": next_level_xp,
            "remaining_xp": remaining_xp,
            "xp_progress": xp_progress,
            "game": game,
            "my_game": game,
            "leaderboard": leaderboard_qs[:10],
            "my_rank": my_rank,
            "daily_challenge": "Complete Protein Goal",
            "daily_reward": 20,
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

            return redirect("customer_dashboard")

def show_product(request):

    if "email" in request.session:
        return redirect("customer_dashboard")
    
    else:
        return HttpResponseRedirect("/seller/login/")
    
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

            # Auto-apply FITFUEL10 if no coupon is set in session
            coupon_id = request.session.get("coupon_id")
            if not coupon_id:
                try:
                    default_coupon = Coupon.objects.filter(code="FITFUEL10", is_active=True).first()
                    if default_coupon:
                        request.session["coupon_id"] = default_coupon.id
                        coupon_id = default_coupon.id
                except Exception:
                    pass

            coupon_discount = 0
            coupon = None
            if coupon_id:
                try:
                    coupon = Coupon.objects.get(id=coupon_id, is_active=True)
                    if total_amount >= coupon.minimum_amount:
                        coupon_discount = (total_amount * coupon.discount) // 100
                        if coupon_discount > coupon.maximum_discount:
                            coupon_discount = coupon.maximum_discount
                except Coupon.DoesNotExist:
                    pass

            # Base Discount
            discount = 65 if total_amount >= 100 else 0
            net_amount = total_amount - discount - coupon_discount
            remaining_amount = 100 - total_amount if total_amount < 100 else 0

            context = {
                'item': item,
                'total_amount': total_amount,
                'discount': discount,
                'coupon': coupon,
                'coupon_discount': coupon_discount,
                'net_amount': net_amount,
                'remaining_amount': remaining_amount,
                'is_standalone': True,
            }
            return render(request, "customerapp/cart.html", context)

def checkout(request):
    if "email" in request.session:
        uid = User.objects.get(email = request.session['email'])
        if uid.role == "customer":
            cid = customer.objects.get(user_id = uid)
            Cart_obj, created = cart.objects.get_or_create(customer = cid)
            item = cartitem.objects.filter(cart=Cart_obj)
            # ==========================
            # Buy Now
            # ==========================

            buy_now_product = request.session.get("buy_now_product")

            if buy_now_product:

                product_obj = get_object_or_404(
                    product,
                    id=buy_now_product
                )

                class BuyNowItem:
                    pass

                buy_item = BuyNowItem()

                buy_item.product = product_obj

                buy_item.qty = 1

                item = [buy_item]
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

            coupon_discount = 0

            coupon = None

            coupon_id = request.session.get("coupon_id")

            if coupon_id:

                try:

                    coupon = Coupon.objects.get(id=coupon_id)

                    if total_amount >= coupon.minimum_amount:

                        coupon_discount = (
                            total_amount * coupon.discount
                        ) / 100

                        if coupon_discount > coupon.maximum_discount:

                            coupon_discount = coupon.maximum_discount

                except Coupon.DoesNotExist:

                    pass

            net_amount = total_amount - discount - coupon_discount
            available_coupons = Coupon.objects.all()
            
            context = {
                'item' : item,
                'total_amount' : total_amount,
                'discount': discount,
                'net_amount': net_amount,
                "addresses": addresses,
                "coupon": coupon,
                "coupon_discount": coupon_discount,
                "available_coupons": available_coupons,
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

    buy_now_product = request.session.get("buy_now_product")

    if (
        not buy_now_product and
        not cartitem.objects.filter(cart__customer=cid).exists()
    ):

        messages.error(request, "Your cart is empty.")

        return redirect("view_cart")

    if request.method == "POST":

        payment_method = request.POST.get("payment")

        address_id = request.session.get("address_id")

        if not address_id:
            messages.error(request, "Please select address.")
            return HttpResponseRedirect("/checkout/")

        address = get_object_or_404(Address, id=address_id)

        if buy_now_product:

            product_obj = get_object_or_404(
                product,
                id=buy_now_product
            )

            class BuyNowItem:
                pass

            obj = BuyNowItem()

            obj.product = product_obj
            obj.qty = 1

            items = [obj]

        else:

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

        # ==========================
        # Cashback (5%)
        # ==========================

        wallet, created = Wallet.objects.get_or_create(
            customer=cid
        )

        cashback = round(final * 0.05, 2)

        wallet.balance += cashback
        wallet.save()

        WalletTransaction.objects.create(
            wallet=wallet,
            amount=cashback,
            transaction_type="Credit",
            description=f"5% Cashback on Order #{order.id}"
        )

        Notification.objects.create(
            customer=cid,
            title="Cashback Received",
            message=f"₹{cashback} cashback has been added to your wallet."
        )

        for i in items:

            OrderItem.objects.create(
                order=order,
                product=i.product,
                quantity=i.qty,
                price=i.product.product_price,
                subtotal=i.product.product_price * i.qty
            )

        if not buy_now_product:
            items.delete()

        if "address_id" in request.session:
            del request.session["address_id"]
        if "buy_now_product" in request.session:
            del request.session["buy_now_product"]
        if "coupon_id" in request.session:
            del request.session["coupon_id"]

        Notification.objects.create(

            customer=cid,

            title="Order Placed",

            message=f"Your Order #{order.id} has been placed successfully."

        )
        check_user_achievements(cid)

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

    Notification.objects.create(

        customer=cid,

        title="Order Cancelled",

        message=f"Your Order #{order.id} has been cancelled successfully."

    )

    messages.success(request, "Order Cancelled Successfully.")

    return redirect("orders")

def notifications(request):

    if "email" not in request.session:
        return redirect("login")

    uid = User.objects.get(
        email=request.session["email"]
    )

    cid = customer.objects.get(
        user_id=uid
    )

    notifications = Notification.objects.filter(
        customer=cid
    ).order_by("-created_at")

    context = {

        "notifications": notifications

    }

    return render(
        request,
        "customerapp/notifications.html",
        context
    )

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

    if cid.subscription_plan == "Free":
        messages.error(request, "AI Assessment is a premium feature. Please upgrade your plan to access it.")
        return redirect("subscription_plans")

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

        try:
            profile = UserHealthProfile.objects.get(customer=cid)
        except UserHealthProfile.DoesNotExist:
            profile = UserHealthProfile(customer=cid)

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
            "Health Profile Saved Successfully!"
        )

    return redirect("meal_planner")

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

def product_details(request, pk):

    if "email" not in request.session:
        return redirect("login")

    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)

    product_obj = get_object_or_404(product, id=pk)

    related_products = product.objects.filter(
        product_category=product_obj.product_category
    ).exclude(
        id=product_obj.id
    )[:4]

    reviews = ProductReview.objects.filter(product=product_obj)

    context = {
        "uid": uid,
        "cid": cid,
        "product": product_obj,
        "related_products": related_products,
        "reviews": reviews,
    }

    return render(
        request,
        "customerapp/product_details.html",
        context
    )

def add_to_wishlist(request, pk):

    if "email" not in request.session:
        return redirect("login")

    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)

    product_obj = get_object_or_404(product, id=pk)

    Wishlist.objects.get_or_create(
        customer=cid,
        product=product_obj
    )

    messages.success(request, "Added to Wishlist ❤️")

    return redirect(request.META.get("HTTP_REFERER", "customer_dashboard"))

def toggle_wishlist(request, pk):

    if "email" not in request.session:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)
    product_obj = get_object_or_404(product, id=pk)

    wish_item = Wishlist.objects.filter(customer=cid, product=product_obj).first()
    if wish_item:
        wish_item.delete()
        action = "removed"
    else:
        Wishlist.objects.create(customer=cid, product=product_obj)
        action = "added"

    wishlist_count = Wishlist.objects.filter(customer=cid).count()
    return JsonResponse({
        "success": True,
        "action": action,
        "wishlist_count": wishlist_count
    })

def remove_from_wishlist(request, pk):

    if "email" not in request.session:
        return redirect("login")

    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)

    Wishlist.objects.filter(
        Q(customer=cid) & (Q(product_id=pk) | Q(id=pk))
    ).delete()

    messages.success(request, "Removed from Wishlist")

    return redirect(request.META.get("HTTP_REFERER", "wishlist"))

def wishlist(request):

    if "email" not in request.session:
        return redirect("login")

    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)

    wishlist_items = Wishlist.objects.filter(
        customer=cid
    ).select_related("product")

    context = {

        "uid": uid,

        "cid": cid,

        "wishlist_items": wishlist_items,

    }

    return render(
        request,
        "customerapp/wishlist.html",
        context
    )

def add_review(request, pk):

    if "email" not in request.session:
        return redirect("login")

    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)

    product_obj = get_object_or_404(product, id=pk)

    if request.method == "POST":

        rating = request.POST["rating"]

        review = request.POST["review"]

        ProductReview.objects.create(

            customer=cid,

            product=product_obj,

            rating=rating,

            review=review

        )

        reviews = ProductReview.objects.filter(
            product=product_obj
        )

        avg = reviews.aggregate(
            Avg("rating")
        )["rating__avg"]

        product_obj.rating = round(avg,1)

        product_obj.review_count = reviews.count()

        product_obj.save()

        check_user_achievements(cid)

        messages.success(
            request,
            "Review Added Successfully."
        )

    return redirect(
        "product_details",
        pk=pk
    )

def buy_now(request, pk):

    if "email" not in request.session:
        return redirect("login")

    request.session["buy_now_product"] = pk

    return redirect("checkout")

def read_notification(request, pk):

    if "email" not in request.session:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
            return JsonResponse({"error": "Unauthorized"}, status=401)
        return redirect("login")

    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)

    notification = get_object_or_404(
        Notification,
        id=pk,
        customer=cid
    )

    notification.is_read = True
    notification.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
        unread_count = Notification.objects.filter(customer=cid, is_read=False).count()
        return JsonResponse({"success": True, "unread_count": unread_count})

    return redirect("notifications")

def mark_all_notifications_read(request):

    if "email" not in request.session:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
            return JsonResponse({"error": "Unauthorized"}, status=401)
        return redirect("login")

    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)

    Notification.objects.filter(customer=cid, is_read=False).update(is_read=True)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
        return JsonResponse({"success": True, "unread_count": 0})

    return redirect("customer_dashboard")

def wallet(request):

    if "email" not in request.session:
        return redirect("login")

    uid = User.objects.get(
        email=request.session["email"]
    )

    cid = customer.objects.get(
        user_id=uid
    )

    wallet, created = Wallet.objects.get_or_create(
        customer=cid
    )

    transactions = WalletTransaction.objects.filter(
        wallet=wallet
    ).order_by("-created_at")

    return render(

        request,

        "customerapp/wallet.html",

        {

            "wallet": wallet,

            "transactions": transactions

        }

    )

def coupons(request):

    if "email" not in request.session:
        return redirect("login")

    coupons = Coupon.objects.filter(
        is_active=True,
        expiry_date__gte=timezone.now().date()
    ).order_by("expiry_date")

    return render(
        request,
        "customerapp/coupons.html",
        {
            "coupons": coupons
        }
    )

def apply_coupon(request):

    if "email" not in request.session:
        return redirect("login")

    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)

    if request.method == "POST":

        code = request.POST.get("coupon_code", "").strip().upper()

        if not code:

            messages.error(request, "Please enter a coupon code.")

            return redirect("checkout")

        try:

            coupon = Coupon.objects.get(
                code=code,
                is_active=True
            )

        except Coupon.DoesNotExist:

            messages.error(request, "Invalid Coupon Code.")

            return redirect("checkout")

        # ==========================
        # Expiry Check
        # ==========================

        if coupon.expiry_date < timezone.now().date():

            messages.error(request, "This coupon has expired.")

            return redirect("checkout")

        # ==========================
        # Already Used Check
        # ==========================

        already_used = UserCoupon.objects.filter(

            customer=cid,

            coupon=coupon,

            is_used=True

        ).exists()

        if already_used:

            messages.error(

                request,

                "You have already used this coupon."

            )

            return redirect("checkout")

        # ==========================
        # Cart Total Check
        # ==========================

        cart_obj, created = cart.objects.get_or_create(customer=cid)

        items = cartitem.objects.filter(cart=cart_obj)

        total = 0

        for i in items:

            total += i.product.product_price * i.qty

        if total < coupon.minimum_amount:

            messages.error(

                request,

                f"This coupon requires a minimum order of ₹{coupon.minimum_amount}."

            )

            return redirect("checkout")

        # ==========================
        # Apply Coupon
        # ==========================

        request.session["coupon_id"] = coupon.id

        messages.success(

            request,

            f"{coupon.code} applied successfully."

        )

    return redirect("checkout")

def remove_coupon(request):

    if "coupon_id" in request.session:

        del request.session["coupon_id"]

    return redirect("checkout")

def wishlist_to_cart(request, pk):

    if "email" not in request.session:
        return redirect("login")

    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)

    wish = get_object_or_404(
        Wishlist,
        id=pk,
        customer=cid
    )

    cart_obj, created = cart.objects.get_or_create(
        customer=cid
    )

    cart_item, created = cartitem.objects.get_or_create(

        cart=cart_obj,

        product=wish.product,

        defaults={"qty": 1}

    )

    if not created:

        cart_item.qty += 1

        cart_item.save()

    wish.delete()

    messages.success(

        request,

        "Product moved to cart."

    )

    return redirect("wishlist")

def meal_planner(request):

    if "email" not in request.session:
        return redirect("login")

    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)

    if cid.subscription_plan == "Free":
        return redirect("subscription_plans")

    try:
        health = UserHealthProfile.objects.get(customer=cid)
    except UserHealthProfile.DoesNotExist:

        messages.error(
            request,
            "Please complete your Health Profile first."
        )

        return redirect(
            reverse("customer_dashboard") +
            "?active_page=profile"
        )

    meal_plan = MealPlan.objects.filter(
        customer=cid
    ).select_related("product")

    

    # ==========================
    # AI Meal Reasons
    # ==========================

    for meal in meal_plan:

        score = 50

        if health.goal == meal.product.goal_type:
            score += 20

        if health.diet_type == meal.product.diet_type:
            score += 15

        if meal.product.protein >= 25:
            score += 10

        if meal.product.rating >= 4.5:
            score += 5

        meal.ai_score = min(score, 99)

        reasons = []

        if health.goal == meal.product.goal_type:
            reasons.append(f"Perfect for {health.goal}")

        if health.diet_type == meal.product.diet_type:
            reasons.append(f"{health.diet_type} Friendly")

        if meal.product.protein >= 25:
            reasons.append("High Protein")

        elif meal.product.protein >= 15:
            reasons.append("Good Protein")

        if meal.product.sugar <= 5:
            reasons.append("Low Sugar")

        if meal.product.fiber >= 5:
            reasons.append("High Fiber")

        meal.ai_reasons = reasons[:4]

    today = timezone.now().date()

    for meal in meal_plan:

        meal.is_consumed = DailyMealLog.objects.filter(
            customer=cid,
            product=meal.product,
            meal_type=meal.meal_type,
            log_date=today,
            consumed=True
        ).exists()

    # ==========================
    # Nutrition Summary
    # ==========================

    today = timezone.now().date()

    daily_logs = DailyMealLog.objects.filter(
        customer=cid,
        log_date=today,
        consumed=True
    )

    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0

    for log in daily_logs:

        total_calories += log.calories * log.quantity

        total_protein += log.protein * log.quantity

        total_carbs += log.carbs * log.quantity

        total_fat += log.fat * log.quantity
    
    # ==========================
    # Goal Progress
    # ==========================

    calorie_progress = 0
    protein_progress = 0

    if health.daily_calories > 0:

        calorie_progress = min(
            round((total_calories / health.daily_calories) * 100),
            100
        )

    if health.protein_goal > 0:

        protein_progress = min(
            round((total_protein / health.protein_goal) * 100),
            100
        )
    today_logs = DailyMealLog.objects.filter(
    customer=cid,
    consumed=True,
    log_date=timezone.now().date()
    )

    today_meals = today_logs.count()

    last_7_days = []

    for i in range(6, -1, -1):

        day = timezone.now().date() - timedelta(days=i)

        logs = DailyMealLog.objects.filter(
            customer=cid,
            consumed=True,
            log_date=day
        )

        calories = sum(
            log.calories * log.quantity
            for log in logs
        )

        protein = sum(
            log.protein * log.quantity
            for log in logs
        )

        last_7_days.append({

            "day": day.strftime("%a"),

            "calories": calories,

            "protein": round(protein, 1)

        })
    
    # ==========================
    # AI Health Score
    # ==========================

    health_score = 0

    # Protein Score (30)
    if health.protein_goal > 0:

        protein_ratio = min(
            total_protein / health.protein_goal,
            1
        )

        health_score += int(protein_ratio * 30)

    # Calories Score (30)
    if health.daily_calories > 0:

        calorie_difference = abs(
            health.daily_calories - total_calories
        )

        calorie_ratio = max(
            0,
            1 - (calorie_difference / health.daily_calories)
        )

        health_score += int(calorie_ratio * 30)

        health_score = min(health_score,100)
        
        

    # Meals Score (20)

    consumed_meals = DailyMealLog.objects.filter(
        customer=cid,
        consumed=True,
        log_date=today
    ).values(
        "meal_type"
    ).distinct().count()

    health_score += min(consumed_meals * 5, 20)

    # Water Score (Temporary)
    health_score += 10

    # Consistency Score (Temporary)
    health_score += 10

    health_score = min(health_score, 100)
    
    generate_health_insight(cid)

    if health_score >= 90:

        health_status = "Excellent 🏆"

    elif health_score >= 75:

        health_status = "Very Good 💪"

    elif health_score >= 60:

        health_status = "Good 👍"

    elif health_score >= 40:

        health_status = "Average 🙂"

    else:

        health_status = "Needs Improvement ⚠️"

    # ==========================
    # AI Feedback
    # ==========================

    if health_score >= 90:

        ai_feedback = "Excellent! Keep following your nutrition plan."

    elif health_score >= 75:

        ai_feedback = "Great job! A little more consistency will improve your score."

    elif health_score >= 60:

        ai_feedback = "You're doing well. Try completing all meals and protein goals."

    elif health_score >= 40:

        ai_feedback = "You need to improve your daily nutrition intake."

    else:

        ai_feedback = "Let's restart your healthy journey. Complete today's meals."
    
    # =====================================
    # AUTO UNLOCK ACHIEVEMENTS
    # =====================================
    latest_insight = DailyHealthInsight.objects.filter(
        customer=cid
    ).first()

    context = {

        "health": health,

        "meal_plan": meal_plan,

        "today_meals": today_meals,

        "total_calories": total_calories,

        "total_protein": round(total_protein, 1),

        "total_carbs": round(total_carbs, 1),

        "total_fat": round(total_fat, 1),

        "calorie_progress": calorie_progress,

        "protein_progress": protein_progress,

        "last_7_days": last_7_days,

        "health_score": health_score,

        "health_status": health_status,

        "ai_feedback": ai_feedback,

        "latest_insight": latest_insight,

    }

    return render(
        request,
        "customerapp/meal_planner.html",
        context
    )

def unlock(title, description, badge):

    if not UserAchievement.objects.filter(
        customer=cid,
        title=title
    ).exists():

        UserAchievement.objects.create(

            customer=cid,

            title=title,

            description=description,

            badge=badge

        )
    # Protein Champion

    if protein_progress >= 100:

        unlock(

            "Protein Champion",

            "Completed Daily Protein Goal.",

            "💪"

        )

    # Calorie Master

    if calorie_progress >= 100:

        unlock(

            "Calorie Master",

            "Completed Daily Calories Goal.",

            "🔥"

        )

    # Nutrition Master

    if health_score >= 90:

        unlock(

            "Nutrition Master",

            "Health Score above 90.",

            "🏆"

        )

    # Meal Finisher

    if today_meals >= 4:

        unlock(

            "Meal Finisher",

            "Completed all meals today.",

            "🍽"

        )

    achievements = UserAchievement.objects.filter(customer=cid).order_by("-unlocked_at")

    context = {

        "health": health,
        "total_calories": total_calories,
        "total_protein": round(total_protein, 1),
        "total_carbs": round(total_carbs, 1),
        "total_fat": round(total_fat, 1),
        "calorie_progress": calorie_progress,
        "protein_progress": protein_progress,
        "meal_plan": meal_plan,
        "today_meals": today_meals,
        "last_7_days": last_7_days,
        "health_score": health_score,
        "health_status": health_status,
        "ai_feedback": ai_feedback,
        "achievements": achievements,
    }

    return render(
        request,
        "customerapp/meal_planner.html",
        context
    )

def generate_meal_plan(request):

    print("===== GENERATE MEAL PLAN CALLED =====")

    if "email" not in request.session:
        return redirect("login")

    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)

    if cid.subscription_plan == "Free":
        messages.error(request, "Please upgrade to FitFuel Pro/Elite to access this feature.")
        return redirect("meal_planner")

    try:
        hp = UserHealthProfile.objects.get(customer=cid)

    except UserHealthProfile.DoesNotExist:

        messages.error(
            request,
            "Please complete your Health Profile first."
        )

        return redirect("meal_planner")

    # Delete Old Meal Plan
    MealPlan.objects.filter(customer=cid).delete()

    # ==================================
    # AI Product Selection
    # ==================================

    products = product.objects.filter(
        diet_type=hp.diet_type,
        goal_type=hp.goal
    ).order_by("-protein")

    # Fallback 1
    if not products.exists():

        products = product.objects.filter(
            diet_type=hp.diet_type
        ).order_by("-protein")

    # Fallback 2
    if not products.exists():

        products = product.objects.filter(
            goal_type=hp.goal
        ).order_by("-protein")

    # Fallback 3
    if not products.exists():

        products = product.objects.all().order_by("-protein")

    # Convert to list & Shuffle
    products = list(products)
    random.shuffle(products)

    # No products available
    if not products:

        messages.error(
            request,
            "No products available to generate meal plan."
        )

        return redirect("meal_planner")

    # ==================================
    # Meal Distribution
    # ==================================

    if len(products) >= 8:

        breakfast = products[0:2]
        lunch = products[2:4]
        dinner = products[4:6]
        snacks = products[6:8]

    else:

        breakfast = [products[0]]

        lunch = [products[1]] if len(products) > 1 else breakfast

        dinner = [products[2]] if len(products) > 2 else lunch

        snacks = [products[3]] if len(products) > 3 else breakfast

    # ==================================
    # Save Meal Plan
    # ==================================

    meal_data = {
        "Breakfast": breakfast,
        "Lunch": lunch,
        "Dinner": dinner,
        "Snacks": snacks,
    }

    for meal_type, meal_products in meal_data.items():
        print("MealPlan Count:", MealPlan.objects.filter(customer=cid).count())
        for p in meal_products:
            print(meal_type, p.product_name)
            MealPlan.objects.create(
                customer=cid,
                meal_type=meal_type,
                product=p,
                quantity=1
            )
            print("Saved Successfully")

    messages.success(
        request,
        "AI Meal Plan Generated Successfully."
    )
    check_user_achievements(cid)
    print(MealPlan.objects.filter(customer=cid).count())

    return redirect("meal_planner")

def nutrition_report(request):

    if "email" not in request.session:
        return redirect("login")

    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)

    if cid.subscription_plan == "Free":
        messages.error(request, "Please upgrade to FitFuel Pro/Elite to access this feature.")
        return redirect("meal_planner")

    try:
        health = UserHealthProfile.objects.get(customer=cid)
    except UserHealthProfile.DoesNotExist:

        messages.error(
            request,
            "Please complete your Health Profile first."
        )

        return redirect("meal_planner")

    meal_plan = MealPlan.objects.filter(
        customer=cid
    ).select_related("product")

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'attachment; filename="FitFuel_AI_Report.pdf"'
    )

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    elements = []

    # ==========================
    # Title
    # ==========================

    elements.append(
        Paragraph(
            "<b><font size=20>FitFuel AI</font></b>",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            "Personalized Nutrition Report",
            styles["Heading2"]
        )
    )

    elements.append(
        Spacer(1, 0.3 * inch)
    )

    # ==========================
    # User Details
    # ==========================

    data = [

        ["Name",
         f"{cid.firstname} {cid.lastname}"],

        ["Goal",
         health.goal],

        ["Diet",
         health.diet_type],

        ["BMI",
         str(health.bmi)],

        ["Daily Calories",
         f"{health.daily_calories} kcal"],

        ["Protein Goal",
         f"{health.protein_goal} g"],

        ["Carbs Goal",
         f"{health.carbs_goal} g"],

        ["Fat Goal",
         f"{health.fat_goal} g"],

        ["Water Goal",
         f"{health.water_goal} L"]

    ]

    table = Table(data, colWidths=[170, 250])

    table.setStyle(

        TableStyle([

            ("BACKGROUND", (0,0), (-1,0), colors.green),

            ("TEXTCOLOR", (0,0), (-1,0), colors.white),

            ("GRID", (0,0), (-1,-1), 1, colors.grey),

            ("BACKGROUND", (0,1), (-1,-1), colors.beige),

            ("BOTTOMPADDING", (0,0), (-1,0), 10),

        ])

    )

    elements.append(table)

    elements.append(
        Spacer(1, 0.4 * inch)
    )

    # ==========================
    # Meal Plan
    # ==========================

    elements.append(
        Paragraph(
            "<b>AI Meal Plan</b>",
            styles["Heading2"]
        )
    )

    for meal in meal_plan:

        elements.append(

            Paragraph(

                f"{meal.meal_type} : "

                f"{meal.product.product_name}"

                f" ({meal.product.calories} kcal)",

                styles["BodyText"]

            )

        )

    elements.append(
        Spacer(1, 0.3 * inch)
    )

    elements.append(

        Paragraph(

            "Generated by FitFuel AI",

            styles["Italic"]

        )

    )

    doc.build(elements)

    return response

def product_details(request, pk):
    prod = get_object_or_404(product, id=pk)
    reviews = ProductReview.objects.filter(product=prod)
    related_products = product.objects.filter(product_category=prod.product_category).exclude(id=prod.id)[:4]
    
    if reviews.exists():
        total_rating = sum(r.rating for r in reviews)
        prod.rating = round(total_rating / reviews.count(), 1)
        prod.review_count = reviews.count()
    
    context = {
        "product": prod,
        "reviews": reviews,
        "related_products": related_products,
    }
    return render(request, "customerapp/product_details.html", context)

def ask_ai(request):

    if "email" not in request.session:

        return JsonResponse({
            "success":False,
            "message":"Login Required"
        })

    if request.method!="POST":

        return JsonResponse({
            "success":False
        })

    product_id=request.POST.get("product_id")

    question=request.POST.get("question")

    try:

        p=product.objects.get(id=product_id)

    except product.DoesNotExist:

        return JsonResponse({
            "success":False,
            "message":"Product Not Found"
        })

    prompt=product_chat_prompt(
        p,
        question
    )

    try:

        response=model.generate_content(prompt)

        return JsonResponse({

            "success":True,

            "answer":response.text

        })

    except Exception as e:

        return JsonResponse({

            "success":False,

            "message":str(e)

        })

def add_daily_log(request, pk, meal_type):

    if "email" not in request.session:
        return redirect("login")

    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)

    p = get_object_or_404(product, id=pk)

    today = timezone.now().date()

    already_logged = DailyMealLog.objects.filter(
        customer=cid,
        product=p,
        meal_type=meal_type,
        log_date=today
    ).exists()

    if already_logged:

        messages.info(
            request,
            "This meal is already marked as consumed."
        )
        

        return redirect("meal_planner")

    DailyMealLog.objects.create(
        customer=cid,
        product=p,
        meal_type=meal_type,
        quantity=1,
        calories=p.calories,
        protein=p.protein,
        carbs=p.carbs,
        fat=p.fat,
        consumed=True,
    )

    check_user_achievements(cid)

    messages.success(
        request,
        f"{p.product_name} added to today's nutrition log."
    )
    game = UserGamification.objects.get_or_create(
    customer=cid
    )[0]

    context = {
        "game": game,
    }

    return redirect("meal_planner")

def achievements(request):

    if "email" not in request.session:

        return redirect("login")

    return redirect(reverse("customer_dashboard") + "?active_page=achievements")

def leaderboard(request):

    if "email" not in request.session:
        return redirect("login")

    return redirect(reverse("customer_dashboard") + "?active_page=leaderboard")
def generate_health_insight(customer):

    today = timezone.now().date()

    logs = DailyMealLog.objects.filter(
        customer=customer,
        consumed=True,
        log_date=today
    )

    total_calories = sum(
        log.calories * log.quantity
        for log in logs
    )

    total_protein = sum(
        log.protein * log.quantity
        for log in logs
    )

    try:

        profile = UserHealthProfile.objects.get(
            customer=customer
        )

    except UserHealthProfile.DoesNotExist:

        return
    messages = []

    if total_protein < profile.protein_goal:

        remain = round(
            profile.protein_goal - total_protein,
            1
        )

        messages.append(
            f"You still need {remain}g protein today."
        )

    else:

        messages.append(
            "Excellent! Protein goal completed."
        )
    if total_calories < profile.daily_calories:

        remain = profile.daily_calories - total_calories

        messages.append(
            f"You can consume {remain} kcal today."
        )

    else:

        messages.append(
            "Daily calorie goal completed."
        )

    # Meal Count
    meals = logs.values(
        "meal_type"
    ).distinct().count()

    if meals < 4:

        messages.append(
            "Complete all meals to improve your Health Score."
        )

    else:

        messages.append(
            "Awesome! All meals completed."
        )

    insight = " ".join(messages)

    DailyHealthInsight.objects.create(

        customer=customer,

        insight=insight,

        calories=total_calories,

        protein=total_protein,

        health_score=0

    )

def root_redirect(request):
    if "email" in request.session:
        try:
            uid = User.objects.get(email=request.session["email"])
            if uid.role == "seller":
                return redirect("admin_panel")
            elif uid.role == "customer":
                return redirect("customer_dashboard")
        except User.DoesNotExist:
            pass
    return redirect("login")

def add_progress_log(request):
    if "email" not in request.session:
        return redirect("login")
    
    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)
    
    if request.method == "POST":
        try:
            weight = float(request.POST.get("weight", 0))
            water = float(request.POST.get("water", 0))
            calories = int(request.POST.get("calories", 0))
            protein = float(request.POST.get("protein", 0))
            
            bmi = 0
            try:
                hp = cid.health_profile
                height_m = hp.height / 100.0
                if height_m > 0:
                    bmi = round(weight / (height_m * height_m), 1)
            except Exception:
                pass
                
            ProgressLog.objects.create(
                customer=cid,
                weight=weight,
                bmi=bmi,
                calories=calories,
                protein=protein,
                water=water
            )
            
            try:
                hp = cid.health_profile
                hp.weight = weight
                if bmi > 0:
                    hp.bmi = bmi
                hp.save()
            except Exception:
                pass
                
            try:
                game = UserGamification.objects.get(customer=cid)
                game.xp += 15
                if game.xp >= game.level * 100:
                    game.xp -= game.level * 100
                    game.level += 1
                game.save()
            except Exception:
                pass
                
            messages.success(request, "Daily progress logged successfully!")
        except Exception as e:
            messages.error(request, f"Error logging progress: {str(e)}")
            
    return redirect("/customer-dashboard/?active_page=progress")

def subscription_plans(request):
    if "email" not in request.session:
        return redirect("login")
        
    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)
    
    unread_notifications = Notification.objects.filter(customer=cid, is_read=False).count()
    notifications = Notification.objects.filter(customer=cid).order_by("-created_at")[:5]
    wishlist_count = cid.wishlist_count
    
    context = {
        "uid": uid,
        "cid": cid,
        "unread_notifications": unread_notifications,
        "notifications": notifications,
        "wishlist_count": wishlist_count,
    }
    
    return render(request, "customerapp/subscription.html", context)

def update_subscription(request):
    if "email" not in request.session:
        return JsonResponse({"success": False, "message": "Authentication required."})
        
    uid = User.objects.get(email=request.session["email"])
    cid = customer.objects.get(user_id=uid)
    
    plan = request.POST.get("plan") or request.GET.get("plan")
    if plan not in ["Free", "Pro", "Elite"]:
        return JsonResponse({"success": False, "message": "Invalid subscription plan selected."})
        
    cid.subscription_plan = plan
    cid.save()
    
    return JsonResponse({
        "success": True,
        "plan": plan,
        "message": f"Welcome to FitFuel {plan}! Your subscription has been activated successfully."
    })