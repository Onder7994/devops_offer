document.getElementById('change_password_checkbox').addEventListener('change', function() {
    var passwordFields = document.querySelectorAll('.password-fields');
        if (this.checked) {
            passwordFields.forEach(function(field) {
                field.style.display = 'block';  // Показываем поля
                field.querySelector('input').required = true; // Делаем обязательными
            });
        } else {
            passwordFields.forEach(function(field) {
                field.style.display = 'none';  // Скрываем поля
                field.querySelector('input').required = false; // Убираем обязательность
            });
        }
});