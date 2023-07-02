from django import forms
from .models import Feedback

#define a form class named "TicketSEarchForm";
#"forms.Form"-base class provided by Django for creating forms;
#inside the form class, defining field;
#define fields using django librery;
#using label='', to connect this class with my HTML template;
#WE NEEN THIS to capture and validate user input for searching tickets;

class TicketSearchForm(forms.Form):
    from_location = forms.CharField(label='From', max_length=100)
    destination = forms.CharField(label='Your Destination', max_length=100)
    depart_date = forms.DateField(label='Check In')
    quantity = forms.IntegerField(label='Number of people')
    ticket_type = forms.ChoiceField(label='Type of ticket', choices=(
        ('economy', 'Economy'),
        ('first_class', 'First class'),
        ('business_class', 'Business class'),
    ))

    #'is_valid()'return True regardless of whether the form is valid or not


    #get() returns on clened data using 'self.cleaned_data' otherwise 'None'
    
    def get(self):
        if self.is_valid():
            return self.cleaned_data
        return None

   #class called 'FeedbackForm' which inherits subclass 'forms.ModelForm'
   #class Meta provides additional information about the form
   #form is associated with 'Feedback' model(SQL)
   #fileds:fileds from 'Feedback model' that should be included in the form
   #'Meta'class- Django applies default validation rules
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields=['title','email','description']

        
        