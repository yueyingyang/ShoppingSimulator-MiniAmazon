from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Package, Warehouse, my_user
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
import socket

AMAZON_HOST, AMAZON_PORT = "vcm-13522.vm.duke.edu", 23333

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
    products = Product.objects.all().order_by('id')
    showid = None
    error = None
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
                if request.POST['addr_x'] == "" or request.POST['addr_y'] == "":
                    context = {'products': products, 'showid':None, 'error': "Please enter address!"}
                    return render(request, 'frontEndServer/display.html', context) 
                pkg = Package.objects.create(item_str = buy_str, user=request.user, addr_x=request.POST['addr_x'], addr_y=request.POST['addr_y'])
                pkg.save()
                print(pkg.id)
                showid = pkg.id
                if 'ups' in request.POST and request.POST['ups'] != '':
                    Package.objects.filter(id = showid).update(upsAccount = request.POST['ups'])  
                try:
                    s = connect_amazon()
                    print("================== socket =================")
                    print(s)
                    with s:
                        s.sendall(str(pkg.id).encode('utf-8'))
                        # to be more robust
                        print("finish sending")
                except BaseException as e:
                    context = {'products': products, 'showid':None, 'error': "Please check Amazon server is running and AMAZON_HOST in views.py."}
                    return render(request, 'frontEndServer/display.html', context) 
            else:
                error = 'Please select at least one product.'
    context = {'products': products, 'showid':showid, 'error': error}
    return render(request, 'frontEndServer/display.html', context)


def connect_amazon():
    amazon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    amazon_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # try:
    amazon_socket.connect((AMAZON_HOST, AMAZON_PORT))
    print('Connected to Amazon backend')
    return amazon_socket
    # except:
    #     print('Failed to connect to Amazon backend')

pid = None
uid = None

@login_required
def query_status(request):
    info1 = None
    info2 = None
    info3 = None
    msg_pkg = None
    msg_ups = None
    global pid
    global uid
    if request.method == 'POST':
        if 'button1' in request.POST:
            if 'pkg' in request.POST and request.POST['pkg'] != '':
                try:
                    if Package.objects.filter(user = request.user, id = request.POST['pkg']).exists():
                        pid = request.POST['pkg']
                        info1 = Package.objects.get(id = pid)
                    else:
                        msg_pkg = 'Sorry. This package ID #' + request.POST['pkg'] + ' is not found.'
                except:
                    msg_pkg = 'Sorry. Your input is not a number.'

        if 'button2' in request.POST:
            if 'ups' in request.POST and request.POST['ups'] != '': 
                print("*********************UPS Account********************")
                print(request.POST['ups']) 
                if Package.objects.filter(user = request.user, upsAccount = request.POST['ups']).exists():
                    uid = request.POST['ups']
                    print("*********************UPS Account********************")
                    print(uid)
                    it = Package.objects.filter(user = request.user, upsAccount = uid).values('id').order_by('-id')
                    print("*********************UPS package********************")
                    print(it)
                    info2 = []
                    for value in it:
                        info2.append(Package.objects.get(id = value['id']))  
                else:
                    msg_ups = 'Sorry. This UPS account #' + request.POST['ups'] + ' is not found.'
        
        if 'return1' in request.POST:
            Package.objects.filter(id = pid).update(status = 9)
            msg_pkg = 'Your Package #' + pid +' has been cancelled Successfuly.'
      
        if 'return2' in request.POST:
            if 'ups_cancel_check' in request.POST and request.POST['ups_cancel_check'] != '':
                print("******************************UPS Cancel******************************")
                print(request.POST.getlist('ups_cancel_check'))
                print("******************************UPS Cancel End**************************")
                pid_list = request.POST.getlist('ups_cancel_check')
                for thisid in pid_list:
                    Package.objects.filter(id = thisid).update(status = 9)
                pid_str = ', '.join(pid_list)
                msg_ups = 'Your package #' + pid_str +' has been cancelled Successfuly.'
            else:
                msg_ups = 'No package is cancelled.'

    all_order = Package.objects.filter(user = request.user).values('id').order_by('-id')
    if all_order.exists():
        info3 = []
        for value in all_order:
            info3.append(Package.objects.get(id = value['id']))
    context = {'info1': info1, 'msg_pkg' : msg_pkg,'info2': info2, 'msg_ups' : msg_ups, 'info3': info3}
    return render(request, 'frontEndServer/query.html', context)

@login_required
def PrimeRegiseterView(request):
    # if not prime member, go to prime_register page
    user = request.user
    prime = my_user.objects.get(email = user).prime
    msg = None
    if not prime:
        if request.method == 'POST':
            if 'prime' in request.POST:
                try:
                    my_user.objects.filter(email = user).update(prime = True)
                    msg = 'Cong! You have been successfully registered!'
                except:
                    msg = 'Register error.'
    else:
        msg = 'You are a Prime member now.'
    context = {'msg': msg}
    return render(request, 'frontEndServer/prime_register.html', context)
            
