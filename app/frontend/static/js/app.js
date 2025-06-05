// Глобальные переменные для хранения состояния
let currentTaskId = null;
let transcriptionComplete = false;
let summarizationComplete = false;

// Элементы DOM
const uploadForm = document.getElementById('upload-form');
const transcriptionStatus = document.getElementById('transcription-status');
const summarizationSection = document.getElementById('summarization-section');
const summarizationStatus = document.getElementById('summarization-status');

// Табы
const tabTranscript = document.getElementById('tab-transcript');
const tabSummary = document.getElementById('tab-summary');
const tabChat = document.getElementById('tab-chat');

const contentTranscript = document.getElementById('content-transcript');
const contentSummary = document.getElementById('content-summary');
const contentChat = document.getElementById('content-chat');

// Содержимое
const transcriptContent = document.getElementById('transcript-content');
const summaryContent = document.getElementById('summary-content');
const chatMessages = document.getElementById('chat-messages');

// Кнопки и ввод
const uploadButton = document.getElementById('upload-button');
const summarizeButton = document.getElementById('summarize-button');
const chatInput = document.getElementById('chat-input');
const chatButton = document.getElementById('chat-button');

// Модели
const modelSize = document.getElementById('model-size');
const summaryModel = document.getElementById('summary-model');
const chatModel = document.getElementById('chat-model');

// Прогресс-бар
const progressBar = document.getElementById('progress-bar');

// Переключение табов
tabTranscript.addEventListener('click', () => switchTab('transcript'));
tabSummary.addEventListener('click', () => switchTab('summary'));
tabChat.addEventListener('click', () => switchTab('chat'));

function switchTab(tabName) {
    // Сброс всех табов
    [tabTranscript, tabSummary, tabChat].forEach(tab => {
        tab.classList.remove('text-blue-600', 'border-b-2', 'border-blue-600');
        tab.classList.add('text-gray-500');
    });
    
    // Сброс содержимого
    [contentTranscript, contentSummary, contentChat].forEach(content => {
        content.classList.add('hidden');
    });
    
    // Активация выбранного таба
    if (tabName === 'transcript') {
        tabTranscript.classList.add('text-blue-600', 'border-b-2', 'border-blue-600');
        tabTranscript.classList.remove('text-gray-500');
        contentTranscript.classList.remove('hidden');
    } else if (tabName === 'summary') {
        tabSummary.classList.add('text-blue-600', 'border-b-2', 'border-blue-600');
        tabSummary.classList.remove('text-gray-500');
        contentSummary.classList.remove('hidden');
    } else if (tabName === 'chat') {
        tabChat.classList.add('text-blue-600', 'border-b-2', 'border-blue-600');
        tabChat.classList.remove('text-gray-500');
        contentChat.classList.remove('hidden');
    }
}

