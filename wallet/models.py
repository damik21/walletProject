from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

CURRENCY_CHOICES = (
    ('RUB', 'Ruble'),
    ('USD', 'US Dollar'),
    ('EUR', 'Euro'),
)


class UserProfile(models.Model):
    """User Profile"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def post_save_user(sender, **kwargs):
    user = kwargs.get('instance')
    if kwargs.get('created'):
        user_profile = UserProfile.objects.create(user=user)
        for curr in CURRENCY_CHOICES:
            Wallet.objects.create(user=user_profile, currency=curr[0])


class Wallet(models.Model):
    """Wallet"""

    user = models.ForeignKey('UserProfile', on_delete=models.PROTECT)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='RUB')
    amount = models.FloatField('Amount', default=0.0)

    class Meta:
        unique_together = ['user', 'currency']

    def __str__(self):
        return self.user.user.username + " " + self.currency


class Currency(models.Model):
    """Currency"""

    name = models.CharField('Name', max_length=64)
    char_code = models.CharField(max_length=3, db_index=True)
    value = models.FloatField('Value')
    date_update = models.DateField('Updated')
    nominal = models.IntegerField('Nominal', default=1)
    nominal_value = models.FloatField('Nominal Value', default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Currencies'
        unique_together = ['char_code', 'date_update']


class Transaction(models.Model):
    """Transaction"""

    wallet_from = models.ForeignKey('Wallet', on_delete=models.PROTECT, null=True,
                                    related_name='outcoming_transactions')
    wallet_to = models.ForeignKey('Wallet', on_delete=models.PROTECT, null=True,
                                  related_name='incoming_transactions')
    amount = models.FloatField('Amount', default=0.0)
    created_on = models.DateTimeField(auto_now_add=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='RUB')

    def __str__(self):
        return "{:.2f} {} : {} -> {}, at {} ".format(self.amount, self.currency, self.wallet_from, self.wallet_to,
                                                self.created_on)
