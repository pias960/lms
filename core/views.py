from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Enrollment, CourseMaterial, Assignment, AssignmentSubmission, Payment, Category
from .forms import PaymentForm, AssignmentSubmissionForm

# Home page with course listing
def home(request):
    return render(request, 'core/home.html')

def course_list(request):
    courses = Course.objects.all()
    category = Category.objects.all().values('name')

    return render(request, 'core/course_list.html', {'courses': courses, 'cats' : category})

# Course details with materials and assignments
# Non-enrolled users can see the course details but not the materials and assignments
@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    assignments = Assignment.objects.filter(course=course) if is_enrolled else None

    return render(request, 'core/course_details.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'assignments': assignments
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

    return render(request, 'core/payment.html', {'form': form, 'course': course})

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

    return render(request, 'core/submit_assingment.html', {'form': form, 'assignment': assignment})

# Category-based course filtering


def metarials(request, course_id):
    course = Course.objects.get(pk=course_id)
    metarials = CourseMaterial.objects.filter(course=course)
    is_enrolled = Enrollment.objects.filter(user=request.user,course=course).exists()
    if not is_enrolled:
        messages.info(request, "You are not enrolled in this course.")
        return redirect('course_detail', course_id=course_id)
    return render(request, 'core/course_materials.html', {'course': course, 'metarials': metarials})



def user_coure_list(request):
    courses = Enrollment.objects.filter(student=request.user) 

    return render(request, 'core/user_course_list.html', {'courses': courses})

def dashboard(request):
    # enrolled_courses = Enrollment.objects.filter(user=request.user)
    # assignments_submitted = AssignmentSubmission.objects.filter(student=request.user)
    # total_payments = Payment.objects.filter(student=request.user).aggregate(total=Sum('amount'))
    return render(request, 'core/dashboard.html')