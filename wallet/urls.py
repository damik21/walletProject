from django.urls import path, register_converter
from .utils import converter
from . import views


register_converter(converter.FloatConverter, 'float')

urlpatterns = [
    path('mywallet/<str:currency>/', views.MyWalletAPIView.as_view(), name='my_wallet'),
    path('mywallet/<str:currency_from>/convert/',
         views.MyWalletConvertAPIView.as_view(), name='my_wallet_convert'),
    path('mywallet/<str:currency_from>/transfer/',
         views.MyWalletTransferAPIView.as_view(), name='my_wallet_transfer'),
]
