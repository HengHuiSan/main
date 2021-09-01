from enum import unique
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

from django.utils import timezone
from numpy import random # get today date and time 

class Customer_Profile(models.Model):
    custId = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phoneNo = models.CharField(max_length=20, null=True)
    gender = models.CharField(max_length=10, null=True)
    dob = models.DateField(auto_now=False, null=True)
    address1 = models.CharField(max_length=255, null=True)
    address2 = models.CharField(max_length=255, null=True)
    town = models.CharField(max_length=50, null=True)
    postcode = models.IntegerField(default=0, null=True)
    state = models.CharField(max_length=50, null=True)

    def __str__(self):
        template = '{0.custId} {0.phoneNo}'
        return template.format(self)


class Category(models.Model):
    categoryId = models.IntegerField(primary_key=True,auto_created=True)
    categoryName = models.CharField(max_length=100)

    def __str__(self):
        return self.categoryName

class Furniture(models.Model):
    furnitureId = models.CharField(primary_key=True, max_length=50)
    furnitureName = models.CharField(max_length=50)
    furnitureImg = models.ImageField(upload_to='furniture')
    furnitureGenres = models.TextField(max_length=1000)
    unitPrice = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.IntegerField(default=0)
    categoryId = models.ForeignKey(Category, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100)
    
    def __str__(self):
        template = '{0.furnitureId} {0.furnitureName}'
        return template.format(self)
    
    def get_absolute_url(self):
        return reverse("ecommerce:product", kwargs={
            'slug': self.slug
        })
    
    def update_view_count_url(self):
        return reverse("ecommerce:view", kwargs={
            'slug': self.slug
        })

    def add_to_cart_url(self):
        return reverse("ecommerce:add-to-cart", kwargs={
            'slug': self.slug
        })

class User_Views(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    furnitureId = models.ForeignKey(Furniture, on_delete=models.CASCADE)
    viewCount = models.IntegerField()
    
    def __str__(self):
        template = '{0.userId} {0.furnitureId} {0.viewCount}'
        return template.format(self)
    
class Cart_Products(models.Model):
    cartId = models.IntegerField(primary_key=True, auto_created=True)
    furnitureId = models.ForeignKey(Furniture, on_delete=models.CASCADE)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    dateCreated = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=50)

    def __str__(self):
        template = '{0.furnitureId} {0.userId}  {0.quantity}'
        return template.format(self)
    
    def remove_from_cart_url(self):
        return reverse("ecommerce:remove-from-cart", kwargs={
            'slug': self.slug
        })

    @property
    def get_item_total_price(self):
        return self.quantity * self.furnitureId.unitPrice

    @property
    def get_cart_total(self):
        return self.objects.all().count()
        # return self.objects.all().aggregate(sum('quantity'))
        # return sum([item.get_item_total_price for item in self.objects.all()])

class Payment(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.userId

class Order(models.Model):
    orderId = models.CharField(primary_key=True, max_length=50)
    orderDate = models.DateField(auto_now_add=True)
    name = models.CharField(max_length=100, null=True)
    shippingAddress = models.CharField(max_length=255)
    phoneNo = models.CharField(max_length=20)
    email = models.CharField(max_length=255, null=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    isDelivered = models.BooleanField(default=False)
    isReceived = models.BooleanField(default=False)

    def __str__(self):
        return self.orderId

    def make_order_id():
        return str(random.randint(100000, 999999))
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