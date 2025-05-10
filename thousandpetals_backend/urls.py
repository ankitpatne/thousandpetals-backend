"""
URL configuration for thousandpetals_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from news_app.api import router as news_router
from projects_app.api import router as projects_router
from news_app.api import contact_form

api = NinjaAPI()

api.add_router("/news", news_router)
api.add_router("/projects", projects_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("api/news/contact/", contact_form, name="contact_form")
]
