from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import PaymentForm, AssignmentSubmissionForm
from .decorators import is_enrolled
from django.views.generic.edit import CreateView

# Home page with course listing
def home(request):
    courses = Course.objects.all().order_by('-id')[:8]
    context = {'courses' : courses}

    return render(request, 'base/index.html', context )

from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Course, Category

def course_list(request):
    category_filter = request.GET.get('category', None)  # Get the category from the GET request
    search_query = request.GET.get('search', None)  # Get the search query (if any)

    # Filter courses by category if specified
    if category_filter:
        courses = Course.objects.filter(category__name=category_filter)
    else:
        courses = Course.objects.all()

    # Further filter by search query (if any)
    if search_query:
        courses = courses.filter(title__icontains=search_query)

    # Paginate the courses
    paginator = Paginator(courses, 6)  # Show 6 courses per page
    page = request.GET.get('page')  # Get the current page
    courses_page = paginator.get_page(page)  # Get the courses for the current page

    # Fetch categories for the sidebar
    categories = Category.objects.all()

    context = {
        'courses': courses_page,
        'cats': categories,
        'selected_category': category_filter,
        'search_query': search_query,
    }

    return render(request, 'base/course/course_list.html', context)

# Course details with materials and assignments
# Non-enrolled users can see the course details but not the materials and assignments
@login_required
def course_detail(request, course_id):
    category = Category.objects.all().values('name')
    course = get_object_or_404(Course, id=course_id)
    students = Enrollment.objects.filter(course=course).count()
    courses = Course.objects.order_by('-id')[:5]
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists() 
    return render(request, 'base/course/course_details.html', {
        'course': course,
        'courses': courses,
        'categorys' : category,
        'is_enrolled': is_enrolled,
        'students' : students,
     
    })

# Enroll in a course
@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if course.is_free:
        Enrollment.objects.get_or_create(student=request.user, course=course)
        messages.success(request, f"Successfully enrolled in {course.title}.")
    else:
        messages.info(request, "This course requires payment.")
        return redirect('payment', course_id=course.id)

    return redirect('course_detail', course_id=course.id)

# Payment for a course
@login_required
def payment(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES,)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.student = request.user
            payment.course = course
            payment.save()
            messages.success(request, "Payment submitted successfully. Awaiting admin verification.")
            return redirect('course_detail', course_id=course.id)
    else:
        form = PaymentForm()

    return render(request, 'core/payment.html', {
        'form': form, 
        'course': course})

# Submit assignment
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

    return render(request, 'core/submit_assingment.html', {
        'form': form,
        'assignment': assignment
        })

# Category-based course filtering

@login_required
def metarial_details(request, metarial_id):
    metarial = CourseMaterial.objects.get(id=metarial_id)
    course = metarial.course
    course_id = course.id
    assignment = Assignment.objects.filter(course=course)
    is_enrolled = Enrollment.objects.filter(student=request.user,course=course).exists()
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
    paginator = Paginator(courses, 6)  # Show 6 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'base/user/user_course_list.html', {
        'courses': courses,
        'page_obj': page_obj
        })

def dashboard(request):
    # enrolled_courses = Enrollment.objects.filter(user=request.user)
    # assignments_submitted = AssignmentSubmission.objects.filter(student=request.user)
    # total_payments = Payment.objects.filter(student=request.user).aggregate(total=Sum('amount'))
    return render(request, 'core/dashboard.html')

@login_required
def metarial_list(request, course_id):
    course = Course.objects.get(id=course_id)
    metarials = CourseMaterial.objects.filter(course=course).only('id','title', 'duration','image','description','uploaded_at')
    
    paginator = Paginator(metarials, 6)  # Show 6 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    #check the url of image
    m = CourseMaterial.objects.first()
    print(m.image.url)

    
    return render(request, 'base/metarial/metarial_list.html', {'metarials': metarials, 'course':course, 'page_obj': page_obj})


@login_required
def assignment_list(request,course_id):
    assignments = Assignment.objects.all().order_by('-uploaded_at')  # নতুন অ্যাসাইনমেন্ট আগে দেখাবে
    paginator = Paginator(assignments, 6)  # প্রতি পেজে 6টি অ্যাসাইনমেন্ট দেখাবে

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'base/assignment/assignment_list.html', {'assignments': page_obj})



def notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by('-id')
        notifications.update(is_read=True)
        
    return render(request, 'base/notifications.html', {'notification': notifications})




##Teacher Views##
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator


# Function to check if the user is in the "Instructor" group
def is_instructor(user):
    return user.groups.filter(name="Teacher").exists()

class CreateCourse(CreateView):
    model = Course
    fields = ['title', 'description', 'category', 'price', 'image', 'duration', 'prerequisites', 'tags']
    template_name = 'base/course_add.html'
    success_url = '/'

    # Apply the decorator to restrict access
    @method_decorator(user_passes_test(is_instructor, login_url="home"))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['cats'] = Category.objects.all()
        return context
