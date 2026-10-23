from django.contrib import admin
from .models import (
    Menu, 
    Category, 
    District, 
    Restaurant, 
    Role, 
    Order, 
    OrderItem,
    User
)

admin.site.register(Menu)
admin.site.register(Category)
admin.site.register(District)
admin.site.register(Restaurant)
admin.site.register(Role)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(User)
