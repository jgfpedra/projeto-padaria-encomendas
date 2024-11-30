document.addEventListener("DOMContentLoaded", function () {
    let selectedRow = null; // Variable to store the currently selected row

    // Function to handle row selection: ensure only one row can be selected at a time
    function handleRowClick(row) {
        // If a row is already selected, remove the 'selected' class from it
        if (selectedRow) {
            selectedRow.classList.remove('selected');
        }

        // Add the 'selected' class to the clicked row
        row.classList.add('selected');
        selectedRow = row;  // Update the selected row
    }

    // Add click event listeners to each row in the table
    document.querySelectorAll('.results-table .client-row').forEach(function (row) {
        row.addEventListener('click', function () {
            handleRowClick(row);
        });
    });

    // "Edit" button functionality: navigate to edit page with the client ID
    document.getElementById('editButton').addEventListener('click', function () {
        if (selectedRow) {
            const clientId = selectedRow.cells[0].textContent; // Assuming the client ID is in the first column
            window.location.href = `cliente_cadastrar/${clientId}`;  // Redirect to the edit page for the selected client
        } else {
            alert('Nenhum cliente selecionado para editar.');
        }
    });

    // "Delete" button functionality: confirm deletion and delete the client
    document.getElementById('deleteButton').addEventListener('click', function () {
        if (selectedRow) {
            const clientId = selectedRow.cells[0].textContent; // Assuming the client ID is in the first column
            const confirmDelete = confirm(`Tem certeza que deseja deletar o cliente com código ${clientId}?`);
            if (confirmDelete) {
                // Proceed with deleting the selected client
                const formData = new FormData();
                formData.append('id', clientId);

                fetch('/delete_cliente', {
                    method: 'POST',
                    body: formData
                })
                    .then(response => {
                        if (response.ok) {
                            // Remove the selected row from the table
                            selectedRow.remove();
                            selectedRow = null;  // Deselect after deleting
                        } else {
                            alert('Erro ao deletar o cliente.');
                        }
                    })
                    .catch(error => console.error('Error during fetch:', error));
            }
        } else {
            alert('Nenhum cliente selecionado para deletar.');
        }
    });

    // Search form validation logic
    function validateForm(event) {
        event.preventDefault(); // Prevent the form from submitting right away
        const formValues = {
            id: document.getElementById('id')?.value ?? '',
            nome: document.getElementById('nome')?.value ?? '',
            telefone: document.getElementById('telefone')?.value ?? '',
            endereco: document.getElementById('endereco')?.value ?? ''
        };
        const errorDiv = document.getElementById('error-message-container');
        errorDiv.innerHTML = '';
        errorDiv.style.color = 'red'; // Set error message color
        const validationRules = {
            id: {
                regex: /^[1-9][0-9]*$/, // Allows positive numbers greater than or equal to 1
                errorMessage: 'Código deve ser um número positivo maior ou igual a 1.'
            },
            nome: {
                regex: /^[A-Za-zÀ-ÿ\s]*$/, // Allows letters and spaces or empty
                errorMessage: 'O campo Nome é obrigatório e deve conter apenas letras.'
            },
            telefone: {
                regex: /^\(\d{2}\)\d{8,9}$/, // Matches phone format like (99)999999999 or (99)99999999
                errorMessage: 'O telefone é obrigatório e deve estar no formato (99)999999999 ou (99)99999999.'
            },
            endereco: {
                regex: /^[A-Za-zÀ-ÿ0-9\s,.-]*$/, // Allows letters, numbers, spaces, commas, periods, and hyphens
                errorMessage: 'Endereço contém caracteres inválidos.'
            }
        };
        for (const field in formValues) {
            const value = formValues[field];
            const rule = validationRules[field];
            if (value && rule && !rule.regex.test(value)) {
                errorDiv.innerHTML = rule.errorMessage;
                return false;
            }
            if (field === 'id' && value !== '' && !/^[1-9]\d*$/.test(value)) {
                errorDiv.innerHTML = 'O Código deve ser um número positivo maior ou igual a 1.';
                return false;
            }
        }
        return true;
    }

    // Handle the search button click event
    document.getElementById('pesquisarButton').addEventListener('click', function (event) {
        const isValid = validateForm(event); // Call the validation function
        if (isValid) {
            const formData = new FormData(document.getElementById('searchForm'));
            fetch('/pesquisar_cliente', {
                method: 'POST',
                body: formData
            })
                .then(response => {
                    if (!response.ok) {
                        return response.text().then(text => {
                            throw new Error(text || 'Erro ocorreu ao buscar dados');
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
                                <tr class="client-row">
                                    <td>${cliente.id}</td>
                                    <td>${cliente.nome}</td>
                                    <td>${cliente.endereco}</td>
                                    <td>${cliente.numero}</td>
                                    <td>${cliente.bairro}</td>
                                    <td>${cliente.complemento}</td>
                                    <td>${cliente.observacao}</td>
                                    <td>
                                        <div class="telefone-container">
                                            <span>${cliente.telefones.join(', ')}</span>
                                        </div>
                                    </td>
                                </tr>
                            `;
                        });
                        tableHTML += `</tbody></table>`;
                        clientTableContainer.innerHTML = tableHTML;

                        // Reapply the row selection event listeners after populating the table
                        document.querySelectorAll('.results-table .client-row').forEach(function (row) {
                            row.addEventListener('click', function () {
                                handleRowClick(row);
                            });
                        });
                    } else {
                        clientTableContainer.innerHTML = '<p>Nenhum cliente encontrado.</p>';
                    }
                })
                .catch(error => {
                    const existingErrorDiv = document.querySelector('.error-message');
                    if (existingErrorDiv) {
                        existingErrorDiv.remove(); // Remove the old error message
                    }

                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'error-message';
                    errorDiv.style.color = 'red';

                    errorDiv.textContent = 'Erro ao processar a resposta do servidor';
                    document.getElementById('error-message-container').appendChild(errorDiv);
                    console.error('Error during fetch:', error);
                });
        }
    });
});

function formatCellphone(input) {
    // Get the input value without any non-digit characters
    let value = input.value.replace(/\D/g, '');

    // Check the length of the value and format accordingly
    if (value.length <= 2) {
        // Format as (XX)
        input.value = '(' + value;
    } else if (value.length <= 6) {
        // Format as (XX)XXXXX
        input.value = '(' + value.substring(0, 2) + ')' + value.substring(2);
    } else {
        // Format as (XX)XXXXXXXXX
        input.value = '(' + value.substring(0, 2) + ')' + value.substring(2, 7) + value.substring(7, 11);
    }
}
