function validateSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput.value.trim() === ' ') {
        // Если поле поиска пустое, просто перезагружаем страницу
        window.location.href = "{{ url_for('document_list') }}";
        return false;
    }
    return true;
}

// Дополнительно: отключаем кнопку, если поле пустое
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    
    searchInput.addEventListener('input', function() {
        searchButton.disabled = this.value.trim() === '';
    });
    
    // Инициализация состояния кнопки при загрузке
    searchButton.disabled = searchInput.value.trim() === '';
});