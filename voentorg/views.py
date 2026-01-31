import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from .models import Product, Category, Cart, CartItem, Order, OrderItem, OrderStatus
from .forms import CustomUserCreationForm
from django.db import models


# Главная страница
def home(request):
    """Главная страница с каталогом товаров"""
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()

    # Фильтрация по категории
    category_id = request.GET.get('category')
    if category_id and category_id != 'all':
        try:
            category_id = int(category_id)
            products = products.filter(category_id=category_id)
            selected_category = category_id
        except ValueError:
            selected_category = None
    else:
        selected_category = None

    # Сортировка
    sort = request.GET.get('sort', 'popular')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-stock', '-created_at')

    # Определяем диапазон цен для фильтров
    if products.exists():
        min_price = products.aggregate(models.Min('price'))['price__min']
        max_price = products.aggregate(models.Max('price'))['price__max']
    else:
        min_price = 0
        max_price = 10000

    # Получаем данные корзины для отображения количества
    cart_data = get_cart_data(request)

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'sort': sort,
        'min_price': min_price,
        'max_price': max_price,
        'cart_count': cart_data['total_items'],
        'title': 'Военторг - Каталог товаров'
    }
    return render(request, 'voentorg/index.html', context)


# Каталог товаров
def catalog(request):
    """Полный каталог товаров"""
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()

    # Фильтрация по категории
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    # Сортировка
    sort = request.GET.get('sort', 'popular')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')

    context = {
        'products': products,
        'categories': categories,
        'title': 'Каталог товаров'
    }
    return render(request, 'voentorg/catalog.html', context)


# Детальная страница товара
def product_detail(request, product_id):
    """Страница товара"""
    product = get_object_or_404(Product, id=product_id)
    context = {
        'product': product,
        'title': product.name
    }
    return render(request, 'voentorg/product_detail.html', context)


# Регистрация
def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Объединяем сессионную корзину с корзиной пользователя
            merge_session_cart_with_user(request, user)

            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    context = {'form': form, 'title': 'Регистрация'}
    return render(request, 'voentorg/register.html', context)


# Вход (используем стандартный LoginView, но добавим merge корзины)
from django.contrib.auth import views as auth_views


class CustomLoginView(auth_views.LoginView):
    def form_valid(self, form):
        # Выполняем стандартную логику входа
        response = super().form_valid(form)

        # Объединяем сессионную корзину с корзиной пользователя
        merge_session_cart_with_user(self.request, self.request.user)

        return response


# Профиль пользователя
@login_required
def profile(request):
    """Личный кабинет пользователя"""
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'user_orders': user_orders,
        'title': 'Личный кабинет'
    }
    return render(request, 'voentorg/profile.html', context)


# Корзина
def cart(request):
    """Корзина пользователя (работает для всех)"""
    cart_data = get_cart_data(request)

    context = {
        'cart_data': cart_data,
        'title': 'Корзина'
    }
    return render(request, 'voentorg/cart.html', context)


# О нас
def about(request):
    """Страница "О нас" """
    context = {'title': 'О компании'}
    return render(request, 'voentorg/about.html', context)


# Контакты
def contacts(request):
    """Страница контактов"""
    context = {'title': 'Контакты'}
    return render(request, 'voentorg/contacts.html', context)


# Поиск товаров
def search(request):
    """Поиск товаров"""
    query = request.GET.get('q', '')
    products = Product.objects.filter(is_available=True)

    if query:
        products = products.filter(name__icontains=query)

    context = {
        'products': products,
        'query': query,
        'title': f'Поиск: {query}'
    }
    return render(request, 'voentorg/search.html', context)


# Перенаправление на админку
def admin_redirect(request):
    """Перенаправление на стандартную Django админку"""
    return redirect('/admin/')


