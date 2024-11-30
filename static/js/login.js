document.addEventListener('DOMContentLoaded', function() {
    // Manipular o envio do formulário de login
    document.getElementById('login-form').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevenir o envio padrão do formulário

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorMessage = document.getElementById('error-message');
        const usernameInput = document.getElementById('username');
        const passwordInput = document.getElementById('password');

        // Reiniciar a mensagem de erro e os estilos dos inputs
        errorMessage.style.display = 'none'; // Ocultar mensagem de erro

        // Verificar se todos os campos estão preenchidos
        if (!username || !password) {
            errorMessage.textContent = 'Por favor, preencha todos os campos.'; // Mensagem personalizada
            errorMessage.style.display = 'block'; // Mostrar mensagem de erro
            return; // Impedir envio do formulário
        }

        // Verificar se o username contém apenas letras maiúsculas
        const uppercasePattern = /^[A-Z]+$/; // Regex para apenas letras maiúsculas
        if (!uppercasePattern.test(username)) {
            errorMessage.textContent = 'O nome de usuário deve conter apenas letras maiúsculas.'; // Mensagem personalizada
            errorMessage.style.display = 'block'; // Mostrar mensagem de erro
            usernameInput.classList.add('input-error'); // Destacar input de username
            return; // Impedir envio do formulário
        }

        // Limpar erros anteriores
        usernameInput.classList.remove('input-error'); // Remover borda vermelha
        passwordInput.classList.remove('input-error'); // Remover borda vermelha

        fetch('/login', {
            method: 'POST', // Usar método POST
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password }) // Enviar carga JSON
        })
        .then(response => {
            if (response.status === 401) {
                // Manipular resposta 401 Não Autorizado
                return response.json().then(data => {
                    errorMessage.textContent = data.message; // Definir o texto da mensagem de erro
                    errorMessage.style.display = 'block'; // Mostrar a mensagem de erro
                    usernameInput.classList.add('input-error'); // Destacar input de username
                    passwordInput.classList.add('input-error'); // Destacar input de senha
                });
            } else if (!response.ok) {
                throw new Error('A resposta da rede não foi ok: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Redirecionar para a página inicial em caso de login bem-sucedido
                window.location.href = '/'; 
            }
        });
    });
});
