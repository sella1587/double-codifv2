from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from core.models import Ouvrage, OuvrageGroupe, OuvrageAd

@admin.register(Ouvrage)
class ClientAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('ouvrage', 'schema_name','code_client','is_active')

@admin.register(OuvrageGroupe)
class OuvrageGroup(admin.ModelAdmin):
    list_display  = ('ouvrage', 'groupe', 'droit')

@admin.register(OuvrageAd)
class groupList(admin.ModelAdmin):
    list_display = ("name_ad", "description")

admin.sites.AdminSite.site_title = "Double Codif Admin"
admin.site.site_header = "Double Codif Admin"

admin.site.site_title ="Administration Double Codification"
admin.site.index_title = "Admin Double Codification"


# admin.site.register(LDAPBackend)