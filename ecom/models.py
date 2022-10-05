from tabnanny import verbose
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import reverse

CATEGORY_CHOICES = (
    ('TP', 'Track Pants'),
    ('H', 'Hoodie'),
    ('SH', 'Sweatshirt'),
    ('SS','Sport suit')
)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)
    
    def __str__(self):
        return f'Профиль пользователя {self.user.username}' 
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
        
class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("ecom:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("ecom:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("ecom:remove-from-cart", kwargs={
            'slug': self.slug
        })

class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()