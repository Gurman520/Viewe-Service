function validateSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput.value === ' ') {
        // Если поле поиска пустое, просто перезагружаем страницу
        window.location.href = "/view/list";
        return false;
    }
    return true;
}

// Дополнительно: отключаем кнопку, если поле пустое
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    
    searchInput.addEventListener('input', function() {
        searchButton.disabled = this.value === '';
    });
    
    // Инициализация состояния кнопки при загрузке
    searchButton.disabled = searchInput.value === '';
});