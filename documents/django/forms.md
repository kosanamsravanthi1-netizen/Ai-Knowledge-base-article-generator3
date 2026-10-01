<!-- Title: Django Documentation — Forms and Input Validation -->
<!-- Category: django -->
<!-- Section: Forms Layer -->
<!-- SourceURL: https://docs.djangoproject.com/en/5.0/topics/forms/ -->

# Django Forms and Input Validation

Django provides a comprehensive form framework that handles rendering form fields, validating incoming user data, and converting submitted values into native Python data types.

## Standard Form Class
```python
from django import forms

class QuestionForm(forms.Form):
    question = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={'placeholder': 'Ask a Python or Django question...'})
    )
    conversation_id = forms.UUIDField(required=False)

    def clean_question(self):
        data = self.cleaned_data['question'].strip()
        if len(data) < 3:
            raise forms.ValidationError("Question must be at least 3 characters long.")
        return data
```

## ModelForm Class
If your form directly creates or updates a Django model instance, use `ModelForm`.

```python
from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
```

## Form Processing in Views
```python
def submit_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_validate():
            # Process cleaned data
            q = form.cleaned_data['question']
            return redirect('success')
    else:
        form = QuestionForm()

    return render(request, 'ask.html', {'form': form})
```
