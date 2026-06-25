from datetime import timedelta

from django.shortcuts import get_object_or_404, render, redirect
import random
from .models import *
from customerapp.models import *
from django.http import *
from .utils import *
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count

def register(request):
    if request.method == "POST":
        role = request.POST['role']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        contectno = request.POST['contectno']

        # Duplicate Email Validation
        if User.objects.filter(email=email).exists():
            context = {
                "e_msg": "Email already registered! Please Login."
            }
            return render(request, "sellerapp/register.html", context)
        
        # Mobile Validation
        if not contectno.isdigit() or len(contectno) != 10:
            context = {
                "e_msg": "Please enter a valid 10-digit mobile number."
            }
            return render(request, "sellerapp/register.html", context)

        # Generate a strong random password (instead of the old predictable scheme)
        plain_password = generate_strong_password()

        try:
                uid = User.objects.create(
                    email=email,
                    password=make_password(plain_password),
                    role=role
                )
        except Exception:
                context = {
                    "e_msg": "Something went wrong. Please try again."
                }
                return render(request, "sellerapp/register.html", context)
        
        myCustomMail(
        "Welcome To QuickBasket",
        "welcome_mail",
        email,
        {
            'name': firstname,
            'email': email
        }
    )

        try:
            myCustomMail(
                "Welcome - Your Account Password",
                "mail_template",    
                email,
                {'otp': plain_password}
            )
        except Exception:
            pass

        if role == "seller":
            seller.objects.create(
                user_id=uid,
                firstname=firstname,
                lastname=lastname,
                contectno=contectno,
            )
            context = {
                "s_msg": "Successfully registration Completed - please check your Email for password"
            }
            return render(request, "sellerapp/login.html", context)
        elif role == "customer":
            customer.objects.create(
                user_id=uid,
                firstname=firstname,
                lastname=lastname,
                contectno=contectno,
            )

        context = {
            "s_msg": "Successfully registration Completed - please check your Email for password"
        }
        return render(request, "sellerapp/login.html", context)

    return render(request, "sellerapp/register.html")


def login(request):

    if "email" in request.session:
        try:
            uid = User.objects.get(email=request.session["email"])
        except:
            del request.session["email"]
            return render(request,"sellerapp/login.html")

        if uid.role == "seller":
            sid = seller.objects.get(user_id=uid)
            pid = product.objects.all()

            context = {
                "uid": uid,
                "sid": sid,
                "pid": pid,
                "categories": Category.objects.all().order_by("id"),
            }

            return render(request,"sellerapp/admin_panel.html",context)

        elif uid.role == "customer":
            cid = customer.objects.get(user_id=uid)
            pid = product.objects.all()

            cart_item = cart.objects.filter(customer=cid)

            if cart_item:

                Cart_obj = cart_item.first()  
                item = cartitem.objects.filter(cart=Cart_obj)
   
                total_amount = 0
                for i in item:
                    total_amount += i.product.product_price * i.qty
                    
                context = {
                    "uid": uid,
                    "cid": cid,
                    "pid": pid,
                    "item" : item,
                    "total_amount" : total_amount,
                    'net_amount' : total_amount - 65,
                }

                return render(request,"customerapp/customer_dashboard.html",context)
            else:
                context = {
                    "uid": uid,
                    "cid": cid,
                    "pid": pid, 
                }
                return render(request, "customerapp/customer_dashboard.html", context)

    else:

        if request.POST:

            email = request.POST['email']
            password = request.POST['password']

            try:
                uid = User.objects.get(email=email)

                password_ok = check_password(password, uid.password)

                # Backward-compat: old accounts created before hashing was added
                # still have a plain-text password. If it matches, accept it
                # once and silently upgrade it to a proper hash.
                if not password_ok and uid.password == password:
                    password_ok = True
                    uid.password = make_password(password)
                    uid.save()

                if password_ok:

                    request.session["email"] = email
                    request.session.cycle_key()  # rotate session id on login (session fixation protection)
                    if uid.role == "seller":
                        sid = seller.objects.get(user_id=uid)
                        pid = product.objects.all()

                        context = {
                            "uid": uid,
                            "sid": sid,
                            "pid": pid,
                        }

                        return render(request,"sellerapp/admin_panel.html",context)

                    elif uid.role == "customer":
                        cid = customer.objects.get(user_id=uid)
                        pid = product.objects.all()

                        context = {
                            "uid": uid,
                            "cid": cid,
                            "pid": pid,
                        }

                        return render(request,"customerapp/customer_dashboard.html",context)

            except:
                return render(request,"sellerapp/login.html")

    return render(request,"sellerapp/login.html")


