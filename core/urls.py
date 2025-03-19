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
    path('notification/', views.notifications, name="notifications"),
    path('add_course/', views.CreateCourse.as_view(), name='add'),
    path('teacher_course_list/', views.teacher_courses, name='teacher_course_list'),
    path('courses_category/', views.courses_category, name='category_courses'),
    path('course/<int:pk>/update/', views.TeacherCourseUpdate.as_view(), name='course_update'),

    path('course/<int:pk>/delete/', views.teacher_course_delete, name='course_delete'),
    path('contact/', views.ApplicationsView.as_view(), name='contact'),

    
]






