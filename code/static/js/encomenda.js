document.addEventListener('DOMContentLoaded', function() {
    const observationCells = document.querySelectorAll('td.observation-cell');

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

    function saveObservation(cell, newObservation) {
        const itensEncomendaId = cell.dataset.itensEncomendaId;
        const idProduto = cell.dataset.idProduto;
        console.log(itensEncomendaId, idProduto);

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
