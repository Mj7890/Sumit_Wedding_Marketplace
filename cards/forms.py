from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Customization, Review, PrinterCardOrder


class CustomizationForm(forms.ModelForm):
    class Meta:
        model = Customization
        fields = ['bride_name', 'groom_name', 'wedding_date', 'venue',
                  'font_choice', 'card_style', 'palette', 'ornament']
        widgets = {
            'bride_name':   forms.TextInput(attrs={'placeholder': "Bride's name", 'class': 'form-input'}),
            'groom_name':   forms.TextInput(attrs={'placeholder': "Groom's name", 'class': 'form-input'}),
            'wedding_date': forms.TextInput(attrs={'placeholder': 'e.g. Saturday, 14th December 2024', 'class': 'form-input'}),
            'venue':        forms.TextInput(attrs={'placeholder': 'Venue name & city', 'class': 'form-input'}),
            'font_choice':  forms.Select(attrs={'class': 'form-select'}),
            'card_style':   forms.Select(attrs={'class': 'form-select'}),
            'palette':      forms.HiddenInput(),
            'ornament':     forms.HiddenInput(),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating':  forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-textarea', 'placeholder': 'Share your experience...'}),
        }


class UserRegistrationForm(UserCreationForm):
    """
    Only username + password — email is injected from session in the view.
    Removing email from the form entirely so it never causes silent validation failure.
    """
    class Meta:
        model  = User
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Choose a username',
                'autofocus': True,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Create a strong password',
            'id': 'id_password1',
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Repeat your password',
            'id': 'id_password2',
        })
        # Remove verbose help texts
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''


def _fi(placeholder='', cls='form-input', **kw):
    """Helper: TextInput with class and placeholder."""
    return forms.TextInput(attrs={'class': cls, 'placeholder': placeholder, **kw})


class PrinterCardOrderForm(forms.ModelForm):
    class Meta:
        model  = PrinterCardOrder
        fields = [
            'card_type',
            'primary_name', 'primary_father_name', 'primary_dada_name', 'primary_address',
            'secondary_name', 'secondary_father_name', 'secondary_address',
            'sagaai_date', 'sagaai_time', 'sagaai_preetibhoj',
            'shaadi_date',
            # bride fields
            'barat_swagat', 'shaadi_preetibhoj', 'vivah_sthal',
            # groom fields
            'ghudchadi_time', 'barat_prasthan', 'barat_destination',
            'reception_date', 'reception_preetibhoj', 'reception_sthal',
            # common
            'extra_info', 'bal_aakanksha',
            'darshanaabhilashi', 'vineet', 'phone',
        ]
        widgets = {
            'card_type':              forms.HiddenInput(),
            'primary_name':           _fi('पूरा नाम लिखें'),
            'primary_father_name':    _fi(),
            'primary_dada_name':      _fi(),
            'primary_address':        forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'पूरा पता'}),
            'secondary_name':         _fi('पूरा नाम लिखें'),
            'secondary_father_name':  _fi(),
            'secondary_address':      forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'पूरा पता'}),
            'sagaai_date':            _fi('दिनांक'),
            'sagaai_time':            _fi('बजे'),
            'sagaai_preetibhoj':      _fi(),
            'shaadi_date':            _fi('दिनांक'),
            'barat_swagat':           _fi('समय'),
            'shaadi_preetibhoj':      _fi(),
            'vivah_sthal':            forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
            'ghudchadi_time':         _fi(),
            'barat_prasthan':         _fi(),
            'barat_destination':      forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
            'reception_date':         _fi('दिनांक'),
            'reception_preetibhoj':   _fi('समय'),
            'reception_sthal':        _fi(),
            'extra_info':             forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'अतिरिक्त जानकारी...'}),
            'bal_aakanksha':          _fi(),
            'darshanaabhilashi':      _fi(),
            'vineet':                 _fi(),
            'phone':                  forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'फोन नंबर', 'type': 'tel'}),
        }
