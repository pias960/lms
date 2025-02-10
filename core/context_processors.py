
from .models import Category,Notification
def cats(request):
    cats = Category.objects.all()
    return {'categorys': cats}

def notifications(request):
    notifications = 0
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, is_read=False).count()
    is_teacher = request.user.groups.filter(name='Teacher').exists()
    return {'notifications': notifications, 'is_teacher': is_teacher}

