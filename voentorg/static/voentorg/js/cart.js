// ===== КОРЗИНА - JAVASCRIPT =====

document.addEventListener('DOMContentLoaded', function() {
    initializeCart();
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
            // Обновляем интерфейс
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
            // Обновляем интерфейс
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

function guestCheckout() {
    // Реализация оформления заказа для гостя
    showNotification('Функция оформления заказа для гостей в разработке', 'info');
    // Временная реализация - предлагаем зарегистрироваться
    if (confirm('Для оформления заказа необходимо войти в систему. Перейти к регистрации?')) {
        window.location.href = "/register/";
    }
}

function updateCartUI() {
    // Обновляем счетчик корзины в хедере
    updateCartCount();

    // Перезагружаем страницу для обновления данных
    // Можно заменить на более сложную логику обновления без перезагрузки
    fetch('/cart/')
        .then(response => response.text())
        .then(html => {
            // Можно обновить только часть страницы без полной перезагрузки
            // Но для простоты используем перезагрузку
            setTimeout(() => {
                location.reload();
            }, 500); // Небольшая задержка для показа уведомления
        })
        .catch(error => {
            console.error('Error:', error);
            location.reload();
        });
}

function updateCartCount() {
    // Обновление счетчика в хедере через AJAX
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
    // Ищем CSRF токен в cookies
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

// Добавляем анимации для уведомлений, если их еще нет
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