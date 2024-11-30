// Regras de validação para os campos do formulário
const validationRules = {
    nome: {
        regex: /^[A-Za-zÀ-ÿ\s]+$/, // Aceita apenas letras e espaços (incluindo acentos)
        errorMessage: 'O campo Nome é obrigatório e deve conter apenas letras.'
    },
    endereco: {
        regex: /^[A-Za-zÀ-ÿ\s]+$/, // Aceita apenas letras e espaços (incluindo acentos)
        errorMessage: 'O campo Endereco é obrigatório e deve conter apenas letras.'
    },
    numero: {
        regex: /^[a-zA-Z0-9\s\-\/]{1,10}$/, // Aceita letras, números, espaços, traços e barras, até 10 caracteres
        errorMessage: 'O campo Número pode conter letras e dígitos - maximo de 10 caracteres'
    },
    bairro: {
        regex: /^[A-Za-zÀ-ÿ\s]+$/,
        errorMessage: 'O campo Bairro é obrigatório e deve conter apenas letras (mínimo 1 caractere).'
    },
    complemento: {
        regex: /^[a-zA-Z0-9\s\-\/]*$/,
        errorMessage: 'O campo Complemento é opcional e pode conter letras, números, espaços, traços e barras (sem limite).'
    },
    observacao: {
        regex: /^[a-zA-Z0-9\s\-\/]*$/,
        errorMessage: 'O campo Observação é opcional e pode conter letras, números, espaços, traços e barras (sem limite).'
    },
    telefones: {
        regex: /^\(\d{2}\)\d{8,9}$/,
        errorMessage: 'O telefone é obrigatório e deve estar no formato (99)999999999 ou (99)99999999.'
    }
};

function validateInputs() {
    const inputs = document.querySelectorAll('#meu_formulario input');
    const errorMessageDiv = document.getElementById('error-message');
    errorMessageDiv.style.display = 'none'; // Hide the error message initially
    errorMessageDiv.textContent = ''; // Clear any previous error messages
    let hasError = false;

    for (const input of inputs) {
        const name = input.name;
        if (validationRules[name]) {
            if (!validationRules[name].regex.test(input.value)) {
                errorMessageDiv.textContent = validationRules[name].errorMessage; // Show the first error
                hasError = true;
                break; // Exit the loop on first error
            }
        }
    }

    // Validate phone numbers
    const phoneInputs = document.querySelectorAll('input[name="telefones"]');
    
    for (const input of phoneInputs) {
        if (!validationRules.telefones.regex.test(input.value)) {
            errorMessageDiv.textContent = validationRules.telefones.errorMessage; // Show phone error
            hasError = true;
            break; // Exit on first phone error
        }
    }

    if (hasError) {
        errorMessageDiv.style.display = 'block'; // Show the error message div
        inputs[0].focus(); // Focus on the first invalid field
        return false; // Validation failed
    }

    return true; // All inputs are valid
}

  function submeter_formulario() {
      if (validateInputs()) {
          const formData = new FormData(document.getElementById('meu_formulario'));

          fetch('/cliente_cadastrar', {
              method: 'POST',
              body: formData
          })
          .then(response => {
              return response.json().then(data => {
                  if (!response.ok) {
                      // Handle HTTP error responses (4xx, 5xx)
                      const errorMessageDiv = document.getElementById('error-message');
                      errorMessageDiv.textContent = data.message || 'Erro ao enviar os dados.';
                      errorMessageDiv.style.display = 'block';
                      throw new Error(data.message || 'Erro ao enviar os dados.');
                  }
                  return data; // Proceed to handle success
              });
          })
          .then(data => {
              if (data.success) {
                  alert('Cliente salvo com sucesso!');
                  window.location.href = '/pesquisar_cliente';
              } else {
                  // Display error message if not successful
                  const errorMessageDiv = document.getElementById('error-message');
                  errorMessageDiv.textContent = data.message;
                  errorMessageDiv.style.display = 'block';
              }
          })
          .catch(error => {
              console.error('Erro:', error);
              alert('Ocorreu um erro ao enviar os dados.');
          });
      }
  }

  function carregar_popup_cancelar() {
      fetch('/cancelar_cliente')
          .then(response => response.json())
          .then(data => {
              if (data.popup_cancelar_cliente_html) {
                document.getElementById('popup-cancelar-cliente').innerHTML = data.popup_cancelar_cliente_html;
                document.getElementById('botao-salvar').onclick = function() {
                    if (validateInputs()) { // Verifica todos os campos antes de submeter
                        document.getElementById('meu_form').submit();
                        window.location.href = '/pesquisar_cliente'
                        fechar_popup();
                    }
                };
                document.getElementById('botao-cancelar').onclick = function(event) {
                    event.preventDefault(); // Impede o envio do formulário
                    window.location.href = '/pesquisar_cliente';
                    fechar_popup();
                };
                document.getElementById('popup-container-cancelar-display').style.display = 'flex'; 
            } else {
                console.error('Popup HTML is missing');
            }
        })
        .catch(error => console.error('Error loading pop-up:', error));
}

