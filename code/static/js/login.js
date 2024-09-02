document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('login-form').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        fetch('/login', {
            method: 'POST', // Ensure POST method is used
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password }) // Ensure JSON is sent
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/'; // Redirect on success
            } else {
                alert(data.message); // Show error message
            }
        })
        .catch(error => console.error('Error:', error));
    });
});
