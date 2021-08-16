from enum import unique
from django.db import models
from django.contrib.auth.models import User
from django.db.models.base import Model
from django.utils import timezone # get today date and time 

class Customer_Info(models.Model):
    customerId = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True)
    phoneNo = models.CharField(max_length=20, null=True)
    gender = models.CharField(max_length=10, null=True)
    dob = models.DateField(auto_now=False, null=True)

    def __str__(self):
        return self.customerId

class Category(models.Model):
    categoryId = models.CharField(primary_key=True, max_length=10,auto_created=True)
    categoryName = models.CharField(max_length=20)

    def __str__(self):
        return self.categoryId

class Furniture(models.Model):
    furnitureId = models.CharField(primary_key=True, max_length=50)
    furnitureName = models.CharField(max_length=50)
    furnitureImg = models.ImageField(upload_to='furniture')
    furnitureDesc = models.TextField(max_length=1000)
    unitPrice = models.DecimalField(max_digits=5, decimal_places=2)
    categoryId = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.furnitureId

class User_Profile(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    furnitureId = models.ForeignKey(Furniture, on_delete=models.CASCADE)
    viewCount = models.IntegerField()

    class Meta: 
        unique_together = (("userId","furnitureId"),)

    def __str__(self):
        return self.userId + " and " + self.furnitureId

class Cart(models.Model):
    cartId = models.IntegerField(primary_key=True, auto_created=True)
    furnitureId = models.ForeignKey(Furniture, on_delete=models.CASCADE)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.cartId

class Order(models.Model):
    orderId = models.CharField(primary_key=True, max_length=50)
    orderDate = models.DateField(auto_now=True)
    status = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    furnitureId = models.ForeignKey(Furniture, on_delete=models.CASCADE)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.orderId