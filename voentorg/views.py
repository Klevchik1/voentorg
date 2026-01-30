from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from .models import Product, Category, Cart, CartItem, Order, OrderItem
from .forms import CustomUserCreationForm  # создадим позже


# Главная страница (уже есть)
def home(request):
    """Главная страница с каталогом товаров"""
    products = Product.objects.filter(is_available=True)[:12]
    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
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
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    context = {'form': form, 'title': 'Регистрация'}
    return render(request, 'voentorg/register.html', context)


# Профиль пользователя
@login_required
def profile(request):
    """Личный кабинет пользователя"""
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:10]
    context = {
        'user_orders': user_orders,
        'title': 'Личный кабинет'
    }
    return render(request, 'voentorg/profile.html', context)


# Корзина
@login_required
def cart(request):
    """Корзина пользователя"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    context = {
        'cart': cart,
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


# Пустые представления для временного использования
@login_required
def add_to_cart(request, product_id):
    """Добавление товара в корзину (заглушка)"""
    messages.info(request, 'Функция добавления в корзину будет реализована позже')
    return redirect('product_detail', product_id=product_id)


@login_required
def user_orders(request):
    """Список заказов пользователя (заглушка)"""
    context = {'title': 'Мои заказы'}
    return render(request, 'voentorg/orders.html', context)


@login_required
def create_order(request):
    """Создание заказа (заглушка)"""
    messages.info(request, 'Функция оформления заказа будет реализована позже')
    return redirect('cart')