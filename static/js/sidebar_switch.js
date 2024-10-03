document.addEventListener('DOMContentLoaded', function() {
    const categoryLink = document.getElementById('category-link');
    const questionLink = document.getElementById('question-link');
    const categoriesSection = document.getElementById('categories-section');
    const questionsSection = document.getElementById('questions-section');

    // Функция для получения параметров запроса
    function getQueryParam(param) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(param);
    }

    // Определяем текущий раздел из URL
    const currentSection = getQueryParam('section') || 'categories';

    // Устанавливаем активный раздел
    if (currentSection === 'categories') {
        categoryLink.classList.add('active');
        questionLink.classList.remove('active');
        categoriesSection.style.display = 'block';
        questionsSection.style.display = 'none';
    } else if (currentSection === 'questions') {
        questionLink.classList.add('active');
        categoryLink.classList.remove('active');
        categoriesSection.style.display = 'none';
        questionsSection.style.display = 'block';
    }

    // Обработчики событий для ссылок боковой панели
    categoryLink.addEventListener('click', function(e) {
        e.preventDefault();
        window.location.href = '?section=categories';
    });

    questionLink.addEventListener('click', function(e) {
        e.preventDefault();
        window.location.href = '?section=questions';
    });
});
