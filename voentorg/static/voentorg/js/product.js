// ===== JAVASCRIPT ДЛЯ СТРАНИЦЫ ТОВАРА =====

document.addEventListener('DOMContentLoaded', function() {
    initializeProductGallery();
    initializeQuantitySelector();
    initializeAddToCart();
    initializeWishlist();
});

// Инициализация галереи изображений
function initializeProductGallery() {
    const thumbnails = document.querySelectorAll('.thumbnail');
    const mainImage = document.getElementById('main-product-image');

    if (!mainImage || thumbnails.length === 0) return;

    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            // Убираем активный класс у всех
            thumbnails.forEach(t => t.classList.remove('active'));

            // Добавляем активный класс текущему
            this.classList.add('active');

            // Меняем главное изображение
            const imageUrl = this.getAttribute('data-image');
            mainImage.src = imageUrl;

            // Добавляем плавную смену изображения
            mainImage.style.opacity = '0.7';
            setTimeout(() => {
                mainImage.style.opacity = '1';
            }, 150);
        });
    });
}

// Управление количеством товара
function initializeQuantitySelector() {
    const quantityInput = document.getElementById('quantity');
    const minusBtn = document.querySelector('.qty-btn.minus');
    const plusBtn = document.querySelector('.qty-btn.plus');

    if (!quantityInput || !minusBtn || !plusBtn) return;

    minusBtn.addEventListener('click', function() {
        let value = parseInt(quantityInput.value);
        if (value > 1) {
            quantityInput.value = value - 1;
        }
    });

    plusBtn.addEventListener('click', function() {
        let value = parseInt(quantityInput.value);
        const max = parseInt(quantityInput.max);
        if (value < max) {
            quantityInput.value = value + 1;
        }
    });

    quantityInput.addEventListener('change', function() {
        let value = parseInt(this.value);
        const min = parseInt(this.min);
        const max = parseInt(this.max);

        if (isNaN(value) || value < min) {
            this.value = min;
        } else if (value > max) {
            this.value = max;
        }
    });

    quantityInput.addEventListener('input', function() {
        // Разрешаем только цифры
        this.value = this.value.replace(/[^\d]/g, '');
    });
}

// Добавление в корзину
function initializeAddToCart() {
    const addToCartBtn = document.querySelector('.btn-add-to-cart');
    if (!addToCartBtn) return;

    addToCartBtn.addEventListener('click', function() {
        const productId = this.getAttribute('data-product');
        const quantity = parseInt(document.getElementById('quantity').value);

        // Получаем информацию о товаре
        const productName = document.querySelector('.product-info h1')?.textContent || `Товар #${productId}`;
        const productPrice = parseFloat(document.querySelector('.price')?.textContent?.replace(/[^\d.]/g, '') || 0);

        // Добавляем в корзину (временная реализация через localStorage)
        // addProductToCart(productId, productName, productPrice, quantity);

        // Показываем уведомление
        showNotification(`Добавлено ${quantity} шт. в корзину`, 'success');

        // Обновляем счетчик в шапке
        updateCartCount();
    });
}

// Добавление товара в корзину
// function addProductToCart(productId, productName, productPrice, quantity) {
//     let cart = JSON.parse(localStorage.getItem('voentorg_cart') || '[]');
//
//     // Проверяем, есть ли товар уже в корзине
//     const existingItemIndex = cart.findIndex(item => item.id == productId);
//
//     if (existingItemIndex !== -1) {
//         // Увеличиваем количество
//         cart[existingItemIndex].quantity += quantity;
//     } else {
//         // Добавляем новый товар
//         cart.push({
//             id: productId,
//             name: productName,
//             price: productPrice,
//             quantity: quantity,
//             addedAt: new Date().toISOString()
//         });
//     }
//
//     // Сохраняем корзину
//     localStorage.setItem('voentorg_cart', JSON.stringify(cart));
// }

// Обновление счетчика корзины
function updateCartCount() {
    const cart = JSON.parse(localStorage.getItem('voentorg_cart') || '[]');
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);

    // Обновляем счетчик в шапке
    const cartCountElements = document.querySelectorAll('.cart-count');
    cartCountElements.forEach(element => {
        element.textContent = totalItems;
    });
}

// Добавление в избранное
function initializeWishlist() {
    const wishlistBtn = document.querySelector('.btn-wishlist');
    if (!wishlistBtn) return;

    wishlistBtn.addEventListener('click', function() {
        const productId = document.querySelector('.btn-add-to-cart')?.getAttribute('data-product');
        const productName = document.querySelector('.product-info h1')?.textContent || `Товар #${productId}`;

        // Временная реализация через localStorage
        let wishlist = JSON.parse(localStorage.getItem('voentorg_wishlist') || '[]');

        if (!wishlist.some(item => item.id == productId)) {
            wishlist.push({
                id: productId,
                name: productName,
                addedAt: new Date().toISOString()
            });

            localStorage.setItem('voentorg_wishlist', JSON.stringify(wishlist));

            // Меняем иконку
            this.innerHTML = '<i class="fas fa-heart"></i> В избранном';
            this.style.backgroundColor = '#e74c3c';
            this.style.color = 'white';

            showNotification('Товар добавлен в избранное', 'success');
        } else {
            // Удаляем из избранного
            wishlist = wishlist.filter(item => item.id != productId);
            localStorage.setItem('voentorg_wishlist', JSON.stringify(wishlist));

            // Возвращаем иконку
            this.innerHTML = '<i class="far fa-heart"></i> В избранное';
            this.style.backgroundColor = '';
            this.style.color = '';

            showNotification('Товар удален из избранного', 'info');
        }
    });

    // Проверяем, есть ли товар в избранном
    checkWishlistStatus();
}

// Проверка статуса избранного
function checkWishlistStatus() {
    const wishlistBtn = document.querySelector('.btn-wishlist');
    const productId = document.querySelector('.btn-add-to-cart')?.getAttribute('data-product');

    if (!wishlistBtn || !productId) return;

    const wishlist = JSON.parse(localStorage.getItem('voentorg_wishlist') || '[]');
    const isInWishlist = wishlist.some(item => item.id == productId);

    if (isInWishlist) {
        wishlistBtn.innerHTML = '<i class="fas fa-heart"></i> В избранном';
        wishlistBtn.style.backgroundColor = '#e74c3c';
        wishlistBtn.style.color = 'white';
    }
}

// Показать уведомление
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;

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

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            if (notification.parentNode) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

console.log('Военторг: Страница товара загружена');