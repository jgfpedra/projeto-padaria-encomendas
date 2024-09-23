function getSelectedencomendaId() {
    const selectedencomenda = document.querySelector('input[name="selected-encomenda"]:checked');
    return selectedencomenda ? selectedEncomenda.value : null;
}

function redirectToEdit() {
    const encomendaId = getSelectedEncomendaId();
    if (encomendaId) {
        window.location.href = `encomenda_cadastrar/${encomendaId}`;
    } else {
        alert('Nenhum encomenda selecionado para editar.');
    }
}

function confirmDelete() {
  const encomendaId = getSelectedEncomendaId();

  if (encomendaId) {
    const confirmDelete = confirm('Tem certeza que deseja deletar este encomenda?');
    if (confirmDelete) {
      console.log(`Submitting delete request for client ID: ${encomendaId}`);

      const formData = new FormData();
      formData.append('id', encomendaId);
      
      fetch('/delete_encomenda', {
        method: 'POST',
        body: formData
      })
      .then(response => {
        if (response.ok) {
          window.location.reload();  // Reloads the page to reflect changes
        }
      })
      .catch(error => console.error('Error during fetch:', error));
    }
  } else {
    alert('Nenhum encomenda selecionado para deletar.');
  }
}
