# Create your views here.
import os
import json
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection, transaction
from django.db.models import F, Sum
from django.utils import timezone

# Импорты для Django REST Framework
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token


# Импорты для генерации PDF-чеков
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


######

# импорты моделей
from .models import (
    Category, Menu, Restaurant, District, User, 
    Role, UserRole, ClientAddress, ClientCard, 
    ClientFavorite, CartItems, Order, OrderItem
)

# импорты сер-в
from .serializers import (
    CategorySerializer, MenuSerializer, RestaurantSerializer, 
    DistrictSerializer, UserSerializer, RoleSerializer, 
    UserRoleSerializer, ClientAddressSerializer, ClientCardSerializer, 
    ClientFavoriteSerializer, CartItemsSerializer, OrderSerializer, 
    OrderItemSerializer
)


###################################################################### МЕНЮ #########################################################################################################

# 1. Получение всех позиций из меню таблица menu
class MenuViewSet(viewsets.ModelViewSet):
    # Метод select_related('category') подтягивает данные из связанной таблицы за 1 JOIN запрос
    queryset = Menu.objects.all().select_related('category').order_by('id')
    serializer_class = MenuSerializer

    def list(self, request, *args, **kwargs):
        client_id = request.query_params.get('client_id', None)
        if client_id in ('null', '', None):
            client_id = None

        queryset = self.get_queryset()
        
        # Получаем ID лайкнутых блюд из связующей таблицы для текущего пользователя
        favorite_ids = set()
        if client_id:
            try:
                favorite_ids = set(
                    ClientFavorite.objects.filter(client_id=client_id)
                    .values_list('item_id', flat=True)
                )
            except Exception as e:
                print("🚨 ОШИБКА ПРИ ПОЛУЧЕНИИ ИЗБРАННОГО:", str(e))

        # Передаем объекты в сериализатор
        serializer = self.get_serializer(queryset, many=True)
        menu_items = serializer.data

        # Динамически проставляем булевы флаги (true/false) для сердечек на фронтенде
        for item in menu_items:
            item["is_favorite"] = item["id"] in favorite_ids

        return Response(menu_items, status=status.HTTP_200_OK)


# 2. Получение списка категорий из таблицы category
class CategoriesListView(APIView):
    def get(self, request):
        try:
            categories = Category.objects.all().order_by('id')
            serializer = CategorySerializer(categories, many=True)
            print(f"🍏 УСПЕШНО ЗАГРУЖЕНО ИЗ БД: {categories.count()} КАТЕГОРИЙ")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print("🚨 ОШИБКА ПОДКЛЮЧЕНИЯ К ТАБЛИЦЕ CATEGORY:", str(e))
            return Response([], status=status.HTTP_200_OK)
            


