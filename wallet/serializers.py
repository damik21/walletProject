from .models import Wallet
from rest_framework import serializers


class WalletSerializer(serializers.ModelSerializer):
    """Currency"""

    class Meta:
        model = Wallet
        fields = ('currency', 'amount')
