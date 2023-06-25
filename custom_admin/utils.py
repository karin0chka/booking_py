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