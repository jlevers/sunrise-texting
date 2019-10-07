from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('textin/', include('textin.urls'), name='textin'),
    path('', lambda r: redirect('textin/'), name='root_redirect')
]
