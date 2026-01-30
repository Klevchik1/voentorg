// ===== ОСНОВНОЙ ФАЙЛ JAVASCRIPT =====

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация корзины
    initializeCart();

    // Инициализация фильтров
    initializeFilters();

    // Инициализация событий товаров
    initializeProducts();

    // Инициализация поиска
    initializeSearch();
});

// ===== ФУНКЦИИ КОРЗИНЫ =====
function initializeCart() {
    const cartCountElement = document.querySelector('.cart-count');

    // Загружаем количество товаров в корзине
    updateCartCount();

    // События для кнопок добавления в корзину
    document.addEventListener('click', function(e) {
        if (e.target.closest('.add-to-cart')) {
            const button = e.target.closest('.add-to-cart');
            const productId = button.getAttribute('data-product');
            addToCart(productId);
        }
    });
}

function updateCartCount() {
    // Здесь будет запрос к API для получения реального количества товаров
    // Временно используем localStorage для демонстрации
    const cart = JSON.parse(localStorage.getItem('voentorg_cart') || '[]');
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);

    const cartCountElement = document.querySelector('.cart-count');
    if (cartCountElement) {
        cartCountElement.textContent = totalItems;
    }
}

function addToCart(productId) {
    // Получаем информацию о товаре из DOM
    const productCard = document.querySelector(`.add-to-cart[data-product="${productId}"]`).closest('.product-card');
    const productName = productCard.querySelector('.product-title').textContent;
    const productPrice = parseFloat(productCard.querySelector('.product-price').textContent.replace(/[^\d.]/g, ''));

    // Получаем текущую корзину
    let cart = JSON.parse(localStorage.getItem('voentorg_cart') || '[]');

    // Проверяем, есть ли товар уже в корзине
    const existingItemIndex = cart.findIndex(item => item.id === productId);

    if (existingItemIndex !== -1) {
        // Увеличиваем количество
        cart[existingItemIndex].quantity += 1;
    } else {
        // Добавляем новый товар
        cart.push({
            id: productId,
            name: productName,
            price: productPrice,
            quantity: 1,
            addedAt: new Date().toISOString()
        });
    }

    // Сохраняем корзину
    localStorage.setItem('voentorg_cart', JSON.stringify(cart));

    // Обновляем счетчик
    updateCartCount();

    // Показываем уведомление
    showNotification('Товар добавлен в корзину', 'success');

    console.log('Корзина обновлена:', cart);
}

// ===== ФУНКЦИИ ФИЛЬТРОВ =====
function initializeFilters() {
    // Активные фильтры
    const activeFilters = {
        category: 'all',
        sort: 'popular',
        minPrice: 0,
        maxPrice: 10000,
        colors: []
    };

    // События для категорий
    const categoryLinks = document.querySelectorAll('.category-list a');
    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            // Убираем активный класс у всех
            categoryLinks.forEach(l => l.classList.remove('active'));

            // Добавляем активный класс текущему
            this.classList.add('active');

            // Обновляем фильтр
            activeFilters.category = this.getAttribute('href').replace('?category=', '');

            // Применяем фильтры
            applyFilters(activeFilters);
        });
    });

    // Событие для сортировки
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            activeFilters.sort = this.value;
            applyFilters(activeFilters);
        });
    }

    // События для цены
    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    const priceSlider = document.getElementById('price-slider');

    if (minPriceInput && maxPriceInput) {
        minPriceInput.addEventListener('input', function() {
            activeFilters.minPrice = parseInt(this.value) || 0;
            applyFilters(activeFilters);
        });

        maxPriceInput.addEventListener('input', function() {
            activeFilters.maxPrice = parseInt(this.value) || 10000;
            applyFilters(activeFilters);
        });
    }

    if (priceSlider) {
        priceSlider.addEventListener('input', function() {
            const value = parseInt(this.value);
            if (maxPriceInput) {
                maxPriceInput.value = value;
                activeFilters.maxPrice = value;
                applyFilters(activeFilters);
            }
        });
    }

    // События для цвета
    const colorOptions = document.querySelectorAll('.color-option');
    colorOptions.forEach(option => {
        option.addEventListener('click', function() {
            const color = this.getAttribute('data-color');

            if (this.classList.contains('active')) {
                // Убираем цвет из фильтра
                this.classList.remove('active');
                const index = activeFilters.colors.indexOf(color);
                if (index !== -1) {
                    activeFilters.colors.splice(index, 1);
                }
            } else {
                // Добавляем цвет в фильтр
                this.classList.add('active');
                activeFilters.colors.push(color);
            }

            applyFilters(activeFilters);
        });
    });

    // Кнопка Применить фильтры
    const applyButton = document.getElementById('apply-filters');
    if (applyButton) {
        applyButton.addEventListener('click', function() {
            applyFilters(activeFilters);
            showNotification('Фильтры применены', 'success');
        });
    }

    // Кнопка Сбросить фильтры
    const resetButton = document.getElementById('reset-filters');
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            resetFilters(activeFilters);
            showNotification('Фильтры сброшены', 'info');
        });
    }
}

