from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.db.models import Q, Sum
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from .models import Course, Category, Enrollment, Comment, Assignment, CourseMaterial, Notification
from .forms import PaymentForm, AssignmentSubmissionForm
from .decorators import is_enrolled
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator

def is_instructor(user):
    return user.groups.filter(name='Teacher').exists()

# Home page with course listing
@cache_page(60 * 10)  # Cache for 15 minutes
def home(request):
    query = request.GET.get('q', '')
    courses = Course.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    ) if query else Course.objects.all().order_by('-id')[:8]
    
    context = {
        's_count': Course.objects.count(),
        't_count': User.objects.filter(groups__name="Teacher").count(),
        'courses': courses,
        'c_count': Course.objects.count()
    }
    return render(request, 'base/index.html', context)

# Course listing with pagination
@cache_page(60 * 10)  # Cache for 10 minutes
def course_list(request):
    category_filter = request.GET.get('category')
    search_query = request.GET.get('search')

    courses = Course.objects.all()
    if category_filter:
        courses = courses.filter(category__name=category_filter)
    if search_query:
        courses = courses.filter(title__icontains=search_query)

    paginator = Paginator(courses, 6)
    courses_page = paginator.get_page(request.GET.get('page'))
    categories = Category.objects.all()

    context = {
        'courses': courses_page,
        'cats': categories,
        'selected_category': category_filter,
        'search_query': search_query,
    }
    return render(request, 'base/course/course_list.html', context)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator
from django.db.models import Sum
from .models import Course, Enrollment, Comment, Category, Assignment, CourseMaterial, Notification
from .forms import PaymentForm, AssignmentSubmissionForm

@cache_page(60 * 15)
def course_detail(request, course_id):
    categories = Category.objects.values('name')
    course = get_object_or_404(Course, id=course_id)
    students = Enrollment.objects.filter(course=course).count()
    recent_courses = Course.objects.order_by('-id')[:5]
    is_enrolled = request.user.is_authenticated and Enrollment.objects.filter(student=request.user, course=course).exists()
    
    if request.method == "POST" and request.user.is_authenticated:
        comment_text = request.POST.get('text')
        if comment_text:
            Comment.objects.create(course=course, comment=comment_text, user=request.user)
    
    comments = Comment.objects.filter(course=course).order_by('-id')[:5]
    
    context = {
        'course': course,
        'recent_courses': recent_courses,
        'categories': categories,
        'is_enrolled': is_enrolled,
        'students': students,
        'comments': comments,
    }
    return render(request, 'base/course/course_details.html', context)

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.is_free:
        Enrollment.objects.get_or_create(student=request.user, course=course)
        messages.success(request, f"Successfully enrolled in {course.title}.")
    else:
        return redirect('payment', course_id=course.id)
    return redirect('course_detail', course_id=course.id)

@login_required
def payment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.student = request.user
            payment.course = course
            payment.save()
            messages.success(request, "Payment submitted successfully. Awaiting admin verification.")
            return redirect('course_detail', course_id=course.id)
        else:
            messages.error(request, f"{form.errors}")
    else:
        messages.info(request, "This course requires payment. Please complete the payment form.")
    return render(request, 'base/payment.html', {'course': course})

@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if not Enrollment.objects.filter(student=request.user, course=assignment.course).exists():
        messages.error(request, "You are not enrolled in this course.")
        return redirect('course_detail', course_id=assignment.course.id)
    
    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = request.user
            submission.assignment = assignment
            submission.save()
            messages.success(request, "Assignment submitted successfully.")
            return redirect('course_detail', course_id=assignment.course.id)
    else:
        form = AssignmentSubmissionForm()
    
    return render(request, 'core/submit_assingment.html', {'form': form, 'assignment': assignment})

@login_required
@cache_page(60 * 10)
def metarial_details(request, metarial_id):
    metarial = get_object_or_404(CourseMaterial, id=metarial_id)
    course = metarial.course
    course_id = course.id
    assignment = Assignment.objects.filter(course=course)
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    if not is_enrolled:
        messages.info(request, "You are not enrolled in this course.")
        return redirect('course_detail', course_id=course_id)
    
    return render(request, 'base/metarial/metarials_details.html', { 
        'metarial': metarial,
        'assignments': assignment
    })

@login_required
def user_coure_list(request):
    courses = Enrollment.objects.filter(student=request.user) 
    paginator = Paginator(courses, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'base/user/user_course_list.html', {
        'courses': courses,
        'page_obj': page_obj
    })

def dashboard(request):
    return render(request, 'core/dashboard.html')

@login_required
@cache_page(60 * 10)
def metarial_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    metarials = CourseMaterial.objects.filter(course=course).only('id', 'title', 'duration', 'image', 'description', 'uploaded_at')
    paginator = Paginator(metarials, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'base/metarial/metarial_list.html', {'metarials': metarials, 'course': course, 'page_obj': page_obj})

@login_required
@cache_page(60 * 10)
def assignment_list(request, course_id):
    assignments = Assignment.objects.filter(id=course_id).order_by('-uploaded_at')
    paginator = Paginator(assignments, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'base/assignment/assignment_list.html', {'assignments': page_obj})

def notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by('-id')
        notifications.update(is_read=True)
    return render(request, 'base/notifications.html', {'notification': notifications})

def courses_category(request):
    category_name = request.GET.get('category_name', None)
    courses = Course.objects.filter(category__name=category_name)
    paginator = Paginator(courses, 6)
    page = request.GET.get('page')
    courses_page = paginator.get_page(page)
    return render(request, 'base/course/category_courses.html', {
        'page_obj': courses_page,
        'selected_category': category_name,
    })


class CreateCourse(CreateView):
    model = Course
    fields = ['title', 'description', 'category', 'price', 'image', 'duration', 'prerequisites', 'tags']
    template_name = 'base/course/course_add.html'
    success_url = '/'

    @method_decorator(user_passes_test(is_instructor, login_url="home"))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cats'] = Category.objects.all()
        return context
    


class TeacherCourseUpdate(UpdateView):
    model = Course
    fields = ['title', 'description', 'category', 'price', 'image', 'duration', 'prerequisites', 'tags']
    template_name = 'base/course/teacher_course_update.html'
    success_url = reverse_lazy('course_detail', kwargs={'course_id': Course.id})
    context_object_name = 'course'

    @method_decorator(user_passes_test(is_instructor, login_url="home"))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

@user_passes_test(is_instructor, login_url="home")
def teacher_courses(request):
    courses = Course.objects.filter(teacher=request.user)
    pagination = Paginator(courses, 6)
    page = request.GET.get('page')
    courses = pagination.get_page(page)
    return render(request, 'base/teacher/teacher_courses.html', {'page_obj': courses})

@user_passes_test(is_instructor, login_url="home")
def teacher_course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    messages.success(request, "Course deleted successfully.")
    return redirect('teacher_courses')
