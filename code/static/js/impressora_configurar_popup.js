function loadPopupConfigurar() {
  fetch('/impressora_configurar_popup')
    .then(response => response.json())
    .then(data => {
      if (data.popup_html) {
        document.getElementById('popup-container-impressora').innerHTML = data.popup_html;

        // If the popup HTML contains the printer select element,
        // populate it with the printer options received from the server.
        const printerSelect = document.getElementById('printerSelect');
        if (printerSelect) {
          // Assuming `data.printer_options` is passed along with `popup_html`
          data.printer_options.forEach(printer => {
            const option = document.createElement('option');
            option.value = printer.id;
            option.textContent = printer.nome;
            printerSelect.appendChild(option);
          });
        }

        document.getElementById('popup').style.display = 'flex'; // Show the pop-up
      } else {
        console.error('Popup HTML is missing');
      }
    })
    .catch(error => console.error('Error loading pop-up:', error));
}

function showPopupConfigurar() {
  loadPopupConfigurar();
}

function closePopupConfigurar() {
  const popup = document.getElementById('popup');
  if (popup) {
    popup.style.display = 'none'; // Hide the pop-up
  }
}

// Submit event for the printer form
document.addEventListener('submit', function(event) {
  if (event.target.id === 'printerForm') {
    event.preventDefault();
    const selectedPrinter = document.getElementById('printerSelect').value;

    // Make an AJAX POST request to configure the printer
    fetch('/configurar_impressora', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({ id_impressora: selectedPrinter })
    })
    .then(response => response.json())
    .then(data => {
      alert('Order finalized with printer ID: ' + selectedPrinter);
      closePopupConfigurar(); // Close the popup after submission
    })
    .catch(error => console.error('Error finalizing order:', error));
  }
});
