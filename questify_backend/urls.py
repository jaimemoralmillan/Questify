from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from api.views import TaskViewSet, UserProfileViewSet  # Import UserProfileViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'profile', UserProfileViewSet, basename='userprofile')  # Register UserProfileViewSet

urlpatterns = [
    path('', RedirectView.as_view(url='/api/tasks/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls))
]
