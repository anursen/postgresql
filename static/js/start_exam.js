document.addEventListener("DOMContentLoaded", function() {
    // Load non-admin users
    fetch('/non-admin-users-data')
        .then(response => response.json())
        .then(data => {
            const userSelect = document.getElementById('user');
            data.forEach(user => {
                const option = document.createElement('option');
                option.value = user.id;
                option.textContent = `${user.name} ${user.surname}`;
                userSelect.appendChild(option);
            });
        });

    // Load sections
    fetch('/unique-sections')
        .then(response => response.json())
        .then(data => {
            const sectionSelect = document.getElementById('section');
            data.forEach(section => {
                const option = document.createElement('option');
                option.value = section;
                option.textContent = section;
                sectionSelect.appendChild(option);
            });
        });

    // Handle form submission
    document.getElementById('start-exam-form').addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        
        fetch('/start-exam', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const section = formData.get('section');
                const user = formData.get('user');
                window.location.href = `/exam/${data.exam_id}?section=${section}&user_id=${user}`;
            } else {
                alert(data.message || 'Failed to start exam');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while starting the exam');
        });
    });
});
