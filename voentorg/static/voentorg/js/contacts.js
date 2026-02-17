// voentorg/static/voentorg/js/contacts.js
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contact-form');

    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Здесь можно добавить AJAX отправку формы
            // или просто показать сообщение об успешной отправке

            const formData = new FormData(this);
            const data = Object.fromEntries(formData);

            // Валидация формы
            if (!data.name || !data.email || !data.subject || !data.message) {
                alert('Пожалуйста, заполните все обязательные поля');
                return;
            }

            // Здесь будет отправка данных на сервер
            console.log('Отправка формы:', data);

            // Показываем сообщение об успешной отправке
            alert('Спасибо за обращение! Мы свяжемся с вами в ближайшее время.');
            this.reset();
        });
    }
});