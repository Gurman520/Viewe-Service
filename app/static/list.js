function validateSearch() {
    const searchInput = document.getElementById('searchInput');
    let doc_type = $('#doc-info').attr('data-doc-type');
    if (searchInput.value === ' ') {
        // Если поле поиска пустое, просто перезагружаем страницу
        if (doc_type == 'doctor'){
            window.location.href = "/view/list";
            return false;
        } else {
            window.location.href = "/view/adm/list";
            return false;
        }
        
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

    const selected = document.getElementById('subgroupSelect');
    const quer = searchInput.value
    
    if (quer) {
        for (let i = 0; i < selected.options.length; i++) {
            if (selected.options[i].value === quer) {
                selected.selectedIndex = i;
                break;
            }
        }
    }
});

document.getElementById('subgroupSelect').addEventListener('change', function() {
    const selectedSubgroup = this.value;
    const searchInput = document.getElementById('searchInput');

    searchInput.value = selectedSubgroup;
    if (selectedSubgroup != "") {
        searchButton.disabled = false;
    }
    else if (selectedSubgroup != " ") {
        searchInput.value = " "
    }

    console.log(selectedSubgroup)
});
