from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Enrollment, CourseMaterial, Assignment, AssignmentSubmission, Payment, Category
from .forms import PaymentForm, AssignmentSubmissionForm
from .decorators import is_enrolled

# Home page with course listing
def home(request):
    courses = Course.objects.all().reverse()[0:4]
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

    return render(request, 'base/course_list.html', context)

# Course details with materials and assignments
# Non-enrolled users can see the course details but not the materials and assignments
@login_required
def course_detail(request, course_id):
    category = Category.objects.all().values('name')
    course = get_object_or_404(Course, id=course_id)
    students = Enrollment.objects.filter(course=course).count()
    courses = Course.objects.order_by('-id')[:5]
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists() 
    return render(request, 'base/course_details.html', {
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


def metarial_details(request, metarial_id):
    metarial = CourseMaterial.objects.get(id=metarial_id)
    course = metarial.course
    course_id = course.id
    assignment = Assignment.objects.filter(course=course)
    is_enrolled = Enrollment.objects.filter(student=request.user,course=course).exists()
    if not is_enrolled:
        messages.info(request, "You are not enrolled in this course.")
        return redirect('course_detail', course_id=course_id)
        
    return render(request, 'base/metarials_details.html', { 
        'metarial': metarial,
        'assignments': assignment
        })



def user_coure_list(request):
    courses = Enrollment.objects.filter(student=request.user) 

    return render(request, 'core/user_course_list.html', {
        'courses': courses
        })

def dashboard(request):
    # enrolled_courses = Enrollment.objects.filter(user=request.user)
    # assignments_submitted = AssignmentSubmission.objects.filter(student=request.user)
    # total_payments = Payment.objects.filter(student=request.user).aggregate(total=Sum('amount'))
    return render(request, 'core/dashboard.html')

@is_enrolled
def metarial_list(request, course_id):
    course = Course.objects.get(id=course_id)
    metarials = CourseMaterial.objects.filter(course=course).values('id','title', 'duration','image','description','uploaded_at')
    
    paginator = Paginator(metarials, 6)  # Show 6 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'base/metarial_list.html', {'metarials': metarials, 'course':course})


@is_enrolled
def assignment_list(request, course_id):
    course = Course.objects.get(id=course_id)
    assignments = Assignment.objects.filter(course=course)
    return render(request, 'base/assignment_list.html', {'assignments': assignments})