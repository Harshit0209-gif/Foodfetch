// JavaScript code for admin panel actions
function acceptOrder(orderId) {
    fetch(`/accept_order/${orderId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // Include CSRF token
        },
        body: JSON.stringify({})  // Empty body since it's a POST request
    })
    .then(response => response.text())
    .then(data => {
        console.log('Response:', data);  // Log the response from the backend
        // Handle the response as needed
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function rejectOrder(orderId) {
    fetch(`/reject_order/${orderId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // Include CSRF token
        },
        body: JSON.stringify({})  // Empty body since it's a POST request
    })
    .then(response => response.text())
    .then(data => {
        console.log('Response:', data);  // Log the response from the backend
        // Handle the response as needed
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
