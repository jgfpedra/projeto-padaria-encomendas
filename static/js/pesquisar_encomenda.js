function getSelectedEncomendaId() {
    const selectedEncomenda = document.querySelector('input[name="selected-encomenda"]:checked');
    return selectedEncomenda ? selectedEncomenda.value : null;
}

function loadSelected() {
    const encomendaId = getSelectedEncomendaId();
    if (encomendaId) {
        const row = document.querySelector(`input[value="${encomendaId}"]`).closest('tr'); // Find the corresponding row
        const creationDateCell = row.cells[4]; // Assuming Data Criação is in the 5th column
        const creationDate = creationDateCell.textContent; // Get the date text

        // Format the date to YYYY-MM-DD
        const formattedDate = new Date(creationDate).toISOString().split('T')[0]; 

        // Redirect to the desired URL
        window.location.href = `/encomenda/${formattedDate}/${encomendaId}`;
    } else {
        alert('Please select an encomenda to load.');
    }
}

function confirmDelete() {
    const encomendaId = getSelectedEncomendaId();

    if (encomendaId) {
        const confirmDelete = confirm('Tem certeza que deseja deletar este encomenda?');
        if (confirmDelete) {
            console.log(`Submitting delete request for encomenda ID: ${encomendaId}`);

            const formData = new FormData();
            formData.append('id', encomendaId);
            
            fetch('/delete_encomenda', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    window.location.reload();  // Reloads the page to reflect changes
                } else {
                    alert('Failed to delete the encomenda.'); // Handle error case
                }
            })
            .catch(error => console.error('Error during fetch:', error));
        }
    } else {
        alert('Nenhum encomenda selecionado para deletar.');
    }
}

