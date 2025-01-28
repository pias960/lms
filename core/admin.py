from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Course, Enrollment, CourseMaterial, Assignment, AssignmentSubmission, Payment



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
  


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'is_free', 'created_at')
    list_filter = ('category', 'is_free')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('title', 'description', 'category', 'price', 'is_free')}),
        ('Additional Info', {'fields': ('image', 'duration', 'prerequisites', 'created_at')}),
    )


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    search_fields = ('student__username', 'course__title')
    list_filter = ('enrolled_at',)
    readonly_fields = ('enrolled_at',)


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'uploaded_at')
    search_fields = ('title', 'course__title')
    list_filter = ('uploaded_at',)
    readonly_fields = ('uploaded_at',)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date', 'uploaded_at')
    search_fields = ('title', 'course__title')
    list_filter = ('due_date', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'grade')
    search_fields = ('assignment__title', 'student__username')
    list_filter = ('submitted_at',)
    readonly_fields = ('submitted_at',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'payment_method', 'transaction_id', 'payment_date', 'is_verified','payment_status')
    search_fields = ('student__username', 'course__title', 'transaction_id')
    list_filter = ('payment_method', 'is_verified', 'payment_date')
    readonly_fields = ('payment_date',)
    fieldsets = (
        (None, {'fields': ('student', 'course', 'payment_method', 'transaction_id', 'is_verified','payment_status')}),
        ('Additional Info', {'fields': ('receipt', 'payment_date')}),
    )