// Функция для загрузки видео
uploadButton.addEventListener('click', async () => {
    const videoFileInput = document.getElementById('video-file');
    const file = videoFileInput.files[0];
    
    if (!file) {
        alert('Пожалуйста, выберите файл');
        return;
    }
    
    uploadForm.classList.add('hidden');
    transcriptionStatus.classList.remove('hidden');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('model_size', modelSize.value);
    
    try {
        const response = await fetch('/api/transcribe/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        currentTaskId = data.task_id;
        
        // Запуск проверки статуса
        checkTranscriptionStatus();
    } catch (error) {
        console.error('Ошибка при загрузке:', error);
        alert('Произошла ошибка при загрузке видео.');
        
        uploadForm.classList.remove('hidden');
        transcriptionStatus.classList.add('hidden');
    }
});

// Функция для проверки статуса транскрибации
async function checkTranscriptionStatus() {
    if (!currentTaskId) return;
    
    try {
        const response = await fetch(`/api/transcribe/status/${currentTaskId}`);
        const data = await response.json();
        
        if (data.status === 'completed') {
            // Транскрибация завершена
            transcriptionComplete = true;
            transcriptionStatus.classList.add('hidden');
            summarizationSection.classList.remove('hidden');
            
            // Загрузка результата транскрибации
            loadTranscription();
        } else {
            // Продолжаем проверять
            updateProgressBar();
            setTimeout(checkTranscriptionStatus, 5000);
        }
    } catch (error) {
        console.error('Ошибка при проверке статуса:', error);
        setTimeout(checkTranscriptionStatus, 5000);
    }
}

// Функция для загрузки транскрипции
async function loadTranscription() {
    if (!currentTaskId) return;
    
    try {
        const response = await fetch(`/api/transcribe/result/${currentTaskId}`);
        const data = await response.json();
        
        transcriptContent.innerHTML = formatTranscript(data.transcript);
    } catch (error) {
        console.error('Ошибка при загрузке транскрипции:', error);
        transcriptContent.innerHTML = '<p class="text-red-500">Ошибка при загрузке транскрипции</p>';
    }
}

// Форматирование транскрипции
function formatTranscript(transcript) {
    return transcript.replace(/\[(\d{2}:\d{2}:\d{2}) - (\d{2}:\d{2}:\d{2})\] (.*?)(?=\[|$)/g, 
        '<div class="mb-2"><span class="text-xs text-gray-500">[$1 - $2]</span><br>$3</div>');
}

// Функция для имитации прогресса
function updateProgressBar() {
    const currentWidth = parseInt(progressBar.style.width) || 0;
    const newWidth = Math.min(currentWidth + Math.random() * 10, 90);
    progressBar.style.width = newWidth + '%';
}

// Функция для суммаризации
summarizeButton.addEventListener('click', async () => {
    if (!currentTaskId || !transcriptionComplete) return;
    
    summarizeButton.disabled = true;
    summarizationStatus.classList.remove('hidden');
    
    try {
        const response = await fetch(`/api/summarize/${currentTaskId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model_name: summaryModel.value
            })
        });
        
        const data = await response.json();
        
        // Запуск проверки статуса
        checkSummarizationStatus();
    } catch (error) {
        console.error('Ошибка при запуске суммаризации:', error);
        alert('Произошла ошибка при запуске суммаризации.');
        
        summarizeButton.disabled = false;
        summarizationStatus.classList.add('hidden');
    }
});

// Функция для проверки статуса суммаризации
async function checkSummarizationStatus() {
    if (!currentTaskId) return;
    
    try {
        const response = await fetch(`/api/summarize/status/${currentTaskId}`);
        const data = await response.json();
        
        if (data.status === 'completed') {
            // Суммаризация завершена
            summarizationComplete = true;
            summarizeButton.disabled = false;
            summarizationStatus.classList.add('hidden');
            
            // Загрузка результата суммаризации
            loadSummary();
            
            // Активация чата
            enableChat();
            
            // Переключение на вкладку резюме
            switchTab('summary');
        } else {
            // Продолжаем проверять
            setTimeout(checkSummarizationStatus, 5000);
        }
    } catch (error) {
        console.error('Ошибка при проверке статуса суммаризации:', error);
        setTimeout(checkSummarizationStatus, 5000);
    }
}

// Функция для загрузки суммаризации
async function loadSummary() {
    if (!currentTaskId) return;
    
    try {
        const response = await fetch(`/api/summarize/result/${currentTaskId}`);
        const data = await response.json();
        
        // Форматирование и отображение резюме
        summaryContent.innerHTML = formatSummary(data);
    } catch (error) {
        console.error('Ошибка при загрузке резюме:', error);
        summaryContent.innerHTML = '<p class="text-red-500">Ошибка при загрузке резюме</p>';
    }
}

// Форматирование резюме
function formatSummary(summary) {
    let html = `<div class="mb-6">
        <h3 class="text-xl font-bold mb-3">Общая суть встречи</h3>
        <p>${summary.summary}</p>
    </div>`;
    
    if (summary.key_points && summary.key_points.length > 0) {
        html += `<div class="mb-6">
            <h3 class="text-lg font-bold mb-3">Ключевые моменты</h3>
            <ul class="list-disc list-inside">
                ${summary.key_points.map(point => `<li class="mb-1">${point}</li>`).join('')}
            </ul>
        </div>`;
    }
    
    if (summary.action_items && summary.action_items.length > 0) {
        html += `<div class="mb-6">
            <h3 class="text-lg font-bold mb-3">Задачи</h3>
            <ul class="list-disc list-inside">
                ${summary.action_items.map(item => `<li class="mb-1">${item}</li>`).join('')}
            </ul>
        </div>`;
    }
    
    if (summary.participants && summary.participants.length > 0) {
        html += `<div class="mb-6">
            <h3 class="text-lg font-bold mb-3">Участники</h3>
            <ul class="list-disc list-inside">
                ${summary.participants.map(participant => `<li>${participant}</li>`).join('')}
            </ul>
        </div>`;
    }
    
    return html;
}

// Функция для активации чата
function enableChat() {
    chatInput.disabled = false;
    chatButton.disabled = false;
    
    // Добавление сообщения в чат
    const message = document.createElement('div');
    message.className = 'assistant-message chat-message';
    message.textContent = 'Транскрипция и суммаризация завершены. Теперь вы можете задавать вопросы о встрече!';
    chatMessages.appendChild(message);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Функция для отправки сообщения в чат
chatButton.addEventListener('click', sendChatMessage);
chatInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
});

async function sendChatMessage() {
    if (!currentTaskId || !transcriptionComplete || chatInput.disabled) return;
    
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Очистка поля ввода
    chatInput.value = '';
    
    // Добавление сообщения пользователя
    const userMessageElement = document.createElement('div');
    userMessageElement.className = 'user-message chat-message';
    userMessageElement.textContent = message;
    chatMessages.appendChild(userMessageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Добавление индикатора загрузки
    const loadingElement = document.createElement('div');
    loadingElement.className = 'flex items-center assistant-message chat-message';
    loadingElement.innerHTML = '<div class="loading-spinner mr-2"></div><span>Думаю...</span>';
    chatMessages.appendChild(loadingElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Отключение ввода на время обработки
    chatInput.disabled = true;
    chatButton.disabled = true;
    
    try {
        const response = await fetch('/api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                task_id: currentTaskId,
                messages: [
                    { role: 'user', content: message }
                ],
                model_name: chatModel.value
            })
        });
        
        const data = await response.json();
        
        // Удаление индикатора загрузки
        chatMessages.removeChild(loadingElement);
        
        // Добавление ответа ассистента
        const assistantMessageElement = document.createElement('div');
        assistantMessageElement.className = 'assistant-message chat-message';
        assistantMessageElement.textContent = data.response;
        chatMessages.appendChild(assistantMessageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    } catch (error) {
        console.error('Ошибка при отправке сообщения:', error);
        
        // Удаление индикатора загрузки
        chatMessages.removeChild(loadingElement);
        
        // Добавление сообщения об ошибке
        const errorMessageElement = document.createElement('div');
        errorMessageElement.className = 'assistant-message chat-message';
        errorMessageElement.textContent = 'Произошла ошибка при обработке вашего запроса. Попробуйте еще раз.';
        chatMessages.appendChild(errorMessageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    } finally {
        // Включение ввода
        chatInput.disabled = false;
        chatButton.disabled = false;
        chatInput.focus();
    }
} 