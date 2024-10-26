
function getSelectedImpressoraId() {
    const selectedImpressora = document.querySelector('input[name="selected-impressora"]:checked');
    return selectedImpressora ? selectedImpressora.value : null;
}

function redirectToEdit() {
    const impressoraId = getSelectedImpressoraId();
    if (impressoraId) {
        window.location.href = `impressora_cadastrar/${impressoraId}`;
    } else {
        alert('Nenhum impressora selecionado para editar.');
    }
}

function confirmDelete() {
  const impressoraId = getSelectedImpressoraId();

  if (impressoraId) {
    const confirmDelete = confirm('Tem certeza que deseja deletar este impressora?');
    if (confirmDelete) {
      console.log(`Submitting delete request for client ID: ${impressoraId}`);

      const formData = new FormData();
      formData.append('id', impressoraId);
      
      fetch('/delete_impressora', {
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
    alert('Nenhum impressora selecionado para deletar.');
  }
}
