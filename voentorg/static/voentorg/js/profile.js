// ===== ЛИЧНЫЙ КАБИНЕТ - JAVASCRIPT =====

document.addEventListener('DOMContentLoaded', function() {
    initializeProfile();
});

function initializeProfile() {
    // Инициализация кнопки смены email
    const changeEmailBtn = document.querySelector('.btn-change-email');
    if (changeEmailBtn) {
        changeEmailBtn.addEventListener('click', function() {
            requestEmailChange();
        });
    }

    // Инициализация кнопки сохранения изменений
    const saveBtn = document.querySelector('.btn-save-changes');
    if (saveBtn) {
        saveBtn.addEventListener('click', function() {
            saveProfileChanges();
        });
    }

    // Инициализация ссылок скачивания чека
    const downloadReceiptLinks = document.querySelectorAll('.download-receipt');
    downloadReceiptLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            downloadReceipt(this);
        });
    });
}

function requestEmailChange() {
    // Здесь можно реализовать логику запроса смены email
    showNotification('Запрос на смену email отправлен администратору', 'info');
}

function saveProfileChanges() {
    const firstName = document.getElementById('first_name')?.value;
    const lastName = document.getElementById('last_name')?.value;
    const phone = document.getElementById('phone')?.value;

    // Валидация
    if (!validatePhone(phone)) {
        showNotification('Некорректный номер телефона', 'error');
        return;
    }

    // Отправка данных на сервер
    const formData = new FormData();
    formData.append('first_name', firstName);
    formData.append('last_name', lastName);
    formData.append('phone', phone);

    fetch('/profile/update/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Данные успешно сохранены', 'success');
        } else {
            showNotification('Ошибка при сохранении данных', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Ошибка при сохранении данных', 'error');
    });
}

function validatePhone(phone) {
    if (!phone) return true; // Телефон не обязателен

    const phoneRegex = /^[0-9+()-]{7,20}$/;
    return phoneRegex.test(phone);
}

function downloadReceipt(link) {
    const orderId = link.closest('.order-card')?.querySelector('.order-id')?.textContent;

    if (!orderId) {
        showNotification('Невозможно определить номер заказа', 'error');
        return;
    }

    // Здесь можно реализовать генерацию PDF чека
    showNotification('Чек будет сгенерирован и отправлен на ваш email', 'info');

    // Временная заглушка
    setTimeout(() => {
        showNotification('Чек успешно сгенерирован', 'success');
    }, 1500);
}

function getCsrfToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : '';
}

function showNotification(message, type = 'info') {
    // Временная реализация через alert
    alert(message);

    // В будущем можно реализовать красивую систему уведомлений
}