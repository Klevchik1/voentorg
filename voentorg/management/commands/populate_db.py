import os
import random
import shutil
from django.core.management.base import BaseCommand
from django.core.files import File
from django.core.files.images import ImageFile
from django.conf import settings
from voentorg.models import CustomUser, Category, Product, ProductImage, OrderStatus, Order, OrderItem, Cart, CartItem
from django.utils.text import slugify
from PIL import Image
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
        parser.add_argument(
            '--force-placeholders',
            action='store_true',
            help='Использовать заглушки даже если есть реальные изображения',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Очистка базы данных...')

            # Удаляем все связанные данные в правильном порядке
            self.stdout.write('Удаление заказов...')
            OrderItem.objects.all().delete()
            Order.objects.all().delete()

            self.stdout.write('Удаление корзин...')
            CartItem.objects.all().delete()
            Cart.objects.all().delete()

            self.stdout.write('Удаление изображений товаров...')
            ProductImage.objects.all().delete()

            self.stdout.write('Удаление товаров...')
            Product.objects.all().delete()

            self.stdout.write('Удаление категорий...')
            Category.objects.all().delete()

            self.stdout.write('Удаление тестовых пользователей...')
            CustomUser.objects.filter(is_superuser=False).delete()

            self.stdout.write('Удаление статусов заказов...')
            OrderStatus.objects.all().delete()

            # Очищаем папку media/products
            self.clean_media_files()

            self.stdout.write(self.style.SUCCESS('База данных очищена'))

        self.create_order_statuses()
        self.create_categories()

        # Сканируем папку с исходными изображениями
        source_images = self.scan_source_images()
        self.stdout.write(f'Найдено исходных изображений: {len(source_images)}')

        self.create_products(
            source_images=source_images,
            skip_images=options['skip_images'],
            force_placeholders=options['force_placeholders']
        )
        self.create_test_users()

        self.stdout.write(self.style.SUCCESS('База данных успешно заполнена!'))

    def clean_media_files(self):
        """Очищает папку media/products"""
        products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        if os.path.exists(products_dir):
            try:
                shutil.rmtree(products_dir)
                self.stdout.write(f'Очищена папка: {products_dir}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Ошибка при очистке папки: {e}'))

        # Создаем пустые папки заново
        os.makedirs(os.path.join(products_dir, 'main'), exist_ok=True)
        os.makedirs(os.path.join(products_dir, 'images'), exist_ok=True)

    def scan_source_images(self):
        """Сканирует папку source_images и возвращает словарь с изображениями по категориям"""
        source_dir = os.path.join(settings.MEDIA_ROOT, 'source_images')
        images_by_category = {}

        if not os.path.exists(source_dir):
            self.stdout.write(self.style.WARNING(f'Папка {source_dir} не найдена. Создаю...'))
            os.makedirs(source_dir, exist_ok=True)
            return images_by_category

        # Проходим по всем подпапкам
        for category_folder in os.listdir(source_dir):
            category_path = os.path.join(source_dir, category_folder)
            if os.path.isdir(category_path):
                # Собираем все изображения в этой папке
                images = []
                for file in os.listdir(category_path):
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        full_path = os.path.join(category_path, file)
                        # Проверяем, что файл действительно является изображением
                        try:
                            with Image.open(full_path) as img:
                                # Просто проверяем, что открывается
                                images.append(full_path)
                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(f'  Файл {file} поврежден или не является изображением: {e}')
                            )

                if images:
                    images.sort()  # Сортируем для предсказуемого порядка
                    images_by_category[category_folder.lower()] = images
                    self.stdout.write(f'  Найдено {len(images)} рабочих изображений в папке {category_folder}')

        return images_by_category

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

    def copy_image_to_product(self, source_path, product, is_main=False, display_order=0):
        """
        Копирует изображение в папку product и создает запись в БД
        Возвращает True в случае успеха
        """
        try:
            # Открываем изображение и проверяем его
            with Image.open(source_path) as img:
                # Конвертируем в RGB если нужно
                if img.mode in ('RGBA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = rgb_img

                # Сохраняем во временный буфер
                img_io = io.BytesIO()
                img.save(img_io, format='JPEG', quality=85)
                img_io.seek(0)

                # Определяем имя файла - с порядковым номером для гарантии порядка
                filename = f"{slugify(product.name)}_{display_order}.jpg"

                # Создаем Django File объект
                django_file = File(img_io, name=filename)

                if is_main:
                    # Сохраняем основное изображение
                    product.image.save(filename, django_file, save=False)
                    product.save()

                    # Также создаем запись в ProductImage для основного изображения
                    # чтобы оно тоже было в product.images.all()
                    img_obj = ProductImage.objects.create(
                        product=product,
                        image=django_file,
                        is_main=True,
                        display_order=0  # Основное всегда с порядком 0
                    )
                    save_path = str(img_obj.image)
                    self.stdout.write(
                        self.style.SUCCESS(f'  Основное изображение сохранено: {save_path}')
                    )
                else:
                    # Создаем дополнительное изображение
                    img_obj = ProductImage.objects.create(
                        product=product,
                        image=django_file,
                        is_main=False,
                        display_order=display_order
                    )
                    save_path = str(img_obj.image)
                    self.stdout.write(
                        self.style.SUCCESS(f'  Доп.изображение {display_order} сохранено: {save_path}')
                    )
                return True

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'  Ошибка при обработке {source_path}: {str(e)}')
            )
            return False

    def create_products(self, source_images=None, skip_images=False, force_placeholders=False):
        """Создание товаров с реальными изображениями из source_images"""
        if source_images is None:
            source_images = {}

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

        # Соответствие категорий товаров и папок с изображениями
        category_to_folder = {
            'одежда': ['clothing', 'одежда'],
            'рюкзаки': ['backpacks', 'рюкзаки'],
            'снаряжение': ['gear', 'снаряжение'],
            'палатки': ['tents', 'палатки'],
            'обувь': ['footwear', 'обувь'],
            'медицина': ['medicine', 'медицина'],
            'аксессуары': ['accessories', 'аксессуары'],
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

        # Счетчики для распределения изображений
        image_index = {}
        for category_key, folders in category_to_folder.items():
            for folder in folders:
                if folder in source_images:
                    image_index[category_key] = source_images[folder]
                    break
            if category_key not in image_index:
                image_index[category_key] = []

        stats = {
            'total_products': 0,
            'with_real_images': 0,
            'with_placeholders': 0,
            'real_images_count': 0,
            'placeholder_images_count': 0
        }

        # Создаем товары
        for product_data in products_data:
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
                stats['total_products'] += 1

                if skip_images:
                    self.stdout.write(self.style.SUCCESS(f'Создан товар: {product.name} (без изображений)'))
                    continue

                # Определяем категорию товара для поиска изображений
                category_key = None
                for key, cat in categories.items():
                    if cat == product_data['category']:
                        category_key = key
                        break

                # Получаем изображения для этой категории
                category_images = image_index.get(category_key, [])

                # Если есть изображения и не форсируем заглушки
                if not force_placeholders and category_images:
                    # Берем изображения для этого товара (по 3 на товар)
                    if not hasattr(self, '_img_counter'):
                        self._img_counter = {}

                    counter_key = category_key
                    start_idx = self._img_counter.get(counter_key, 0)

                    # Берем до 3 изображений для этого товара
                    images_for_product = category_images[start_idx:start_idx + 3]

                    if images_for_product:
                        # Основное изображение - первое (display_order = 0)
                        main_success = self.copy_image_to_product(
                            images_for_product[0],
                            product,
                            is_main=True,
                            display_order=0
                        )

                        if main_success:
                            stats['with_real_images'] += 1
                            stats['real_images_count'] += 1
                            images_added = 1

                            # Дополнительные изображения - остальные (display_order = 1, 2, ...)
                            for j, img_path in enumerate(images_for_product[1:], 1):
                                add_success = self.copy_image_to_product(
                                    img_path,
                                    product,
                                    is_main=False,
                                    display_order=j
                                )
                                if add_success:
                                    stats['real_images_count'] += 1
                                    images_added += 1

                            # Обновляем счетчик
                            self._img_counter[counter_key] = start_idx + len(images_for_product)

                            self.stdout.write(
                                self.style.SUCCESS(f'Товар "{product.name}" получил {images_added} изображений')
                            )
                        else:
                            # Если основное изображение не скопировалось, создаем заглушки
                            self._create_placeholder_images(product, product_data, stats)
                    else:
                        # Если изображения кончились, создаем заглушки
                        self._create_placeholder_images(product, product_data, stats)
                else:
                    # Нет изображений для категории или форсируем заглушки
                    self._create_placeholder_images(product, product_data, stats)

        # Выводим статистику
        self.stdout.write(self.style.SUCCESS('\n=== СТАТИСТИКА ИЗОБРАЖЕНИЙ ==='))
        self.stdout.write(f'Всего создано товаров: {stats["total_products"]}')
        self.stdout.write(f'Товаров с реальными изображениями: {stats["with_real_images"]}')
        self.stdout.write(f'Товаров с заглушками: {stats["with_placeholders"]}')
        self.stdout.write(f'Всего реальных изображений: {stats["real_images_count"]}')
        self.stdout.write(f'Всего заглушек: {stats["placeholder_images_count"]}')

    def _create_placeholder_images(self, product, product_data, stats):
        """Создает изображения-заглушки для товара"""
        stats['with_placeholders'] += 1

        self.stdout.write(
            self.style.WARNING(f'Создание заглушек для: {product_data["name"]}')
        )

        # Здесь можно добавить логику создания заглушек если нужно
        # Но пока просто сохраняем товар без изображений
        product.save()

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