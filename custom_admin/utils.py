from django.shortcuts import redirect
from django.contrib.auth import logout
from django .db import connection



def check_if_admin(request):
     
     if not request.user.is_superuser:
        logout(request)
        return redirect('/custom_admin/login')
     
 #Using raw  SQL insted of ORM to fetch all the allowences and put it in the dictionary

def return_allowances():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM main_allowance")
        rows = cursor.fetchall()
        # Process the query results
        allowances = []
        for row in rows:
            # Create a dictionary or an object to represent the allowance
            allowance = {
                'id':row[0],
                'from_location':row[1],
                'destination':row[2],
                'depart_date':row[3],
                'arriving_date':row[4],
                'economy_seats':row[5],
                'first_class_seats':row[6],
                'business_class_seats':row[7],
                'economy_seat_price':row[8],
                'first_class_seat_price':row[9],
                'business_class_seat_price':row[10],
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