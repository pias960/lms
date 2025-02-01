from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from .models import  Enrollment

def is_enrolled(view_func):
    @wraps(view_func)
    def wrapper(request,course_id,*args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        enrollment = Enrollment.objects.filter(student=request.user, course_id=course_id).first()
        if not enrollment:
            return HttpResponseForbidden("You are not enrolled in this course.")
        return view_func(request, course_id,*args, **kwargs)
    return wrapper