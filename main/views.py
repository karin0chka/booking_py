from multiprocessing import connection
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import FeedbackForm, TicketSearchForm
from .models import Allowance, Ticket, Feedback, Discount
from datetime import date
from django.db.models import Q
from .forms import FeedbackForm
import json
from django.http import HttpResponse
from .utils import generate_random_string, send_new_email


# 'home' function- handles the logic for the home page;
# 'request' parameter - representing  an HTTP request made to the server;

def home(request):
    if (request.POST):
        from_location = request.POST.get('from_location').lower()
        destination = request.POST.get('destination').lower()
        ticket_type = request.POST.get('ticket_type')
        quantity = int(request.POST.get('quantity'))

        # checks if the  request method is POST, indicating that a form has been submitted;
        # get()- to retrieve the cleaned form data and assigns it to 'form';

        # checks if the form is valid;
        # if it is extracts the values;

        if from_location and destination and ticket_type and quantity > 0:
            query = Q()
            if ticket_type == 'economy':
                query = Q(economy_seats__gte=quantity)
            elif ticket_type == 'first_class':
                query = Q(first_class_seats__gte=quantity)
            else:
                query = Q(business_class_seats__gte=quantity)

        # filter allowance
            allowances = Allowance.objects.filter(
                query,
                from_location=from_location,
                destination=destination,
            )
            # if the form is valid, creates 'context' dictionary;
            context = {
                'type':  ticket_type,
                'allowances': allowances,
                'form': from_location,
                'quantity': quantity,
            }
            print(quantity)
            return render(request, 'main/list.html', context)
        # if form is not valid return 'Not valid!'
        else:
            return HttpResponse('Not valid!')
    # Here we're processing not Post requests(GET request)
    else:
        today = date.today().isoformat()
        return render(request, 'main/home.html', {'today': today})


# displaying a booked ticket
def booked_ticket(request, booking_id):
    # retrieving(Cross-Site-Request Forgery);
    # request.Meta - dictionary that contains all avaible HTTP with request;
    # 'CSRE_COOKIE'-represent CSRF token(secret value to prevent CSRF attacks);

    # if statement for 'GET'method;
    if request.method == "GET":
        context = {'ticket': None, 'feedback': [], 'error': None}
        try:
            # Attempt to  retrieve the ticket with the specified booking_id
            ticket = Ticket.objects.select_related(
                'allowance').get(booking_id=booking_id)
            # Retrieve the feedback associated with the ticket
            feedback = Feedback.objects.filter(
                ticket_id=ticket.id).order_by('created_at')
            # Update the context with the retrieved ticket and feedback
            context['ticket'] = ticket
            context['feedback'] = feedback
            # Render  the confirmation.html tamplate with the updated contexr
            return render(request, 'main/confirmation.html', context)
        # for exception
        except:
            context['error'] = 'Booking not valid!'
            # Render the confirmation.html with the updated context
            return render(request, 'main/confirmation.html', context)
     # for 'DELITE'
     #
    elif request.method == "DELETE":
        try:
            # retrieve the 'Ticket' object with specified 'booking-id'
            ticket = Ticket.objects.get(booking_id=booking_id)
            ticket.canceled_by = 'client'
            ticket.save()
            return HttpResponse("Ok")
        # if the ticket is no value
        except:
            context['error'] = 'Booking not valid!'
            return render(request, 'main/confirmation.html', context)


def feedback(request, booking_id):
    # checks if the request method is 'POST'(indicates that a form has been submitted);
    if request.method == 'POST':
        # specifies the fields;
        # request.POST - form is bound to the submitted data;
        form = FeedbackForm(request.POST)
        # if data passed the form validation
        if form.is_valid():
            # code retrieves the ticket object using 'booking_id'
            ticket = Ticket.objects.get(booking_id=booking_id)
            # form is not immediately saved to the database
            feedback = form.save(commit=False)
            feedback.ticket = ticket
            feedback.save()
         # if form is not valid
        else:
            return HttpResponse(form.errors)
    else:
        # if the request method is not 'POST' it is creating a new instance
        form = FeedbackForm()

    return redirect("/ticket/"+booking_id)

