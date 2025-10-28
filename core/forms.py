from django import forms
from core.models import ServiceRequest, Technician, Skill


class BulkUploadForm(forms.Form):
    """Form for bulk uploading users via Excel"""
    
    excel_file = forms.FileField(
        label='Excel File',
        help_text='Upload Excel file with customer/technician data (.xlsx or .xls)',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls'
        })
    )
    
    def clean_excel_file(self):
        file = self.cleaned_data.get('excel_file')
        if file:
            # Check file extension
            if not file.name.endswith(('.xlsx', '.xls')):
                raise forms.ValidationError('Only Excel files (.xlsx or .xls) are allowed.')
            
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size should not exceed 10MB.')
        
        return file


# Common service types
SERVICE_TYPE_CHOICES = [
    ('Gas Leak Repair', 'Gas Leak Repair'),
    ('Electrical Fault', 'Electrical Fault'),
    ('Plumbing Issue', 'Plumbing Issue'),
    ('HVAC Maintenance', 'HVAC Maintenance'),
    ('Appliance Installation', 'Appliance Installation'),
    ('Emergency Callout', 'Emergency Callout'),
    ('Routine Service', 'Routine Service'),
    ('Maintenance Check', 'Maintenance Check'),
    ('Safety Inspection', 'Safety Inspection'),
    ('System Upgrade', 'System Upgrade'),
]


class ServiceRequestForm(forms.ModelForm):
    """Form for customers to submit service requests"""
    
    service_type = forms.ChoiceField(
        choices=[('', 'Select service type...')] + SERVICE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'service-type'}),
        help_text='Choose the type of service you need',
    )
    
    class Meta:
        model = ServiceRequest
        fields = ['address', 'service_minutes', 'window_start', 'window_end', 
                  'required_skill', 'priority', 'notes']
        widgets = {
            'address': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter Melbourne address',
                'id': 'address-input',
                'autocomplete': 'off',
            }),
            'service_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 15, 'max': 480}),
            'window_start': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'window_end': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'required_skill': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        help_texts = {
            'address': 'Enter a Melbourne address where service is needed.',
            'window_start': 'Earliest time technician can arrive.',
            'window_end': 'Latest time technician should complete the job.',
            'service_minutes': 'Estimated duration of the service in minutes.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['required_skill'].queryset = Skill.objects.filter(is_active=True)
    
    def clean(self):
        cleaned_data = super().clean()
        service_type = cleaned_data.get('service_type')
        
        # If service type is selected, use it as the name; otherwise require a custom name
        if not service_type and not self.instance.name:
            # This will be handled in the view
            pass
        
        return cleaned_data


class TechnicianSignupForm(forms.ModelForm):
    """Form for technicians to create their profile"""
    
    capacity_hours = forms.IntegerField(
        label='Available Hours Per Day',
        min_value=1,
        max_value=12,
        initial=8,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='How many hours per day are you available?'
    )
    
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    
    class Meta:
        model = Technician
        fields = ['depot_address', 'shift_start', 'shift_end', 'color_hex']
        widgets = {
            'depot_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your depot address in Melbourne'}),
            'shift_start': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'shift_end': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'color_hex': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }

