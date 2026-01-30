from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import home  # импортируем функцию home

urlpatterns = [
    # Главная страница
    path('', home, name='home'),

    # Аутентификация
    path('login/', auth_views.LoginView.as_view(template_name='voentorg/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),

    # Каталог и товары
    path('catalog/', views.catalog, name='catalog'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),

    # Корзина
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    # path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    # path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    # path('cart/clear/', views.clear_cart, name='clear_cart'),

    # Заказы
    path('order/create/', views.create_order, name='create_order'),
    # path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/', views.user_orders, name='user_orders'),

    # Профиль
    path('profile/', views.profile, name='profile'),

    # Статические страницы
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),

    # Админка (перенаправление на стандартную Django админку)
    path('admin/', views.admin_redirect, name='admin_redirect'),
]