// Запрет выхода по кнопке "Назад"
history.pushState(null, null, location.href);
window.onpopstate = function() {
    history.go(1);
};
        
// Запрет контекстного меню
document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
});

// Увеличение картинок
document.addEventListener('DOMContentLoaded', () => {
    // Создаем элементы модального окна
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    
    const modalImg = document.createElement('img');
    modalImg.className = 'modal-image';
    
    overlay.appendChild(modalImg);
    document.body.appendChild(overlay);

    // Обработчики для картинок
    document.querySelectorAll('.wiki-image').forEach(img => {
        img.addEventListener('click', () => {
            modalImg.src = img.src;
            modalImg.alt = img.alt;
            overlay.classList.add('active');
            overlay.style.display = 'flex';
        });
    });

    // Закрытие по клику
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay || e.target === modalImg) {
            overlay.classList.remove('active');
            setTimeout(() => {
                overlay.style.display = 'none';
            }, 300);
        }
    });
});

