from datetime import date

from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Currency, Wallet, Transaction
from .serializers import WalletSerializer


def get_wallets_and_rate(username_from, currency_from, currency_to, username_to=False):
    """
        :returns wallet_from, wallet_to, rate
    """
    wallet_queryset = Wallet.objects.all()
    currency_queryset = Currency.objects.all()
    today = date.today()
    last_date = currency_queryset.last().date_update
    if today < last_date:
        currency_queryset = Currency.objects.exclude(date_update=last_date)
        last_date = currency_queryset.last().date_update

    user = get_object_or_404(User.objects.all(), username=username_from)

    currency_from_charcode = currency_from.upper()
    currency_to_charcode = currency_to.upper()

    wallet_from = get_object_or_404(wallet_queryset, currency=currency_from_charcode, user=user.profile)
    if username_to:
        user = get_object_or_404(User.objects.all(), username=username_to)
    wallet_to = get_object_or_404(wallet_queryset, currency=currency_to_charcode, user=user.profile)

    currency_from = get_object_or_404(currency_queryset, char_code=currency_from_charcode, date_update=last_date)
    currency_to = get_object_or_404(currency_queryset, char_code=currency_to_charcode, date_update=last_date)

    return wallet_from, wallet_to, (currency_from.value / currency_to.value)


def take_from_wallet(wallet, amount):
    if wallet.amount >= amount:
        wallet.amount -= amount
        wallet.save()
        return True
    return False


def create_transaction(amount, wallet_from=None, wallet_to=None, rate=False):
    """
        :returns
            None if all is ok,
            -1 if don't have any wallet
            -2 if don't have enough money on wallet from
    """

    if not (wallet_to or wallet_from):
        return -1
    if wallet_from:
        if not take_from_wallet(wallet_from, amount):
            return -2
    if wallet_to:
        if rate:
            amount = rate * amount
        fill_wallet(wallet_to, amount)
    currency = wallet_from.currency if wallet_from else wallet_to.currency
    Transaction.objects.create(wallet_to=wallet_to, wallet_from=wallet_from, amount=amount, currency=currency)


def fill_wallet(wallet, amount):
    wallet.amount += amount
    wallet.save()


class MyWalletAPIView(APIView):
    """
        My Wallet Operations

        :parameter currency - Char code of Currency
        :parameter operation - Only 'fill' and 'take', else 404
        :parameter amount - Float

        :returns new Amount if all is OK
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, currency):
        queryset = Wallet.objects.all()
        user = get_object_or_404(User.objects.all(), username=request.user.username)
        currency = currency.upper()
        wallet = get_object_or_404(queryset, currency=currency, user=user.profile)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data, status=200)

    def post(self, request, currency):
        operation = request.POST.get('operation')
        amount = request.POST.get('amount')
        try:
            amount = float(amount)
        except Exception as e:
            raise Exception(e)

        if not (operation and amount):
            return Response('Need operation and amount parameters', status=403)

        if operation not in ['fill', 'take']:
            return Response(' Operation can be \'fill\' or \'take\' ', status=404)
        if amount < 0:
            return Response('Amount should be positive ', status=403)

        queryset = Wallet.objects.all()
        user = get_object_or_404(User.objects.all(), username=request.user.username)
        currency = currency.upper()
        wallet = get_object_or_404(queryset, currency=currency, user=user.profile)
        if operation == 'fill':
            create_transaction(wallet_to=wallet, amount=amount)
        else:
            if create_transaction(wallet_from=wallet, amount=amount) == -2:
                return Response("You don't have enough money", status=403)
        result_dict = {
            'new amount': wallet.amount,
        }
        return Response(result_dict)


class MyWalletConvertAPIView(APIView):
    """
        My Wallet Convert Operation

        :parameter currency_from - Char code of Currency From
        :parameter currency_to - Char code of Currency To
        :parameter amount - Amount of From Currency

        :returns new Amount of 2 Wallets if all is OK
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, currency_from):
        currency_to = request.POST.get('currency_to')
        amount = request.POST.get('amount')
        try:
            amount = float(amount)
        except Exception as e:
            raise Exception(e)

        if not (currency_to and amount):
            return Response('Need operation and amount parameters', status=403)
        if amount < 0:
            return Response('Amount should be positive ', status=403)

        wallet_from, wallet_to, rate = get_wallets_and_rate(username_from=request.user.username,
                                                            currency_from=currency_from,
                                                            currency_to=currency_to, )

        if create_transaction(wallet_from=wallet_from, wallet_to=wallet_to, amount=amount, rate=rate) == -2:
            return Response("You don't have enough money", status=403)
        result_dict = {
            'new amount from': wallet_from.amount,
            'new amount to': wallet_to.amount,
        }
        return Response(result_dict)


class MyWalletTransferAPIView(APIView):
    """
        My Wallet Transfer Operation

        :parameter currency_from - Currency of sender Wallet
        :parameter user_to - recipient User
        :parameter currency_to - Currency of recipient Wallet
        :parameter amount - Amount of Transfer

        :returns new Amount of your Wallet
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, currency_from):
        user_to = request.POST.get('user_to')
        currency_to = request.POST.get('currency_to')
        amount = request.POST.get('amount')
        try:
            amount = float(amount)
        except Exception as e:
            raise Exception(e)

        if not (currency_to and amount and user_to):
            return Response('Need operation and amount parameters', status=403)
        if amount < 0:
            return Response('Amount should be positive ', status=403)

        wallet_from, wallet_to, rate = get_wallets_and_rate(username_from=request.user.username,
                                                            currency_from=currency_from,
                                                            currency_to=currency_to,
                                                            username_to=user_to, )

        if create_transaction(wallet_from=wallet_from, wallet_to=wallet_to, amount=amount, rate=rate) == -2:
            return Response("You don't have enough money", status=403)
        result_dict = {
            'new amount': wallet_from.amount,
        }
        return Response(result_dict)
