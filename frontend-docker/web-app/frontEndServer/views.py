from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Package, Warehouse
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import socket

AMAZON_HOST, AMAZON_PORT = "vcm-13659.vm.duke.edu", 23333

def UserRegister(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            return redirect("home")
    else:
        form = UserRegisterForm()
    return render(request, 'frontEndServer/user_register.html', {'form': form})

@login_required
def home(request):
    return render(request, 'frontEndServer/home.html',{})


@login_required
def buy(request):
    model = Product
    products = Product.objects.all()
    showid = None
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
                pkg = Package.objects.create(item_str = buy_str, user=request.user)
                pkg.save()
                print(pkg.id)
                showid = pkg.id
                s = connect_amazon()
                print("================== socket =================")
                print(s)
                with s:
                    s.sendall(str(pkg.id).encode('utf-8'))
                    # to be more robust
                    print("finish sending")
                # return redirect('home')
            else:
                return redirect('buy')   
    context = {'products': products, 'showid':showid}
    return render(request, 'frontEndServer/display.html', context)


def connect_amazon():
    amazon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    amazon_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        amazon_socket.connect((AMAZON_HOST, AMAZON_PORT))
        print('Connected to Amazon backend')
        return amazon_socket
    except:
        print('Failed to connect to Amazon backend')

@login_required
def query_status(request):
    #form = queryStatus()
    info1 = None
    info2 = None
    msg_pkg = None
    msg_ups = None
    if request.method == 'POST':
        #if use pkg id to query
        if 'button1' in request.POST:
            if 'pkg' in request.POST and request.POST['pkg'] != '':  
                if Package.objects.filter(id = request.POST['pkg']).exists():
                    info1 = Package.objects.get(id = request.POST['pkg'])
                else:
                    msg_pkg = 'Sorry. Not Found.'
        if 'button2' in request.POST:
            if 'ups' in request.POST and request.POST['ups'] != '':  
                if Package.objects.filter(upsAccount = request.POST['ups']).exists():
                    info2 = Package.objects.get(upsAccount = request.POST['ups'])
                else:
                    msg_ups = 'Sorry. Not Found.'
    context = {'info1': info1, 'msg_pkg' : msg_pkg,'info2': info2, 'msg_ups' : msg_ups}
    return render(request, 'frontEndServer/query.html', context)

