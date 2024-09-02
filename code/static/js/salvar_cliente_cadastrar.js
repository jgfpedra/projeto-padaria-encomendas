function loadPopupSalvar() {
  fetch('/salvar_cliente_cadastrar')
    .then(response => response.json())
    .then(data => {
      if (data.popup_html) {
        document.getElementById('popup-container-salvar').innerHTML = data.popup_html;
        document.getElementById('popup-container-salvar-display').style.display = 'flex'; // Show the pop-up
      } else {
        console.error('Popup HTML is missing');
      }
    })
    .catch(error => console.error('Error loading pop-up:', error));
}

function showPopupSalvar() {
        loadPopupSalvar();
}

function closePopupSalvar() {
	document.getElementById('popup-container-salvar-display').style.display = 'none';
}

function submitFormSalvar() {
	document.getElementById('meuForm').addEventListener('submit', function(event) {
	  const nome = document.getElementById('nome').value;
	  const numero = document.getElementById('numero').value;

	  // Example custom validation
	  if (nome.length < 2) {
	    alert('Nome must be at least 2 characters long.');
	    event.preventDefault(); // Prevent form submission
	  }

	  if (!/^\d+$/.test(numero)) {
	    alert('Numero must be a valid number.');
	    event.preventDefault(); // Prevent form submission
	  }
		document.querySelector('input[name="form_action"]').value = 'submit'; // Set the hidden field value
		closePopupSalvar();
		document.getElementById('meuForm').submit();
	});
}

function cancelForm() {
	document.querySelector('input[name="form_action"]').value = 'cancel'; // Set the hidden field value
	document.getElementById('meuForm').submit(); // Submit the form to handle cancellation
}
