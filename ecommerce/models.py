from enum import unique
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

from django.utils import timezone # get today date and time 

class Customer_Profile(models.Model):
    custId = models.OneToOneField(User, on_delete=models.CASCADE)
    phoneNo = models.CharField(max_length=20, null=True)
    gender = models.CharField(max_length=10, null=True)
    dob = models.DateField(auto_now=False, null=True)

    def __str__(self):
        return self.custId

class Addresses(models.Model):
    addressId = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField()
    postcode = models.IntegerField()
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)

    def __str__(self):
        return self.address

class Customer_Addresses(models.Model):
    userId = models.OneToOneField(User, on_delete=models.CASCADE)
    addressId = models.IntegerField(primary_key=True,auto_created=True)

    class Meta:
        unique_together = (("userId","addressId"),)

    def __str__(self):
        return self.userId,  " and ", self.addressId

class Category(models.Model):
    categoryId = models.IntegerField(primary_key=True,auto_created=True)
    categoryName = models.CharField(max_length=20)

    def __str__(self):
        return self.categoryId

class Furniture(models.Model):
    furnitureId = models.CharField(primary_key=True, max_length=50)
    furnitureName = models.CharField(max_length=50)
    furnitureImg = models.ImageField(upload_to='furniture')
    furnitureDesc = models.TextField(max_length=1000)
    unitPrice = models.DecimalField(max_digits=5, decimal_places=2)
    stock = models.IntegerField(default=0)
    categoryId = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.furnitureId

    # def get_add_to_cart_url(self):
    #     return reverse("core:add-to-cart", kwargs={
    #         'slug': self.slug
    #     })

    # def get_remove_from_cart_url(self):
    #     return reverse("core:remove-from-cart", kwargs={
    #         'slug': self.slug
    #     })

class User_Views(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    furnitureId = models.ForeignKey(Furniture, on_delete=models.CASCADE)
    viewCount = models.IntegerField()
    
    def __str__(self):
        return self.userId, " and ", self.furnitureId

class Cart_Products(models.Model):
    cartId = models.IntegerField(primary_key=True, auto_created=True)
    furnitureId = models.ForeignKey(Furniture, on_delete=models.CASCADE)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    dateCreated = models.DateField(auto_now=True)

    def __str__(self):
        return self.cartId

class Payment(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.userId

class Order(models.Model):
    orderId = models.CharField(primary_key=True, max_length=50)
    orderDate = models.DateField(auto_now=True)
    startDate = models.DateTimeField(auto_now_add=True)
    shippingAddress = models.ForeignKey(Customer_Addresses, related_name='shiiping_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, blank=True, null=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    isDelivered = models.BooleanField(default=False)
    isReceived = models.BooleanField(default=False)

    def __str__(self):
        return self.orderId

    # def get_total(self):
    #     total = 0
    #     for order_item in self.items.all():
    #         total += order_item.get_final_price()
    #     if self.coupon:
    #         total -= self.coupon.amount
    #     return total    

class Order_Products(models.Model):
    orderId = models.ForeignKey(Order, on_delete=models.CASCADE)
    furnitureId = models.ForeignKey(Furniture, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    def __str__(self):
        return self.orderId, " and ", self.furnitureId

    # def get_total_item_price(self):
    #     return self.quantity * self.item.price

    # def get_total_discount_item_price(self):
    #     return self.quantity * self.item.discount_price

    # def get_amount_saved(self):
    #     return self.get_total_item_price() - self.get_total_discount_item_price()

    # def get_final_price(self):
    #     if self.item.discount_price:
    #         return self.get_total_discount_item_price()
    #     return self.get_total_item_price()



class Rating(models.Model):
    furnitureId = models.ForeignKey(Furniture, on_delete=models.CASCADE)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True)

    def __str__(self):
        return self.furnitureId, " and ", self.userId, " and ", self.rating