def admin_panel(request):
    if "email" in request.session:
        uid = User.objects.get(email=request.session["email"])
        if uid.role == "seller":
            sid = seller.objects.get(user_id=uid)
            pid = product.objects.all()
            categories = Category.objects.all()

            context = {
                "uid": uid,
                "sid": sid,
                "pid": pid,
                "categories": categories,
            }
            return render(request, "sellerapp/admin_panel.html", context)
    return HttpResponseRedirect("/seller/login")


def logout(request):
    request.session.flush()   # destroys session data + cycles session key
    return HttpResponseRedirect("/seller/login/")


def update_profile(request):
    if "email" in request.session:
        uid = User.objects.get(email=request.session['email'])

        if uid.role == "seller":
            sid = seller.objects.get(user_id=uid)

            sid.firstname = request.POST['firstname']
            sid.lastname = request.POST['lastname']
            sid.contectno = request.POST['contectno']
            sid.seller_store_name = request.POST['seller_store_name']

            if "pic" in request.FILES:
                sid.pic = request.FILES['pic']

            sid.save()

            pid = product.objects.all()   
            context = {
                "uid": uid,
                "sid": sid,
                "pid": pid,   
            }
            return render(request, "sellerapp/admin_panel.html", context)

    return HttpResponseRedirect("/seller/login")


def add_product(request):
    if "email" in request.session:
        uid = User.objects.get(email=request.session['email'])
        sid = seller.objects.get(user_id=uid)
        pid = product.objects.all()

        if request.method == "POST" and uid.role == "seller":

            category = Category.objects.get(
                id=request.POST['product_category']
            )

            product.objects.create(
                user_id=uid,
                product_name=request.POST['product_name'],
                product_category=category,
                product_price=int(request.POST.get('product_price') or 0),
                stock_qty=int(request.POST.get('stock_qty') or 0),
                picture=request.FILES['picture'],
                description=request.POST.get('description'),
                discount=int(request.POST.get('discount') or 0),
                badge_text=request.POST.get('badge_text'),
                weight_unit=request.POST.get('weight_unit'),
                brand=request.POST.get('brand'),
            )

            messages.success(request, "Product Added Successfully")
            return redirect("view_product")

        context = {
            "uid": uid,
            "sid": sid,
            "pid": pid,
            "categories": Category.objects.all(),
            "active_nav": "addProduct",
        }

        return render(request, "sellerapp/admin_panel.html", context)

    return HttpResponseRedirect("/sellerapp/login/")


def view_product(request):
    if "email" in request.session:
        uid = User.objects.get(email=request.session['email'])
        sid = seller.objects.get(user_id=uid)
        pid = product.objects.all()

        context = {
            "uid": uid,
            "sid": sid,
            "pid": pid,
            "categories": Category.objects.all(),
            "active_nav": "allProducts",  
        }

        return render(request, "sellerapp/admin_panel.html", context)

    return HttpResponseRedirect("/seller/login/")


def edit_product(request, pid):
    
    if "email" not in request.session:
        return HttpResponseRedirect("/seller/login")

    uid = User.objects.get(email=request.session['email'])
    sid = seller.objects.get(user_id=uid)
    all_products = product.objects.all() 
    
    p = get_object_or_404(product, id=pid)

    if request.method == "POST":
        p.product_name = request.POST['product_name']
        p.product_category = request.POST['product_category']
        p.product_price = request.POST['product_price']
        p.stock_qty = request.POST['stock_qty']
        p.discount = request.POST['discount']
        p.badge_text = request.POST['badge_text']
        p.weight_unit = request.POST['weight_unit']
        p.description = request.POST['description']

        if "picture" in request.FILES:
            p.picture = request.FILES['picture']

        p.save()

    context = {
        "p": p,
        "uid": uid,
        "sid": sid,
        "pid": all_products,  
    }

    return render(request, "sellerapp/admin_panel.html", context)

def delete_product(request, pid):   
    if "email" in request.session:
        p = get_object_or_404(product, id=pid).delete()
        return redirect('admin_panel')
    return HttpResponseRedirect("/seller/login")

def forgot_password(request):
    if request.POST:
        email = request.POST['email']
        try:
            uid = User.objects.get(email = email)
            otp = random.randint(1111,9999)
            uid.otp = otp
            uid.otp_created_at = timezone.now()
            uid.otp_attempts = 0 
            uid.save()
            print("EMAIL:", email)
            myCustomMail("Forgot Password","mail_template",email,{'otp':otp})
            if uid:
                context = {
                    'email' : email,
                }
                return render(request,"sellerapp/reset_password.html",context)
        except:
            context = {
                    'e_msg' : "User Does Not Exits !"
                }
            return render(request,"sellerapp/forgot_password.html",context)
    else:
        return render(request,"sellerapp/forgot_password.html")

