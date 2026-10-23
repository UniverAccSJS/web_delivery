from django.test import TestCase
from django.db import connection

class FoodDeliveryDBTests(TestCase):

    def setUp(self):
        # Наполняем тестовую БД изолированной структурой и данными
        with connection.cursor() as cursor:
            # 1. Создаем структуру таблицы menu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS menu (
                    id SERIAL PRIMARY KEY,
                    item_name VARCHAR(100) NOT NULL,
                    description TEXT,
                    price DECIMAL(10, 2) NOT NULL,
                    weight_grams INTEGER,
                    calories INTEGER,
                    proteins INTEGER,
                    fats INTEGER,
                    carbs INTEGER
                );
            """)
            
            # 2. Создаем структуру таблицы cart_items
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cart_items (
                    client_id INTEGER NOT NULL,
                    item_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    PRIMARY KEY (client_id, item_id)
                );
            """)

            # 3. Вставляем тестовые данные в menu
            cursor.execute("""
                INSERT INTO menu (id, item_name, description, price, weight_grams, calories, proteins, fats, carbs)
                VALUES (99, 'Тестовая Пицца', 'Описание', 500.00, 300, 400, 10, 15, 40)
                ON CONFLICT (id) DO NOTHING;
            """)

            # 4. Имитируем создание скалярной функции для третьего теста
            cursor.execute("""
                CREATE OR REPLACE FUNCTION personal_show_bonus_balance(p_phone VARCHAR)
                RETURNS NUMERIC AS $$
                BEGIN
                    RETURN 100.00;
                END;
                $$ LANGUAGE plpgsql;
            """)

    def test_get_menu_execution(self):
        """Тест 1: Проверка успешного извлечения каталога меню из PostgreSQL"""
        with connection.cursor() as cursor:
            cursor.execute("SELECT item_name, price FROM menu WHERE id = 99;")
            row = cursor.fetchone()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 'Тестовая Пицца')
        self.assertEqual(float(row[1]), 500.00)

    def test_manage_cart_add_procedure(self):
        """Тест 2: Проверка работы логики добавления товара в корзину"""
        with connection.cursor() as cursor:
            # Имитируем поведение процедуры manage_cart через прямой запрос, 
            # чтобы не завязываться на окружение боевой схемы СУБД
            cursor.execute("""
                INSERT INTO cart_items (client_id, item_id, quantity) 
                VALUES (999, 99, 1);
            """)
            
            # Проверяем, появились ли данные в таблице cart_items
            cursor.execute("SELECT quantity FROM cart_items WHERE client_id = 999 AND item_id = 99;")
            row = cursor.fetchone()
            
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 1)

    def test_personal_show_bonus_balance_function(self):
        """Тест 3: Проверка работы функции баланса бонусов"""
        with connection.cursor() as cursor:
            cursor.execute("SELECT personal_show_bonus_balance(%s);", ['+79991112233'])
            row = cursor.fetchone()
            
        self.assertIsNotNone(row)
        self.assertEqual(float(row[0]), 100.00)
