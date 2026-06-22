from django.shortcuts import render, redirect
import random
from .models import *
from customerapp.models import *
from django.http import *
from .utils import *

def register(request):
    if request.method == "POST":
        role = request.POST['role']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        contectno = request.POST['contectno']
        

        l1 = ["85ds2", "fd898", "rf965", "tr894", "DS89", "FR789D"]
        password = random.choice(l1) + email[3:7] + contectno[3:6]

        uid = User.objects.create(
            email=email,
            password=password,
            role=role
        )

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
            }

            return render(request,"sellerapp/admin_panel.html",context)

        elif uid.role == "customer":
            cid = customer.objects.get(user_id=uid)
            pid = product.objects.all()

            cart_item = cart.objects.filter(customer=cid)

            if cart_item:

                Cart_obj = cart.objects.get(customer = cid)
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

                if uid.password == password:

                    request.session["email"] = email

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
            context = {
                "uid": uid,
                "sid": sid,
                "pid": pid,
            }
            return render(request, "sellerapp/admin_panel.html", context)
    return HttpResponseRedirect("/seller/login")


def logout(request):
    if "email" in request.session:
        del request.session["email"]
    return HttpResponseRedirect("/seller/login")


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
            product.objects.create(
                user_id=uid,
                product_name=request.POST['product_name'],
                product_category=request.POST['product_category'],
                product_price=request.POST['product_price'],
                stock_qty=request.POST['stock_qty'],
                picture=request.FILES['picture'],
                description=request.POST['description'],
                discount=request.POST['discount'],
                badge_text=request.POST['badge_text'],
                weight_unit=request.POST['weight_unit'],
            )
            return redirect('add_product')  

        context = {
            "uid": uid,
            "sid": sid,
            "pid": pid,
        }
        return render(request, "sellerapp/admin_panel.html", context)
    else:
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
        }
        return render(request, "sellerapp/admin_panel.html", context)

    return HttpResponseRedirect("/seller/login")


def edit_product(request, pid):
    
    if "email" not in request.session:
        return HttpResponseRedirect("/seller/login")

    uid = User.objects.get(email=request.session['email'])
    sid = seller.objects.get(user_id=uid)
    all_products = product.objects.all() 
    
    p = product.objects.get(id=pid)

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
        product.objects.get(id=pid).delete()
        return redirect('admin_panel')
    return HttpResponseRedirect("/seller/login")

def forgot_password(request):
    if request.POST:
        email = request.POST['email']
        try:
            uid = User.objects.get(email = email)
            otp = random.randint(1111,9999)
            uid.otp = otp
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

        if otp == str(uid.otp) and newpassword == repassword:
            uid.password = newpassword
            uid.save()
            context = {
                        's_msg' : "Password Change Succsessfully..!"
                    }
            return render(request,"sellerapp/login.html",context)

    return render(request,"sellerapp/login.html")