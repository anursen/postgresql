document.addEventListener('DOMContentLoaded', function() {
    // Load current settings
    fetch('/admin-settings')
        .then(response => response.json())
        .then(settings => {
            document.getElementById('question_time').value = settings.question_time;
            document.getElementById('question_count').value = settings.question_count;
            document.getElementById('exam_duration').value = settings.exam_duration;
            document.getElementById('passing_score').value = settings.passing_score;
            document.getElementById('max_attempts').value = settings.max_attempts;
            document.getElementById('shuffle_questions').checked = settings.shuffle_questions;
            document.getElementById('enable_notifications').checked = settings.enable_notifications;
        })
        .catch(error => console.error('Error loading settings:', error));

    // Handle form submission
    document.getElementById('admin-settings-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const settings = {
            question_time: parseInt(document.getElementById('question_time').value),
            question_count: parseInt(document.getElementById('question_count').value),
            exam_duration: parseInt(document.getElementById('exam_duration').value),
            passing_score: parseInt(document.getElementById('passing_score').value),
            max_attempts: parseInt(document.getElementById('max_attempts').value),
            shuffle_questions: document.getElementById('shuffle_questions').checked,
            enable_notifications: document.getElementById('enable_notifications').checked
        };

        fetch('/admin-settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => console.error('Error saving settings:', error));
    });
});
