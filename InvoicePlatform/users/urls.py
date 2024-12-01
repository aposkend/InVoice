#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: urls.py 3467 2024-04-21 08:31:00Z Claire $
#
# Copyright (c) 2024 Nuwa Information Co., Ltd, All Rights Reserved.
#
# Licensed under the Proprietary License,
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at our web site.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# $Author: Claire $
# $Date: 2024-04-21 16:31:00 +0800 (週日, 21 四月 2024) $
# $Revision: 3467 $
from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path('', views.getHomePage, name='getHomePage'),
    path('signup/', views.signUp, name='signup'),
    path('login/', views.logIn, name='login'),
    path('logout/', views.logOut, name='logout'),
    path('password/update', views.changePassword, name='resetPassword'),
]
