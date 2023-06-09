from django.shortcuts import redirect
from django.contrib.auth import logout
from django.db.models import Count
from django.db import models
from django .db import connection
from .models import Report
from main.models import Allowance, Ticket, Feedback

import pandas as pd


def check_if_admin(request):

    if not request.user.is_superuser:
        logout(request)
        return redirect('/custom_admin/login')

 # Using raw  SQL insted of ORM to fetch all the allowences and put it in the dictionary


def return_tickets():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM main_ticket")
        rows = cursor.fetchall()
        # Process the query results
        tickets = []
        for row in rows:
            # Create a dictionary or an object to represent the ticket
            ticket = {
                'id': row[0],
                'quantity': row[1],
                'ticket_type': row[2],
                'canceled_by': row[3],
                'booking_id': row[4],
                'total_price': row[5],
                'created_at': row[6],
                'updated_at': row[7],
            }
            tickets.append(ticket)
        return tickets


def return_allowances():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM main_allowance")
        rows = cursor.fetchall()
        # Process the query results
        allowances = []
        for row in rows:
            # Create a dictionary or an object to represent the allowance
            allowance = {
                'id': row[0],
                'from_location': row[1],
                'destination': row[2],
                'depart_date': row[3],
                'arriving_date': row[4],
                'economy_seats': row[5],
                'first_class_seats': row[6],
                'business_class_seats': row[7],
                'economy_seat_price': row[8],
                'first_class_seat_price': row[9],
                'business_class_seat_price': row[10],
            }
            allowances.append(allowance)
        return allowances


def get_tickets_with_feedbacks_and_allowance():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                ticket.id,
                ticket.quantity,
                ticket.ticket_type,
                ticket.canceled_by,
                ticket.booking_id,
                ticket.total_price,
                ticket.created_at AS ticket_created_at,
                ticket.updated_at AS ticket_updated_at,
                allowance.id AS allowance_id,
                allowance.from_location,
                allowance.destination,
                allowance.depart_date,
                allowance.arriving_date,
                allowance.economy_seats,
                allowance.first_class_seats,
                allowance.business_class_seats,
                allowance.economy_seat_price,
                allowance.first_class_seat_price,
                allowance.business_class_seat_price,
                allowance.created_at AS allowance_created_at,
                allowance.updated_at AS allowance_updated_at,
                feedback.id AS feedback_id,
                feedback.title,
                feedback.description,
                feedback.email,
                feedback.created_at AS feedback_created_at,
                feedback.updated_at AS feedback_updated_at
            FROM
                main_ticket AS ticket
            LEFT JOIN
                main_allowance AS allowance ON ticket.allowance_id = allowance.id
            LEFT JOIN
                main_feedback AS feedback ON ticket.id = feedback.ticket_id
            ORDER BY
                ticket.created_at ASC
        """)

        results = cursor.fetchall()
        tickets = []
        ticket_dict = {}

        for row in results:
            ticket_id = row[0]
            if ticket_id not in ticket_dict:
                # Create a new ticket dictionary
                ticket = {
                    'id': ticket_id,
                    'quantity': row[1],
                    'ticket_type': row[2],
                    'canceled_by': row[3],
                    'booking_id': row[4],
                    'total_price': row[5],
                    'created_at': row[6],
                    'updated_at': row[7],
                    'allowance': {
                        'id': row[8],
                        'from_location': row[9],
                        'destination': row[10],
                        'depart_date': row[11],
                        'arriving_date': row[12],
                        'economy_seats': row[13],
                        'first_class_seats': row[14],
                        'business_class_seats': row[15],
                        'economy_seat_price': row[16],
                        'first_class_seat_price': row[17],
                        'business_class_seat_price': row[18],
                        'created_at': row[19],
                        'updated_at': row[20],
                    },
                    'feedbacks': []
                }
                ticket_dict[ticket_id] = ticket
                tickets.append(ticket)

            feedback_id = row[21]
            if feedback_id:
                # Create a new feedback object and add it to the corresponding ticket
                feedback = {
                    'id': feedback_id,
                    'title': row[22],
                    'description': row[23],
                    'email': row[24],
                    'created_at': row[25],
                    'updated_at': row[26],
                }
                ticket_dict[ticket_id]['feedbacks'].append(feedback)

    return tickets

    """
   The function generate_ticket_report() generates a report based on the ticket data.
    1. Retrieves the ticket data using the return_tickets() function.
    2. Converts the ticket data into a Pandas DataFrame.
    3. Calculates the number of tickets booked per type by grouping the DataFrame by 'ticket_type' and summing the 'quantity' column.
    4. Calculates the total number of tickets booked by summing the 'quantity' column.
    5. Calculates the income made per ticket type by grouping the DataFrame by 'ticket_type' and summing the 'total_price' column.
    6. Calculates the total income made by summing the 'total_price' column.
    7. Creates a new DataFrame for the report with columns 'Ticket Type', 'Tickets Booked', and 'Income' using the calculated values.
    8. Calculates the total row for the report by creating a new DataFrame with a single row containing the values 'Total', total_tickets, and total_income.
    9. Concatenates the report DataFrame with the total row to include the total information in the report.
    10. Returns the final report DataFrame.
    """



def generate_ticket_report():
    # Retrieve the ticket data
    tickets = return_tickets()
    # Convert the data into a Pandas DataFrame
    df = pd.DataFrame.from_records(tickets)

    # Calculate the number of tickets booked per type
    tickets_per_type = df.groupby('ticket_type')['quantity'].sum()

    # Calculate the total number of tickets booked
    total_tickets = df['quantity'].sum()

    # Calculate the income made per ticket type
    income_per_type = df.groupby('ticket_type')['total_price'].sum()

    # Calculate the total income made
    total_income = df['total_price'].sum()

    # Create a new DataFrame for the report
    report_df = pd.DataFrame({
        'Ticket Type': tickets_per_type.index,
        'Tickets Booked': tickets_per_type.values,
        'Income': income_per_type.values,
    })

    # Calculate the total row for the report
    total_row = pd.DataFrame({
        'Ticket Type': 'Total',
        'Tickets Booked': total_tickets,
        'Income': total_income
    }, index=[0])

    # Concatenate the report DataFrame with the total row
    report_df = pd.concat([report_df, total_row])
    return report_df


def generate_report_of_report():
    # Retrieve data from the tables
    allowances = Allowance.objects.all()
    # Prepare the data for the report
    report_data = []
    for allowance in allowances:
        tickets = Ticket.objects.select_related('allowance').filter(allowance_id=allowance.id)
        feedbacks = Feedback.objects.filter(ticket__allowance_id=allowance.id).values('ticket_id').annotate(feedback_count=Count('ticket_id'))

        allowance_data = {
            'From Location': allowance.from_location,
            'Destination': allowance.destination,
            'Economy Seats Remaining': allowance.economy_seats - sum(ticket.quantity for ticket in tickets if ticket.ticket_type == 'econom'),
            'First Class Seats Remaining': allowance.first_class_seats - sum(ticket.quantity for ticket in tickets if ticket.ticket_type == 'first'),
            'Business Class Seats Remaining': allowance.business_class_seats - sum(ticket.quantity for ticket in tickets if ticket.ticket_type == 'business'),
            'Total Booked Tickets': sum(ticket.quantity for ticket in tickets),
            'Total Price of Booked Tickets': sum(ticket.total_price for ticket in tickets),
            'Feedback Count': next((feedback['feedback_count'] for feedback in feedbacks if feedback['ticket_id'] == allowance.id), 0)
        }
        report_data.append(allowance_data)
        
    report_df = pd.DataFrame(report_data)
    return report_df