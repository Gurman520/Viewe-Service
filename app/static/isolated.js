// Запрет выхода по кнопке "Назад"
history.pushState(null, null, location.href);
window.onpopstate = function() {
    history.go(1);
};
        
// Запрет контекстного меню
document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
});