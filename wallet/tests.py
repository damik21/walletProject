from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from . import tasks


class CurrencyTestCase(APITestCase):
    ok = status.HTTP_200_OK
    not_found = status.HTTP_404_NOT_FOUND
    token = ''
    rub_wallet_amount = ''
    usd_wallet_amount = ''
    eur_wallet_amount = ''

    def setUp(self):
        tasks.update_currency()
        self.client.post("/auth/users/", {'username': 'John', 'password': 'Smith123456'})
        response = self.client.post("/auth/token/login/", {'username': 'John', 'password': 'Smith123456'})
        self.token = 'Token ' + response.json()['auth_token']

        self.client.post(
            reverse('my_wallet', kwargs={'currency': 'RUB'}), {'operation': 'fill', 'amount': '1000000'},
            HTTP_AUTHORIZATION=self.token)

        self.client.post(
            reverse('my_wallet', kwargs={'currency': 'EUR'}), {'operation': 'fill', 'amount': '1000000'},
            HTTP_AUTHORIZATION=self.token)

        self.client.post(
            reverse('my_wallet', kwargs={'currency': 'USD'}), {'operation': 'fill', 'amount': '1000000'},
            HTTP_AUTHORIZATION=self.token)

        self.rub_wallet_amount = float(self.client.get(reverse('my_wallet', kwargs={'currency': 'RUB'}),
                                                       HTTP_AUTHORIZATION=self.token).json()['amount'])
        self.usd_wallet_amount = float(self.client.get(reverse('my_wallet', kwargs={'currency': 'USD'}),
                                                       HTTP_AUTHORIZATION=self.token).json()['amount'])
        self.eur_wallet_amount = float(self.client.get(reverse('my_wallet', kwargs={'currency': 'EUR'}),
                                                       HTTP_AUTHORIZATION=self.token).json()['amount'])

    def test_positive_wallet_convert_usd_to_rub(self):
        convert_amount = 1

        response = self.client.post(reverse('my_wallet_convert', kwargs={'currency_from': 'USD'}),
                                    {'currency_to': 'RUB', 'amount': convert_amount},
                                    HTTP_AUTHORIZATION=self.token)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(float(response.json()['new amount from']), self.usd_wallet_amount - convert_amount)
        self.assertTrue(float(response.json()['new amount to']) > self.rub_wallet_amount)

    def test_negative_wallet_convert_usd_to_rub(self):
        convert_amount = self.usd_wallet_amount + 1

        response = self.client.post(reverse('my_wallet_convert', kwargs={'currency_from': 'USD'}),
                                    {'currency_to': 'RUB', 'amount': convert_amount},
                                    HTTP_AUTHORIZATION=self.token)

        new_rub_wallet_amount = float(self.client.get(reverse('my_wallet', kwargs={'currency': 'RUB'}),
                                                      HTTP_AUTHORIZATION=self.token).json()['amount'])
        new_usd_wallet_amount = float(self.client.get(reverse('my_wallet', kwargs={'currency': 'USD'}),
                                                      HTTP_AUTHORIZATION=self.token).json()['amount'])

        self.assertEquals(response.status_code, 403)
        self.assertEquals(response.json(), 'You don\'t have enough money')
        self.assertEquals(self.usd_wallet_amount, new_usd_wallet_amount)
        self.assertEquals(self.rub_wallet_amount, new_rub_wallet_amount)
