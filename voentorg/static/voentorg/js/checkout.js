// ===== ОФОРМЛЕНИЕ ЗАКАЗА - JAVASCRIPT =====

document.addEventListener('DOMContentLoaded', function() {
    initializeCheckout();
});

function initializeCheckout() {
    // Инициализация маски для телефона
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            formatPhoneNumber(this);
        });
    }

    // Валидация формы при отправке
    const checkoutForm = document.querySelector('.checkout-form-section form');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function(e) {
            if (!validateCheckoutForm()) {
                e.preventDefault();
            }
        });
    }
}

function formatPhoneNumber(input) {
    // Удаляем все нецифровые символы
    let value = input.value.replace(/\D/g, '');

    // Форматируем номер
    if (value.length === 0) return '';

    let formatted = '+7 ';

    if (value.length > 1) {
        formatted += '(' + value.substring(1, 4);
    }
    if (value.length >= 4) {
        formatted += ') ' + value.substring(4, 7);
    }
    if (value.length >= 7) {
        formatted += '-' + value.substring(7, 9);
    }
    if (value.length >= 9) {
        formatted += '-' + value.substring(9, 11);
    }

    input.value = formatted;
}

function validateCheckoutForm() {
    const email = document.getElementById('email');
    const phone = document.getElementById('phone');
    const shippingAddress = document.getElementById('shipping_address');
    const agreeTerms = document.getElementById('agree_terms');

    let isValid = true;

    // Валидация email
    if (!email.value.trim()) {
        showFieldError(email, 'Введите email');
        isValid = false;
    } else if (!isValidEmail(email.value)) {
        showFieldError(email, 'Введите корректный email');
        isValid = false;
    } else {
        clearFieldError(email);
    }

    // Валидация телефона
    if (!phone.value.trim()) {
        showFieldError(phone, 'Введите телефон');
        isValid = false;
    } else if (!isValidPhone(phone.value)) {
        showFieldError(phone, 'Введите корректный телефон');
        isValid = false;
    } else {
        clearFieldError(phone);
    }

    // Валидация адреса
    if (!shippingAddress.value.trim()) {
        showFieldError(shippingAddress, 'Введите адрес доставки');
        isValid = false;
    } else {
        clearFieldError(shippingAddress);
    }

    // Проверка согласия
    if (!agreeTerms.checked) {
        showNotification('Необходимо согласиться с условиями', 'error');
        isValid = false;
    }

    return isValid;
}

function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function isValidPhone(phone) {
    // Упрощенная проверка телефона
    const digits = phone.replace(/\D/g, '');
    return digits.length >= 10;
}

function showFieldError(input, message) {
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        // Удаляем старую ошибку
        const oldError = formGroup.querySelector('.field-error');
        if (oldError) oldError.remove();

        // Добавляем новую ошибку
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.style.color = '#e74c3c';
        errorDiv.style.fontSize = '0.85rem';
        errorDiv.style.marginTop = '5px';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;

        formGroup.appendChild(errorDiv);

        // Подсвечиваем поле
        input.style.borderColor = '#e74c3c';
    }
}

function clearFieldError(input) {
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        const error = formGroup.querySelector('.field-error');
        if (error) error.remove();

        input.style.borderColor = '#ddd';
    }
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