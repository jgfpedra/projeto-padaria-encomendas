
function getSelectedClientId() {
    const selectedClient = document.querySelector('input[name="selected-client"]:checked');
    return selectedClient ? selectedClient.value : null;
}

function redirectToEdit() {
    const clientId = getSelectedClientId();
    if (clientId) {
        // Construct the URL with the client ID
        window.location.href = `cliente_cadastrar/${clientId}`;
    } else {
        alert('Nenhum cliente selecionado para editar.');
    }
}

function confirmDelete() {
  const clientId = getSelectedClientId();  // Ensure this function returns a valid client ID

  if (clientId) {
    const confirmDelete = confirm('Tem certeza que deseja deletar este cliente?');
    if (confirmDelete) {
      const formData = new FormData();
      formData.append('id', clientId);
      
      fetch('/delete_cliente', {
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
    alert('Nenhum cliente selecionado para deletar.');
  }
}
