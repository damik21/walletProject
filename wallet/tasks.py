from __future__ import absolute_import, unicode_literals
from datetime import datetime
import xml.etree.ElementTree as ET
import requests
from .models import Currency
from celery import shared_task


@shared_task()
def update_currency():
    req = requests.get("http://www.cbr.ru/scripts/XML_daily_eng.asp")
    if req.ok:
        root = ET.fromstring(req.text)
        date = root.attrib.get('Date')
        date_update = datetime.strptime(date, '%d.%m.%Y').date()
        date_currencies = Currency.objects.filter(date_update=date_update)
        if not date_currencies:
            for item in root.findall('Valute'):
                nominal = int(item.find('Nominal').text)
                nominal_value = float(item.find('Value').text.replace(',', '.'))
                Currency.objects.create(
                    char_code=item.find('CharCode').text,
                    name=item.find('Name').text,
                    nominal=nominal,
                    nominal_value=nominal_value,
                    value=nominal_value / nominal,
                    date_update=date_update,
                )
            Currency.objects.create(
                char_code='RUB',
                name='Russian Ruble',
                nominal=1,
                nominal_value=1,
                value=1,
                date_update=date_update,
            )
