#!/usr/bin/env python
# -*- coding: utf-8 -*-
# $Id: forms.py 3467 2024-04-21 08:31:00Z Claire $
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

from django import forms
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class SignupForm(UserCreationForm):

    username = forms.CharField(
        label='帳號', widget=forms.TextInput(attrs={
            'placeholder': '請輸入帳號',
            'class': 'myPlaceholder'
        })
    )
    email = forms.CharField(
        label='信箱', widget=forms.TextInput(attrs={
            'placeholder': '請輸入信箱',
            'class': 'myPlaceholder'
        })
    )
    password1 = forms.CharField(
        label='密碼', widget=forms.PasswordInput(attrs={
            'placeholder': '至少8碼，不能全為數字',
            'class': 'myPlaceholder'
        })
    )
    password2 = forms.CharField(
        label='確認密碼', widget=forms.PasswordInput(attrs={
            'placeholder': '請輸入密碼以確認',
            'class': 'myPlaceholder'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("此帳號已被註冊！請檢查後再輸入")
        return username

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")

        if len(password1) < 8:
            raise ValidationError("密碼太短！請至少輸入 8 個字符。")

        if password1.isdigit():
            raise ValidationError("密碼不能全為數字！")
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 != password2:
            raise ValidationError("密碼確認未通過！")
        return password2


class LoginForm(forms.Form):
    username = forms.CharField(
        label='帳號', widget=forms.TextInput(attrs={
            'placeholder': '請輸入帳號',
            'class': 'myPlaceholder'
        })
    )
    password = forms.CharField(
        label='密碼', widget=forms.PasswordInput(attrs={
            'placeholder': '請輸入密碼',
            'class': 'myPlaceholder'
        })
    )


class PasswordForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = '請輸入現在的密碼'
        self.fields['new_password1'].label = '請輸入新密碼'
        self.fields['new_password2'].label = '再次輸入新密碼'
        self.fields['old_password'].widget.attrs.update({'class': 'myPlaceholder'})
        self.fields['new_password1'].widget.attrs.update({'class': 'myPlaceholder'})
        self.fields['new_password2'].widget.attrs.update({'class': 'myPlaceholder'})

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):
            raise ValidationError("原密碼輸入錯誤！")
        return old_password

    def clean(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if len(password1) < 8:
            raise ValidationError("密碼太短！請至少輸入 8 個字符。")

        if password1.isdigit():
            raise ValidationError("密碼不能全為數字！")

        if password1 != password2:
            raise ValidationError("密碼確認未通過！")
