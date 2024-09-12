function addPhoneInput() {
    phoneCounter++;
    const phoneContainer = document.getElementById('phone-container');
    const newPhoneRow = document.createElement('div');
    newPhoneRow.className = 'phone-row';
    newPhoneRow.innerHTML = `
        <label for="phone-${phoneCounter}" required>Telefone ${phoneCounter}:</label>
        <input type="text" name="telefones" id="phone-${phoneCounter}" placeholder="Digite o telefone">
    `;
    phoneContainer.appendChild(newPhoneRow);
    updateRemoveButtonState();
}

function removePhoneInput() {
    const phoneContainer = document.getElementById('phone-container');
    // Check if there is more than one phone input row
    if (phoneContainer.children.length > 1) {
        // Remove the last phone input row
        phoneContainer.removeChild(phoneContainer.lastChild);
        phoneCounter--;
        updateRemoveButtonState();
    } else {
        // If there's only one phone input row, show a message
        alert('Você deve manter pelo menos um campo de telefone.');
    }
}

function updateRemoveButtonState() {
    const removeButton = document.querySelector('button[onclick="removePhoneInput()"]');
    const phoneContainer = document.getElementById('phone-container');
    removeButton.disabled = phoneContainer.children.length <= 1;
}

// Initial button state update
updateRemoveButtonState();
