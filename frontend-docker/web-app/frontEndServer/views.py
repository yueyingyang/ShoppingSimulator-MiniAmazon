from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Package, Warehouse, my_user
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
import socket

AMAZON_HOST, AMAZON_PORT = "vcm-12347.vm.duke.edu", 23333

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
                if 'ups' in request.POST and request.POST['ups'] != '':
                    Package.objects.filter(id = showid).update(upsAccount = request.POST['ups'])  
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

pid = None
uid = None

@login_required
def query_status(request):
    info1 = None
    info2 = None
    msg_pkg = None
    msg_ups = None
    global pid
    global uid
    if request.method == 'POST':
        #if use pkg id to query
        if 'button1' in request.POST:
            if 'pkg' in request.POST and request.POST['pkg'] != '':  
                if Package.objects.filter(id = request.POST['pkg']).exists():
                    pid = request.POST['pkg']
                    info1 = Package.objects.get(id = request.POST['pkg'])
                else:
                    msg_pkg = 'Sorry. Not Found.'

        if 'button2' in request.POST:
            if 'ups' in request.POST and request.POST['ups'] != '': 
                print("*********************UPS Account********************")
                print(request.POST['ups']) 
                if Package.objects.filter(upsAccount = request.POST['ups']).exists():
                    uid = request.POST['ups']
                    print("*********************UPS Account********************")
                    print(uid)
                    it = Package.objects.filter(upsAccount = uid).values('id')
                    print("*********************UPS package********************")
                    print(it)
                    info2 = []
                    for value in it:
                        info2.append(Package.objects.get(id = value['id']))
                    
                else:
                    msg_ups = 'Sorry. Not Found.'
        
        if 'return1' in request.POST:
            Package.objects.filter(id = pid).update(status = 9)
            msg_pkg = 'Your Package #' + pid +' has been cancelled Successfuly.'
      
        if 'return2' in request.POST:
            Package.objects.filter(id = uid).update(status = 9)
            msg_ups = 'Your Package #' + uid +' has been cancelled Successfuly.'

    context = {'info1': info1, 'msg_pkg' : msg_pkg,'info2': info2, 'msg_ups' : msg_ups}
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
                my_user.objects.filter(email = user).update(prime = True)
                msg = 'Cong! You have been successfully registered!'
    else:
        msg = 'You are a Prime member now.'
    context = {'msg': msg}
    return render(request, 'frontEndServer/prime_register.html', context)
            
#     # else go to prime_detail page

#     if not vehicle.objects.filter(driver=request.user).exists():
#         if request.method == 'POST':
#             form = DriverRegisterForm(request.POST)  # request.user.id,
#             if form.is_valid():
#                 fs = form.save()
#                 fs.driver = request.user
#                 fs.save()
#                 return redirect('prime_detail')
#         else:
#             form = DriverRegisterForm()
#         return render(request, 'frontEndServer/prime_register.html', {'form': form})
#     else:
#         return redirect('prime_detail')
