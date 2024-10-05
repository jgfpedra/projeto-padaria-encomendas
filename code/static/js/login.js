document.addEventListener('DOMContentLoaded', function() {
    // Handle login form submission
    document.getElementById('login-form').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        fetch('/login', {
            method: 'POST', // Use POST method
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password }) // Send JSON payload
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Redirect to home page on successful login
                window.location.href = '/'; 
            } else {
                // Show error message on login failure
                alert(data.message);
            }
        })
        .catch(error => console.error('Error during login:', error));
    });
});
