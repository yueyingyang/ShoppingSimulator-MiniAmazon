from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Package, Warehouse
from .forms import queryStatus
import socket

AMAZON_HOST, AMAZON_PORT = "vcm-12347.vm.duke.edu", 23333

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
                s = connect_amazon()
                print("================== socket =================")
                print(s)
                with s:
                    s.sendall(str(pkg.id).encode('utf-8'))
                    # to be more robust
                    print("finish sending")
                return redirect('home')
            else:
                return redirect('display')   
    context = {'products': products}
    return render(request, 'frontEndServer/display.html', context)

# Create your views here.

def connect_amazon():
    amazon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    amazon_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        amazon_socket.connect((AMAZON_HOST, AMAZON_PORT))
        print('Connected to Amazon backend')
        return amazon_socket
    except:
        print('Failed to connect to Amazon backend')


def query_status(request):
    form = queryStatus()
    if request.method == 'POST':
        # if use pkg id to query
        if 'ups' in request.POST:
            # filter in db
            return redirect('query')
        # if use ups account to query
        if 'pkg' in request.POST:
            # filter in db
            return redirect('query')
    context = {}
    return render(request, 'frontEndServer/query.html', context)

