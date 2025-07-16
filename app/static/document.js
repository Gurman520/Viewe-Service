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