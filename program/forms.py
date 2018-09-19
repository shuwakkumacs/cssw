#from django.forms import ModelForm, modelformset_factory, inlineformset_factory
from django.forms import *
from django.forms.widgets import *
from .models import *
from .settings import settings  

class ParticipantForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(ParticipantForm, self).__init__(*args, **kwargs)
        for field in self: 
            field.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Participant
        exclude = ["time_created"]
        widgets = {
            "password": TextInput(attrs={"type": "password"})
            "is_admin": HiddenInput()
        }

class ProgramForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(ProgramForm, self).__init__(*args, **kwargs)
        for field in self: 
            field.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Program
        exclude = ["session_number", "program_number", "time_created"]
        widgets = {
            "participant": HiddenInput()
        }