function fechar_popup() {
    document.getElementById('popup-container-cancelar-display').style.display = 'none'; // Apenas fecha o popup
}

document.addEventListener("DOMContentLoaded", function() {
    let phoneCounter = 1; // Start counter at 1

    function addPhoneInput() {
        const phoneContainer = document.getElementById('phone-container');
        const newPhoneRow = document.createElement('div');
        newPhoneRow.className = 'phone-row';
        newPhoneRow.innerHTML = `
            <label for="phone-${phoneCounter}" required>Telefone ${phoneCounter}:</label>
            <input type="text" name="telefones" id="phone-${phoneCounter}" placeholder="Digite o telefone" 
                   pattern="^\\(\\d{2}\\)\\d{8,9}$" title="Formato: (99)999999999 ou (99)99999999" 
                   oninput="formatCellphone(this)" maxlength="13" required>
        `;
        phoneContainer.insertBefore(newPhoneRow, phoneContainer.lastElementChild); // Add above the buttons
        phoneCounter++; // Increment counter after adding input
        updatePhoneLabels(); // Update labels
        updateRemoveButtonState();
    }

    function removePhoneInput() {
        const phoneContainer = document.getElementById('phone-container');
        const phoneRows = phoneContainer.getElementsByClassName('phone-row');
        if (phoneRows.length > 1) { // Check if there's more than one phone input
            phoneContainer.removeChild(phoneRows[phoneRows.length - 1]); // Remove the last input
            phoneCounter--; // Decrement counter only if there's more than one input
            updatePhoneLabels(); // Update labels
            updateRemoveButtonState();
        } else {
            alert('Você deve manter pelo menos um campo de telefone.');
        }
    }

    function updatePhoneLabels() {
        const phoneRows = document.querySelectorAll('.phone-row');
        phoneRows.forEach((row, index) => {
            const label = row.querySelector('label');
            label.textContent = `Telefone ${index + 1}:`; // Update label text
        });
    }

    function updateRemoveButtonState() {
        const removeButton = document.querySelector('button[onclick="removePhoneInput()"]');
        const phoneContainer = document.getElementById('phone-container');
        removeButton.disabled = phoneContainer.children.length <= 1; // Disable if only one input remains
    }

    function formatCellphone(input) {
        let value = input.value.replace(/\D/g, ''); // Remove non-numeric characters
        if (value.length <= 11) {
            value = value.replace(/^(\d{2})(\d{0,9})$/, '($1)$2');
        } else {
            value = value.replace(/^(\d{2})(\d{9})(\d{0,1})$/, '($1)$2$3');
        }
        input.value = value;
    }

    // Define global functions for HTML access
    window.addPhoneInput = addPhoneInput;
    window.removePhoneInput = removePhoneInput;
    window.formatCellphone = formatCellphone;

    updateRemoveButtonState(); // Update button state on load
});

