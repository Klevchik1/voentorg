import os
import random
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from voentorg.models import CustomUser, Category, Product, ProductImage, OrderStatus
from django.utils.text import slugify
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import io


class Command(BaseCommand):
    help = 'Заполняет базу данных начальными данными для приложения Военторг'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить базу данных перед заполнением',
        )
        parser.add_argument(
            '--skip-images',
            action='store_true',
            help='Пропустить создание изображений',
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
        self.create_products(skip_images=options['skip_images'])
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

    def create_image_placeholder(self, text, width=400, height=300, bg_color=None, text_color='white'):
        """Создает изображение-заглушку с текстом"""
        try:
            # Попробуем использовать PIL для создания изображений
            from PIL import Image, ImageDraw, ImageFont

            # Если PIL установлен, создаем настоящее изображение
            if bg_color is None:
                # Случайный цвет из палитры военной тематики
                military_colors = [
                    (45, 90, 45),  # темно-зеленый
                    (93, 93, 93),  # серый
                    (0, 0, 0),  # черный
                    (128, 128, 128),  # серый
                    (45, 45, 45),  # темно-серый
                ]
                bg_color = random.choice(military_colors)

            # Создаем изображение
            image = Image.new('RGB', (width, height), color=bg_color)
            draw = ImageDraw.Draw(image)

            # Пробуем использовать системный шрифт или стандартный
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()

            # Вычисляем размер текста
            try:
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                text_x = (width - text_width) // 2
                text_y = (height - text_height) // 2

                # Рисуем текст
                draw.text((text_x, text_y), text, fill=text_color, font=font)
            except:
                # Если не получилось с текстом, просто рисуем прямоугольник
                draw.rectangle([50, 50, width - 50, height - 50], outline=text_color, width=3)

            # Сохраняем в BytesIO
            img_io = io.BytesIO()
            image.save(img_io, format='JPEG')
            img_io.seek(0)

            return img_io

        except ImportError:
            # Если PIL не установлен, создаем простой текстовый файл как заглушку
            self.stdout.write(self.style.WARNING('PIL/Pillow не установлен, создаем простую заглушку'))
            content = f"Изображение: {text}\nРазмер: {width}x{height}"
            img_io = io.BytesIO(content.encode('utf-8'))
            return img_io

    def create_products(self, skip_images=False):
        """Создание товаров с локальными изображениями-заглушками"""
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
            },
            {
                'name': 'Брюки тактические Flecktarn',
                'category': categories['одежда'],
                'price': 3200.00,
                'stock': 22,
                'description': 'Тактические брюки немецкого камуфляжа Flecktarn. Усиленные колени, карманы для наколенников, регулируемая талия.',
                'short_description': 'Брюки полевые камуфляжные',
            },
            {
                'name': 'Футболка тактическая черная',
                'category': categories['одежда'],
                'price': 1200.00,
                'stock': 40,
                'description': 'Тактическая футболка из быстросохнущего материала. Вентиляционные вставки, плоские швы.',
                'short_description': 'Футболка для активного отдыха',
            },

            # Тактические рюкзаки
            {
                'name': 'Рюкзак тактический 30л',
                'category': categories['рюкзаки'],
                'price': 2800.00,
                'stock': 10,
                'description': 'Тактический рюкзак объемом 30 литров. Система MOLLE, отделение для гидратора, поясной ремень.',
                'short_description': 'Рюкзак для походов и тактики',
            },
            {
                'name': 'Штурмовой рюкзак 20л',
                'category': categories['рюкзаки'],
                'price': 3500.00,
                'stock': 8,
                'description': 'Компактный штурмовой рюкзак для быстрых вылазок. Прочная ткань Cordura, система быстрого доступа.',
                'short_description': 'Компактный рюкзак для активного использования',
            },

            # Тактическое снаряжение
            {
                'name': 'Разгрузочный жилет MOLLE',
                'category': categories['снаряжение'],
                'price': 4200.00,
                'stock': 12,
                'description': 'Разгрузочный жилет с системой MOLLE. Регулируемые лямки, возможность крепления дополнительных подсумков.',
                'short_description': 'Жилет разгрузочный тактический',
            },
            {
                'name': 'Подсумок для магазинов',
                'category': categories['снаряжение'],
                'price': 800.00,
                'stock': 25,
                'description': 'Подсумок на 3 магазина. Быстрое крепление на систему MOLLE, защита от влаги.',
                'short_description': 'Подсумок для тактического снаряжения',
            },

            # Палатки и спальные мешки
            {
                'name': 'Палатка 2-местная',
                'category': categories['палатки'],
                'price': 5500.00,
                'stock': 6,
                'description': 'Двухместная палатка для кемпинга. Водонепроницаемая, с москитной сеткой, вес 3.5 кг.',
                'short_description': 'Палатка для кемпинга и походов',
            },
            {
                'name': 'Спальный мешок -5°C',
                'category': categories['палатки'],
                'price': 3200.00,
                'stock': 15,
                'description': 'Спальный мешок комфортной температуры -5°C. Компактный, легкий, с водоотталкивающей пропиткой.',
                'short_description': 'Спальный мешок для походов',
            },

            # Обувь
            {
                'name': 'Ботинки тактические',
                'category': categories['обувь'],
                'price': 3800.00,
                'stock': 18,
                'description': 'Тактические ботинки с мембраной. Анатомическая стелька, антискользящая подошва, защита щиколотки.',
                'short_description': 'Ботинки для активного отдыха',
            },
            {
                'name': 'Кроссовки треккинговые',
                'category': categories['обувь'],
                'price': 2800.00,
                'stock': 24,
                'description': 'Треккинговые кроссовки для походов. Дышащий материал, амортизирующая подошва.',
                'short_description': 'Кроссовки для пеших походов',
            },

            # Тактическая медицина
            {
                'name': 'Аптечка тактическая',
                'category': categories['медицина'],
                'price': 2500.00,
                'stock': 20,
                'description': 'Тактическая аптечка первой помощи. Водонепроницаемый кейс, базовый набор медикаментов.',
                'short_description': 'Аптечка для полевых условий',
            },
            {
                'name': 'Турникет CAT',
                'category': categories['медицина'],
                'price': 1500.00,
                'stock': 30,
                'description': 'Турникет тактический CAT. Быстрое наложение одной рукой, прочная конструкция.',
                'short_description': 'Турникет для оказания первой помощи',
            },

            # Аксессуары
            {
                'name': 'Фляга армейская 1л',
                'category': categories['аксессуары'],
                'price': 800.00,
                'stock': 35,
                'description': 'Армейская фляга из нержавеющей стали. Объем 1 литр, чехол в комплекте.',
                'short_description': 'Фляга для воды',
            },
            {
                'name': 'Тактический фонарь',
                'category': categories['аксессуары'],
                'price': 1200.00,
                'stock': 28,
                'description': 'Тактический фонарь с несколькими режимами. Яркость 1000 люмен, ударопрочный корпус.',
                'short_description': 'Фонарь для тактического использования',
            },
        ]

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

            if created and not skip_images:
                product_name = product_data['name']
                slug_name = slugify(product_name)

                # Создаем основное изображение
                try:
                    # Создаем изображение с названием товара
                    short_name = product_name[:20]  # Берем первые 20 символов
                    img_io = self.create_image_placeholder(short_name, 400, 300)

                    # Создаем файл Django
                    django_file = File(img_io, name=f"{slug_name}_main.jpg")

                    # Сохраняем основное изображение товара
                    product.image.save(django_file.name, django_file, save=False)

                    self.stdout.write(self.style.SUCCESS(f'Создано основное изображение для: {product_name}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Ошибка создания изображения для {product_name}: {str(e)}'))
                    # Если не удалось создать изображение, оставляем поле пустым

                product.save()

                # Создаем дополнительные изображения (1-3 штуки)
                for j in range(1, random.randint(2, 4)):
                    try:
                        # Создаем изображение с номером вида
                        text = f"{short_name}\nВид {j}"
                        img_io = self.create_image_placeholder(text, 400, 300)

                        # Создаем файл Django
                        django_file = File(img_io, name=f"{slug_name}_{j}.jpg")

                        # Создаем запись ProductImage
                        ProductImage.objects.create(
                            product=product,
                            image=django_file,
                            is_main=False,
                            display_order=j
                        )

                        self.stdout.write(
                            self.style.SUCCESS(f'  Создано дополнительное изображение {j} для: {product_name}'))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(
                            f'  Ошибка создания дополнительного изображения {j} для {product_name}: {str(e)}'))
                        continue

                self.stdout.write(self.style.SUCCESS(f'Создан товар: {product.name} с локальными изображениями'))
            elif created:
                self.stdout.write(self.style.SUCCESS(f'Создан товар: {product.name} (без изображений)'))

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