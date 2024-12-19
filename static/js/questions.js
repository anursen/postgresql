document.addEventListener("DOMContentLoaded", () => {
    fetch('/questions-data')
        .then(response => response.json())
        .then(data => {
            const questionsList = document.getElementById('questions-list');
            data.forEach(({ id, type, text, answer, score, section }) => {
                const questionItem = document.createElement('div');
                questionItem.id = `question-${id}`;
                questionItem.innerHTML = `
                    Type: ${type}, Text: ${text}, Answer: ${answer}, Score: ${score}, Section: ${section}
                    <button onclick="deleteQuestion(${id})">Delete</button>
                `;
                questionsList.appendChild(questionItem);
            });
        })
        .catch(console.error);

    document.getElementById('question-form').addEventListener('submit', (event) => {
        event.preventDefault();
        const formData = new FormData(event.target);
        const questionData = Object.fromEntries(formData.entries());
        fetch('/questions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(questionData),
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            location.reload();
        })
        .catch(console.error);
    });
});

function deleteQuestion(id) {
    fetch(`/questions/${id}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            document.getElementById(`question-${id}`).remove();
        })
        .catch(console.error);
}
