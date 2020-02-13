# from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render, get_object_or_404

from django.contrib import auth
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from sign.models import Event
from sign.models import Guest


def index(request):
    return render(request, "index.html")


def login_action(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        print(username, password)
        # user = auth.authenticate(username=username, password=password)
        # if user is not None:
        #     auth.login(request, user)

        user = auth.authenticate(password = password, username = username)
        # if username == 'admin' and password == 'admin123':
        if user is not None:
            print(user)
            # print(type(user))
            auth.login(request, user)
            # v1.0
            # return HttpResponse('login success')

            # v2.0
            # return HttpResponseRedirect('/event_manage/')
            # request.session['user'] = username  # 将session信息记录到浏览器

            # v3.0 cookie
            response = HttpResponseRedirect('/event_manage/')
            #response.set_cookie('user', username, 3600)  # 添加浏览器cookie

            request.session['user'] = username  # 将session信息记录到浏览器
            return response
        else:
            print(user)
            return render(
                request, 'index.html', {
                    'error': 'username or password error!'})


# 发布会管理
@login_required
def event_manage(request):

    # username = request.session.get("user", '')
    #username = request.POST.get('username','')

    # v1.0 no cookie and session
    # return render(request, 'event_manage.html')

    # v2.0 读取cookie
    #username = request.COOKIES.get("user", '')

    #v3.0 读取session

    event_list = Event.objects.all()
    username = request.session.get("user", '')
    return render(request, "event_manage.html", {"user": username,
                                                 "events": event_list})


@login_required
def search_name(request):
    username = request.session.get('user', '')
    search_name = request.GET.get('name', '')
    event_list = Event.objects.filter(name__contains=search_name)
    return render(request, 'event_manage.html', {"user": username,
                                                 "events":event_list})

# 嘉宾管理
@login_required
def guest_manage(request):

    # username = request.session.get("user", '')
    #username = request.POST.get('username','')

    # v1.0 no cookie and session
    # return render(request, 'event_manage.html')

    # v2.0 读取cookie
    #username = request.COOKIES.get("user", '')

    #v3.0 读取session

    guest_list = Guest.objects.all()
    username = request.session.get("user", '')

    paginator = Paginator(guest_list,2)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # 如果页数不是整型, 取第一页.
        contacts = paginator.page(1)
    except EmptyPage:
        # 如果页数超出查询范围，取最后一页
        contacts = paginator.page(paginator.num_pages)
    return render(request, "guest_manage.html", {"user": username,
                                                 "guests": contacts})

#嘉宾签到页面
@login_required
def sign_index(request, eid):
    event = get_object_or_404(Event, id=eid)
    return render(request, 'sign_index.html', {'event': event})


# 签到动作
@login_required
def sign_index_action(request, eid):

    event = get_object_or_404(Event, id=eid)
    guest_list = Guest.objects.filter(event_id=eid)
    guest_data = str(len(guest_list))
    sign_data = 0   #计算发布会“已签到”的数量
    for guest in guest_list:
        if guest.sign == True:
            sign_data += 1

    phone =  request.POST.get('phone','')

    result = Guest.objects.filter(phone = phone)
    if not result:
        return render(request, 'sign_index.html', {'event': event,'hint': 'phone error.','guest':guest_data,'sign':sign_data})

    result = Guest.objects.filter(phone = phone,event_id = eid)
    if not result:
        return render(request, 'sign_index.html', {'event': event,'hint': 'event id or phone error.','guest':guest_data,'sign':sign_data})

    result = Guest.objects.get(event_id = eid,phone = phone)

    if result.sign:
        return render(request, 'sign_index.html', {'event': event,'hint': "user has sign in.",'guest':guest_data,'sign':sign_data})
    else:
        Guest.objects.filter(event_id = eid,phone = phone).update(sign = '1')
        return render(request, 'sign_index.html', {'event': event,'hint':'sign in success!',
            'user': result,
            'guest':guest_data,
            'sign':str(int(sign_data)+1)
            })


'''
get方法是从数据库的取得一个匹配的结果，返回一个对象，如果记录不存在的话，它会报错。
filter方法是从数据库的取得匹配的结果，返回一个对象列表，如果记录不存在的话，它会返回[]。
'''

#退出登录
@login_required
def logout(request):
    auth.logout(request)
    response = HttpResponseRedirect('/index/')
    return response