def add_to_cart(request, product_id):
    """Добавление товара в корзину"""
    try:
        product = Product.objects.get(id=product_id, is_available=True)
        quantity = int(request.POST.get('quantity', 1))

        if request.user.is_authenticated:
            # Для авторизованных пользователей
            cart_obj, created = Cart.objects.get_or_create(user=request.user)
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart_obj,
                product=product,
                defaults={'quantity': quantity}
            )

            if not item_created:
                # Если товар уже есть в корзине, увеличиваем количество
                new_quantity = cart_item.quantity + quantity
                if new_quantity <= product.stock:
                    cart_item.quantity = new_quantity
                    cart_item.save()
                else:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'message': f'Достигнуто максимальное количество товара "{product.name}" на складе'
                        })
                    messages.warning(request, f'Достигнуто максимальное количество товара "{product.name}" на складе')
                    return redirect(request.META.get('HTTP_REFERER', 'home'))

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Товар "{product.name}" добавлен в корзину'
                })
            messages.success(request, f'Товар "{product.name}" добавлен в корзину')

        else:
            # Для неавторизованных пользователей
            session_cart = get_session_cart(request)
            current_quantity = session_cart.get(str(product_id), 0)
            new_quantity = current_quantity + quantity

            # Проверяем наличие на складе
            if new_quantity <= product.stock:
                session_cart[str(product_id)] = new_quantity
                save_session_cart(request, session_cart)

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Товар "{product.name}" добавлен в корзину'
                    })
                messages.success(request, f'Товар "{product.name}" добавлен в корзину')
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Достигнуто максимальное количество товара "{product.name}" на складе'
                    })
                messages.warning(request, f'Достигнуто максимальное количество товара "{product.name}" на складе')

    except Product.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Товар не найден'
            })
        messages.error(request, 'Товар не найден')
    except ValueError:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Некорректное количество'
            })
        messages.error(request, 'Некорректное количество')

    # Если это не AJAX запрос, перенаправляем обратно
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    else:
        return JsonResponse({'success': False, 'message': 'Неизвестная ошибка'})


# Удаление из корзины
def remove_from_cart(request, product_id):
    """Удаление товара из корзины"""
    try:
        product = Product.objects.get(id=product_id)

        if request.user.is_authenticated:
            # Для авторизованных пользователей
            try:
                cart_obj = Cart.objects.get(user=request.user)
                cart_item = CartItem.objects.get(cart=cart_obj, product=product)
                cart_item.delete()

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Товар "{product.name}" удален из корзины'
                    })
                messages.success(request, f'Товар "{product.name}" удален из корзины')

            except (Cart.DoesNotExist, CartItem.DoesNotExist):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Товар не найден в корзине'
                    })
                messages.error(request, 'Товар не найден в корзине')

        else:
            # Для неавторизованных пользователей
            session_cart = get_session_cart(request)
            if str(product_id) in session_cart:
                del session_cart[str(product_id)]
                save_session_cart(request, session_cart)

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'Товар "{product.name}" удален из корзины'
                    })
                messages.success(request, f'Товар "{product.name}" удален из корзины')
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Товар не найден в корзине'
                    })
                messages.error(request, 'Товар не найден в корзине')

    except Product.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Товар не найден'
            })
        messages.error(request, 'Товар не найден')

    # Если это не AJAX запрос, перенаправляем обратно
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return redirect('cart')
    else:
        return JsonResponse({'success': False, 'message': 'Неизвестная ошибка'})


# Обновление количества товара в корзине
def update_cart_item(request, product_id):
    """Обновление количества товара в корзине"""
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            product = Product.objects.get(id=product_id, is_available=True)

            if quantity <= 0:
                return remove_from_cart(request, product_id)

            if quantity > product.stock:
                quantity = product.stock
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'На складе только {product.stock} шт. товара "{product.name}"'
                    })
                messages.warning(request, f'На складе только {product.stock} шт. товара "{product.name}"')

            if request.user.is_authenticated:
                # Для авторизованных пользователей
                cart_obj, created = Cart.objects.get_or_create(user=request.user)
                cart_item, item_created = CartItem.objects.get_or_create(
                    cart=cart_obj,
                    product=product,
                    defaults={'quantity': quantity}
                )

                if not item_created:
                    cart_item.quantity = quantity
                    cart_item.save()

            else:
                # Для неавторизованных пользователей
                session_cart = get_session_cart(request)
                session_cart[str(product_id)] = quantity
                save_session_cart(request, session_cart)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Количество товара "{product.name}" обновлено'
                })
            messages.success(request, f'Количество товара "{product.name}" обновлено')

        except (ValueError, Product.DoesNotExist) as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Ошибка при обновлении корзины'
                })
            messages.error(request, 'Ошибка при обновлении корзины')

    # Если это не AJAX запрос, перенаправляем обратно
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return redirect('cart')
    else:
        return JsonResponse({'success': False, 'message': 'Неверный метод запроса'})


# Очистка корзины
def clear_cart(request):
    """Очистка корзины"""
    if request.user.is_authenticated:
        try:
            cart_obj = Cart.objects.get(user=request.user)
            cart_obj.items.all().delete()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Корзина очищена'
                })
            messages.success(request, 'Корзина очищена')

        except Cart.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Корзина не найдена'
                })
            messages.error(request, 'Корзина не найдена')
    else:
        request.session['cart'] = '{}'
        request.session.modified = True

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Корзина очищена'
            })
        messages.success(request, 'Корзина очищена')

    # Если это не AJAX запрос, перенаправляем обратно
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return redirect('cart')
    else:
        return JsonResponse({'success': False, 'message': 'Неизвестная ошибка'})