# handles the creation of new ticket based on the data fron request


def newTicket(request):
    # 'POST'-user has submitted a form;t()
    if request.method == 'POST':
        # Retrieve JSON data from the request body;
        allowance_id = int(request.POST.get('allowance_id'))
        quantity = int(request.POST.get('quantity'))
        type_value = request.POST.get('ticket_type')
        email = request.POST.get('email')
        # checks the availability of seats based on the 'ticket_type';
        allowance = Allowance.objects.get(id=allowance_id)
        # Check seat availibility based on ticket_type and quantity
        is_available = False

        if type_value == 'economy':
            is_available = quantity <= allowance.economy_seats
        elif type_value == 'first_class':
            is_available = quantity <= allowance.first_class_seats
        else:
            is_available = quantity <= allowance.business_class_seats

        if is_available:
            # Generate a unique booking_id
            booking_id = generate_random_string(10)
            # Calculate the total price based on ticket_type and quantity
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
             # Save the  updated Allowance object
            allowance.save()
            # Calculating the discount if the quantity is more than 1 and cannot be more than 40%
            discount_applied = False
            if quantity > 1:
                discount_applied = True
                if quantity > 4:
                    total_price = (total_price * (100 - 40)) / 100
                else:
                    total_price = (total_price * (100 - (quantity * 10))) / 100

            # Ticket object with the ticket deteils
            ticket = Ticket(
                allowance=allowance,
                quantity=quantity,
                ticket_type=type_value,
                booking_id=booking_id,
                total_price=total_price,
                discount_applied=discount_applied
            )

            # Save the Ticket object to the database
            ticket.save()
            subject = 'New Ticket'
            message = 'Your new ticket is booked. \n\n' + 'Booking ID: ' + booking_id + '\n\n' + 'Total Price: ' + \
                str(total_price) + 'To view your ticket follow the link: ' + \
                'http://127.0.0.1:8000/ticket' + booking_id
            from_email = 'no-reply@bookticket.com'
            recipient_list = [email]
            print(subject, message, from_email, recipient_list)
            # send_new_email(subject, message, from_email, recipient_list)
            return redirect('/ticket/' + booking_id)
        else:
            # If is not available,
            print('NOPE', is_available)
            return HttpResponse("Not available!")
# his function is responsible for handling a discount request.


def discount(request):
    # if the HTTP method is POST, the discount code and booking ID are extracted from the request.
    try:
        # Retrieve discount code and booking ID from the request
        if request.method == 'POST':
            code = request.POST.get('code')
            booking_id = request.POST.get('booking_id')

            # # Find the ticket in the database that matches the booking ID and has no discount applied
            ticket = Ticket.objects.select_related('allowance').get(
                booking_id=booking_id, discount_applied=False)
           # Find the discount in the database that matches the code and the associated allowance of the ticket
            discount = Discount.objects.get(
                code=code, allowance_id=ticket.allowance.id)

            # Apply the discount to the ticket's total price
            ticket.discount_applied = True
            ticket.total_price = (ticket.total_price *
                                  (100 - discount.value)) / 100
            # Save the updated ticket in the database
            ticket.save()
            # Redirect the user to the ticket page for the updated ticket
            return redirect('/ticket/' + ticket.booking_id)
        else:
            # Render a confirmation page with an error message for invalid request (if not a POST request)
            return render('main/confirmation.html', {'error': 'Invalid request'})

    except Exception as e:
        print(e)
        # Fetch the ticket again (without considering discount_applied flag) in case of an error
        ticket = Ticket.objects.select_related(
            'allowance').get(booking_id=booking_id)
        # Render a confirmation page with an error message and the ticket information
        return render(request, 'main/confirmation.html', {'error': 'Invalid request', 'ticket': ticket})
