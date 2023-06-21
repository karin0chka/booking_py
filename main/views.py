from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import FeedbackForm, TicketSearchForm
from .models import Allowance, Ticket
from datetime import date
from django.db.models import Q
from .models import Feedback
from .forms import FeedbackForm
import json
from django.http import HttpResponse
from .utils import generate_random_string





# 'home' function- handles the logic for the home page;
#'request' parameter - representing  an HTTP request made to the server;

def home(request):
    if(request.POST):
        # checks if the  request method is POST, indicating that a form has been submitted;
        #get()- to retrieve the cleaned form data and assigns it to 'form'; 
        formDto = TicketSearchForm(request.POST)
        form = formDto.get()
            

        #checks if the form is valid;
        # if it is extracts the values;
                 
        if formDto.is_valid():
            type_value=form['ticket_type']
            search_value=form['quantity']

            query=Q()
            if type_value == 'economy':
                query = Q(economy_seats__gte=search_value)
            elif type_value == 'first_class':
                query=Q(first_class_seats__gte=search_value)    
            else:
                query=Q(business_class_seats__gte=search_value)    

        #filter allowance
            allowances = Allowance.objects.filter(
                query,
                from_location=form['from_location'],
                destination=form['destination'],
            ) 
            #if the form is valid, creates 'context' dictionary;  
            context ={
                'type':type_value,
                'allowances':allowances,
                'form': form,
                'quantity':search_value,
                
                
            }
            return render(request, 'main/list.html', context)
        #if form is not valid return 'Not valid!'
        else:
            return HttpResponse('Not valid!')
    # Here we're processing not Post requests(GET request)
    else:
        today= date.today().isoformat()
        return render(request, 'main/home.html',{'today':today})

#displaying a booked ticket 
def booked_ticket(request, booking_id):
    #retrieving(Cross-Site-Request Forgery);
    #request.Meta - dictionary that contains all avaible HTTP with request;
    #'CSRE_COOKIE'-represent CSRF token(secret value to prevent CSRF attacks);

      # if statement for 'GET'method;
    if request.method== "GET":
        context = {'ticket': None, 'feedback':[], 'error': None}
        try:
            #Attempt to  retrieve the ticket with the specified booking_id
            ticket = Ticket.objects.get(booking_id=booking_id)
            #Retrieve the feedback associated with the ticket
            feedback = Feedback.objects.filter(ticket_id=ticket.id).order_by('created_at')
            #Update the context with the retrieved ticket and feedback
            context['ticket']=ticket
            context['feedback']=feedback
            #Render  the confirmation.html tamplate with the updated contexr
            return render(request,'main/confirmation.html',context)
        #for exception
        except:
            context['error']='Booking not valid!'
            #Render the confirmation.html with the updated context
            return render(request,'main/confirmation.html',context)
     #for 'DELITE'
     #    
    elif request.method=="DELETE":
        try:
            #retrieve the 'Ticket' object with specified 'booking-id'
            ticket = Ticket.objects.get(booking_id=booking_id)
            ticket.canceled_by='client'
            ticket.save()
            return HttpResponse("Ok")
        #if the ticket is no value
        except:
            context['error']='Booking not valid!'
            return render(request,'main/confirmation.html',context)


        
   

def feedback(request, booking_id):
    #checks if the request method is 'POST'(indicates that a form has been submitted);
    if request.method == 'POST':
        #specifies the fields;
        #request.POST - form is bound to the submitted data;
        form = FeedbackForm(request.POST)
        #if data passed the form validation
        if form.is_valid():
            #code retrieves the ticket object using 'booking_id'
            ticket=Ticket.objects.get(booking_id= booking_id)
            #form is not immediately saved to the database
            feedback = form.save(commit=False)
            feedback.ticket=ticket
            feedback.save()  
         # if form is not valid            
        else:
            return HttpResponse(form.errors)
    else:
        #if the request method is not 'POST' it is creating a new instance
        form = FeedbackForm()

    return redirect("/ticket/"+booking_id) 

#handles the creation of new ticket based on the data fron request
def newTicket(request):
    #'POST'-user has submitted a form;
    if request.method=='POST':
        #Retrieve JSON data from the request body;
        json_data = json.loads(request.body)
        #checks the availability of seats based on the 'ticket_type';
        allowance = Allowance.objects.get(id=json_data['allowance_id'])
        #Tacking data from Json;
        quantity = json_data['quantity']
        type_value = json_data['ticket_type']
        #Check seat availibility based on ticket_type and quantity
        is_available=False

        if type_value == 'economy':
            is_available = quantity <= allowance.economy_seats 
        elif type_value == 'first_class':
            is_available = quantity <= allowance.first_class_seats 
        else:
            is_available = quantity <= allowance.business_class_seats   

        if is_available:
            #Generate a unique booking_id
            booking_id=generate_random_string(10)
            #Calculate the total price based on ticket_type and quantity
            total_price = 0
            if type_value == 'economy':
                allowance.economy_seats = allowance.economy_seats - quantity
                total_price = quantity * allowance.economy_seat_price
            elif type_value == 'first_class':
                allowance.first_class_seats = allowance.first_class_seats - quantity
                total_price = quantity * allowance.first_class_seat_price
            else:
                allowance.business_class_seats = allowance.business_class_seats - quantity
                total_price = quantity * allowance.business_class_seat_price
             #Save the  updated Allowance object   
            allowance.save()

            # Ticket object with the ticket deteils
            ticket = Ticket(
                allowance=allowance,
                quantity=quantity,
                ticket_type=type_value,
                booking_id=booking_id,
                total_price=total_price
            )
            
            #Save the Ticket object to the database
            ticket.save()
            #Response JSON object with the URL of the new ticket
            returnDto = {'url':'/ticket/'+ booking_id}
            return HttpResponse(json.dumps(returnDto), content_type='application/json')
        else:
            #If is not available,
            print('NOPE',is_available)
            return HttpResponse("Not available!")
                
             
        
    
    
     

    
        