from django.db import models
import datetime

#Allowance model- table(SQL)
class Allowance(models.Model):
    from_location = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    depart_date = models.DateField()
    arriving_date = models.DateField()
    economy_seats = models.IntegerField()
    first_class_seats = models.IntegerField()
    business_class_seats = models.IntegerField()
    economy_seat_price = models.IntegerField()
    first_class_seat_price = models.IntegerField()
    business_class_seat_price = models.IntegerField()
    created_at = models.DateTimeField(default=datetime.date.today)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # def __str__(self):
    #     return f"Allowance: {self.from_location} to {self.destination}"

#Ticket model - table(SQL
#
class Ticket(models.Model):
    #'TICKET_TYPES'-tuple of tuples
    #database value and readable name 
    # for comfort when I am assigning value from this table
    TICKET_TYPES = (
        ('econom', 'Economy'),
        ('first', 'First Class'),
        ('business', 'Business Class'),
    )
    #'CANCELED_BY'-tuple of tuples
    #database value and readable name 
    # for comfort when I am assigning value from this table
    CANCELED_BY =(
        ('client','Client'),
        ('admin','Admin')
    )
    allowance=models.ForeignKey(Allowance, on_delete=models.CASCADE,null=True,blank=True)
    discount_applied=models.BooleanField(default=False)
    quantity = models.IntegerField()
    ticket_type = models.CharField(max_length=100, choices=TICKET_TYPES)
    canceled_by = models.CharField(max_length=100, choices=CANCELED_BY)
    booking_id = models.CharField(max_length=100)
    total_price = models.IntegerField()
    created_at = models.DateTimeField(default=datetime.date.today)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)


#Feedback model - table(SQL)for users feedback
class Feedback(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    email = models.EmailField(null=True,blank=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE,null=True,blank=True)
    created_at = models.DateTimeField(default=datetime.date.today)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

class Discount(models.Model):
    value=models.IntegerField()
    code=models.CharField(max_length=100)
    allowance=models.ForeignKey(Allowance, on_delete=models.CASCADE,null=True,blank=True)
    created_at = models.DateTimeField(default=datetime.date.today)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)


# class User(models.Model):
#     first_name = models.CharField(max_length=50)
#     last_name = models.CharField(max_length=50)
#     password = models.CharField(max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     deleted_at = models.DateTimeField(null=True, blank=True)        


#each field represents a column in table;
# this models allow to perform database and interact wirh the data