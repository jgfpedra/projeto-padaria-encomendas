let phoneCounter = 0; // Counter for new phone input fields

function addPhoneInput() {
    phoneCounter++;
    const phoneContainer = document.getElementById('phone-container');
    const newPhoneRow = document.createElement('div');
    newPhoneRow.className = 'phone-row';
    newPhoneRow.innerHTML = `
	<label for="phone-${phoneCounter}" required>Telefone ${phoneCounter}:</label>
	<input type="text" name="telefones[]" id="phone-${phoneCounter}" placeholder="Digite o telefone">
    `;
    phoneContainer.appendChild(newPhoneRow);
}

function removePhoneInput() {
    const phoneContainer = document.getElementById('phone-container');
    if (phoneContainer.children.length > 0) {
	// Remove the last phone input row
	phoneContainer.removeChild(phoneContainer.lastChild);
	phoneCounter--;
    }
}
