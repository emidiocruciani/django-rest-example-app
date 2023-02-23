"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
"""
from django.urls import path, include

urlpatterns = [
    path('auth/', include('app.auth.urls')),
    path('accounts/', include('app.accounts.urls')),
]
