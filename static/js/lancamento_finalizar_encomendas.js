function loadPopupFinalizar() {
    fetch('/lancamento_finalizar_encomendas')
    .then(response => response.json())
    .then(data => {
        if (data.popup_html_finalizar) {
            document.getElementById('popup-content-lancamento-finalizar').innerHTML = data.popup_html_finalizar;
            document.getElementById('popup-content-lancamento-finalizar-display').style.display = 'flex';
        } else {
            console.error('Popup HTML is missing');
        }
    })
    .catch(error => console.error('Error loading pop-up:', error));
}

function closePopupFinalizar() {
  const popup = document.getElementById('popup-content-lancamento-finalizar-display');
  if (popup) {
    popup.style.display = 'none'; // Hide the pop-up
  }
}
