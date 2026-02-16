// ===== КОРЗИНА - JAVASCRIPT =====

document.addEventListener('DOMContentLoaded', function() {
    console.log('Cart.js initialized');
    initializeCart();
    initializeAddToCartButtons();
});

function initializeCart() {
    // Инициализация обработчиков событий для инпутов количества
    const quantityInputs = document.querySelectorAll('.qty-input');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const productId = this.closest('.cart-item')?.getAttribute('data-product-id');
            if (productId && this.value) {
                updateCartQuantity(productId, 0, parseInt(this.value));
            }
        });
    });
}

function initializeAddToCartButtons() {
    console.log('Initializing add to cart buttons');

    // Находим все кнопки добавления в корзину
    const addToCartButtons = document.querySelectorAll('.btn-add-to-cart');

    console.log('Found buttons:', addToCartButtons.length);

    // Удаляем старые обработчики
    addToCartButtons.forEach(button => {
        // Создаем копию кнопки без обработчиков
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);

        // Добавляем новый обработчик к скопированной кнопке
        newButton.addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();

            console.log('Add to cart clicked');

            const productId = this.getAttribute('data-product');
            console.log('Product ID:', productId);

            if (!productId) {
                console.error('Product ID not found');
                return;
            }

            // Получаем количество
            let quantity = 1;
            const quantityInput = document.getElementById('quantity');
            if (quantityInput) {
                quantity = parseInt(quantityInput.value) || 1;
                console.log('Quantity from input:', quantity);
            }

            addToCart(productId, quantity);
        });
    });
}

function addToCart(productId, quantity = 1) {
    console.log('=== addToCart called ===');
    console.log('Product ID:', productId);
    console.log('Quantity:', quantity);

    const formData = new FormData();
    formData.append('quantity', quantity);
    formData.append('csrfmiddlewaretoken', getCsrfToken());

    fetch(`/cart/ajax_add/${productId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        console.log('Response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        if (data.success) {
            updateCartCount();
            showNotification(data.message || 'Товар добавлен в корзину', 'success');

            // Блокируем кнопку на 1 секунду чтобы предотвратить повторные клики
            const button = document.querySelector(`.btn-add-to-cart[data-product="${productId}"]`);
            if (button) {
                button.disabled = true;
                setTimeout(() => {
                    button.disabled = false;
                }, 1000);
            }
        } else {
            showNotification(data.message || 'Ошибка при добавлении в корзину', 'error');
        }
    })
    .catch(error => {
        console.error('Error in fetch:', error);
        showNotification('Ошибка при добавлении в корзину', 'error');
    });
}

function updateCartQuantity(productId, delta, newQuantity = null) {
    const quantityInput = document.querySelector(`.cart-item[data-product-id="${productId}"] .qty-input`);

    let quantity;
    if (newQuantity !== null) {
        quantity = newQuantity;
    } else {
        quantity = parseInt(quantityInput.value) + delta;
    }

    // Валидация минимального значения
    if (quantity < 1) {
        removeFromCart(productId);
        return;
    }

    // Отправка запроса на сервер
    const formData = new FormData();
    formData.append('quantity', quantity);
    formData.append('csrfmiddlewaretoken', getCsrfToken());

    fetch(`/cart/update/${productId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            updateCartUI();
            showNotification(data.message || 'Корзина обновлена', 'success');
        } else {
            showNotification(data.message || 'Ошибка при обновлении корзины', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка при обновлении корзины', 'error');
    });
}

function removeFromCart(productId) {
    if (!confirm('Удалить товар из корзины?')) {
        return;
    }

    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', getCsrfToken());

    fetch(`/cart/remove/${productId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            updateCartUI();
            showNotification(data.message || 'Товар удален из корзины', 'success');
        } else {
            showNotification(data.message || 'Ошибка при удалении товара', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка при удалении товара', 'error');
    });
}

function clearCart() {
    if (!confirm('Очистить всю корзину?')) {
        return;
    }

    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', getCsrfToken());

    fetch('/cart/clear/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            showNotification(data.message || 'Ошибка при очистке корзины', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка при очистке корзины', 'error');
    });
}

function proceedToCheckout() {
    window.location.href = "/order/create/";
}

function updateCartUI() {
    updateCartCount();
    fetch('/cart/')
        .then(response => response.text())
        .then(html => {
            setTimeout(() => {
                location.reload();
            }, 500);
        })
        .catch(error => {
            console.error('Error:', error);
            location.reload();
        });
}

function updateCartCount() {
    fetch('/cart/get_count/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        const cartCountElement = document.querySelector('.cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = data.count || 0;
        }
    })
    .catch(error => {
        console.error('Error updating cart count:', error);
    });
}

function getCsrfToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === ('csrftoken=')) {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
}

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