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
    document.querySelectorAll('.results-table .impressora-row').forEach(function (row) {
        row.addEventListener('click', function () {
            handleRowClick(row);
        });
    });

    // "Edit" button functionality: navigate to edit page with the impressora ID
    document.getElementById('editButton').addEventListener('click', function () {
        if (selectedRow) {
            const impressoraId = selectedRow.cells[0].textContent;
            window.location.href = `impressora_cadastrar/${impressoraId}`;  // Redirect to the edit page for the selected client
        } else {
            alert('Nenhum impressora selecionado para editar.');
        }
    });

    // "Delete" button functionality: confirm deletion and delete the impressora
    document.getElementById('deleteButton').addEventListener('click', function () {
        if (selectedRow) {
            const impressoraId = selectedRow.cells[0].textContent; // Assuming the client ID is in the first column
            const confirmDelete = confirm(`Tem certeza que deseja deletar o impressora com código ${impressoraId}?`);
            if (confirmDelete) {
                // Proceed with deleting the selected impressora
                const formData = new FormData();
                formData.append('id', impressoraId);

                fetch('/delete_impressora', {
                    method: 'POST',
                    body: formData
                })
                    .then(response => {
                        if (response.ok) {
                            // Remove the selected row from the table
                            selectedRow.remove();
                            selectedRow = null;  // Deselect after deleting
                        } else {
                            alert('Erro ao deletar o impressora.');
                        }
                    })
                    .catch(error => console.error('Error during fetch:', error));
            }
        } else {
            alert('Nenhum impressora selecionado para deletar.');
        }
    });

    // Search form validation logic
    function validateForm(event) {
        event.preventDefault(); // Prevent the form from submitting right away
        const formValues = {
            id: document.getElementById('id')?.value ?? '',
            descricao: document.getElementById('descricao')?.value ?? '',
            endereco: document.getElementById('endereco')?.value ?? '',
            porta: document.getElementById('porta')?.value ?? '',
            tipo_impressora: document.getElementById('tipo_impressora')?.value ?? '',
            modelo_impressora: document.getElementById('modelo_impressora')?.value ?? ''
        };
        console.log(formValues);
        const errorDiv = document.getElementById('error-message-container');
        errorDiv.innerHTML = '';
        errorDiv.style.color = 'red'; // Set error message color
        const validationRules = {
            id: {
                regex: /^[1-9][0-9]*$/, // Apenas números positivos a partir de 1
                errorMessage: 'Código deve ser um número positivo maior ou igual a 1.'
            },
            descricao: {
                regex: /^[A-Za-z0-9\s]+$/, // Letras, números e espaços
                errorMessage: 'O campo Nome é obrigatório e deve conter apenas letras, números e espaços.'
            },
            endereco: {
                regex: /^([0-9]{1,3}\.){3}[0-9]{1,3}$/, // Formato de IPv4
                errorMessage: 'O endereço deve ser um endereço IPv4 válido.'
            },
            porta: {
                regex: /^(6553[0-5]|655[0-2][0-9]|65[0-4][0-9]{2}|6[0-4][0-9]{3}|[1-9][0-9]{0,3})$/, // Números entre 1 e 65535
                errorMessage: 'A porta deve ser um número entre 1 e 65535.'
            },
            tipo_impressora: {
                regex: /^(REDE|LOCAL)$/, // Somente letras maiúsculas e espaços
                errorMessage: 'Tipo de impressão inválido. Escolha entre "REDE" ou "LOCAL".'
            },
            modelo_impressora: {
                regex: /^(BEMATECH|EPSON)$/, // Somente letras maiúsculas e espaços
                errorMessage: 'Modelo de impressora inválido. Escolha entre "BEMATECH" ou "EPSON".'
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

    document.getElementById('endereco').addEventListener('input', function(event) {
      let value = event.target.value.replace(/\D/g, '');
      value = value.replace(/(\d{3})(?=\d)/g, '$1.');
      event.target.value = value.substring(0, 15);
    });

    document.getElementById('porta').addEventListener('input', function(event) {
      let value = event.target.value;
      value = value.replace(/[^\d.]/g, '');
      value = value.split('.').map(part => part.replace(/^0+/, '')).join('.');
      if (value.length > 15) {
        value = value.substring(0, 15);
      }
      event.target.value = value;
    });

    document.getElementById('pesquisarButton').addEventListener('click', function (event) {
        const isValid = validateForm(event); // Call the validation function
        console.log(isValid);
        if (isValid) {
          const formData = new FormData(document.getElementById('searchForm'));
          fetch('/pesquisar_impressora', {
              method: 'POST',
              body: formData
          })
          .then(response => {
              if (!response.ok) {
                  return response.text().then(text => {
                      throw new Error(text || 'Erro ocorreu ao buscar dados');
                  });
              }
              console.log()
              return response.json(); // Parse the JSON response
          })
          .then(data => {
              const impressoraTableContainer = document.getElementById('impressoraTableContainer');
              impressoraTableContainer.innerHTML = '';
              impressoraTableContainer.style.display = '';
              document.querySelector('.error-message')?.remove();
              if (data.impressoras && data.impressoras.length > 0) {
                  let tableHTML = `
                      <table class="results-table">
                          <thead>
                              <tr>
                                  <th>Código</th>
                                  <th>Descrição</th>
                                  <th>Endereço (IP)</th>
                                  <th>Porta</th>
                                  <th>Tipo Impressora</th>
                                  <th>Modelo Impressora</th>
                                  <th>Selecionado</th>
                              </tr>
                          </thead>
                          <tbody>
                  `;

                  data.impressoras.forEach(impressora => {
                      tableHTML += `
                          <tr class="impressora-row">
                              <td>${impressora.id}</td>
                              <td>${impressora.descricao}</td>
                              <td>${impressora.endereco}</td>
                              <td>${impressora.porta}</td>
                              <td>${impressora.tipo_impressora}</td>
                              <td>${impressora.modelo_impressora}</td>
                              <td>${impressora.selecionado}</td>
                          </tr>
                      `;
                  });
                  tableHTML += `</tbody></table>`;
                  impressoraTableContainer.innerHTML = tableHTML;

                  // Reapply the row selection event listeners after populating the table
                  document.querySelectorAll('.results-table .impressora-row').forEach(function (row) {
                      row.addEventListener('click', function () {
                          handleRowClick(row);
                      });
                  });
              } else {
                  impressoraTableContainer.innerHTML = '<p>Nenhum impressora encontrado.</p>';
              }
          })
          .catch(error => {
              const existingErrorDiv = document.querySelector('.error-message');
              if (existingErrorDiv) {
                  existingErrorDiv.remove();
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
