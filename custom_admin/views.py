from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .utils import check_if_admin, return_allowances, get_tickets_with_feedbacks_and_allowance, generate_ticket_report, generate_report_of_report
from django .db import connection
from datetime import datetime
from .models import Report
import json


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.is_superuser:
            login(request, user)
            return redirect('/custom_admin/')
        else:
            return redirect('/custom_admin/login/')
    else:
        return render(request, 'login.html')




@login_required(login_url="login/")
def logout_view(request):
    logout(request)
    return redirect('/custom_admin/login')


# Updated and created allowences logic
@login_required(login_url="login/")
def update_allowance(request):
    check_if_admin(request)
    if request.method == "POST":
        id = request.POST.get('allowance_id')
        economy_seats = request.POST.get('economy_seats')
        first_class_seats = request.POST.get('first_class_seats')
        business_class_seats = request.POST.get('business_class_seats')
        economy_seat_price = request.POST.get('economy_seat_price')
        first_class_seat_price = request.POST.get('first_class_seat_price')
        business_class_seat_price = request.POST.get(
            'business_class_seat_price')
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE main_allowance SET economy_seats=%s, first_class_seats=%s, business_class_seats=%s, economy_seat_price=%s, first_class_seat_price=%s, business_class_seat_price=%s WHERE id=%s",
                [economy_seats, first_class_seats, business_class_seats,
                    economy_seat_price, first_class_seat_price, business_class_seat_price, id]
            )
            connection.commit()
        return redirect('custom_admin')

@login_required(login_url="login/")
def dashboard_view(request):
    check_if_admin(request)
    context = {'allowances': [], 'tickets':[], 'reports':[]}
    context['allowances'] = return_allowances()
    context['tickets'] = get_tickets_with_feedbacks_and_allowance()
    context['reports'] = Report.objects.all().order_by('created_at')
    return render(request, 'dash.html', context)

@login_required(login_url="login/")
def create_allowance(request):
    check_if_admin(request)
    if request.method == "POST":
        created_at= datetime.now()
        from_location = request.POST.get('from_location')
        destination = request.POST.get('destination')
        depart_date = request.POST.get('depart_date')
        arriving_date = request.POST.get('arriving_date')
        economy_seats = request.POST.get('economy_seats')
        first_class_seats = request.POST.get('first_class_seats')
        business_class_seats = request.POST.get('business_class_seats')
        economy_seat_price = request.POST.get('economy_seat_price')
        first_class_seat_price = request.POST.get('first_class_seat_price')
        business_class_seat_price = request.POST.get(
            'business_class_seat_price')
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO main_allowance (from_location, destination, depart_date, arriving_date, economy_seats, first_class_seats, business_class_seats, economy_seat_price, first_class_seat_price, business_class_seat_price, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )",
                [from_location, destination, depart_date, arriving_date, economy_seats, first_class_seats,
                    business_class_seats, economy_seat_price, first_class_seat_price, business_class_seat_price, created_at, created_at]
            )
            # Remember to commit the transaction
            connection.commit()
        return redirect('custom_admin')
    

@login_required(login_url="login/")
def new_admin_feedback(request):
    check_if_admin(request)
    if request.method == "POST":
        created_at= datetime.now()
        ticket_id=request.POST.get('ticket_id')
        title=request.POST.get('title')
        description=request.POST.get('description')

        with connection.cursor() as cursor:
            cursor.execute(
                 "INSERT INTO main_feedback (ticket_id, title, description, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
                 [ticket_id, title, description, created_at, created_at ]
            )
            connection.commit()
        return redirect('custom_admin')
    

@login_required(login_url="login/")
def return_ticket_csv_report(request):
    check_if_admin(request)
    report_df = generate_ticket_report() 

    created_at= datetime.now()
    json_str = json.dumps(report_df.to_dict(orient='records'))
    with connection.cursor() as cursor:
        cursor.execute(
             "INSERT INTO custom_admin_report (value, created_at, updated_at) VALUES (%s, %s, %s)",
             [json_str, created_at, created_at ]
        )
        connection.commit() 
    # Create the HTTP response with the CSV file
    report_csv = report_df.to_csv(index=False)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="report.csv"'
    response.write(report_csv)
    return response
    
@login_required(login_url="login/")
def return_all_report(request):
    check_if_admin(request)
    report_df=generate_report_of_report()
    json_str = report_df.to_dict(orient='records')
    print(json_str)

    report_csv = report_df.to_csv(index=False)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="report.csv"'
    response.write(report_csv)
    return response


