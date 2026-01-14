from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Informações VBMonitor', {
            'fields': ('perfil', 'ativo', 'dois_fatores'),
        }),
    )
    list_display = ('username', 'email', 'perfil', 'ativo', 'is_staff')
    list_filter = ('perfil', 'ativo', 'is_staff', 'is_superuser')

admin.site.register(Usuario, UsuarioAdmin)