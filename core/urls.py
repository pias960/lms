from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('course/<int:course_id>/payment/', views.payment, name='payment'),
    path('assignment/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('metarials/<int:metarial_id>/',views.metarial_details, name='metarials_details'),
    path('dashbord/', views.dashboard, name='dashboard'),
    path('user_course_list/', views.user_coure_list, name='user_course_list'),
    path('vedio_list/<int:course_id>', views.metarial_list, name='metarial_list'),
    path('assignment_list/<int:course_id>', views.assignment_list, name='assignment_list'),
]




