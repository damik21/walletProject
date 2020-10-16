from django.contrib import admin

from wallet.models import Currency, Wallet, UserProfile, Transaction

admin.site.register(Currency)
admin.site.register(Wallet)
admin.site.register(UserProfile)
admin.site.register(Transaction)
