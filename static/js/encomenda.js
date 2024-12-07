document.addEventListener('DOMContentLoaded', function() {
    const observationCells = document.querySelectorAll('td.observation-cell');
    const itemRows = document.querySelectorAll('tr.selectable-row');
    const deleteForm = document.querySelector('.delete-form');
    const entregaDetails = document.getElementById('entregaDetails');
    const quantityInput = document.getElementById('quantity');
    const encomendaStatus = document.getElementById('encomenda-status').getAttribute('data-status');

    if (quantityInput) {
        quantityInput.addEventListener('input', function(e) {
            let value = e.target.value;
            value = value.replace(',', '.');
            let numericValue = parseFloat(value);
            if (!isNaN(numericValue)) {
                if (numericValue > 9999) {
                    value = '9999';
                } else if (value.includes('.') && value.split('.')[1].length > 2) {
                    value = value.substring(0, value.indexOf('.') + 3);
                }
            } else {
                value = '';
            }
            e.target.value = value;
        });
    }

    observationCells.forEach(cell => {
        if (encomendaStatus === 'Finalizado') {
            console.log("a");
            cell.style.pointerEvents = 'none';
            cell.classList.add('disabled');
            return;
        }
        cell.addEventListener('click', function() {
            if (this.querySelector('input')) return;
            const observationText = this.querySelector('.observation-text');
            const currentObservation = observationText.textContent.trim();
            const inputHtml = `<input type="text" value="${currentObservation}">`;
            this.innerHTML = inputHtml;
            const input = this.querySelector('input');
            input.focus();
            input.addEventListener('blur', () => saveObservation(cell, input.value));
            input.addEventListener('keypress', function(event) {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    saveObservation(cell, input.value);
                }
            });
        });
    });

    itemRows.forEach(row => {
        row.addEventListener('click', function () {
            const selectedRow = document.querySelector('.selected');
            if (selectedRow && selectedRow !== this) {
                selectedRow.classList.remove('selected');
            }
            const itensEncomendaId = this.dataset.itensEncomendaId;
            const idProduto = this.dataset.idProduto;
            const date = this.dataset.date;
            document.getElementById('delete-itens-encomenda-id').value = itensEncomendaId;
            document.getElementById('delete-product-id').value = idProduto;
            document.getElementById('delete-date').value = date;
            this.classList.toggle('selected');
        });
    });

    if(deleteForm != null){
      deleteForm.addEventListener('submit', function (event) {
          event.preventDefault();
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
            const row = document.querySelector(`tr[data-itens-encomenda-id="${itensEncomendaId}"][data-id-produto="${idProduto}"]`);
            if (row) {
                row.remove();
            }
        })
        .catch(error => {
            console.error('Error deleting item:', error);
        });
    }
    function saveObservation(cell, newObservation) {
        const itensEncomendaId = cell.dataset.itensEncomendaId;
        const idProduto = cell.dataset.idProduto;
        if (!newObservation.trim()) {
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
                const span = document.createElement('span');
                span.classList.add('observation-text');
                span.textContent = '';
                cell.replaceChild(span, cell.querySelector('input'));
            })
            .catch(error => {
                console.error('Error deleting observation:', error);
                const span = document.createElement('span');
                span.classList.add('observation-text');
                span.textContent = cell.querySelector('input').value;
                cell.replaceChild(span, cell.querySelector('input'));
            });
        } else {
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
                const span = document.createElement('span');
                span.classList.add('observation-text');
                span.textContent = newObservation; // Update with the new observation
                cell.replaceChild(span, cell.querySelector('input'));
            })
            .catch(error => {
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
    let value = input.value.replace(/\D/g, '');
    if (value.length > 11) {
        value = value.slice(0, 11);
    }
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
