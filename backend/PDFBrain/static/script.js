// PDF Knowledge Bot Frontend JavaScript

class PDFKnowledgeBot {
    constructor() {
        this.baseUrl = window.location.origin;
        this.currentSessionId = null;
        this.currentDocumentId = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDocuments();
        this.loadQuizzes();
        this.populateDocumentSelects();
    }

    setupEventListeners() {
        // Upload form
        document.getElementById('uploadForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.uploadPDF();
        });

        // Chat form
        document.getElementById('sendChatBtn').addEventListener('click', () => {
            this.sendChatMessage();
        });

        document.getElementById('chatInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendChatMessage();
            }
        });

        // Chat document selection
        document.getElementById('chatDocumentSelect').addEventListener('change', (e) => {
            this.selectChatDocument(e.target.value);
        });

        // Quiz generation form
        document.getElementById('quizGenerationForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateQuiz();
        });

        // Tab change events
        document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                const target = e.target.getAttribute('data-bs-target');
                if (target === '#documents-pane') {
                    this.loadDocuments();
                } else if (target === '#quiz-pane') {
                    this.loadQuizzes();
                }
            });
        });
    }

    // Utility methods
    showAlert(message, type = 'info', timeout = 5000) {
        const alertContainer = document.getElementById('alertContainer');
        const alertId = 'alert-' + Date.now();
        
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" id="${alertId}" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        alertContainer.insertAdjacentHTML('beforeend', alertHtml);
        
        if (timeout > 0) {
            setTimeout(() => {
                const alert = document.getElementById(alertId);
                if (alert) {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }
            }, timeout);
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleString();
    }

    // PDF Upload
    async uploadPDF() {
        const form = document.getElementById('uploadForm');
        const fileInput = document.getElementById('pdfFile');
        const uploadBtn = document.getElementById('uploadBtn');
        const uploadProgress = document.getElementById('uploadProgress');

        if (!fileInput.files[0]) {
            this.showAlert('Please select a PDF file', 'warning');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        try {
            uploadBtn.disabled = true;
            uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
            uploadProgress.style.display = 'block';

            const response = await fetch(`${this.baseUrl}/api/pdf/upload`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.showAlert(result.message, 'success');
                form.reset();
                this.loadDocuments();
                this.populateDocumentSelects();
            } else {
                this.showAlert(result.detail || result.error || 'Upload failed', 'danger');
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showAlert('Network error during upload', 'danger');
        } finally {
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = '<i class="fas fa-upload me-2"></i>Upload and Process';
            uploadProgress.style.display = 'none';
        }
    }

    // Document Management
    async loadDocuments() {
        const container = document.getElementById('documentsContainer');
        
        try {
            const response = await fetch(`${this.baseUrl}/api/pdf/documents`);
            const documents = await response.json();

            if (documents.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-file-pdf"></i>
                        <p>No documents uploaded yet. Upload your first PDF to get started!</p>
                    </div>
                `;
                return;
            }

            container.innerHTML = documents.map(doc => `
                <div class="document-item">
                    <div class="document-title">${doc.original_filename}</div>
                    <div class="document-meta">
                        <span class="me-3"><i class="fas fa-calendar me-1"></i>${this.formatDate(doc.upload_time)}</span>
                        <span class="me-3"><i class="fas fa-file-alt me-1"></i>${doc.page_count || 'N/A'} pages</span>
                        <span><i class="fas fa-weight me-1"></i>${this.formatFileSize(doc.file_size)}</span>
                    </div>
                    ${doc.summary ? `<div class="mt-2"><small class="text-muted">${doc.summary.substring(0, 200)}...</small></div>` : ''}
                    <div class="document-actions">
                        <button class="btn btn-sm btn-primary" onclick="app.viewDocumentContent(${doc.id})">
                            <i class="fas fa-eye me-1"></i>View Content
                        </button>
                        <button class="btn btn-sm btn-success" onclick="app.startChatWithDocument(${doc.id})">
                            <i class="fas fa-comments me-1"></i>Chat
                        </button>
                        <button class="btn btn-sm btn-info" onclick="app.generateQuizForDocument(${doc.id})">
                            <i class="fas fa-question-circle me-1"></i>Generate Quiz
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="app.deleteDocument(${doc.id}, '${doc.original_filename}')">
                            <i class="fas fa-trash me-1"></i>Delete
                        </button>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading documents:', error);
            container.innerHTML = '<div class="alert alert-danger">Error loading documents</div>';
        }
    }

    async deleteDocument(documentId, filename) {
        if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
            return;
        }

        try {
            const response = await fetch(`${this.baseUrl}/api/pdf/documents/${documentId}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (response.ok) {
                this.showAlert(result.message, 'success');
                this.loadDocuments();
                this.populateDocumentSelects();
            } else {
                this.showAlert(result.detail || 'Delete failed', 'danger');
            }
        } catch (error) {
            console.error('Delete error:', error);
            this.showAlert('Network error during delete', 'danger');
        }
    }

    async viewDocumentContent(documentId) {
        try {
            const response = await fetch(`${this.baseUrl}/api/pdf/documents/${documentId}/content`);
            const data = await response.json();

            if (response.ok) {
                const modal = new bootstrap.Modal(document.getElementById('quizModal'));
                document.getElementById('quizModalTitle').textContent = `Content: ${data.filename}`;
                document.getElementById('quizModalBody').innerHTML = `
                    <div class="mb-3">
                        <h6>Summary:</h6>
                        <p class="text-muted">${data.summary || 'No summary available'}</p>
                    </div>
                    <div>
                        <h6>Full Content:</h6>
                        <div class="border p-3" style="max-height: 400px; overflow-y: auto; background-color: #f8f9fa;">
                            <pre style="white-space: pre-wrap; font-size: 0.9rem;">${data.content}</pre>
                        </div>
                    </div>
                `;
                modal.show();
            } else {
                this.showAlert('Error loading document content', 'danger');
            }
        } catch (error) {
            console.error('Error viewing document:', error);
            this.showAlert('Network error', 'danger');
        }
    }

    // Chat functionality
    async populateDocumentSelects() {
        try {
            const response = await fetch(`${this.baseUrl}/api/pdf/documents`);
            const documents = await response.json();

            const chatSelect = document.getElementById('chatDocumentSelect');
            const quizSelect = document.getElementById('quizDocumentSelect');

            const options = documents.map(doc => 
                `<option value="${doc.id}">${doc.original_filename}</option>`
            ).join('');

            chatSelect.innerHTML = '<option value="">Choose a document...</option>' + options;
            quizSelect.innerHTML = '<option value="">Choose a document...</option>' + options;
        } catch (error) {
            console.error('Error loading documents for select:', error);
        }
    }

    selectChatDocument(documentId) {
        if (documentId) {
            this.currentDocumentId = parseInt(documentId);
            this.currentSessionId = this.generateSessionId();
            this.clearChatContainer();
            this.enableChatInput();
            this.showAlert('Document selected. You can now start chatting!', 'info', 3000);
        } else {
            this.currentDocumentId = null;
            this.currentSessionId = null;
            this.disableChatInput();
            this.clearChatContainer();
        }
    }

    startChatWithDocument(documentId) {
        // Switch to chat tab
        const chatTab = document.getElementById('chat-tab');
        chatTab.click();
        
        // Select the document
        const chatSelect = document.getElementById('chatDocumentSelect');
        chatSelect.value = documentId;
        this.selectChatDocument(documentId);
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    enableChatInput() {
        document.getElementById('chatInput').disabled = false;
        document.getElementById('sendChatBtn').disabled = false;
    }

    disableChatInput() {
        document.getElementById('chatInput').disabled = true;
        document.getElementById('sendChatBtn').disabled = true;
    }

    clearChatContainer() {
        const container = document.getElementById('chatContainer');
        if (this.currentDocumentId) {
            container.innerHTML = '<div class="text-muted text-center p-2">Start a conversation by typing a question below</div>';
        } else {
            container.innerHTML = '<div class="text-muted text-center p-4">Select a document to start chatting</div>';
        }
    }

    async sendChatMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();

        if (!message || !this.currentDocumentId) {
            return;
        }

        const sendBtn = document.getElementById('sendChatBtn');
        const originalContent = sendBtn.innerHTML;

        try {
            // Add user message to chat
            this.addMessageToChat(message, 'user');
            input.value = '';
            
            sendBtn.disabled = true;
            sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

            const response = await fetch(`${this.baseUrl}/api/chat/ask`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    document_id: this.currentDocumentId,
                    message: message,
                    session_id: this.currentSessionId
                })
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.addMessageToChat(result.response, 'ai');
                this.currentSessionId = result.session_id;
            } else {
                this.addMessageToChat('Sorry, I encountered an error while processing your question.', 'ai');
                this.showAlert(result.detail || 'Chat error', 'danger');
            }
        } catch (error) {
            console.error('Chat error:', error);
            this.addMessageToChat('Sorry, there was a network error. Please try again.', 'ai');
            this.showAlert('Network error', 'danger');
        } finally {
            sendBtn.disabled = false;
            sendBtn.innerHTML = originalContent;
        }
    }

    addMessageToChat(message, sender) {
        const container = document.getElementById('chatContainer');
        
        // Clear initial message if present
        if (container.innerHTML.includes('Start a conversation')) {
            container.innerHTML = '';
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        
        const bubble = document.createElement('div');
        bubble.className = `message-bubble ${sender}`;
        bubble.textContent = message;
        
        const timestamp = document.createElement('div');
        timestamp.className = 'message-timestamp';
        timestamp.textContent = new Date().toLocaleTimeString();
        
        messageDiv.appendChild(bubble);
        messageDiv.appendChild(timestamp);
        container.appendChild(messageDiv);
        
        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    }

    // Quiz functionality
    async generateQuiz() {
        const form = document.getElementById('quizGenerationForm');
        const formData = new FormData(form);
        
        const documentId = formData.get('quizDocumentSelect');
        const numQuestions = formData.get('numQuestions');
        const difficulty = formData.get('difficulty');
        
        // Get selected question types
        const questionTypes = [];
        if (document.getElementById('mcqType').checked) questionTypes.push('mcq');
        if (document.getElementById('trueFalseType').checked) questionTypes.push('true_false');
        if (document.getElementById('fillBlankType').checked) questionTypes.push('fill_blank');

        if (!documentId) {
            this.showAlert('Please select a document', 'warning');
            return;
        }

        if (questionTypes.length === 0) {
            this.showAlert('Please select at least one question type', 'warning');
            return;
        }

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalContent = submitBtn.innerHTML;

        try {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';

            const response = await fetch(`${this.baseUrl}/api/quiz/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    document_id: parseInt(documentId),
                    num_questions: parseInt(numQuestions),
                    question_types: questionTypes,
                    difficulty: difficulty
                })
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.showAlert(result.message, 'success');
                this.loadQuizzes();
                form.reset();
                document.getElementById('mcqType').checked = true; // Reset to default
            } else {
                this.showAlert(result.detail || 'Quiz generation failed', 'danger');
            }
        } catch (error) {
            console.error('Quiz generation error:', error);
            this.showAlert('Network error during quiz generation', 'danger');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalContent;
        }
    }

    generateQuizForDocument(documentId) {
        // Switch to quiz tab
        const quizTab = document.getElementById('quiz-tab');
        quizTab.click();
        
        // Select the document
        const quizSelect = document.getElementById('quizDocumentSelect');
        quizSelect.value = documentId;
    }

    async loadQuizzes() {
        const container = document.getElementById('quizzesContainer');
        
        try {
            const response = await fetch(`${this.baseUrl}/api/quiz/`);
            const data = await response.json();

            if (data.quizzes.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-question-circle"></i>
                        <p>No quizzes generated yet. Create your first quiz from a document!</p>
                    </div>
                `;
                return;
            }

            container.innerHTML = data.quizzes.map(quiz => `
                <div class="quiz-item">
                    <div class="quiz-title fw-bold">${quiz.title}</div>
                    <div class="quiz-meta text-muted mb-2">
                        <small>
                            <i class="fas fa-file me-1"></i>${quiz.document_filename}<br>
                            <i class="fas fa-calendar me-1"></i>${this.formatDate(quiz.created_at)}<br>
                            <i class="fas fa-list-ol me-1"></i>${quiz.total_questions} questions
                        </small>
                    </div>
                    <div class="quiz-actions">
                        <button class="btn btn-sm btn-primary" onclick="app.viewQuiz(${quiz.id})">
                            <i class="fas fa-eye me-1"></i>View Quiz
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="app.deleteQuiz(${quiz.id})">
                            <i class="fas fa-trash me-1"></i>Delete
                        </button>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading quizzes:', error);
            container.innerHTML = '<div class="alert alert-danger">Error loading quizzes</div>';
        }
    }

    async viewQuiz(quizId) {
        try {
            const response = await fetch(`${this.baseUrl}/api/quiz/quiz/${quizId}`);
            const quiz = await response.json();

            if (response.ok) {
                const modal = new bootstrap.Modal(document.getElementById('quizModal'));
                document.getElementById('quizModalTitle').textContent = quiz.title;
                
                const questionsHtml = quiz.questions.map((q, index) => {
                    let optionsHtml = '';
                    
                    if (q.question_type === 'mcq' && q.options) {
                        optionsHtml = `
                            <div class="question-options">
                                ${q.options.map(option => `
                                    <div class="form-check">
                                        <input class="form-check-input" type="radio" name="q${q.id}" disabled>
                                        <label class="form-check-label">${option}</label>
                                    </div>
                                `).join('')}
                            </div>
                        `;
                    } else if (q.question_type === 'true_false') {
                        optionsHtml = `
                            <div class="question-options">
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="q${q.id}" disabled>
                                    <label class="form-check-label">True</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="radio" name="q${q.id}" disabled>
                                    <label class="form-check-label">False</label>
                                </div>
                            </div>
                        `;
                    } else if (q.question_type === 'fill_blank') {
                        optionsHtml = `
                            <div class="question-options">
                                <input type="text" class="form-control" placeholder="Your answer..." disabled>
                            </div>
                        `;
                    }

                    return `
                        <div class="quiz-question">
                            <h6>Question ${index + 1}</h6>
                            <p>${q.question_text}</p>
                            ${optionsHtml}
                            <div class="correct-answer">
                                <strong>Correct Answer:</strong> ${q.correct_answer}
                            </div>
                            ${q.explanation ? `<div class="quiz-explanation">${q.explanation}</div>` : ''}
                        </div>
                    `;
                }).join('');

                document.getElementById('quizModalBody').innerHTML = questionsHtml;
                modal.show();
            } else {
                this.showAlert('Error loading quiz', 'danger');
            }
        } catch (error) {
            console.error('Error viewing quiz:', error);
            this.showAlert('Network error', 'danger');
        }
    }

    async deleteQuiz(quizId) {
        if (!confirm('Are you sure you want to delete this quiz?')) {
            return;
        }

        try {
            const response = await fetch(`${this.baseUrl}/api/quiz/quiz/${quizId}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (response.ok) {
                this.showAlert(result.message, 'success');
                this.loadQuizzes();
            } else {
                this.showAlert(result.detail || 'Delete failed', 'danger');
            }
        } catch (error) {
            console.error('Delete quiz error:', error);
            this.showAlert('Network error during delete', 'danger');
        }
    }
}

// Initialize the application
const app = new PDFKnowledgeBot();