def reset_password(request):
    if request.POST:
        otp = request.POST['otp']
        email = request.POST['email']
        newpassword = request.POST['newpassword']
        repassword = request.POST['repassword']

        uid = User.objects.get(email = email)
        # OTP Attempt Limit Check
        if uid.otp_attempts >= 3:
            context = {
                'email': email,
                'e_msg': '❌ Too many wrong OTP attempts. Please resend OTP.'
            }
            return render(request, "sellerapp/reset_password.html", context)
        if uid.otp_created_at:
            if timezone.now() > uid.otp_created_at + timedelta(minutes=1):
                context = {
                    'email': email,
                    'e_msg': 'OTP Expired! Please request a new OTP.'
                }
                return render(request, "sellerapp/reset_password.html", context)
        # Wrong OTP Check
        if otp != str(uid.otp):

            uid.otp_attempts += 1
            uid.save()

            remaining = 3 - uid.otp_attempts

            context = {
                'email': email,
                'e_msg': f'❌ Invalid OTP. {remaining} attempt(s) left.'
            }

            return render(request, "sellerapp/reset_password.html", context)

        if otp == str(uid.otp) and newpassword == repassword:

            ok, reason = is_strong_password(newpassword)
            if not ok:
                context = {
                    'email': email,
                    'e_msg': reason,
                }
                return render(request, "sellerapp/reset_password.html", context)

            uid.password = make_password(newpassword)

            uid.otp = None
            uid.otp_created_at = None
            uid.otp_attempts = 0
            uid.save()
            context = {
                        's_msg' : "Password Change Succsessfully..!"
                    }
            return render(request,"sellerapp/login.html",context)

    return render(request,"sellerapp/login.html")

def change_password(request):

    """
    Lets a LOGGED-IN user (seller or customer) change their own password.
    Requires current password + new password + confirm password.
    """
    if "email" not in request.session:
        return HttpResponseRedirect("/seller/login/")

    uid = User.objects.get(email=request.session['email'])

    def role_context(extra=None):
        ctx = {"uid": uid}
        if uid.role == "seller":
            ctx["sid"] = seller.objects.get(user_id=uid)
            ctx["pid"] = product.objects.all()
            ctx["active_nav"] = "editProfile"
            template = "sellerapp/admin_panel.html"
        else:
            ctx["cid"] = customer.objects.get(user_id=uid)
            ctx["pid"] = product.objects.all()
            ctx["active_page"] = "edit"
            template = "customerapp/customer_dashboard.html"
        if extra:
            ctx.update(extra)
        return template, ctx

    if request.method == "POST":
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        current_ok = check_password(current_password, uid.password) or uid.password == current_password

        if not current_ok:
            template, ctx = role_context({"pwd_e_msg": "Current password is incorrect."})
            return render(request, template, ctx)

        if new_password != confirm_password:
            template, ctx = role_context({"pwd_e_msg": "New password and confirm password do not match."})
            return render(request, template, ctx)

        ok, reason = is_strong_password(new_password)
        if not ok:
            template, ctx = role_context({"pwd_e_msg": reason})
            return render(request, template, ctx)

        uid.password = make_password(new_password)
        uid.save()

        template, ctx = role_context({"pwd_s_msg": "Password changed successfully."})
        return render(request, template, ctx)

    template, ctx = role_context()
    return render(request, template, ctx)


def resend_otp(request, email):

    uid = User.objects.get(email=email)

    otp = random.randint(1111,9999)

    uid.otp = otp
    uid.save()

    myCustomMail(
        "Forgot Password",
        "mail_template",
        email,
        {'otp': otp}
    )

    context = {
        'email': email,
        's_msg': 'New OTP Sent Successfully'
    }

    return render(
        request,
        "sellerapp/reset_password.html",
        context
    )

# ═══════════════════════════════════════════════════════════════════════
# PHASE 2 - CATEGORY MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════

