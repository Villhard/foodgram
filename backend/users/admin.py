from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models import Subscription

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username')
    search_fields = ('email', 'username')
    readonly_fields = ('date_joined', 'last_login')


admin.site.register(Subscription)
