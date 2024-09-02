function getSelectedClientId() {
  const selectedRadio = document.querySelector('input[name="selected-client"]:checked');
  return selectedRadio ? selectedRadio.value : null;
}

function redirectToEdit() {
  const clientId = getSelectedClientId();
  if (clientId) {
    console.log(`Redirecting to edit page with client ID: ${clientId}`);
    window.location.href = `${}${clientId}`;
  } else {
    alert('Nenhum cliente selecionado para editar.');
  }
}

function confirmDelete() {
  const clientId = getSelectedClientId();
  if (clientId) {
    const confirmDelete = confirm('Tem certeza que deseja deletar este cliente?');
    if (confirmDelete) {
      console.log(`Submitting delete request for client ID: ${clientId}`);
      // Create a new form to submit the delete request
      const deleteForm = document.createElement('form');
      deleteForm.method = 'POST';
      deleteForm.action = deleteUrl;

      const idInput = document.createElement('input');
      idInput.type = 'hidden';
      idInput.name = 'id';
      idInput.value = clientId;
      deleteForm.appendChild(idInput);

      document.body.appendChild(deleteForm);
      deleteForm.submit();
    }
  } else {
    alert('Nenhum cliente selecionado para deletar.');
  }
}
