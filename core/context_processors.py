
from .models import Category
def cats(request):
    cats = Category.objects.all()
    return {'categorys': cats}