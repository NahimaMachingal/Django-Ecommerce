from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from .models import Account, UserProfile, Address, Wallet

# Register your models here.
class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined','is_active',  )
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class AddressAdmin(admin.ModelAdmin):
    list_display = ('street_address', 'city', 'state', 'country', 'phone_number')

class WalletAdmin(admin.ModelAdmin):
    list_display = ('account', 'wallet_balance' )

admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile)  # No need for UserProfileAdmin if no customization required
admin.site.register(Address, AddressAdmin)
admin.site.register(Wallet, WalletAdmin)