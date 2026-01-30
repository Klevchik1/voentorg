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
    // Временная реализация через localStorage
    const cart = JSON.parse(localStorage.getItem('voentorg_cart') || '[]');
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);

    const cartCountElement = document.querySelector('.cart-count');
    if (cartCountElement) {
        cartCountElement.textContent = totalItems;
    }
}

function addToCart(productId) {
    // Временная реализация через localStorage
    let cart = JSON.parse(localStorage.getItem('voentorg_cart') || '[]');

    // Проверяем, есть ли товар уже в корзине
    const existingItemIndex = cart.findIndex(item => item.id == productId);

    if (existingItemIndex !== -1) {
        // Увеличиваем количество
        cart[existingItemIndex].quantity += 1;
    } else {
        // Добавляем новый товар
        const productCard = document.querySelector(`.add-to-cart[data-product="${productId}"]`)?.closest('.product-card');
        const productName = productCard?.querySelector('.product-title')?.textContent || `Товар #${productId}`;
        const productPrice = parseFloat(productCard?.querySelector('.product-price')?.textContent?.replace(/[^\d.]/g, '') || 0);

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
}

// ===== ФУНКЦИИ ФИЛЬТРОВ =====
function initializeFilters() {
    // Активные фильтры
    const activeFilters = {
        category: 'all',
        sort: 'popular',
        minPrice: 0,
        maxPrice: 10000,
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
            const categoryParam = this.getAttribute('href');
            if (categoryParam.includes('category=')) {
                activeFilters.category = categoryParam.split('category=')[1];

                // Перезагружаем страницу с новым параметром
                const url = new URL(window.location);
                if (activeFilters.category === 'all') {
                    url.searchParams.delete('category');
                } else {
                    url.searchParams.set('category', activeFilters.category);
                }
                window.location.href = url.toString();
            }
        });
    });

    // Событие для сортировки
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            activeFilters.sort = this.value;

            // Перезагружаем страницу с новым параметром сортировки
            const url = new URL(window.location);
            url.searchParams.set('sort', activeFilters.sort);
            window.location.href = url.toString();
        });
    }

    // События для цены (клиентская фильтрация)
    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    const priceSlider = document.getElementById('price-slider');

    if (minPriceInput && maxPriceInput) {
        minPriceInput.addEventListener('change', function() {
            activeFilters.minPrice = parseInt(this.value) || 0;
            filterProductsByPrice();
        });

        maxPriceInput.addEventListener('change', function() {
            activeFilters.maxPrice = parseInt(this.value) || 10000;
            filterProductsByPrice();
        });
    }

    if (priceSlider) {
        priceSlider.addEventListener('input', function() {
            const value = parseInt(this.value);
            if (maxPriceInput) {
                maxPriceInput.value = value;
                activeFilters.maxPrice = value;
            }
        });

        priceSlider.addEventListener('change', function() {
            filterProductsByPrice();
        });
    }

    // Кнопка Применить фильтры (для цен)
    const applyButton = document.getElementById('apply-filters');
    if (applyButton) {
        applyButton.addEventListener('click', function() {
            filterProductsByPrice();
            showNotification('Фильтры применены', 'success');
        });
    }

    // Кнопка Сбросить фильтры
    const resetButton = document.getElementById('reset-filters');
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            resetFilters(activeFilters);
        });
    }
}

function filterProductsByPrice() {
    const minPrice = parseInt(document.getElementById('min-price').value) || 0;
    const maxPrice = parseInt(document.getElementById('max-price').value) || 10000;

    const productCards = document.querySelectorAll('.product-card');
    let visibleCount = 0;

    productCards.forEach(card => {
        const price = parseFloat(card.getAttribute('data-price'));

        if (price >= minPrice && price <= maxPrice) {
            card.style.display = 'block';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });

    // Обновляем счетчик товаров
    const productCountElement = document.getElementById('product-count');
    if (productCountElement) {
        productCountElement.textContent = visibleCount;
    }

    // Показываем сообщение, если товаров нет
    const productsContainer = document.getElementById('products-container');
    if (visibleCount === 0 && productsContainer) {
        const noProductsMsg = document.createElement('div');
        noProductsMsg.className = 'no-products';
        noProductsMsg.innerHTML = `
            <i class="fas fa-box-open fa-3x"></i>
            <h3>Товары не найдены</h3>
            <p>Попробуйте изменить параметры фильтрации</p>
        `;

        // Удаляем старое сообщение если есть
        const oldMsg = productsContainer.querySelector('.no-products');
        if (oldMsg) oldMsg.remove();

        productsContainer.appendChild(noProductsMsg);
    } else {
        const noProductsMsg = productsContainer?.querySelector('.no-products');
        if (noProductsMsg) noProductsMsg.remove();
    }
}

function resetFilters(activeFilters) {
    // Сброс значений фильтров в URL
    const url = new URL(window.location);
    url.searchParams.delete('category');
    url.searchParams.delete('sort');
    url.searchParams.delete('min_price');
    url.searchParams.delete('max_price');

    window.location.href = url.toString();
}

// ===== ФУНКЦИИ ТОВАРОВ =====
function initializeProducts() {
    // События для кнопки "Посмотреть" уже обрабатываются ссылкой
    // Дополнительная логика может быть добавлена здесь
}

// ===== ФУНКЦИИ ПОИСКА =====
function initializeSearch() {
    const searchForm = document.querySelector('.search-bar');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = this.querySelector('input[name="q"]');
            const searchTerm = searchInput.value.trim();

            if (!searchTerm) {
                e.preventDefault();
                showNotification('Введите поисковый запрос', 'info');
            }
        });
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
            if (notification.parentNode) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Добавляем анимации для уведомлений
if (!document.querySelector('#notification-styles')) {
    const style = document.createElement('style');
    style.id = 'notification-styles';
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
}

// ===== ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ =====
console.log('Военторг: Главная страница загружена');