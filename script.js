const uploadButton = document.getElementById('uploadButton');
const fileInput = document.getElementById('fileInput');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');
const uploadedFilesList = document.getElementById('uploadedFilesList');
const sidebar = document.getElementById('sidebar');
const toggleSidebar = document.getElementById('toggleSidebar');

let uploadedFiles = [];
let contextText = '';

uploadButton.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', () => {
    const formData = new FormData();
    Array.from(fileInput.files).forEach(file => {
        formData.append('files[]', file);
    });

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        contextText = data.context_text;
        Array.from(fileInput.files).forEach(file => {
            if (!uploadedFiles.includes(file.name)) {
                uploadedFiles.push(file.name);
                updateUploadedFilesList();
            }
        });
    })
    .catch(error => console.error('Error uploading files:', error));
});

sendButton.addEventListener('click', () => {
    const message = userInput.value.trim();
    if (message) {
        displayMessage('user', message);

        fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: message, context_text: contextText })
        })
        .then(response => response.json())
        .then(data => {
            displayMessage('bot', data.response);
        })
        .catch(error => console.error('Error sending message:', error));

        userInput.value = '';
    }
});

function displayMessage(sender, message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ' + sender;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
}

function updateUploadedFilesList() {
    uploadedFilesList.innerHTML = '';
    uploadedFiles.forEach(filename => {
        const listItem = document.createElement('li');
        listItem.textContent = filename;
        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'X';
        deleteButton.classList.add('delete-button');
        deleteButton.addEventListener('click', () => {
            const index = uploadedFiles.indexOf(filename);
            if (index > -1) {
                uploadedFiles.splice(index, 1);
                updateUploadedFilesList();
            }
        });
        listItem.appendChild(deleteButton);
        uploadedFilesList.appendChild(listItem);
    });
}

toggleSidebar.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
    if (sidebar.classList.contains('collapsed')) {
        toggleSidebar.textContent = 'Expand Sidebar';
    } else {
        toggleSidebar.textContent = 'Collapse Sidebar';
    }
});
