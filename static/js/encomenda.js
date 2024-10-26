document.addEventListener('DOMContentLoaded', function() {
    const observationCells = document.querySelectorAll('td.observation-cell');
    const itemRows = document.querySelectorAll('tr.selectable-row');
    const deleteForm = document.querySelector('.delete-form');
    const orderTypeRadios = document.querySelectorAll('input[name="orderType"]');
    const entregaDetails = document.getElementById('entregaDetails');

    orderTypeRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            entregaDetails.style.display = radio.value === 'entrega' ? 'block' : 'none';
        });
    });

    observationCells.forEach(cell => {
        cell.addEventListener('click', function() {
            // Check if the input already exists
            if (this.querySelector('input')) return;

            const observationText = this.querySelector('.observation-text');
            const currentObservation = observationText.textContent.trim();

            // Create an input element
            const input = document.createElement('input');
            input.type = 'text';
            input.value = currentObservation;

            // Replace the text with the input field
            this.replaceChild(input, observationText);
            input.focus();

            // Handle losing focus or pressing Enter
            input.addEventListener('blur', () => saveObservation(cell, input.value));
            input.addEventListener('keypress', function(event) {
                if (event.key === 'Enter') {
                    event.preventDefault(); // Prevent form submission if in a form
                    saveObservation(cell, input.value);
                }
            });
        });
    });

    itemRows.forEach(row => {
        row.addEventListener('click', function () {
            // Deselect any previously selected row
            const selectedRow = document.querySelector('.selected');
            if (selectedRow && selectedRow !== this) {
                selectedRow.classList.remove('selected');
            }

            // Populate the hidden input fields in the form
            const itensEncomendaId = this.dataset.itensEncomendaId;
            const idProduto = this.dataset.idProduto;
            const date = this.dataset.date;

            document.getElementById('delete-itens-encomenda-id').value = itensEncomendaId;
            document.getElementById('delete-product-id').value = idProduto;
            document.getElementById('delete-date').value = date;

            // Select the current row
            this.classList.toggle('selected');
        });
    });

    if(deleteForm != null){
      deleteForm.addEventListener('submit', function (event) {
          event.preventDefault(); // Stop the form submission

          const itensEncomendaId = document.getElementById('delete-itens-encomenda-id').value;
          const idProduto = document.getElementById('delete-product-id').value;
          const date = document.getElementById('delete-date').value;

          const confirmation = confirm('Do you want to delete this item?');
          if (confirmation) {
              deleteItem(itensEncomendaId, idProduto, date);
          }
      });
    }

    function deleteItem(itensEncomendaId, idProduto, date) {
        fetch('/delete_item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                itens_encomenda_id: itensEncomendaId,
                id_produto: idProduto,
                date: date
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok.');
            }
            return response.json();
        })
        .then(data => {
            // Remove the row from the DOM or hide it
            const row = document.querySelector(`tr[data-itens-encomenda-id="${itensEncomendaId}"][data-id-produto="${idProduto}"]`);
            if (row) {
                row.remove(); // Remove the row from the table
            }
        })
        .catch(error => {
            console.error('Error deleting item:', error);
        });
    }

    function saveObservation(cell, newObservation) {
        const itensEncomendaId = cell.dataset.itensEncomendaId;
        const idProduto = cell.dataset.idProduto;

        // Check if the new observation is empty
        if (!newObservation.trim()) {
            // If empty, send a request to delete the observation
            fetch(`/delete_observacao`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    itens_encomenda_id: itensEncomendaId,
                    id_produto: idProduto
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok.');
                }
                return response.json();
            })
            .then(data => {
                // Handle success response
                const span = document.createElement('span');
                span.classList.add('observation-text');
                span.textContent = ''; // Clear the observation text
                cell.replaceChild(span, cell.querySelector('input'));
            })
            .catch(error => {
                console.error('Error deleting observation:', error);
                // Optionally revert to original text if there's an error
                const span = document.createElement('span');
                span.classList.add('observation-text');
                span.textContent = cell.querySelector('input').value; // Revert to input value
                cell.replaceChild(span, cell.querySelector('input'));
            });
        } else {
            // If not empty, proceed to update the observation
            fetch('/update_observacao', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    itens_encomenda_id: itensEncomendaId,
                    id_produto: idProduto,
                    nova_observacao: newObservation
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok.');
                }
                return response.json();
            })
            .then(data => {
                // Handle success response
                const span = document.createElement('span');
                span.classList.add('observation-text');
                span.textContent = newObservation; // Update with the new observation
                cell.replaceChild(span, cell.querySelector('input'));
            })
            .catch(error => {
                // Revert to original text if there's an error
                const span = document.createElement('span');
                span.classList.add('observation-text');
                span.textContent = cell.querySelector('input').value; // Revert to input value
                cell.replaceChild(span, cell.querySelector('input'));
            });
        }
    }
});

function formatCellphone() {
    const input = document.getElementById('cellphone');
    let value = input.value.replace(/\D/g, ''); // Remove non-digit characters

    // Limit to 11 digits
    if (value.length > 11) {
        value = value.slice(0, 11);
    }

    // Format to (99)999999999 or (99)99999999
    if (value.length <= 11) {
        value = value.replace(/^(\d{2})(\d{0,9})$/, '($1)$2');
    }

    input.value = value;
}

function validateInput() {
    const input = document.getElementById('cellphone');
    const regex = /^\(\d{2}\)\d{8,9}$/;
    if (!regex.test(input.value)) {
        alert("Please enter a valid cellphone number in the format (99)999999999 or (99)99999999.");
        return false;
    }
    return true;
}