def view_categories(request):
    """View all categories (Seller only)"""
    if "email" not in request.session:
        return HttpResponseRedirect("/seller/login/")

    uid = User.objects.get(email=request.session['email'])
    
    if uid.role != "seller":
        return HttpResponseRedirect("/seller/login/")

    sid = seller.objects.get(user_id=uid)
    categories = Category.objects.all().order_by("id")
    pid = product.objects.all()

    context = {
        "uid": uid,
        "sid": sid,
        "pid": pid,
        "categories": categories,
        "active_nav": "categories",
    }
    return render(request, "sellerapp/admin_panel.html", context)


def add_category(request):
    """Add new category (Seller only)"""
    if "email" not in request.session:
        return HttpResponseRedirect("/seller/login/")

    uid = User.objects.get(email=request.session['email'])
    
    if uid.role != "seller":
        return HttpResponseRedirect("/seller/login/")

    if request.method == "POST":
        category_name = request.POST.get('category_name', '').strip()
        description = request.POST.get('description', '').strip()

        if not category_name:
            context = {
                "uid": uid,
                "sid": seller.objects.get(user_id=uid),
                "pid": product.objects.all(),
                "categories": Category.objects.all(),
                "e_msg": "❌ Category name is required.",
                "active_nav": "addCategory",
            }
            return render(request, "sellerapp/admin_panel.html", context)

        if Category.objects.filter(category_name__iexact=category_name).exists():
            context = {
                "uid": uid,
                "sid": seller.objects.get(user_id=uid),
                "pid": product.objects.all(),
                "categories": Category.objects.all(),
                "e_msg": "❌ Category already exists!",
                "active_nav": "addCategory",
            }
            return render(request, "sellerapp/admin_panel.html", context)

        try:
            new_category = Category(
                category_name=category_name,
                description=description,
            )

            if "category_image" in request.FILES:
                new_category.category_image = request.FILES["category_image"]

            # Image ho ya na ho, save hamesha hoga
            new_category.save()

            messages.success(request, "Category Added Successfully")

            return redirect("view_categories")

        except Exception as e:
            context = {
                "uid": uid,
                "sid": seller.objects.get(user_id=uid),
                "pid": product.objects.all(),
                "categories": Category.objects.all(),
                "e_msg": str(e),
                "active_nav": "addCategory",
            }
            return render(request, "sellerapp/admin_panel.html", context)

    sid = seller.objects.get(user_id=uid)
    pid = product.objects.all()
    categories = Category.objects.all()

    context = {
        "uid": uid,
        "sid": sid,
        "pid": pid,
        "categories": categories,
        "active_nav": "addCategory",
    }
    return render(request, "sellerapp/admin_panel.html", context)


def edit_category(request, cid):

    if "email" not in request.session:
        return HttpResponseRedirect("/seller/login/")

    uid = User.objects.get(email=request.session["email"])

    if uid.role != "seller":
        return HttpResponseRedirect("/seller/login/")

    sid = seller.objects.get(user_id=uid)
    pid = product.objects.all()

    try:
        category = Category.objects.get(id=cid)
    except Category.DoesNotExist:
        return redirect("view_categories")

    if request.method == "POST":

        category_name = request.POST.get("category_name").strip()
        description = request.POST.get("description").strip()

        if category_name == "":
            context = {
                "uid": uid,
                "sid": sid,
                "pid": pid,
                "categories": Category.objects.all(),
                "category": category,
                "e_msg": "Category Name is Required",
                "active_nav": "editCategory",
            }
            return render(request, "sellerapp/admin_panel.html", context)

        if Category.objects.filter(category_name=category_name).exclude(id=cid).exists():
            context = {
                "uid": uid,
                "sid": sid,
                "pid": pid,
                "categories": Category.objects.all(),
                "category": category,
                "e_msg": "Category Already Exists",
                "active_nav": "editCategory",
            }
            return render(request, "sellerapp/admin_panel.html", context)

        category.category_name = category_name
        category.description = description

        if "category_image" in request.FILES:
            category.category_image = request.FILES["category_image"]

        category.save()
        messages.success(request,"Category Updated Successfully")
        return redirect("edit_category", cid=category.id)

    context = {
        "uid": uid,
        "sid": sid,
        "pid": pid,
        "categories": Category.objects.all(),
        "category": category,
        "active_nav": "editCategory",
    }

    return render(request, "sellerapp/admin_panel.html", context)

def delete_category(request, cid):
    """Delete category (Seller only)"""
    if "email" not in request.session:
        return HttpResponseRedirect("/seller/login/")

    uid = User.objects.get(email=request.session['email'])
    
    if uid.role != "seller":
        return HttpResponseRedirect("/seller/login/")

    try:
        category = Category.objects.get(id=cid)
        category.delete()
    except Category.DoesNotExist:
        pass

    return redirect("view_categories")