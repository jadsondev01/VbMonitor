from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as auth_views
from .views import UsuarioViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', auth_views.obtain_auth_token, name='login'),
    path('logout/', auth_views.obtain_auth_token, name='logout'),  # Placeholder
]