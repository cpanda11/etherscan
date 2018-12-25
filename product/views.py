from django.shortcuts import redirect

from product.tasks import scrap_ledu


def scrap(request):
    scrap_ledu.delay()
    return redirect('/')
