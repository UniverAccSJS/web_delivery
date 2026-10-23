# authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token


# authentication.py или прямо в views.py / models.py
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from .models import User as ClientUser

class CustomAuthtokenBackend(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            # Напрямую лезем в таблицу authtoken_token через SQL/ORM
            token = Token.objects.get(key=key)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Неверный токен')

        try:
            # Принудительно вытаскиваем клиента из ВАШЕЙ таблицы 'user' по id,
            # который сохранен в поле user_id таблицы токенов
            user = ClientUser.objects.get(id=token.user_id)
        except ClientUser.DoesNotExist:
            raise AuthenticationFailed('Пользователь не найден')

        return (user, token)


class ClientTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None
        
        try:
            token_type, token_key = auth_header.split(' ')
            if token_type.lower() not in ['token', 'bearer']:
                return None
        except ValueError:
            return None

        try:
            # Ищем токен в базе данных DRF
            token = Token.objects.select_related('user').get(key=token_key)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Неверный токен')

        # Возвращаем пользователя из вашей таблицы `user` и сам токен
        return (token.user, token)
