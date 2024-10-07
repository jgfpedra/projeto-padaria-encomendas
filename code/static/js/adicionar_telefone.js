document.addEventListener("DOMContentLoaded", function() {
    let phoneCounter = 1; // Initialize the counter

    function addPhoneInput() {
        phoneCounter++;
        const phoneContainer = document.getElementById('phone-container');
        const newPhoneRow = document.createElement('div');
        newPhoneRow.className = 'phone-row';
        newPhoneRow.innerHTML = `
            <label for="phone-${phoneCounter}" required>Telefone ${phoneCounter}:</label>
            <input type="text" name="telefones" id="phone-${phoneCounter}" placeholder="Digite o telefone" 
                   pattern="^\\(\\d{2}\\)\\d{8,9}$" title="Format: (99)999999999 or (99)99999999" 
                   oninput="formatCellphone(this)" maxlength="13" required>
        `;
        phoneContainer.insertBefore(newPhoneRow, phoneContainer.lastElementChild); // Add above buttons
        updateRemoveButtonState();
    }

    function removePhoneInput() {
        const phoneContainer = document.getElementById('phone-container');
        
        // Get all phone rows
        const phoneRows = phoneContainer.getElementsByClassName('phone-row');
        
        if (phoneRows.length > 1) { // Check if there's more than one phone input
            phoneContainer.removeChild(phoneRows[phoneRows.length - 1]); // Remove last phone input
            phoneCounter--;
            updateRemoveButtonState();
        } else {
            alert('Você deve manter pelo menos um campo de telefone.');
        }
    }

    function updateRemoveButtonState() {
        const removeButton = document.querySelector('button[onclick="removePhoneInput()"]');
        const phoneContainer = document.getElementById('phone-container');
        removeButton.disabled = phoneContainer.children.length <= 2; // Disable if only one input left
    }

    function formatCellphone(input) {
        let value = input.value.replace(/\D/g, ''); // Remove non-digit characters
        if (value.length <= 11) {
            value = value.replace(/^(\d{2})(\d{0,9})$/, '($1)$2');
        } else {
            value = value.replace(/^(\d{2})(\d{9})(\d{0,1})$/, '($1)$2$3');
        }
        input.value = value;
    }

    // Attach functions to global scope
    window.addPhoneInput = addPhoneInput;
    window.removePhoneInput = removePhoneInput;
    window.formatCellphone = formatCellphone;

    // Initial button state update
    updateRemoveButtonState();
});