@login_required
def user_orders(request):
    """Список заказов пользователя (заглушка)"""
    context = {'title': 'Мои заказы'}
    return render(request, 'voentorg/orders.html', context)


# Создание заказа (оформление покупки)
def create_order(request):
    """Создание заказа - перенаправление на соответствующую страницу"""
    if not request.user.is_authenticated:
        # Для гостей
        return redirect('guest_checkout')

    # Для авторизованных пользователей
    try:
        cart_obj = Cart.objects.get(user=request.user)

        if cart_obj.total_items == 0:
            messages.error(request, 'Корзина пуста')
            return redirect('cart')

        # Проверяем наличие товаров
        for item in cart_obj.items.all():
            if not item.product.is_available or item.product.stock < item.quantity:
                messages.error(request, f'Товар "{item.product.name}" недоступен')
                return redirect('cart')

        # Перенаправляем на страницу оформления для авторизованных
        return render(request, 'voentorg/user_checkout.html', {
            'cart': cart_obj,
            'title': 'Оформление заказа'
        })

    except Cart.DoesNotExist:
        messages.error(request, 'Корзина пуста')
        return redirect('cart')


def guest_checkout(request):
    """Оформление заказа для гостей"""
    cart_data = get_cart_data(request)

    if not cart_data['items']:
        messages.error(request, 'Корзина пуста')
        return redirect('cart')

    if request.method == 'POST':
        # Обработка POST запроса (оформление заказа)
        try:
            # Получаем данные из формы
            email = request.POST.get('email', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            shipping_address = request.POST.get('shipping_address', '').strip()
            notes = request.POST.get('notes', '').strip()

            if not email:
                messages.error(request, 'Введите email для связи')
                return redirect('guest_checkout')

            # Проверяем наличие товаров на складе
            for item in cart_data['items']:
                product = item['product']
                if not product.is_available or product.stock < item['quantity']:
                    messages.error(request, f'Товар "{product.name}" недоступен или недостаточно на складе')
                    return redirect('cart')

            # Создаем заказ
            order = Order.objects.create(
                user=None,
                status=OrderStatus.get_default_status(),
                total_amount=cart_data['total_price'],
                shipping_address=shipping_address,
                contact_phone=phone,
                notes=notes,
                guest_email=email,
                guest_name=f"{first_name} {last_name}".strip()
            )

            # Создаем элементы заказа
            for item in cart_data['items']:
                product = item['product']
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=product.price,
                    subtotal=item['subtotal']
                )
                # Уменьшаем количество на складе
                product.decrease_stock(item['quantity'])

            # Очищаем сессионную корзину
            request.session['cart'] = '{}'
            request.session.modified = True

            messages.success(request, f'Заказ #{order.id} успешно оформлен! Детали отправлены на {email}')
            return redirect('home')

        except Exception as e:
            messages.error(request, f'Ошибка при оформлении заказа: {str(e)}')
            return redirect('guest_checkout')

    # GET запрос - показываем форму
    context = {
        'cart_data': cart_data,
        'title': 'Оформление заказа (Гость)'
    }
    return render(request, 'voentorg/guest_checkout.html', context)


def process_guest_order(request, cart_data=None):
    """Обработка заказа гостя"""
    if cart_data is None:
        cart_data = get_cart_data(request)

    if not cart_data['items']:
        messages.error(request, 'Корзина пуста')
        return redirect('cart')

    if request.method == 'POST':
        try:
            # Получаем данные из формы
            email = request.POST.get('email', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            shipping_address = request.POST.get('shipping_address', '').strip()
            notes = request.POST.get('notes', '').strip()

            if not email:
                messages.error(request, 'Введите email для связи')
                return redirect('guest_checkout')

            # Проверяем наличие товаров на складе
            for item in cart_data['items']:
                product = item['product']  # Это объект Product
                if not product.is_available or product.stock < item['quantity']:
                    messages.error(request, f'Товар "{product.name}" недоступен или недостаточно на складе')
                    return redirect('cart')

            # Создаем заказ без привязки к пользователю
            order = Order.objects.create(
                user=None,  # Заказ без пользователя
                status=OrderStatus.get_default_status(),
                total_amount=cart_data['total_price'],
                shipping_address=shipping_address,
                contact_phone=phone,
                notes=notes,
                guest_email=email,
                guest_name=f"{first_name} {last_name}".strip()
            )

            # Создаем элементы заказа
            for item in cart_data['items']:
                product = item['product']
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=product.price,
                    subtotal=item['subtotal']
                )
                # Уменьшаем количество на складе
                product.decrease_stock(item['quantity'])

            # Очищаем сессионную корзину
            request.session['cart'] = '{}'
            request.session.modified = True

            messages.success(request,
                             f'Заказ #{order.id} успешно оформлен! Номер для отслеживания отправлен на {email}')
            return redirect('home')

        except Exception as e:
            messages.error(request, f'Ошибка при оформлении заказа: {str(e)}')
            return redirect('guest_checkout')

    return guest_checkout(request)


