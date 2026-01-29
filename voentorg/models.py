from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone
from django.utils.text import slugify
import uuid


class CustomUser(AbstractUser):
    """Кастомная модель пользователя с дополнительными полями"""
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9_]{3,30}$',
                message='Логин должен содержать от 3 до 30 символов (буквы, цифры, подчеркивание)'
            )
        ],
        verbose_name='Логин'
    )
    email = models.EmailField(
        max_length=50,
        unique=True,
        verbose_name='Электронная почта'
    )
    first_name = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='Фамилия'
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex='^[0-9+()-]{7,20}$',
                message='Номер телефона должен содержать от 7 до 20 цифр и символов +()-'
            )
        ],
        verbose_name='Телефон'
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата регистрации'
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Администратор'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )

    # Убираем поле username из обязательных для формы
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} ({self.email})"

    def get_full_name(self):
        """Возвращает полное имя пользователя"""
        if self.first_name and self.last_name:
            return f"{self.last_name} {self.first_name}"
        return self.username

    def get_short_name(self):
        """Возвращает короткое имя пользователя"""
        return self.first_name if self.first_name else self.username


class OrderStatus(models.Model):
    """Статусы заказов (отдельная таблица для соблюдения 3NF)"""
    STATUS_CHOICES = [
        ('new', 'Новый заказ'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]

    code = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        unique=True,
        verbose_name='Код статуса'
    )
    name = models.CharField(
        max_length=50,
        verbose_name='Название статуса'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Статус заказа'
        verbose_name_plural = 'Статусы заказов'
        ordering = ['id']

    def __str__(self):
        return self.name

    @classmethod
    def get_default_status(cls):
        """Возвращает статус по умолчанию (новый заказ)"""
        status, created = cls.objects.get_or_create(
            code='new',
            defaults={
                'name': 'Новый заказ',
                'description': 'Заказ создан клиентом, ожидает обработки'
            }
        )
        return status


class Category(models.Model):
    """Категории товаров"""
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='URL-слаг'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительская категория'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Автоматически создаем slug при сохранении"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_full_path(self):
        """Возвращает полный путь категории (включая родителей)"""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return ' → '.join(path)


class Product(models.Model):
    """Товары"""
    name = models.CharField(
        max_length=100,
        verbose_name='Название товара'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='URL-слаг'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Полное описание'
    )
    short_description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Краткое описание'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Цена'
    )
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Количество на складе'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products',
        verbose_name='Категория'
    )
    image = models.ImageField(
        upload_to='products/main/',
        blank=True,
        null=True,
        verbose_name='Основное изображение'
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name='Доступен для заказа'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['price']),
            models.Index(fields=['is_available']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return f"{self.name} ({self.price} руб.)"

    def save(self, *args, **kwargs):
        """Автоматически создаем slug при сохранении"""
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    @property
    def in_stock(self):
        """Проверка наличия товара на складе"""
        return self.stock > 0

    def decrease_stock(self, quantity):
        """Уменьшает количество товара на складе"""
        if quantity <= 0:
            raise ValueError("Количество должно быть положительным")
        if self.stock < quantity:
            raise ValueError(f"Недостаточно товара на складе. Доступно: {self.stock}")

        self.stock -= quantity
        self.save()

    def increase_stock(self, quantity):
        """Увеличивает количество товара на складе"""
        if quantity <= 0:
            raise ValueError("Количество должно быть положительным")

        self.stock += quantity
        self.save()


class ProductImage(models.Model):
    """Изображения товаров"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Товар'
    )
    image = models.ImageField(
        upload_to='products/images/',
        verbose_name='Изображение'
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name='Основное изображение'
    )
    display_order = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Порядок отображения'
    )

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'
        ordering = ['display_order', 'id']
        indexes = [
            models.Index(fields=['product', 'is_main']),
            models.Index(fields=['product', 'display_order']),
        ]

    def __str__(self):
        return f"Изображение для {self.product.name}"

    def save(self, *args, **kwargs):
        """Если это основное изображение, снимаем флаг с других изображений этого товара"""
        if self.is_main:
            ProductImage.objects.filter(product=self.product, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)


class Cart(models.Model):
    """Корзины пользователей"""
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"

    @property
    def total_items(self):
        """Общее количество товаров в корзине"""
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        """Общая стоимость товаров в корзине"""
        return sum(item.total_price for item in self.items.all())

    def add_product(self, product, quantity=1):
        """Добавляет товар в корзину"""
        if quantity <= 0:
            raise ValueError("Количество должно быть положительным")

        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item

    def remove_product(self, product):
        """Удаляет товар из корзины"""
        try:
            cart_item = CartItem.objects.get(cart=self, product=product)
            cart_item.delete()
            return True
        except CartItem.DoesNotExist:
            return False

    def update_quantity(self, product, quantity):
        """Обновляет количество товара в корзине"""
        if quantity <= 0:
            return self.remove_product(product)

        try:
            cart_item = CartItem.objects.get(cart=self, product=product)
            cart_item.quantity = quantity
            cart_item.save()
            return cart_item
        except CartItem.DoesNotExist:
            return self.add_product(product, quantity)

    def clear(self):
        """Очищает корзину"""
        self.items.all().delete()

    def create_order(self, shipping_address='', contact_phone='', notes=''):
        """Создает заказ из корзины"""
        if self.total_items == 0:
            raise ValueError("Корзина пуста")

        # Проверяем доступность всех товаров
        for item in self.items.all():
            if not item.product.is_available or item.product.stock < item.quantity:
                raise ValueError(f"Товар '{item.product.name}' недоступен или недостаточно на складе")

        # Создаем заказ
        order = Order.objects.create(
            user=self.user,
            status=OrderStatus.get_default_status(),
            total_amount=self.total_price,
            shipping_address=shipping_address,
            contact_phone=contact_phone or self.user.phone,
            notes=notes
        )

        # Создаем элементы заказа и уменьшаем количество на складе
        for item in self.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                subtotal=item.total_price
            )
            # Уменьшаем количество на складе
            item.product.decrease_stock(item.quantity)

        # Очищаем корзину
        self.clear()

        return order


class CartItem(models.Model):
    """Элементы корзины"""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Корзина'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'
        ordering = ['-added_at']
        unique_together = ['cart', 'product']
        indexes = [
            models.Index(fields=['cart', 'product']),
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        """Общая стоимость элемента"""
        return self.product.price * self.quantity


class Order(models.Model):
    """Заказы"""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.RESTRICT,
        related_name='orders',
        verbose_name='Пользователь'
    )
    status = models.ForeignKey(
        OrderStatus,
        on_delete=models.RESTRICT,
        related_name='orders',
        verbose_name='Статус'
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Общая сумма'
    )
    shipping_address = models.TextField(
        blank=True,
        verbose_name='Адрес доставки'
    )
    contact_phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex='^[0-9+()-]{7,20}$',
                message='Номер телефона должен содержать от 7 до 20 цифр и символов +()-'
            )
        ],
        verbose_name='Контактный телефон'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Комментарий к заказу'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username} ({self.total_amount} руб.)"

    def save(self, *args, **kwargs):
        """Устанавливаем контактный телефон из профиля пользователя, если не указан"""
        if not self.contact_phone and self.user.phone:
            self.contact_phone = self.user.phone
        super().save(*args, **kwargs)

    @property
    def total_items(self):
        """Общее количество товаров в заказе"""
        return sum(item.quantity for item in self.items.all())

    def update_status(self, new_status_code):
        """Обновляет статус заказа"""
        try:
            new_status = OrderStatus.objects.get(code=new_status_code, is_active=True)
            self.status = new_status
            self.save()
            return True
        except OrderStatus.DoesNotExist:
            return False


class OrderItem(models.Model):
    """Элементы заказа"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.RESTRICT,
        verbose_name='Товар'
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Цена на момент покупки'
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Подытог'
    )

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'
        ordering = ['id']
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
            models.Index(fields=['order', 'product']),
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity} (в заказе #{self.order.id})"

    def save(self, *args, **kwargs):
        """Автоматически рассчитываем подытог при сохранении"""
        if not self.subtotal:
            self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)