function applyFilters(filters) {
    const productCards = document.querySelectorAll('.product-card');
    let visibleCount = 0;

    productCards.forEach(card => {
        let show = true;

        // Фильтр по категории
        if (filters.category !== 'all') {
            const category = card.getAttribute('data-category');
            if (category !== filters.category) {
                show = false;
            }
        }

        // Фильтр по цене
        const price = parseFloat(card.getAttribute('data-price'));
        if (price < filters.minPrice || price > filters.maxPrice) {
            show = false;
        }

        // Фильтр по цвету
        if (filters.colors.length > 0) {
            const color = card.getAttribute('data-color');
            if (!filters.colors.includes(color)) {
                show = false;
            }
        }

        // Показываем/скрываем карточку
        card.style.display = show ? 'block' : 'none';
        if (show) visibleCount++;
    });

    // Обновляем счетчик товаров
    const productCountElement = document.getElementById('product-count');
    if (productCountElement) {
        productCountElement.textContent = visibleCount;
    }

    // Сортировка
    sortProducts(filters.sort);
}

function resetFilters(activeFilters) {
    // Сброс значений фильтров
    activeFilters.category = 'all';
    activeFilters.sort = 'popular';
    activeFilters.minPrice = 0;
    activeFilters.maxPrice = 10000;
    activeFilters.colors = [];

    // Сброс UI
    const categoryLinks = document.querySelectorAll('.category-list a');
    categoryLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === '?category=all') {
            link.classList.add('active');
        }
    });

    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) sortSelect.value = 'popular';

    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    const priceSlider = document.getElementById('price-slider');
    if (minPriceInput) minPriceInput.value = 0;
    if (maxPriceInput) maxPriceInput.value = 10000;
    if (priceSlider) priceSlider.value = 5000;

    const colorOptions = document.querySelectorAll('.color-option');
    colorOptions.forEach(option => option.classList.remove('active'));

    // Применяем сброшенные фильтры
    applyFilters(activeFilters);
}

function sortProducts(sortType) {
    const productsContainer = document.getElementById('products-container');
    if (!productsContainer) return;

    const productCards = Array.from(productsContainer.querySelectorAll('.product-card'));

    productCards.sort((a, b) => {
        const priceA = parseFloat(a.getAttribute('data-price'));
        const priceB = parseFloat(b.getAttribute('data-price'));

        switch (sortType) {
            case 'price_asc':
                return priceA - priceB;
            case 'price_desc':
                return priceB - priceA;
            case 'newest':
                // Здесь можно добавить сортировку по дате добавления
                return 0;
            default: // popular
                return 0;
        }
    });

    // Переставляем карточки в контейнере
    productCards.forEach(card => {
        productsContainer.appendChild(card);
    });
}

// ===== ФУНКЦИИ ТОВАРОВ =====
function initializeProducts() {
    // События для кнопки "Посмотреть"
    document.addEventListener('click', function(e) {
        if (e.target.closest('.view-product')) {
            const button = e.target.closest('.view-product');
            const productId = button.getAttribute('data-product');
            viewProduct(productId);
        }
    });
}

function viewProduct(productId) {
    // Здесь будет переход на страницу товара
    // Временно показываем уведомление
    showNotification(`Переход к товару #${productId}`, 'info');
    console.log('Просмотр товара:', productId);
}

// ===== ФУНКЦИИ ПОИСКА =====
function initializeSearch() {
    const searchForm = document.querySelector('.search-bar');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const searchInput = this.querySelector('input[name="q"]');
            const searchTerm = searchInput.value.trim();

            if (searchTerm) {
                performSearch(searchTerm);
            }
        });
    }
}

function performSearch(searchTerm) {
    // Фильтрация товаров по названию
    const productCards = document.querySelectorAll('.product-card');
    let visibleCount = 0;

    productCards.forEach(card => {
        const productName = card.querySelector('.product-title').textContent.toLowerCase();

        if (productName.includes(searchTerm.toLowerCase())) {
            card.style.display = 'block';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });

    // Обновляем счетчик
    const productCountElement = document.getElementById('product-count');
    if (productCountElement) {
        productCountElement.textContent = visibleCount;
    }

    // Показываем уведомление
    if (visibleCount > 0) {
        showNotification(`Найдено ${visibleCount} товаров по запросу "${searchTerm}"`, 'success');
    } else {
        showNotification(`По запросу "${searchTerm}" ничего не найдено`, 'info');
    }
}

// ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====
function showNotification(message, type = 'info') {
    // Создаем элемент уведомления
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;

    // Добавляем стили
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 4px;
        background-color: ${type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : '#d1ecf1'};
        color: ${type === 'success' ? '#155724' : type === 'error' ? '#721c24' : '#0c5460'};
        border: 1px solid ${type === 'success' ? '#c3e6cb' : type === 'error' ? '#f5c6cb' : '#bee5eb'};
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 10px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        animation: slideIn 0.3s ease-out;
    `;

    // Добавляем в body
    document.body.appendChild(notification);

    // Удаляем через 3 секунды
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Добавляем анимации для уведомлений
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ===== ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ =====
console.log('Военторг: Главная страница загружена');