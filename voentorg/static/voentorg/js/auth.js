// ===== АУТЕНТИФИКАЦИЯ - JAVASCRIPT =====

document.addEventListener('DOMContentLoaded', function() {
    initializeAuthForms();
});

function initializeAuthForms() {
    // Валидация формы регистрации
    const registerForm = document.querySelector('.auth-form');
    if (registerForm && registerForm.action.includes('register')) {
        registerForm.addEventListener('submit', function(e) {
            if (!validateRegistrationForm()) {
                e.preventDefault();
            }
        });

        // Реальная валидация в реальном времени
        initializeRealTimeValidation();
    }

    // Форматирование телефона
    const phoneInput = document.getElementById('id_phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            formatPhoneNumber(this);
        });
    }
}

function validateRegistrationForm() {
    const username = document.getElementById('id_username');
    const email = document.getElementById('id_email');
    const password1 = document.getElementById('id_password1');
    const password2 = document.getElementById('id_password2');
    const agreeTerms = document.getElementById('agree_terms');

    let isValid = true;

    // Валидация логина
    if (!validateUsername(username.value)) {
        showFieldError(username, 'Логин должен содержать 3-30 символов (буквы, цифры, подчеркивание)');
        isValid = false;
    } else {
        clearFieldError(username);
    }

    // Валидация email
    if (!validateEmail(email.value)) {
        showFieldError(email, 'Введите корректный email');
        isValid = false;
    } else {
        clearFieldError(email);
    }

    // Валидация пароля
    if (password1.value.length < 8) {
        showFieldError(password1, 'Пароль должен содержать минимум 8 символов');
        isValid = false;
    } else {
        clearFieldError(password1);
    }

    // Проверка совпадения паролей
    if (password1.value !== password2.value) {
        showFieldError(password2, 'Пароли не совпадают');
        isValid = false;
    } else {
        clearFieldError(password2);
    }

    // Проверка согласия с условиями
    if (!agreeTerms || !agreeTerms.checked) {
        showNotification('Необходимо согласиться с условиями использования', 'error');
        isValid = false;
    }

    return isValid;
}

function initializeRealTimeValidation() {
    // Валидация логина в реальном времени
    const usernameInput = document.getElementById('id_username');
    if (usernameInput) {
        usernameInput.addEventListener('blur', function() {
            if (this.value && !validateUsername(this.value)) {
                showFieldError(this, 'Логин должен содержать 3-30 символов (буквы, цифры, подчеркивание)');
            } else {
                clearFieldError(this);
            }
        });
    }

    // Валидация email в реальном времени
    const emailInput = document.getElementById('id_email');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            if (this.value && !validateEmail(this.value)) {
                showFieldError(this, 'Введите корректный email');
            } else {
                clearFieldError(this);
            }
        });
    }

    // Валидация паролей в реальном времени
    const password1Input = document.getElementById('id_password1');
    const password2Input = document.getElementById('id_password2');

    if (password1Input && password2Input) {
        password1Input.addEventListener('blur', validatePasswords);
        password2Input.addEventListener('blur', validatePasswords);
        password2Input.addEventListener('input', validatePasswords);
    }
}

function validatePasswords() {
    const password1 = document.getElementById('id_password1');
    const password2 = document.getElementById('id_password2');

    if (!password1 || !password2) return;

    if (password1.value.length > 0 && password1.value.length < 8) {
        showFieldError(password1, 'Пароль должен содержать минимум 8 символов');
    } else {
        clearFieldError(password1);
    }

    if (password2.value.length > 0 && password1.value !== password2.value) {
        showFieldError(password2, 'Пароли не совпадают');
    } else {
        clearFieldError(password2);
    }
}

function validateUsername(username) {
    const regex = /^[a-zA-Z0-9_]{3,30}$/;
    return regex.test(username);
}

function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');

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

function showFieldError(input, message) {
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        clearFieldError(input);

        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.style.color = '#e74c3c';
        errorDiv.style.fontSize = '0.85rem';
        errorDiv.style.marginTop = '5px';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;

        formGroup.appendChild(errorDiv);

        input.classList.add('error');
        input.style.borderColor = '#e74c3c';
    }
}

function clearFieldError(input) {
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        const error = formGroup.querySelector('.field-error');
        if (error) error.remove();

        input.classList.remove('error');
        input.style.borderColor = '#ddd';
    }
}

function showNotification(message, type = 'info') {
    // Используем существующую функцию из main.js или создаем новую
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, type);
    } else {
        alert(message);
    }
}