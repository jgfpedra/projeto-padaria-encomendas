function loadPopup() {
  fetch('/lancamento_historico_encomendas')
    .then(response => response.json())
    .then(data => {
      if (data.popup_html) {
        document.getElementById('popup-container-historico').innerHTML = data.popup_html;
        document.getElementById('popup').style.display = 'flex'; // Show the pop-up
      } else {
        console.error('Popup HTML is missing');
      }
    })
    .catch(error => console.error('Error loading pop-up:', error));
}

function showPopupHistorico() {
  loadPopup();
}

function closePopup() {
  const popup = document.getElementById('popup');
  if (popup) {
    popup.style.display = 'none'; // Hide the pop-up
  }
}
