// Function to fetch user data from the server
async function fetchUserData() {
    try {
        const response = await fetch('/users-data');
        const data = await response.json();
        displayUsers(data);
    } catch (error) {
        console.error('Error fetching user data:', error);
    }
}

// Function to display user data on the page
function displayUsers(users) {
    const userContainer = document.getElementById('user-container');
    userContainer.innerHTML = '';

    users.forEach(user => {
        const userElement = document.createElement('div');
        userElement.className = 'user';
        userElement.innerHTML = `
            <h3>${user.name} ${user.surname}</h3>
            <p>Email: ${user.email}</p>
            <p>Teacher: ${user.teacher}</p>
            <p>Admin: ${user.admin}</p>
        `;
        userContainer.appendChild(userElement);
    });
}

// Fetch and display users when the page loads
document.addEventListener('DOMContentLoaded', fetchUserData);