def get_session_cart(request):
    """Получить корзину из сессии"""
    cart_data = request.session.get('cart', '{}')
    try:
        return json.loads(cart_data)
    except:
        return {}


def save_session_cart(request, cart):
    """Сохранить корзину в сессию"""
    request.session['cart'] = json.dumps(cart)
    request.session.modified = True


def merge_session_cart_with_user(request, user):
    """Объединить сессионную корзину с корзиной пользователя при авторизации"""
    session_cart = get_session_cart(request)
    if not session_cart:
        return

    # Получаем или создаем корзину пользователя
    user_cart, created = Cart.objects.get_or_create(user=user)

    # Добавляем товары из сессионной корзины в корзину пользователя
    for product_id, quantity in session_cart.items():
        try:
            product = Product.objects.get(id=product_id)
            # Проверяем, есть ли уже такой товар в корзине пользователя
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=product,
                defaults={'quantity': quantity}
            )
            if not item_created:
                # Если товар уже есть, увеличиваем количество
                cart_item.quantity += quantity
                if cart_item.quantity > product.stock:
                    cart_item.quantity = product.stock
                cart_item.save()
        except Product.DoesNotExist:
            continue

    # Очищаем сессионную корзину
    request.session['cart'] = '{}'
    request.session.modified = True


def get_cart_data(request):
    """Получить данные корзины для отображения"""
    if request.user.is_authenticated:
        # Для авторизованных пользователей используем модель Cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        items = []
        total_items = 0
        total_price = 0

        for cart_item in cart.items.all():
            items.append({
                'product': cart_item.product,  # Это объект Product
                'quantity': cart_item.quantity,
                'subtotal': cart_item.total_price
            })
            total_items += cart_item.quantity
            total_price += cart_item.total_price

        return {
            'items': items,
            'total_items': total_items,
            'total_price': total_price,
            'is_authenticated': True
        }
    else:
        # Для неавторизованных используем сессию
        session_cart = get_session_cart(request)
        items = []
        total_items = 0
        total_price = 0

        for product_id, quantity in session_cart.items():
            try:
                product = Product.objects.get(id=product_id)
                subtotal = product.price * quantity
                items.append({
                    'product': product,  # Это объект Product
                    'quantity': quantity,
                    'subtotal': subtotal
                })
                total_items += quantity
                total_price += subtotal
            except Product.DoesNotExist:
                continue

        return {
            'items': items,
            'total_items': total_items,
            'total_price': total_price,
            'is_authenticated': False
        }


# ===== AJAX ФУНКЦИИ =====

def ajax_add_to_cart(request, product_id):
    """Добавление в корзину через AJAX"""
    if request.method == 'POST':
        try:
            product = Product.objects.get(id=product_id, is_available=True)

            if request.user.is_authenticated:
                # Для авторизованных пользователей
                cart_obj, created = Cart.objects.get_or_create(user=request.user)
                cart_item, item_created = CartItem.objects.get_or_create(
                    cart=cart_obj,
                    product=product,
                    defaults={'quantity': 1}
                )

                if not item_created:
                    if cart_item.quantity < product.stock:
                        cart_item.quantity += 1
                        cart_item.save()
                    else:
                        return JsonResponse({
                            'success': False,
                            'message': f'Достигнуто максимальное количество товара "{product.name}" на складе'
                        })

                return JsonResponse({
                    'success': True,
                    'message': f'Товар "{product.name}" добавлен в корзину'
                })

            else:
                # Для неавторизованных пользователей
                session_cart = get_session_cart(request)
                quantity = session_cart.get(str(product_id), 0)

                if quantity < product.stock:
                    session_cart[str(product_id)] = quantity + 1
                    save_session_cart(request, session_cart)
                    return JsonResponse({
                        'success': True,
                        'message': f'Товар "{product.name}" добавлен в корзину'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': f'Достигнуто максимальное количество товара "{product.name}" на складе'
                    })

        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Товар не найден'
            })

    return JsonResponse({'success': False, 'message': 'Неверный метод запроса'})


def get_cart_count(request):
    """Получить количество товаров в корзине (для AJAX)"""
    cart_data = get_cart_data(request)
    return JsonResponse({'count': cart_data['total_items']})