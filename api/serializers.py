from rest_framework import serializers
from .models import (
    Category, Menu, Restaurant, District, User, 
    Role, UserRole, ClientAddress, ClientCard, 
    ClientFavorite, CartItems, Order, OrderItem
)

# 1. КАТЕГОРИИ
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


# 2. МЕНЮ
class MenuSerializer(serializers.ModelSerializer):
    # Красивое название категории для вывода на экран
    category_name = serializers.CharField(source='category.category_name', read_only=True)

    class Meta:
        model = Menu
        fields = [
            'id', 'item_name', 'description', 'price', 'weight_grams', 
            'calories', 'proteins', 'fats', 'carbs', 
            'category',       # Числовой ID категории из БД
            'category_name'   # Текстовое название категории
        ]


# 3. РЕСТОРАНЫ
class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'


# 4. РАЙОНЫ ДОСТАВКИ
class DistrictSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.restaurant_name', read_only=True)

    class Meta:
        model = District
        fields = ['id', 'district_name', 'delivery_price', 'restaurant', 'restaurant_name']


# 5. ПОЛЬЗОВАТЕЛИ
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'full_name', 'bonus_balance', 'is_active']


# 6. РОЛИ ПОЛЬЗОВАТЕЛЕЙ
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

# СОПОСТАВЛЕНИЕ
class UserRoleSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    role_name = serializers.CharField(source='role.role_name', read_only=True)

    class Meta:
        model = UserRole
        fields = ['user', 'user_name', 'role', 'role_name']


# 7. АДРЕСА КЛИЕНТОВ
class ClientAddressSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name', read_only=True)

    class Meta:
        model = ClientAddress
        fields = ['id', 'address_label', 'full_address', 'courier_comment', 'is_active', 'client', 'client_name']


# 8. БАНКОВСКИЕ КАРТЫ
class ClientCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientCard
        fields = ['id', 'masked_number', 'payment_system', 'is_active', 'client']


# 9. ИЗБРАННОЕ с норм ценой
class ClientFavoriteSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.item_name', read_only=True)
    price = serializers.DecimalField(source='item.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ClientFavorite
        fields = ['client', 'item', 'item_name', 'price'] 


# 10. КОРЗИНА
class CartItemsSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.item_name', read_only=True)
    price = serializers.DecimalField(source='item.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItems
        fields = ['client', 'item', 'item_name', 'price', 'quantity']


# 11. ПОЗИЦИИ ЗАКАЗА
class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.item_name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'item', 'item_name', 'quantity', 'price_at_purchase']


# 12. ЗАКАЗЫ
class OrderSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    address_text = serializers.CharField(source='address.full_address', read_only=True)
    district_name = serializers.CharField(source='district.district_name', read_only=True)
    
    # позволяет сразу увидеть все блюда внутри заказа при GET-запросе
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'client', 'client_name', 'address', 'address_text', 
            'district', 'district_name', 'employee', 'total_amount', 
            'payment_method', 'order_status', 'created_at', 
            'predicted_delivery_time', 'bonus_applied', 'bonus_earned', 
            'amount_paid_cash_card', 'card', 'items'
        ]
