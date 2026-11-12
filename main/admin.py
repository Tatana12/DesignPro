from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Application


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('full_name',)}),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Category)
admin.site.register(Application)
