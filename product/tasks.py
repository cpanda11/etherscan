import json
import datetime

from django.utils import timezone

from etherscan.celery import app
from product.models import *


@app.task
def scrap_ledu():
    token = '0x5b26c5d0772e5bbac8b3182ae9a13f9bb2d03765'

    holders_url = 'https://ethplorer.io/service/service.php?refresh=holders&data={token}&page=tab%3Dtab-holders%26pageSize%3D{size}'.format
    res = requests.get(holders_url(token=token, size=1))
    holders_count = json.loads(res.text)['pager']['holders']['total']
    res = requests.get(holders_url(token=token, size=holders_count))
    res = json.loads(res.text)
    for rank, holder in enumerate(res['holders']):
        address, _ = Address.objects.get_or_create(address=holder['address'])
        quantity = holder['balance'] / 100000000
        prev = Holder.objects.filter(address=address).order_by('-id').first()
        if not prev or quantity != prev.quantity:
            change = '%.8f' % ((quantity / prev.quantity - 1) * 100) if prev else 0.0
            prev_quantity = prev.quantity if prev else 0.0
            prev_percentage = prev.percentage if prev else 0.0
            obj = Holder(
                timestamp=datetime.datetime.utcnow().date(),
                rank=rank + 1,
                address=address,
                quantity=quantity,
                percentage=float(holder['share']),
                prev_quantity=prev_quantity,
                prev_percentage=prev_percentage,
                change=change,
            )
            obj.save()
            print(','.join([str(rank + 1), address.address, str(quantity), str(change)]))

    transfers_url = 'https://ethplorer.io/service/service.php?refresh=transfers&data={token}&page=pageSize%3D{size}'.format
    res = requests.get(transfers_url(token=token, size=1))
    transfers_count = json.loads(res.text)['token']['transfersCount']
    res = requests.get(transfers_url(token=token, size=transfers_count))
    res = json.loads(res.text)
    for tx_id, transfer in enumerate(res['transfers']):
        from_address, _ = Address.objects.get_or_create(address=transfer['from'])
        to_address, _ = Address.objects.get_or_create(address=transfer['to'])
        quantity = int(transfer['value']) / 100000000
        timestamp = timezone.make_aware(
            datetime.datetime.utcfromtimestamp(int(transfer['timestamp'])),
            timezone.get_current_timezone())

        transaction, created = Transaction.objects.get_or_create(
            hash=transfer['transactionHash'],
            _from=from_address, _to=to_address,
            timestamp=timestamp, quantity=quantity
        )
        if created:
            print(tx_id + 1, transfer['transactionHash'])
