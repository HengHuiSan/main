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
    postcode = models.CharField(max_length=20, null=True)
    state = models.CharField(max_length=50, null=True)
    profile_pic = models.ImageField(upload_to='account', default="default.png", null=True, blank=True)

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
    
    def update_view_count_url(self):
        return reverse("ecommerce:view", kwargs={
            'slug': self.slug
        })

    def add_to_cart_url(self):
        return reverse("ecommerce:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_absolute_url(self):
        return reverse("administration:edit-item", kwargs={
            'slug':self.slug,
        })
    
    def delete_item_url(self):
        return reverse("administration:delete-item", kwargs={
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
    slug = models.SlugField(max_length=10, null=True)

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


class Order(models.Model):
    orderId = models.CharField(primary_key=True, max_length=50)
    orderDate = models.DateField(auto_now_add=True)
    name = models.CharField(max_length=100, null=True)
    shippingAddress = models.CharField(max_length=255)
    phoneNo = models.CharField(max_length=20)
    email = models.CharField(max_length=255, null=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    isDelivered = models.BooleanField(default=False)
    isReceived = models.BooleanField(default=False)
    slug = models.SlugField(max_length=100)

    def __str__(self):
        template = '{0.orderId} {0.orderDate} {0.name} {0.shippingAddress} {0.phoneNo} {0.amount}'
        return template.format(self)

    
    def get_process_order_url(self):
        return reverse("administration:process-order", kwargs={
            'slug': self.slug,
            'action': 'process'
        })

    def get_view_order_url(self):
        return reverse("administration:process-order", kwargs={
            'slug': self.slug,
            'action': 'view'
        })

class Order_Products(models.Model):
    orderId = models.ForeignKey(Order, on_delete=models.CASCADE)
    furnitureId = models.ForeignKey(Furniture, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    def __str__(self):
        template = '{0.orderId} {0.furnitureId} {0.quantity}'
        return template.format(self)

class Donation(models.Model):
    donationId = models.CharField(primary_key=True, max_length=50)
    dateCreated = models.DateField(auto_now_add=True)
    name = models.CharField(max_length=100, null=True)
    itemType = models.CharField(max_length=20)
    description = models.CharField(max_length=500)
    image = models.ImageField(upload_to='donation')
    yearPurchased = models.PositiveIntegerField()
    originalPrice = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    isApproved = models.BooleanField(null=True)
    slug = models.SlugField(max_length=100)


    def __str__(self):
        template = '{0.donationId} {0.name}  {0.itemType}'
        return template.format(self)
    
    def accept_donation_url(self):
        return reverse("administration:process-donation", kwargs={
            'slug': self.slug,
            'approve':True
        })

    def reject_donation_url(self):
        return reverse("administration:process-donation", kwargs={
            'slug': self.slug,
            'approve':False
        })


class Image(models.Model):
    img = models.ImageField(upload_to='testing')