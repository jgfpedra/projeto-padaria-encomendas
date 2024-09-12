document.addEventListener('DOMContentLoaded', function() {
    const rows = document.querySelectorAll('tr.selectable-row');

    rows.forEach(row => {
        row.addEventListener('click', function() {
            // Remove the selected class from all rows
            rows.forEach(r => r.classList.remove('selected'));

            // Add the selected class to the clicked row
            this.classList.add('selected');

            // Check the radio button associated with this row
            const radio = this.querySelector('input.item-radio');
            if (radio) {
                radio.checked = true;
            }
        });
    });
});
