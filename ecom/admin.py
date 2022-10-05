from django.contrib import admin
from .models import UserProfile,Item,OrderItem,Order,Address,Payment,Coupon,Refund

admin.site.register(UserProfile)
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Address)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)

