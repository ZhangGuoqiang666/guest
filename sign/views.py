from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from sign.models import Event

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
            print(type(user))
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
