function loadPopupSalvar() {
  fetch('/salvar_impressora_cadastrar')
    .then(response => response.json())
    .then(data => {
      if (data.popup_html) {
        document.getElementById('popup-container-salvar').innerHTML = data.popup_html;

        // Attach the event listener to the save button
        document.getElementById('saveButton').onclick = function() {
          // Close the popup
          closePopup();

          // Submit the form directly
          document.getElementById('meuForm').submit();
        };

        document.getElementById('cancelButton').onclick = function(event) {
          event.preventDefault(); // Prevent form submission
          
          // Close the popup
          closePopup();

          // Redirect to the pesquisar_impressora page
          window.location.href = '/pesquisar_impressora';
        };

        // Show the pop-up
        document.getElementById('popup-container-salvar-display').style.display = 'flex'; 
      } else {
        console.error('Popup HTML is missing');
      }
    })
    .catch(error => console.error('Error loading pop-up:', error));
}

function closePopup() {
  document.getElementById('popup-container-salvar-display').style.display = 'none'; // Just close the popup
}
