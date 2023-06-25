from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .utils import check_if_admin, return_allowances
from django .db import connection
from datetime import datetime


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
def dashboard_view(request):
    check_if_admin(request)
    context = {'allowances': []}
    context['allowances'] = return_allowances()

    return render(request, 'dash.html', context)


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