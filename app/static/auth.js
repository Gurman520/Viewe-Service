function decodeHtmlEntities(text) {
    const textArea = document.createElement('textarea');
    textArea.innerHTML = text;
    return textArea.value;
}

document.getElementById('authForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    let doc_name = $('#doc-info').attr('data-doc-name');
    const serverResponse = doc_name;
    const decodedText = decodeHtmlEntities(serverResponse);
    const path = decodedText;
    const encodedPath = encodeURIComponent(path)
        .replace(/'/g, "%27");
    console.log(encodedPath);
    const passwordInput = document.querySelector('#password'); // Пароль из формы
    const passwordValue = passwordInput.value.trim();          // Убираем пробелы

    let utPass = unescape(passwordValue)

    console.log(utPass)

    // Функция для корректного кодирования UTF-8 → Base64
    const utf8ToBase64 = (str) => {
        return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g, 
            (match, p1) => String.fromCharCode(parseInt(p1, 16)))
        );
    };

    console.log(utf8ToBase64(`user:${passwordValue}`))

    const response = await fetch(`/api/auth/${encodedPath}`, {
        method: 'POST',
        headers: {
            // 'Authorization': 'Basic ' + btoa(`user:${utPass}`),
            'Authorization': 'Basic ' + utf8ToBase64(`user:${passwordValue}`),
            'Content-Type': 'application/json'
        },
        credentials: 'include'  // Важно для работы с куками
    });
    
    if (response.ok) {
        const data = await response.json();
        const docResponse = await fetch(`/view/${encodedPath}`, {
                credentials: "include",  // Передаем куки
            });
        if (docResponse.ok) {
                // 3. Получаем HTML и отображаем его
                const html = await docResponse.text();
                document.open();
                document.write(html);
                document.close();
        }
    } else {
        const passwordInput = document.querySelector('#password');
        alert('Неверный пароль');

        passwordInput.value = '';

        passwordInput.style.border = '2px solid red';

        // Анимация
        passwordInput.style.animation = 'shake 0.5s ease-in-out';
        
        // Возвращаем стиль через 5 секунды
        setTimeout(() => {
            passwordInput.style.border = '';
            passwordInput.style.animation = '';
        }, 5000);
        }
});