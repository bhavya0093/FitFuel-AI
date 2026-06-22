from django.shortcuts import render
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
    if "email" in request.session:
        del request.session["email"]
    return HttpResponseRedirect("/seller/login")

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
                "cid": cid
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
        products = product.objects.get(id = pk)

        Cart_obj,is_created = cart.objects.get_or_create(customer = cid)

        print("------> Cart customer ::",Cart_obj)
        print("------> Cart customer status ::",is_created) 

        cartItemData,is_created = cartitem.objects.get_or_create(cart=Cart_obj, product=products)

        if is_created:    
            cartItemData.qty += 1
        else:
            cartItemData.qty += 1      
 
        cartItemData.save()

        item = cartitem.objects.filter(cart=Cart_obj)

        total_amount = 0
        for i in item:
            total_amount += i.product.product_price * i.qty

            

        context = {
            'item' : item,
            'total_amount' : total_amount,  
            'net_amount' : total_amount - 65, 
        }

        return render(request, "customerapp/cart.html",context)
    
def view_cart(request):
    if "email" in request.session:
        uid = User.objects.get(email = request.session['email'])
        if uid.role == "customer":
            cid = customer.objects.get(user_id = uid)
            Cart_obj = cart.objects.get (customer = cid)
            item = cartitem.objects.filter(cart=Cart_obj)

            total_amount = 0
            for i in item:
                total_amount += i.product.product_price * i.qty
                
                

            context = {
                'item' : item,
                'total_amount' : total_amount,
                'net_amount' : total_amount - 65 ,
            }

            return render(request, "customerapp/cart.html",context)

def checkout(request):
    if "email" in request.session:
        uid = User.objects.get(email = request.session['email'])
        if uid.role == "customer":
            cid = customer.objects.get(user_id = uid)
            Cart_obj = cart.objects.get (customer = cid)
            item = cartitem.objects.filter(cart=Cart_obj)
            
            total_amount = 0
            for i in item:
                total_amount += i.product.product_price * i.qty

            context = {
                'item' : item,
                'total_amount' : total_amount,
                'net_amount' : total_amount - 65 ,
            }
        return render(request,"customerapp/check_out.html",context)

def payment(request):
    return render(request,"customerapp/payment.html")
