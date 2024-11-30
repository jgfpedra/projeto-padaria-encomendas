function submeter_formulario() {
  const form = document.getElementById('meu_form');
  const formData = new FormData(form);

  // Validate form and stop submission if any validation fails
  if (!validateForm(formData)) return;

  // Handle empty 'porta' by setting it to null before sending
  if (formData.get('porta') === '') formData.set('porta', null);

  // Submit the form using fetch
  fetch('/impressora_cadastrar', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      window.location.href = "/pesquisar_impressora"; // Redirect on success
    } else {
      // Check if the response has an error field
      if (data.errors && Array.isArray(data.errors)) {
        displayErrors(data.errors); // Show errors if any
      } else {
        // Display general message
        displayErrors([{ field: 'general', message: data.message || 'An error occurred while submitting the form.' }]);
      }
    }
  })
  .catch(error => {
    console.error('Error:', error);
    displayErrors([{ field: 'general', message: 'An error occurred while submitting the form.' }]);
  });
}

function carregar_popup_cancelar() {
  fetch('/cancelar_impressora')
    .then(response => response.json())
    .then(data => {
        if (data.popup_cancelar_impressora_html) {
          document.getElementById('popup-cancelar-impressora').innerHTML = data.popup_cancelar_impressora_html;  // Corrigi o nome da chave 'popup_cancelar_impressora_html'
          document.getElementById('botao-salvar').onclick = function() {
              const formData = new FormData(document.getElementById('meu_form'));  // Coleta os dados do formulário
              if (validateForm(formData)) {  // Valida os dados antes de enviar
                  fechar_popup();
                  document.getElementById('meu_form').submit();
                  window.location.href = '/pesquisar_impressora';
              }
          };
          document.getElementById('botao-cancelar').onclick = function(event) {
              event.preventDefault();
              fechar_popup();
              window.location.href = '/pesquisar_impressora';
          };
          document.getElementById('popup-container-cancelar-display').style.display = 'flex'; 
      } else {
          console.error('Popup HTML is missing');
      }
  }).catch(error => console.error('Error loading pop-up:', error));
}

function fechar_popup() {
    document.getElementById('popup-container-cancelar-display').style.display = 'none'; // Apenas fecha o popup
}

function validateForm(formData) {
  const validationRules = {
    descricao: { regex: /^[a-zA-Z0-9 ]+$/, errorMessage: 'Descrição inválida. Apenas letras, números e espaços são permitidos.' },
    endereco: { regex: /^[0-9.]+$/, errorMessage: 'Endereço inválido. Apenas números e ponto (.) são permitidos.' },
    tipo_impressora: { regex: /^(REDE|LOCAL)$/, errorMessage: 'Tipo de impressão inválido. Escolha entre "REDE" ou "LOCAL".' },
    modelo_impressora: { regex: /^(BEMATECH|EPSON)$/, errorMessage: 'Modelo de impressora inválido. Escolha entre "BEMATECH" ou "EPSON".' },
    porta: { regex: /^[0-9]{1,5}$/, errorMessage: 'Porta inválida. Deve ser um número entre 0 e 65535.' },
    loja: { regex: /^(1|2)$/, errorMessage: 'Loja inválida. Selecione uma loja válida.' },
    utiliza_guilhotina: { regex: /^(True|False)$/, errorMessage: 'Valor inválido para utilizacao de guilhotina. Escolha "Sim" ou "Não".' }
  };

  let valid = true;
  formData.forEach((value, key) => {
    if (validationRules[key] && !validationRules[key].regex.test(value)) {
      displayErrors([{ field: key, message: validationRules[key].errorMessage }]);
      valid = false;
    }
  });

  return valid;
}

function displayErrors(errors) {
  errors.forEach(error => {
    const fieldElement = document.querySelector(`[name="${error.field}"]`);
    if (fieldElement) {
      // Clear existing error message
      const existingError = fieldElement.parentElement.querySelector('.error-message');
      if (existingError) existingError.remove();

      // Create and append new error message
      const errorSpan = document.createElement('span');
      errorSpan.textContent = error.message;
      errorSpan.classList.add('error-message');
      errorSpan.style.color = 'red';
      fieldElement.parentElement.insertBefore(errorSpan, fieldElement);
    }

    // Display general error message
    const generalErrorContainer = document.getElementById('general-error');
    if (generalErrorContainer) {
      generalErrorContainer.innerHTML = error.message;
      generalErrorContainer.style.display = 'block';
    }
  });
}

window.onload = function() {
  document.getElementById("meu_form").addEventListener("submit", function(event) {
    event.preventDefault();
    submeter_formulario();  // Submit the form manually via JavaScript
  });
};

document.addEventListener("DOMContentLoaded", function() {
  atualizarCampos();
  document.getElementById("tipo_impressora").addEventListener("change", atualizarCampos);
});

function atualizarCampos() {
  const tipoImpressao = document.getElementById("tipo_impressora").value;
  document.getElementById("rede-fields").style.display = tipoImpressao === "REDE" ? "block" : "none";
  document.getElementById("local-fields").style.display = tipoImpressao === "LOCAL" ? "block" : "none";
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
