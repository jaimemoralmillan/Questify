from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from api.views import TaskViewSet, UserProfileViewSet, UserViewSet  # Import UserViewSet
from rest_framework.authtoken import views as authtoken_views

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'profile', UserProfileViewSet, basename='userprofile')  # Register UserProfileViewSet
router.register(r'users', UserViewSet, basename='user')  # Register UserViewSet

urlpatterns = [
    path('', RedirectView.as_view(url='/api/tasks/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-token-auth/', authtoken_views.obtain_auth_token),  # Add this line
]
