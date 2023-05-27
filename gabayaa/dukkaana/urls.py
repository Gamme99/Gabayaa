from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('', views.base, name='base'),
    path('shoes', views.shoes, name='shoes'),
    path('cloths', views.cloths, name='cloths'),
    path('electronics', views.electronics, name='electronics'),
    path('renting', views.renting, name='renting'),
    path('buying', views.buying, name='buying'),
    path('manager/add_shoe', views.add_shoe, name='add_shoe'),
    path('manager/add_cloth', views.add_cloth, name='add_cloth'),
    path('manager/add_electronic', views.add_electronic, name='add_electronic'),
    path('manager', views.manager, name='manager'),
    path('login', views.login, name='login'),
    # path('login', auth_views.LoginView.as_view(), name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logoutManager, name='logout'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)