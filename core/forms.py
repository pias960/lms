from django import forms
from .models import Payment, AssignmentSubmission

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method', 'transaction_id', 'receipt']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['file']
