from tabnanny import verbose
from unicodedata import name
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django.db.models.signals import post_save

CATEGORY_CHOICES = (
    ('TP', 'Track Pants'),
    ('H', 'Hoodie'),
    ('SH', 'Sweatshirt'),
    ('SS','Sport suit')
)
ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
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
    title = models.CharField(max_length=100,verbose_name = 'Название')
    price = models.FloatField(verbose_name = 'Цена')
    discount_price = models.FloatField(blank=True, null=True,verbose_name = 'Цена со скидкой')
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2,verbose_name = 'Категория')
    slug = models.SlugField()
    description = models.TextField(verbose_name = 'Описание')
    image = models.ImageField(verbose_name = 'Изображение')

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
    class Meta:
        verbose_name = 'Вещь'
        verbose_name_plural = 'Вещи'

class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name = 'Пользователь')
    ordered = models.BooleanField(default=False,verbose_name = 'Заказано')
    item = models.ForeignKey(Item, on_delete=models.CASCADE,verbose_name = 'Вещь')
    quantity = models.IntegerField(default=1,verbose_name = 'Количество')

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
    class Meta:
        verbose_name = 'Пункт заказа'
        verbose_name_plural = 'Пункты заказа'
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name = 'Пользователь')
    ref_code = models.CharField(max_length=20, blank=True, null=True,verbose_name = 'Реферальный код')
    items = models.ManyToManyField(OrderItem,verbose_name = 'Вещь')
    start_date = models.DateTimeField(auto_now_add=True, verbose_name = 'Время заказа')
    ordered_date = models.DateTimeField(verbose_name = 'Дата заказа')
    ordered = models.BooleanField(default=False, verbose_name = 'Заказано')
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True,verbose_name = 'Адрес доставки')
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True,verbose_name = 'Адрес для выставления счета')
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True, verbose_name = 'Платёж')
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True,verbose_name = 'Купон')
    being_delivered = models.BooleanField(default=False, verbose_name = 'Доставлено')
    received = models.BooleanField(default=False, verbose_name = 'Получено')
    refund_requested = models.BooleanField(default=False,verbose_name = 'Пользователь')
    refund_granted = models.BooleanField(default=False,verbose_name = 'Возврат предоставлен')

    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return f'Профиль пользователя {self.user.username}' 

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
    
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name = 'Пользователь')
    street_address = models.CharField(max_length=100,verbose_name = 'Адрес улицы')
    apartment_address = models.CharField(max_length=100,verbose_name = 'Дом')
    country = CountryField(multiple=False,verbose_name = 'Страна')
    zip = models.CharField(max_length=100, verbose_name = 'Почтовый индекс')
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES,verbose_name = 'Тип адреса')
    default = models.BooleanField(default=False,verbose_name = 'Значение по умолчанию')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'
        

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50,verbose_name = 'ID Транзакции')
    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name = 'Пользователь')
    amount = models.FloatField(verbose_name = 'Количество')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name = 'Отметка времени')

    def __str__(self):
        return f'Профиль пользователя {self.user.username}' 
    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'

class Coupon(models.Model):
    code = models.CharField(max_length=15,verbose_name = 'Код купона')
    amount = models.FloatField(verbose_name = 'Количество')

    def __str__(self):
        return self.code
    class Meta:
        verbose_name = 'Купон'
        verbose_name_plural = 'Купоны'

class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,verbose_name = 'Заказ')
    reason = models.TextField(verbose_name = 'Причина')
    accepted = models.BooleanField(default=False,verbose_name = 'Принято')
    email = models.EmailField(verbose_name = 'Электронная почта')

    def __str__(self):
        return f"{self.pk}"
    class Meta:
        verbose_name = 'Возврат'
        verbose_name_plural = 'Возвраты'
    
def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender= User)