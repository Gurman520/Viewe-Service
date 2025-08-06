function copyShareLink() {
    const shareLink = document.getElementById('shareLink');
    shareLink.select();
    document.execCommand('copy');
    
    // Инициализируем и показываем toast
    const toastEl = document.getElementById('copyToast');
    const toast = new bootstrap.Toast(toastEl);
    toast.show();

    // Автоматическое скрытие через 4 секунды
    setTimeout(() => {
        toast.hide();
    }, 4000);
}

// Инициализация всех toast элементов при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.map(function(toastEl) {
        return new bootstrap.Toast(toastEl);
    });
});

function checkTokenExpiration() {
    const token = document.cookie.split('; ')
        .find(row => row.startsWith('doc_session='))
        ?.split('=')[1];
        
    if (token) {
        fetch('/api/auth/verify_token', {
            method: POST,
            headers: {
                'Authorization': `Bearer ${token}`
            }
        }).then(response => {
            if (!response.ok) {
                let doc_name = $('#doc-info').attr('data-doc-name');
                // Токен невалиден, перенаправляем на аутентификацию
                window.location.href = '/api/auth/{{ document_name | replace(" ", "_") }}';
            }
        });
    }
}
            
// Проверяем каждые 5 минут
setInterval(checkTokenExpiration, 300000);
document.addEventListener('DOMContentLoaded', checkTokenExpiration);

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

    // Обработчики для картинок
    document.querySelectorAll('.wiki-image-left').forEach(img => {
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
