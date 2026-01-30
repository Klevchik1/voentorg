import os
import random
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from voentorg.models import CustomUser, Category, Product, ProductImage, OrderStatus
from django.utils.text import slugify
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Заполняет базу данных начальными данными для приложения Военторг'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить базу данных перед заполнением',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Очистка базы данных...')
            ProductImage.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            CustomUser.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('База данных очищена'))

        self.create_order_statuses()
        self.create_categories()
        self.create_products()
        self.create_test_users()

        self.stdout.write(self.style.SUCCESS('База данных успешно заполнена!'))

    def create_order_statuses(self):
        """Создание статусов заказов"""
        statuses = [
            {'code': 'new', 'name': 'Новый заказ', 'description': 'Заказ создан, ожидает обработки'},
            {'code': 'processing', 'name': 'В обработке', 'description': 'Заказ обрабатывается менеджером'},
            {'code': 'shipped', 'name': 'Отправлен', 'description': 'Товар передан в службу доставки'},
            {'code': 'delivered', 'name': 'Доставлен', 'description': 'Товар получен покупателем'},
            {'code': 'cancelled', 'name': 'Отменён', 'description': 'Заказ отменён'},
        ]

        for status_data in statuses:
            OrderStatus.objects.get_or_create(
                code=status_data['code'],
                defaults=status_data
            )

        self.stdout.write('Созданы статусы заказов')

    def create_categories(self):
        """Создание категорий товаров"""
        categories_data = [
            {
                'name': 'Тактическая одежда',
                'slug': 'tactical-clothing',
                'description': 'Специальная одежда для активного отдыха и тактических операций'
            },
            {
                'name': 'Тактические рюкзаки',
                'slug': 'tactical-backpacks',
                'description': 'Рюкзаки для походов, путешествий и тактического использования'
            },
            {
                'name': 'Тактическое снаряжение',
                'slug': 'tactical-gear',
                'description': 'Специальное снаряжение и оборудование'
            },
            {
                'name': 'Палатки и спальные мешки',
                'slug': 'tents-sleeping-bags',
                'description': 'Снаряжение для кемпинга и полевых условий'
            },
            {
                'name': 'Обувь',
                'slug': 'footwear',
                'description': 'Специальная обувь для активного отдыха и тактики'
            },
            {
                'name': 'Тактическая медицина',
                'slug': 'tactical-medicine',
                'description': 'Медицинское снаряжение и аптечки для полевых условий'
            },
            {
                'name': 'Аксессуары',
                'slug': 'accessories',
                'description': 'Дополнительные аксессуары и мелочи'
            },
        ]

        for cat_data in categories_data:
            Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )

        self.stdout.write('Созданы категории товаров')

    def create_products(self):
        """Создание товаров с изображениями"""
        # Получаем все категории
        categories = {
            'одежда': Category.objects.get(slug='tactical-clothing'),
            'рюкзаки': Category.objects.get(slug='tactical-backpacks'),
            'снаряжение': Category.objects.get(slug='tactical-gear'),
            'палатки': Category.objects.get(slug='tents-sleeping-bags'),
            'обувь': Category.objects.get(slug='footwear'),
            'медицина': Category.objects.get(slug='tactical-medicine'),
            'аксессуары': Category.objects.get(slug='accessories'),
        }

        products_data = [
            # Тактическая одежда
            {
                'name': 'Тактическая куртка MULTICAM',
                'category': categories['одежда'],
                'price': 4500.00,
                'stock': 15,
                'description': 'Прочная тактическая куртка с камуфляжем MULTICAM. Водонепроницаемая ткань, вентиляционные отверстия, множество карманов.',
                'short_description': 'Куртка тактическая камуфляжная',
                'colors': ['#5d5d5d', '#2d5a2d', '#000000'],
            },
            {
                'name': 'Брюки тактические Flecktarn',
                'category': categories['одежда'],
                'price': 3200.00,
                'stock': 22,
                'description': 'Тактические брюки немецкого камуфляжа Flecktarn. Усиленные колени, карманы для наколенников, регулируемая талия.',
                'short_description': 'Брюки полевые камуфляжные',
                'colors': ['#5d5d5d', '#808080'],
            },
            {
                'name': 'Футболка тактическая черная',
                'category': categories['одежда'],
                'price': 1200.00,
                'stock': 40,
                'description': 'Тактическая футболка из быстросохнущего материала. Вентиляционные вставки, плоские швы.',
                'short_description': 'Футболка для активного отдыха',
                'colors': ['#000000', '#2d5a2d'],
            },

            # Тактические рюкзаки
            {
                'name': 'Рюкзак тактический 30л',
                'category': categories['рюкзаки'],
                'price': 2800.00,
                'stock': 10,
                'description': 'Тактический рюкзак объемом 30 литров. Система MOLLE, отделение для гидратора, поясной ремень.',
                'short_description': 'Рюкзак для походов и тактики',
                'colors': ['#000000', '#2d5a2d', '#5d5d5d'],
            },
            {
                'name': 'Штурмовой рюкзак 20л',
                'category': categories['рюкзаки'],
                'price': 3500.00,
                'stock': 8,
                'description': 'Компактный штурмовой рюкзак для быстрых вылазок. Прочная ткань Cordura, система быстрого доступа.',
                'short_description': 'Компактный рюкзак для активного использования',
                'colors': ['#5d5d5d', '#000000'],
            },

            # Тактическое снаряжение
            {
                'name': 'Разгрузочный жилет MOLLE',
                'category': categories['снаряжение'],
                'price': 4200.00,
                'stock': 12,
                'description': 'Разгрузочный жилет с системой MOLLE. Регулируемые лямки, возможность крепления дополнительных подсумков.',
                'short_description': 'Жилет разгрузочный тактический',
                'colors': ['#000000', '#2d5a2d'],
            },
            {
                'name': 'Подсумок для магазинов',
                'category': categories['снаряжение'],
                'price': 800.00,
                'stock': 25,
                'description': 'Подсумок на 3 магазина. Быстрое крепление на систему MOLLE, защита от влаги.',
                'short_description': 'Подсумок для тактического снаряжения',
                'colors': ['#000000', '#5d5d5d'],
            },

            # Палатки и спальные мешки
            {
                'name': 'Палатка 2-местная',
                'category': categories['палатки'],
                'price': 5500.00,
                'stock': 6,
                'description': 'Двухместная палатка для кемпинга. Водонепроницаемая, с москитной сеткой, вес 3.5 кг.',
                'short_description': 'Палатка для кемпинга и походов',
                'colors': ['#2d5a2d', '#5d5d5d'],
            },
            {
                'name': 'Спальный мешок -5°C',
                'category': categories['палатки'],
                'price': 3200.00,
                'stock': 15,
                'description': 'Спальный мешок комфортной температуры -5°C. Компактный, легкий, с водоотталкивающей пропиткой.',
                'short_description': 'Спальный мешок для походов',
                'colors': ['#000000', '#2d5a2d'],
            },

            # Обувь
            {
                'name': 'Ботинки тактические',
                'category': categories['обувь'],
                'price': 3800.00,
                'stock': 18,
                'description': 'Тактические ботинки с мембраной. Анатомическая стелька, антискользящая подошва, защита щиколотки.',
                'short_description': 'Ботинки для активного отдыха',
                'colors': ['#000000', '#5d5d5d'],
            },
            {
                'name': 'Кроссовки треккинговые',
                'category': categories['обувь'],
                'price': 2800.00,
                'stock': 24,
                'description': 'Треккинговые кроссовки для походов. Дышащий материал, амортизирующая подошва.',
                'short_description': 'Кроссовки для пеших походов',
                'colors': ['#5d5d5d', '#2d5a2d'],
            },

            # Тактическая медицина
            {
                'name': 'Аптечка тактическая',
                'category': categories['медицина'],
                'price': 2500.00,
                'stock': 20,
                'description': 'Тактическая аптечка первой помощи. Водонепроницаемый кейс, базовый набор медикаментов.',
                'short_description': 'Аптечка для полевых условий',
                'colors': ['#000000', '#5d5d5d'],
            },
            {
                'name': 'Турникет CAT',
                'category': categories['медицина'],
                'price': 1500.00,
                'stock': 30,
                'description': 'Турникет тактический CAT. Быстрое наложение одной рукой, прочная конструкция.',
                'short_description': 'Турникет для оказания первой помощи',
                'colors': ['#000000'],
            },

            # Аксессуары
            {
                'name': 'Фляга армейская 1л',
                'category': categories['аксессуары'],
                'price': 800.00,
                'stock': 35,
                'description': 'Армейская фляга из нержавеющей стали. Объем 1 литр, чехол в комплекте.',
                'short_description': 'Фляга для воды',
                'colors': ['#c3b091', '#000000'],
            },
            {
                'name': 'Тактический фонарь',
                'category': categories['аксессуары'],
                'price': 1200.00,
                'stock': 28,
                'description': 'Тактический фонарь с несколькими режимами. Яркость 1000 люмен, ударопрочный корпус.',
                'short_description': 'Фонарь для тактического использования',
                'colors': ['#000000'],
            },
        ]

        # Функция для создания изображений-заглушек через API
        def get_image_url(product_name, color='2d5a2d', text_color='ffffff'):
            """Генерирует URL для изображения-заглушки"""
            product_slug = slugify(product_name)[:20]
            return f'https://via.placeholder.com/400x300/{color}/{text_color}?text={product_slug}'

        # Создаем товары
        for i, product_data in enumerate(products_data):
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'category': product_data['category'],
                    'price': product_data['price'],
                    'stock': product_data['stock'],
                    'description': product_data['description'],
                    'short_description': product_data['short_description'],
                    'slug': slugify(product_data['name']),
                    'is_available': True,
                }
            )

            if created:
                # Создаем основное изображение
                color_code = product_data['colors'][0].replace('#', '')
                ProductImage.objects.create(
                    product=product,
                    image=get_image_url(product_data['name'], color_code),
                    is_main=True,
                    display_order=0
                )

                # Создаем дополнительные изображения (2-3 штуки)
                for j in range(1, random.randint(2, 4)):
                    color_code = random.choice(product_data['colors']).replace('#', '')
                    ProductImage.objects.create(
                        product=product,
                        image=get_image_url(f"{product_data['name']} вид {j}", color_code),
                        is_main=False,
                        display_order=j
                    )

                self.stdout.write(f'Создан товар: {product.name}')

    def create_test_users(self):
        """Создание тестовых пользователей"""
        test_users = [
            {
                'username': 'testuser',
                'email': 'test@voentorg.ru',
                'password': 'testpass123',
                'first_name': 'Тест',
                'last_name': 'Пользователь',
                'phone': '+79161234567',
            },
            {
                'username': 'buyer',
                'email': 'buyer@voentorg.ru',
                'password': 'buyerpass123',
                'first_name': 'Покупатель',
                'last_name': 'Обычный',
                'phone': '+79031234567',
            },
        ]

        for user_data in test_users:
            if not CustomUser.objects.filter(username=user_data['username']).exists():
                user = CustomUser.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    phone=user_data['phone'],
                )
                self.stdout.write(f'Создан пользователь: {user.username}')