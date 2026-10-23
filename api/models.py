# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser # <-- Важный импорт для токенов
from django.contrib.auth.models import BaseUserManager # <-- Важный импорт для менеджера с токенами


class CartItems(models.Model):
    pk = models.CompositePrimaryKey('client_id', 'item_id')
    client = models.ForeignKey('User', models.DB_CASCADE)
    item = models.ForeignKey('Menu', models.DB_CASCADE)
    quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'cart_items'


class Category(models.Model):
    category_name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'category'


class ClientAddress(models.Model):
    client = models.ForeignKey('User', models.DO_NOTHING)
    address_label = models.CharField(max_length=30)
    full_address = models.TextField()
    courier_comment = models.TextField(blank=True, null=True)
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'client_address'


class ClientCard(models.Model):
    client = models.ForeignKey('User', models.DO_NOTHING)
    masked_number = models.CharField(max_length=20)
    payment_system = models.CharField(max_length=30)
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'client_card'


class ClientFavorite(models.Model):
    client = models.ForeignKey('User', models.DB_CASCADE)
    item = models.ForeignKey('Menu', models.DB_CASCADE)

    class Meta:
        managed = False
        db_table = 'client_favorite'
        unique_together = (('client', 'item'),)


class District(models.Model):
    restaurant = models.ForeignKey('Restaurant', models.DB_CASCADE)
    district_name = models.CharField(max_length=100)
    delivery_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'district'


class Menu(models.Model):
    item_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    weight_grams = models.IntegerField()
    calories = models.IntegerField()
    proteins = models.IntegerField()
    fats = models.IntegerField()
    carbs = models.IntegerField()
    category = models.ForeignKey(Category, models.DB_SET_NULL, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'menu'


class Order(models.Model):
    client = models.ForeignKey('User', models.DO_NOTHING)
    address = models.ForeignKey(ClientAddress, models.DO_NOTHING)
    district = models.ForeignKey(District, models.DO_NOTHING)
    employee = models.ForeignKey('User', models.DB_SET_NULL, related_name='order_employee_set', blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.TextField()  # This field type is a guess.
    order_status = models.TextField()  # This field type is a guess.
    created_at = models.DateTimeField()
    predicted_delivery_time = models.DateTimeField()
    bonus_applied = models.DecimalField(max_digits=10, decimal_places=2)
    bonus_earned = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid_cash_card = models.DecimalField(max_digits=10, decimal_places=2)
    card = models.ForeignKey(ClientCard, models.DB_SET_NULL, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, models.DB_CASCADE)
    item = models.ForeignKey(Menu, models.DO_NOTHING)
    quantity = models.IntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'order_item'


class Restaurant(models.Model):
    restaurant_name = models.CharField(max_length=100)
    address_text = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'restaurant'


class Role(models.Model):
    role_name = models.CharField(unique=True, max_length=30)

    class Meta:
        managed = False
        db_table = 'role'


class MyUserManager(BaseUserManager):
    def get_by_natural_key(self, username):
        # Обучаем Django искать суперпользователя админки по номеру телефона
        return self.get(**{self.model.USERNAME_FIELD: username})


class User(AbstractBaseUser): # <-- Наследуемся от AbstractBaseUser кастомизация для токенизации
    objects = MyUserManager() # Есть предположение, что это поможет настроить авторизацию 

    phone_number = models.CharField(unique=True, max_length=15)
    full_name = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255, blank=True, null=True)
    # password = models.CharField(max_length=255, db_column='password_hash')
    
    bonus_balance = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField()

    # Скрываем стандартное поле пароля Django, так как у вас свой password_hash
    password = None 

    # # Системные константы, которые требует встроенная аутентификация
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']


    # ИСПРАВЛЕНИЕ: Django Admin использует ФИО как логин для входа
    # USERNAME_FIELD = 'full_name'  
    # REQUIRED_FIELDS = ['password'] # Переносим телефон в список обязательных полей


    class Meta:
        managed = False
        db_table = 'user'

    # Переопределяем встроенный метод проверки пароля под вашу СУБД структуру
    def check_password(self, raw_password):
        return self.password_hash == raw_password


class UserRole(models.Model):
    pk = models.CompositePrimaryKey('user_id', 'role_id')
    user = models.ForeignKey(User, models.DB_CASCADE)
    role = models.ForeignKey(Role, models.DB_CASCADE)

    class Meta:
        managed = False
        db_table = 'user_role'
