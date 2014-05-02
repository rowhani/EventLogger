#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-

from django.views.generic import TemplateView
from django.template import RequestContext
from django.shortcuts import redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
        
class LoginView(TemplateView):

    def get(self, request, *args, **kwargs):  
        if request.user.is_authenticated():
            return redirect('/')
        
        next = request.GET.get("next", "/")        
        return render_to_response('login.html', locals(), context_instance = RequestContext(request))
        
    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        remember = request.POST.get('remember', '0') == '1'
        
        next = request.POST['next'] or "/"
        
        user = authenticate(username=username, password=password, remember=remember)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(next)
            else:
                error = "کاربر غیر فعال است."
                return render_to_response('login.html', locals(), context_instance = RequestContext(request))
        else:
            if not username: username_error = "نام کاریری را وارد کنید."
            if not password: password_error = "گذرواژه را وارد کنید."
            if username and password: error = "نام کاربری یا گذراژه اشتباه وارد شده است."
            return render_to_response('login.html', locals(), context_instance = RequestContext(request))
    
@login_required    
def logout_view(request):
    logout(request)
    return redirect("/")