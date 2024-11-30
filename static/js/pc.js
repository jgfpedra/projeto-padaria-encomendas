function getSelectedClientId() {
    const selectedClient = document.querySelector('input[name="selected-client"]:checked');
    return selectedClient ? selectedClient.value : null;
}

function redirectToEdit() {
    const clientId = getSelectedClientId();
    if (clientId) {
        window.location.href = `cliente_cadastrar/${clientId}`;
    } else {
        alert('Nenhum cliente selecionado para editar.');
    }
}

function confirmDelete() {
    const clientId = getSelectedClientId();
    if (clientId) {
        const confirmDelete = confirm('Tem certeza que deseja deletar este cliente?');
        if (confirmDelete) {
            const formData = new FormData();
            formData.append('id', clientId);
            
            fetch('/delete_cliente', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    window.location.reload(); // Reloads the page to reflect changes
                } else {
                    alert('Erro ao deletar o cliente.');
                }
            })
            .catch(error => console.error('Error during fetch:', error));
        }
    } else {
        alert('Nenhum cliente selecionado para deletar.');
    }
}

document.getElementById('pesquisarButton').addEventListener('click', function(event) {
    event.preventDefault(); // Prevent the form from submitting normally

    const formData = new FormData(document.getElementById('searchForm'));

    console.log(formData);
    fetch('/pesquisar_cliente', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        // Log the response status for debugging
        console.log('Response status:', response.status);

        if (!response.ok) {
            // Attempt to parse JSON error response
            return response.text().then(text => {
                throw new Error(text || 'Error occurred while fetching data');
            });
        }
        return response.json(); // Parse the JSON response
    })
    .then(data => {
        // Clear previous results and error messages
        const clientTableContainer = document.getElementById('clientTableContainer');
        clientTableContainer.innerHTML = ''; // Clear previous results
        clientTableContainer.style.display = ''; // Make sure the container is visible
        document.querySelector('.error-message')?.remove(); // Remove any previous error message

        if (data.clientes && data.clientes.length > 0) {
            let tableHTML = `
                <table class="results-table">
                    <thead>
                        <tr>
                            <th>Select</th>
                            <th>Código</th>
                            <th>Nome</th>
                            <th>Endereço</th>
                            <th>Número</th>
                            <th>Bairro</th>
                            <th>Complemento</th>
                            <th>Observação</th>
                            <th>Telefones</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            data.clientes.forEach(cliente => {
                tableHTML += `
                    <tr>
                        <td><input type="radio" name="selected-client" value="${cliente.id}" class="client-radio"></td>
                        <td>${cliente.id}</td>
                        <td>${cliente.nome}</td>
                        <td>${cliente.endereco}</td>
                        <td>${cliente.numero}</td>
                        <td>${cliente.bairro}</td>
                        <td>${cliente.complemento}</td>
                        <td>${cliente.observacao}</td>
                        <td>${cliente.telefones.join(', ')}</td>
                    </tr>
                `;
            });
            tableHTML += `</tbody></table>`;
            clientTableContainer.innerHTML = tableHTML;
        } else {
            clientTableContainer.innerHTML = '<p>Nenhum cliente encontrado.</p>';
        }
    })
    .catch(error => {
        // Clear any existing error messages
        const existingErrorDiv = document.querySelector('.error-message');
        if (existingErrorDiv) {
            existingErrorDiv.remove(); // Remove the old error message
        }

        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.color = 'red';

        // Check if the error has a response
        if (error.response) {
            return error.response.json().then(errData => {
                // Extract only the error message
                errorDiv.textContent = errData.error || 'Erro desconhecido'; 
                document.getElementById('error-message-container').appendChild(errorDiv);
            });
        } else {
            // If there's no response, it's likely a network error
            // Attempt to extract the relevant part from error.message
            let networkErrorMessage = 'Erro de rede: ' + error.message;
            // Check if the error message is JSON formatted
            try {
                const parsedMessage = JSON.parse(error.message);
                if (parsedMessage.error) {
                    networkErrorMessage = 'Erro de rede: ' + parsedMessage.error; // Use the error message from JSON
                }
            } catch (e) {
                networkErrorMessage = 'Erro de rede: ' + parsedMessage.error; // Use the error message from JSON
            }
            errorDiv.textContent = networkErrorMessage; // Display the network error
            document.getElementById('error-message-container').appendChild(errorDiv);
            console.error('Error during fetch:', error);
        }
    });
});
