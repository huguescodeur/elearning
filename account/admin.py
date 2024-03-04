from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .models import Apprenant
from .models import Formateur


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        ('Roles', {'fields': ('role',)}),
        (None, {'fields': ('username', 'email', 'password')}),
        ('Informations personnelles', {'fields': ('nom', 'first_name', 'last_name', 'image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Dates importantes', {'fields': ('last_login',)}),
    )
    list_display = ('username', 'email', 'password', 'role', 'nom', 'date_joined', 'first_name', 'last_name',
                    'is_staff', 'is_active', 'is_superuser', 'last_login', 'image')
    search_fields = ('username', 'nom', 'role')
    list_filter = ('role', 'is_staff', 'is_superuser', 'groups', 'user_permissions')


class ApprenantAdmin(admin.ModelAdmin):
    list_display = ('nom_apprenant', 'user', 'is_premium')
    search_fields = ('nom_apprenant', 'user__username')
    list_filter = ('is_premium',)


class FormateurAdmin(admin.ModelAdmin):
    list_display = ('nom_formateur', 'user')
    search_fields = ('nom_formateur', 'user__username')


admin.site.register(User, UserAdmin)
admin.site.register(Apprenant, ApprenantAdmin)
admin.site.register(Formateur, FormateurAdmin)
