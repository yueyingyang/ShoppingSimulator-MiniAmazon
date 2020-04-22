from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Package, Warehouse
# from .forms import 
import socket


def home(request):
    return render(request, 'frontEndServer/home.html', {})

def buy(request):
    model = Product
    products = Product.objects.all()
    if request.method == 'POST':
        if 'checkout' in request.POST:
            if 'choose' in request.POST: 
                print("========the item is========")
                print(request.POST.getlist('choose'))
                print(request.POST.getlist('count'))
                print("===========================")
                choose_list = request.POST.getlist('choose')
                count_list = request.POST.getlist('count')
                buy_list = []
                for item in request.POST.getlist('choose'):
                    buyid = item
                    des = Product.objects.get(id=item).description
                    # count = count_list[choose_list.index(item)]
                    count = count_list[int(item)-1]
                    thistuple = (buyid, des, count)
                    buy_list.append(",".join(thistuple))
                buy_str = ";".join(buy_list)
                print("buy_str: " + buy_str)
                # add to db
                pkg = Package.objects.create(item_str = buy_str)
                pkg.save()
                print(pkg.id)
                # send(amazon_socket, buy_str)
                return redirect('home')
            else:
                return redirect('display')   
    context = {'products': products}
    return render(request, 'frontEndServer/display.html', context)

# Create your views here.