###################################################################### ВХОД, АВТОРИЗАЦИЯ, УДАЛЕНИЕ #########################################################################################################
# 3. Вход (Авторизация) пользователя
class LoginView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        password_hash = request.data.get('password_hash')

        try:
            user = User.objects.get(phone_number=phone_number)
            
            if user.check_password(password_hash):
                if user.is_active:
                    # 3. ВСТРОЕННАЯ МАГИЯ: Автоматически создаем или находим токен в СУБД
                    token, created = Token.objects.get_or_create(user_id=user.id)
                    
                    serializer = UserSerializer(user)
                    return Response({
                        "success": True,
                        "token": token.key,
                        "user": serializer.data
                    }, status=status.HTTP_200_OK)
                    
                return Response({"success": False, "error": "Аккаунт деактивирован. Обратитесь в поддержку"}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({"success": False, "error": "Неверный номер телефона или пароль"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"success": False, "error": "Неверный номер телефона или пароль"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



# 4. Регистрация нового пользователя
class RegisterView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        full_name = request.data.get('full_name')
        password_hash = request.data.get('password_hash')

        if not phone_number or not full_name or not password_hash:
            print(f"🚨 ВНИМАНИЕ: Прилетели пустые поля! phone_number={phone_number}, full_name={full_name}")
            return Response({"success": False, "error": "Переданы пустые обязательные поля"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if User.objects.filter(phone_number=phone_number).exists():
                return Response({"success": False, "error": "Пользователь с таким номером уже существует"}, status=status.HTTP_400_BAD_REQUEST)
                
            user = User.objects.create(
                phone_number=phone_number,
                full_name=full_name,
                password_hash=password_hash,
                bonus_balance=0.00,
                is_active=True
            )
            serializer = UserSerializer(user)
            return Response({
                "success": True, 
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"🚨 КРИТИЧЕСКАЯ ОШИБКА В РЕГИСТРАЦИИ: {str(e)}")
            return Response({"success": False, "error": "Ошибка регистрации: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 5. Удаление профиля пользователя
class DeleteProfileView(APIView):
    def post(self, request):
        client_id = request.data.get('client_id')

        try:
            user = User.objects.get(id=client_id)
            user.is_active = False  # Мягкое скрытие аккаунта
            user.save()
            print(f"🍏 Профиль пользователя №{client_id} успешно переведен в неактивный статус")
            return Response({"success": True}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"success": False, "error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print("🚨 ОШИБКА В DELETE_USER_PROFILE:", str(e))
            return Response({"success": False, "error": "Ошибка сервера: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)


###################################################################### ПРОСМОТР ПРОФИЛЯ #########################################################################################################

# 6. Получение актуального баланса бонусов с жестким логированием
class ClientBonusBalanceView(APIView):
    def get(self, request, client_id):
        try:
            user = User.objects.get(id=client_id)
            print(f"📊 БОНУСЫ для клиента {client_id}: {user.bonus_balance}")
            return Response({"bonus_balance": float(user.bonus_balance)}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"bonus_balance": 0.0}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print("🚨 ОШИБКА В GET_CLIENT_BONUS_BALANCE:", str(e))
            return Response({"bonus_balance": 0.0}, status=status.HTTP_200_OK)

# 7. Получение адресов клиента
class ClientAddressesView(APIView):
    def get(self, request, client_id):
        try:
            addresses = ClientAddress.objects.filter(client_id=client_id, is_active=True).order_by('id')
            serializer = ClientAddressSerializer(addresses, many=True)
            print(f"🍏 ОРМ ВЕРНУЛА: {len(serializer.data)} АДРЕСОВ")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print("🚨 ОШИБКА В ПОЛУЧЕНИИ АДРЕСОВ:", str(e))
            return Response([], status=status.HTTP_200_OK)

# 8. Получение активных карт из базы данных
class ClientCardsView(APIView):
    def get(self, request, client_id):
        try:
            cards = ClientCard.objects.filter(client_id=client_id, is_active=True)
            serializer = ClientCardSerializer(cards, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print("🚨 ОШИБКА В ClientCardsView:", str(e))
            return Response([], status=status.HTTP_200_OK)


# 9. Получение истории заказов
class ClientOrderHistoryView(APIView):
    def get(self, request, client_id):
        try:
            history = Order.objects.filter(client_id=client_id).order_by('-created_at')
            serializer = OrderSerializer(history, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print("🚨 ОШИБКА GET_CLIENT_ORDER_HISTORY:", str(e))
            return Response([], status=status.HTTP_200_OK)


# 10. Получение избранного
class ClientFavoritesView(APIView):
    def get(self, request, client_id):
        try:
            favorites = ClientFavorite.objects.filter(client_id=client_id).select_related('item')
            serializer = ClientFavoriteSerializer(favorites, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print("🚨 ОШИБКА В GET_CLIENT_FAVORITES:", str(e))
            return Response([], status=status.HTTP_200_OK)



# 11. Получение активных заказов
class ClientActiveOrdersView(APIView):
    def get(self, request, client_id):
        try:
            # 1. Достаем заказы из СУБД, исключая финальные системные статусы
            active_orders = Order.objects.filter(
                client_id=client_id
            ).exclude(
                order_status__in=['DELIVERED', 'CANCELLED']
            ).order_by('-created_at')
            
            # ТЕХНИЧЕСКИЙ ЛОГ: Посмотрите в терминал Django, сколько заказов нашла ORM!
            print(f"📊 [Active Orders] Для клиента {client_id} в СУБД найдено активных записей: {active_orders.count()}")
            
            serializer = OrderSerializer(active_orders, many=True)
            orders_data = serializer.data


            # 2. Маппинг «всеядности»: дублируем статус, ID, сумму и способ оплаты для React
            for order in orders_data:
                # --- Синхронизация статуса ---
                current_status = order.get("order_status") or order.get("status") or ""
                if current_status in ["CREATED", "PENDING", "PROCESSING"]:
                    ru_status = "В обработке"
                elif current_status in ["DELIVERING", "SHIPPED"]:
                    ru_status = "В пути"
                else:
                    ru_status = current_status if current_status else "В обработке"

                order["order_status"] = ru_status
                order["status"] = ru_status

                # --- Синхронизация ID заказа ---
                original_id = order.get("id") or order.get("order_id")
                order["order_id"] = original_id
                order["id"] = original_id

                # --- Синхронизация денежных ключей ---
                raw_amount = order.get("total_amount") or order.get("amount_paid_cash_card") or order.get("price") or 0
                original_amount = float(raw_amount)
                
                order["total_amount"] = original_amount
                order["amount_paid_cash_card"] = original_amount
                order["price"] = original_amount
                order["amount"] = original_amount
                order["total"] = original_amount
                order["total_price"] = original_amount

                # --- ИСПРАВЛЕНИЕ: Логика перевода способов оплаты ---
                # Читаем способ оплаты из базы (обычно это строки 'CARD' или 'CASH')
                pay_method = order.get("payment_method") or ""
                
                if pay_method == "CARD":
                    payment_text = "Оплачено"
                elif pay_method == "CASH":
                    payment_text = "Наличными курьеру"
                else:
                    payment_text = "Не указан"

                # Записываем перевод в специальное текстовое поле
                order["payment_text"] = payment_text

            return Response(orders_data, status=status.HTTP_200_OK)

        except Exception as e:
            print("🚨 КРИТИЧЕСКАЯ ОШИБКА В ClientActiveOrdersView:", str(e))
            return Response([], status=status.HTTP_200_OK)


###################################################################### РЕДАКТИРОВАНИЕ #########################################################################################################

# 12. Обновление профиля пользователя в PostgreSQL
class UpdateProfileView(APIView):
    def post(self, request):
        client_id = request.data.get('client_id')
        full_name = request.data.get('full_name')
        phone_number = request.data.get('phone_number')

        try:
            user = User.objects.get(id=client_id)
            user.full_name = full_name
            user.phone_number = phone_number
            user.save()
            print(f"🍏 ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ №{client_id} УСПЕШНО ОБНОВЛЕН")
            return Response({"success": True}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"success": False, "error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print("🚨 ОШИБКА ОБНОВЛЕНИЯ ПРОФИЛЯ:", str(e))
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 13. Управление адресами клиента
class ManageAddressView(APIView):
    def post(self, request):
        action = request.data.get('action')          # 'ADD', 'EDIT', 'DELETE'
        client_id = request.data.get('client_id')
        address_id = request.data.get('address_id', None) 
        address_label = request.data.get('address_label', 'Дом')
        full_address = request.data.get('full_address', '')
        comment = request.data.get('comment', '')    

        try:
            if action == 'ADD':
                address = ClientAddress.objects.create(
                    client_id=client_id,
                    address_label=address_label,
                    full_address=full_address,
                    courier_comment=comment,
                    is_active=True
                )
                return Response({"success": True, "address_id": address.id}, status=status.HTTP_200_OK)
                
            elif action == 'EDIT' and address_id:
                address = ClientAddress.objects.get(id=address_id, client_id=client_id)
                address.address_label = address_label
                address.full_address = full_address
                address.courier_comment = comment
                address.save()
                return Response({"success": True, "address_id": address.id}, status=status.HTTP_200_OK)
                
            elif action == 'DELETE' and address_id:
                address = ClientAddress.objects.get(id=address_id, client_id=client_id)
                address.is_active = False  # Безопасное логическое удаление
                address.save()
                return Response({"success": True, "address_id": address.id}, status=status.HTTP_200_OK)
                
            return Response({"success": False, "error": "Неверное действие или отсутствуют параметры"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("🚨 ОШИБКА В MANAGE_ADDRESSES:", str(e))
            return Response({"success": False, "error": "Ошибка сервера: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 14. Управление картами клиента
class ManageCardView(APIView):
    def post(self, request):
        action = request.data.get('action')          # 'ADD' или 'DELETE'
        client_id = request.data.get('client_id')
        card_id = request.data.get('card_id', None)  
        payment_system = request.data.get('payment_system', 'MIR')
        masked_number = request.data.get('masked_number', '')

        if payment_system == 'MIR':
            payment_system = 'Мир'
        elif payment_system == 'VISA':
            payment_system = 'Visa'
        elif payment_system == 'MASTERCARD':
            payment_system = 'Mastercard'

        try:
            if action == 'ADD':
                ClientCard.objects.create(
                    client_id=client_id,
                    masked_number=masked_number,
                    payment_system=payment_system,
                    is_active=True
                )
                print(f"🍏 Карта успешно добавлена через ORM")
                return Response({"success": True}, status=status.HTTP_200_OK)
                
            elif action == 'DELETE' and card_id:
                card = ClientCard.objects.get(id=card_id, client_id=client_id)
                card.is_active = False
                card.save()
                print(f"🍏 Карта успешно удалена через ORM")
                return Response({"success": True}, status=status.HTTP_200_OK)
                
            return Response({"success": False, "error": "Неизвестное действие"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("🚨 ОШИБКА ВНУТРИ MANAGE_CARD_VIEW:", str(e))
            return Response({"success": False, "error": "Ошибка сервера: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 15. Управление избранным клиента
class ManageFavoriteView(APIView):
    def post(self, request):
        client_id = request.data.get('client_id')
        item_id = request.data.get('item_id')
        action = request.data.get('action') # 'ADD' или 'REMOVE'

        try:
            if action == 'ADD':
                ClientFavorite.objects.get_or_create(client_id=client_id, item_id=item_id)
            elif action == 'REMOVE':
                ClientFavorite.objects.filter(client_id=client_id, item_id=item_id).delete()
            return Response({"success": True}, status=status.HTTP_200_OK)
        except Exception as e:
            print("🚨 ОШИБКА В MANAGE_FAVORITES:", str(e))
            return Response({"success": False, "error": "Ошибка сервера: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)


###################################################################### СОЗДАНИЕ И ОФОРМЛЕНИЕ ЗАКАЗА и доступное после #########################################################################################################

# 16. Управление количеством товара в корзине через процедуру manage_cart (добавить отображение стоимость блюд)
class SyncCartItemView(APIView):
    def post(self, request):
        client_id = request.data.get('client_id')
        item_id = request.data.get('item_id')
        action = request.data.get('action') # 'ADD', 'DECREMENT', 'REMOVE_ALL'

        try:
            if action == 'ADD':
                cart_item, created = CartItems.objects.get_or_create(
                    client_id=client_id, item_id=item_id,
                    defaults={'quantity': 1}
                )
                if not created:
                    cart_item.quantity += 1
                    cart_item.save()
                    
            elif action == 'DECREMENT':
                cart_item = CartItems.objects.filter(client_id=client_id, item_id=item_id).first()
                if cart_item:
                    if cart_item.quantity > 1:
                        cart_item.quantity -= 1
                        cart_item.save()
                    else:
                        cart_item.delete()
                        
            elif action == 'REMOVE_ALL':
                CartItems.objects.filter(client_id=client_id, item_id=item_id).delete()
                
            return Response({"success": True}, status=status.HTTP_200_OK)
        except Exception as e:
            print("🚨 ОШИБКА В MANAGE_CART:", str(e))
            return Response({"success": False, "error": "Ошибка сервера: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)

# 17. Оформление заказа (Исправленный вызов со сбросом курсора транзакции)
# class CreateOrderView(APIView):
#     def post(self, request):
#         client_id = request.data.get('client_id')
#         address_id = request.data.get('address_id')
#         district_id = request.data.get('district_id')
#         payment_method = request.data.get('payment_method')       
#         bonuses_to_spend = float(request.data.get('bonuses_to_spend', 0))
#         card_id = request.data.get('card_id', None)                

#         try:
#             with transaction.atomic():
#                 cart_items = CartItems.objects.filter(client_id=client_id)
#                 if not cart_items.exists():
#                     return Response({"success": False, "error": "Корзина пуста"}, status=status.HTTP_400_BAD_REQUEST)
                
#                 # total_items_amount = cart_items.aggregate(
#                 #     total=Sum(F('quantity') * F('item__price'))
#                 # )['total'] or 0
                
#                 # district = District.objects.get(id=district_id)
#                 # # delivery_price = district.delivery_price
                
#                 # user = User.objects.select_for_update().get(id=client_id)
#                 # if bonuses_to_spend > float(user.bonus_balance):
#                 #     return Response({"success": False, "error": "Недостаточно бонусов"}, status=status.HTTP_400_BAD_REQUEST)
                
#                 # total_amount = float(total_items_amount) + float(delivery_price) # - bonuses_to_spend
#                 # total_amount_after_bonuses = total_amount - bonuses_to_spend
#                 # bonus_earned = total_amount * 0.05  # Начисление 5% бонусов
                
#                 # user.bonus_balance = float(user.bonus_balance) - bonuses_to_spend # + bonus_earned
#                 # user.save()

#                 # # Запись заказа
#                 # order = Order.objects.create(
#                 #     client_id=client_id,
#                 #     address_id=address_id,
#                 #     district_id=district_id,
#                 #     total_amount=total_amount,
#                 #     payment_method=payment_method,
#                 #     order_status='CREATED', # 'CREATED', 'ACCEPTED', 'COOKING', 'DELIVERING', 'DELIVERED', 'CANCELLED'
#                 #     created_at=timezone.now(),
#                 #     predicted_delivery_time=timezone.now() + timezone.timedelta(minutes=45),
#                 #     bonus_applied=bonuses_to_spend,
#                 #     bonus_earned=bonus_earned,
#                 #     amount_paid_cash_card=total_amount_after_bonuses,
#                 #     card_id=int(card_id) if card_id else None
#                 # )

#                 total_items_amount = cart_items.aggregate(
#                     total=Sum(F('quantity') * F('item__price'))
#                 )['total'] or 0
                
#                 # 1. ОБЯЗАТЕЛЬНО получаем реальную стоимость доставки из района
#                 district = District.objects.get(id=district_id)
#                 # delivery_price = float(district.delivery_price) if hasattr(district, 'delivery_price') else 0.0
                
#                 # 2. Высчитываем полную "грязную" стоимость (блюда + доставка)
#                 total_amount = float(total_items_amount) # + delivery_price
                
#                 user = User.objects.select_for_update().get(id=client_id)
#                 if bonuses_to_spend > float(user.bonus_balance):
#                     return Response({"success": False, "error": "Недостаточно бонусов"}, status=status.HTTP_400_BAD_REQUEST)
                
#                 # 3. Сумма к оплате деньгами — это строгая разница между полной суммой и бонусами
#                 total_amount_after_bonuses = total_amount - bonuses_to_spend
                
#                 # Защита: сумма к оплате деньгами не может стать отрицательной
#                 if total_amount_after_bonuses < 0:
#                     total_amount_after_bonuses = 0.0
                
#                 bonus_earned = total_amount * 0.05  # Начисление 5% бонусов
                
#                 # user.bonus_balance = float(user.bonus_balance) - bonuses_to_spend
#                 # user.save()

#                 # Запись заказа
#                 order = Order.objects.create(
#                     client_id=client_id,
#                     address_id=address_id,
#                     district_id=district_id,
#                     # Теперь эти три поля гарантированно сойдутся в формуле: total_amount = amount_paid + bonus_applied
#                     total_amount=total_amount,                          # Полная сумма (например, 840.00)
#                     amount_paid_cash_card=total_amount_after_bonuses,   # Деньгами (например, 830.00)
#                     bonus_applied=bonuses_to_spend,                     # Бонусами (например, 10.00)
                    
#                     payment_method=payment_method,
#                     order_status='CREATED',
#                     created_at=timezone.now(),
#                     predicted_delivery_time=timezone.now() + timezone.timedelta(minutes=45),
#                     bonus_earned=bonus_earned,
#                     card_id=int(card_id) if card_id else None
#                 )


#                 # Перенос из корзины в позиции заказа
#                 order_items_to_create = [
#                     OrderItem(
#                         order=order,
#                         item=cart.item,
#                         quantity=cart.quantity,
#                         price_at_purchase=cart.item.price
#                     ) for cart in cart_items
#                 ]
#                 OrderItem.objects.bulk_create(order_items_to_create)

#                 cart_items.delete()

#                 print(f"🍏 Заказ №{order.id} успешно создан через ORM! Карта ID: {card_id}")
#                 return Response({"success": True, "order_id": order.id}, status=status.HTTP_201_CREATED)
                    
#         except Exception as e:
#             print("🚨 ОШИБКА СОЗДАНИЯ ЗАКАЗА:", str(e))
#             return Response({"success": False, "error": "Ошибка сервера: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)



class CreateOrderView(APIView):
    def post(self, request):
        client_id = request.data.get('client_id')
        address_id = request.data.get('address_id')
        district_id = request.data.get('district_id')
        payment_method = request.data.get('payment_method')       
        bonuses_to_spend = float(request.data.get('bonuses_to_spend', 0))
        card_id = request.data.get('card_id', None)                

        try:
            with transaction.atomic():
                cart_items = CartItems.objects.filter(client_id=client_id)
                if not cart_items.exists():
                    return Response({"success": False, "error": "Корзина пуста"}, status=status.HTTP_400_BAD_REQUEST)
                
                # 1. Считаем чистую стоимость блюд из корзины
                total_items_amount = cart_items.aggregate(
                    total=Sum(F('quantity') * F('item__price'))
                )['total'] or 0
                
                total_amount = float(total_items_amount)
                
                user = User.objects.select_for_update().get(id=client_id)
                if bonuses_to_spend > float(user.bonus_balance):
                    return Response({"success": False, "error": "Недостаточно бонусов"}, status=status.HTTP_400_BAD_REQUEST)
                
                # 2. Высчитываем сколько останется оплатить деньгами
                total_amount_after_bonuses = total_amount - bonuses_to_spend
                if total_amount_after_bonuses < 0:
                    total_amount_after_bonuses = 0.0
                
                bonus_earned = total_amount * 0.05  
                
                user.bonus_balance = float(user.bonus_balance) - bonuses_to_spend
                user.save()

                # 3. Запись заказа с точным совпадением констрейнта
                order = Order.objects.create(
                    client_id=client_id,
                    address_id=address_id,
                    district_id=district_id,
                    payment_method=payment_method,
                    order_status='CREATED',
                    created_at=timezone.now(),
                    predicted_delivery_time=timezone.now() + timezone.timedelta(minutes=45),
                    bonus_earned=bonus_earned,
                    card_id=int(card_id) if card_id else None,
                    total_amount=total_amount,                          
                    amount_paid_cash_card=total_amount_after_bonuses,   
                    bonus_applied=bonuses_to_spend                      
                )

                # Перенос из корзины в позиции заказа
                order_items_to_create = [
                    OrderItem(
                        order=order,
                        item=cart.item,
                        quantity=cart.quantity,
                        price_at_purchase=cart.item.price
                    ) for cart in cart_items
                ]
                OrderItem.objects.bulk_create(order_items_to_create)

                cart_items.delete()

                print(f"🍏 Заказ №{order.id} успешно создан через ORM!")
                return Response({"success": True, "order_id": order.id}, status=status.HTTP_201_CREATED)
                    
        except Exception as e:
            print("🚨 ОШИБКА СОЗДАНИЯ ЗАКАЗА:", str(e))
            return Response({"success": False, "error": "Ошибка сервера: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 18. Просмотр деталей заказа (ИСПРАВЛЕНО: добавлен full_address в инфо)
class OrderDetailsView(APIView):
    def get(self, request, order_id):
        try:
            order_items = OrderItem.objects.filter(order_id=order_id).select_related('item')
            items_serializer = OrderItemSerializer(order_items, many=True)

            order = Order.objects.select_related('address').get(id=order_id)
            
            order_serializer = OrderSerializer(order)
            order_data = order_serializer.data

            if order.address:
                order_data["full_address"] = order.address.full_address
            else:
                order_data["full_address"] = "Адрес не указан"

            return Response({
                "items": items_serializer.data,
                "info": order_data
            }, status=status.HTTP_200_OK)
            
        except Order.DoesNotExist:
            return Response({"error": "Заказ не найден"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print("🚨 ОШИБКА В OrderDetailsView:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



# 19. ФОрмирование чека и загрузка
# class DownloadReceiptView(APIView):
#     def get(self, request, order_id):
#         try:
#             order = Order.objects.select_related('address').get(id=order_id)
#             order_items = OrderItem.objects.filter(order=order).select_related('item')
            
#             response = HttpResponse(content_type='application/pdf')
#             response['Content-Disposition'] = f'attachment; filename="receipt_order_{order_id}.pdf"'
            
#             try:
#                 pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
#                 font_name = 'Arial'
#             except Exception:
#                 font_name = 'Helvetica'

#             p = canvas.Canvas(response)
#             p.setFont(font_name, 14)
            
#             p.drawString(100, 800, f"========================================")
#             p.drawString(100, 780, f"       ЧЕК ПО ЗАКАЗУ №{order.id}")
#             p.drawString(100, 760, f"========================================")
#             p.drawString(100, 730, f"Дата создания: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
#             p.drawString(100, 710, f"Адрес доставки: {order.address.full_address if order.address else 'Не указан'}")
#             p.drawString(100, 690, f"Способ оплаты: {'Карта' if order.payment_method == 'CARD' else 'Наличные'}")
#             p.drawString(100, 660, f"----------------------------------------")
#             p.drawString(100, 640, f"Состав заказа:")
            
#             current_y = 610
#             for op in order_items:
#                 subtotal = op.quantity * float(op.price_at_purchase)
#                 p.drawString(100, current_y, f" • {op.item.item_name} x {op.quantity} шт. = {subtotal} руб.")
#                 current_y -= 20
                
#             p.drawString(100, current_y - 10, f"----------------------------------------")
#             if float(order.bonus_applied) > 0:
#                 p.drawString(100, current_y - 30, f"Списано бонусов: -{order.bonus_applied} руб.")
#                 current_y -= 20
                
#             p.drawString(100, current_y - 40, f"ИТОГО К ОПЛАТЕ: {order.total_amount} руб.")
#             p.drawString(100, current_y - 60, f"========================================")
#             p.drawString(100, current_y - 80, f"   Приятного аппетита!")
            
#             p.showPage()
#             p.save()
#             return response
            
#         except Order.DoesNotExist:
#             return HttpResponse("Заказ не найден", status=404)
#         except Exception as e:
#             return HttpResponse(f"Ошибка генерации PDF чека: {str(e)}", status=400)

# 19. ФОрмирование чека и загрузка
class DownloadReceiptView(APIView):
    def get(self, request, order_id):
        try:
            order = Order.objects.select_related('address').get(id=order_id)
            order_items = OrderItem.objects.filter(order=order).select_related('item')
            
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="receipt_order_{order_id}.pdf"'
            
            # Динамически подбираем кириллический шрифт в зависимости от ОС (Windows/Linux)
            font_name = 'DejaVu'
          # Ищем шрифт прямо внутри папки вашего приложения api
            # Автоматический подбор шрифта прямо из папки вашего приложения api
            current_dir = os.path.dirname(os.path.abspath(__file__))
            font_path = os.path.join(current_dir, 'DejaVuSans.ttf')
            
            pdfmetrics.registerFont(TTFont('DejaVu', font_path))
            font_name = 'DejaVu'

            p = canvas.Canvas(response)
            p.setFont(font_name, 14)

            p = canvas.Canvas(response)
            # Применяем подобранный шрифт
            p.setFont(font_name, 14)
            
            p.drawString(100, 800, f"========================================")
            p.drawString(100, 780, f"       ЧЕК ПО ЗАКАЗУ №{order.id}")
            p.drawString(100, 760, f"========================================")
            
            # Локализация даты создания в удобочитаемый вид
            # created_local = timezone.localtime(order.created_at)
            # p.drawString(100, 730, f"Дата создания: {created_local.strftime('%Y-%m-%d %H:%M:%S')}")
            p.drawString(100, 730, f"Дата создания: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            p.drawString(100, 710, f"Адрес доставки: {order.address.full_address if order.address else 'Не указан'}")
            p.drawString(100, 690, f"Способ оплаты: {'Карта' if order.payment_method == 'CARD' else 'Наличные'}")
            p.drawString(100, 660, f"----------------------------------------")
            p.drawString(100, 640, f"Состав заказа:")
            
            current_y = 610
            for op in order_items:
                subtotal = op.quantity * float(op.price_at_purchase)
                p.drawString(100, current_y, f" • {op.item.item_name} x {op.quantity} шт. = {subtotal} руб.")
                current_y -= 20
                
            p.drawString(100, current_y - 10, f"----------------------------------------")
            if float(order.bonus_applied) > 0:
                p.drawString(100, current_y - 30, f"Списано бонусов: -{order.bonus_applied} руб.")
                current_y -= 20
                
            p.drawString(100, current_y - 40, f"ИТОГО К ОПЛАТЕ: {order.total_amount} руб.")
            p.drawString(100, current_y - 60, f"========================================")
            p.drawString(100, current_y - 80, f"   Приятного аппетита!")
            
            p.showPage()
            p.save()
            return response
            
        except Order.DoesNotExist:
            return HttpResponse("Заказ не найден", status=404)
        except Exception as e:
            return HttpResponse(f"Ошибка генерации PDF чека: {str(e)}", status=400)




# 20. Обновление баланаса после получения статуса заказа "DELIVERED"/"Доставлен" взамен функции из СУБД
# api/views.py (добавить в конец файла)

class UpdateOrderStatusView(APIView):
    """
    Эндпоинт для обновления статуса заказа курьером или администратором.
    При переведении в статус DELIVERED автоматически начисляет бонусы клиенту.
    """
    def post(self, request, order_id):
        new_status = request.data.get('status') # Ожидается 'DELIVERED', 'CANCELLED' и т.д.

        if not new_status:
            return Response({"success": False, "error": "Статус не передан"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Находим заказ и блокируем строку для предотвращения гонки данных
                order = Order.objects.select_for_update().get(id=order_id)
                
                # Если заказ уже был доставлен ранее, повторно бонусы не начисляем
                if order.order_status == 'DELIVERED':
                    return Response({"success": False, "error": "Заказ уже имеет статус Доставлен"}, status=status.HTTP_400_BAD_REQUEST)

                # Если новый статус — ДОСТАВЛЕН, выполняем начисление бонусов
                if new_status == 'DELIVERED':
                    client = User.objects.select_for_update().get(id=order.client_id)
                    
                    # Плюсуем заработанные за этот заказ бонусы к балансу клиента
                    client.bonus_balance = float(client.bonus_balance) + float(order.bonus_earned)
                    client.save()
                    
                    print(f"🍏 БОНУСЫ НАЧИСЛЕНЫ: Клиенту №{client.id} добавлено {order.bonus_earned} ₽ за заказ №{order.id}")

                # Обновляем статус самого заказа в СУБД
                order.order_status = new_status
                order.save()

                return Response({"success": True, "current_status": order.order_status}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"success": False, "error": "Заказ не найден"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success": False, "error": "Ошибка СУБД: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
