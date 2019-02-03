from django.shortcuts import render, redirect
from .models import Item
from redis import Redis


redis = Redis(host='redis', port=6379)


def home(request):
    if request.method == 'POST':
        Item.objects.create(text=request.POST['item_text'])
        return redirect('/')
    print ("hello")
    try:
        items = Item.objects.all()
    except Exception as e:
        print('Failed to upload to ftp: '+ str(e))
    print (items)
    counter = redis.incr('counter')
    print ("hello")
    return render(request, 'home.html', {'items': items, 'counter': counter})
