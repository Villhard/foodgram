from django.contrib import admin
from django.urls import include, path

from backend.views import get_recipe_by_short_link

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('rec/<str:link>/', get_recipe_by_short_link),
]
