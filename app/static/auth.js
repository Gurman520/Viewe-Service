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
    const response = await fetch(`/api/auth/${encodedPath}`, {
        method: 'POST',
        headers: {
            'Authorization': 'Basic ' + btoa(`user:${utPass}`),
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
        alert('Неверный пароль');
    }
});