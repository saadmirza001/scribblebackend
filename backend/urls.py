"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from Blog.views import *
from django.conf.urls.static import static
from django.conf import settings




urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', SignUp),
    path('api/login/', Login),
    path('api/count/<str:username>/', CountData),
    path('api/likeBlog/<str:username>/<int:blogId>/', LikeBlogbyUser),
    path('api/commentBlog/<str:username>/<int:blogId>/', WriteComment),
    path('api/sendPayRequest/<str:username>/', SendPaymentRequest),
    path('api/write/', WriteBlog),
    path("", Home)
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)