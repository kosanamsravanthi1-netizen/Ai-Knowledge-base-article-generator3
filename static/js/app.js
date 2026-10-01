/**
 * AI-Powered Python & Django Knowledge Assistant (RAG)
 * Single Page Application JavaScript Engine
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- Application State ---
    let currentConversationId = null;
    let conversations = [];
    let currentMessages = [];

    // --- DOM Elements ---
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const mobileToggleBtn = document.getElementById('mobileToggleBtn');
    const closeSidebarBtn = document.getElementById('closeSidebarBtn');
    
    const newChatBtn = document.getElementById('newChatBtn');
    const searchConvsInput = document.getElementById('searchConvsInput');
    const conversationsList = document.getElementById('conversationsList');
    const convCountBadge = document.getElementById('convCountBadge');
    
    const currentChatTitle = document.getElementById('currentChatTitle');
    const clearChatBtn = document.getElementById('clearChatBtn');
    
    const chatViewport = document.getElementById('chatViewport');
    const emptyState = document.getElementById('emptyState');
    const messagesContainer = document.getElementById('messagesContainer');
    const typingIndicator = document.getElementById('typingIndicator');
    const scrollBottomBtn = document.getElementById('scrollBottomBtn');
    
    const chatForm = document.getElementById('chatForm');
    const questionInput = document.getElementById('questionInput');
    const sendBtn = document.getElementById('sendBtn');
    
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const exportChatBtn = document.getElementById('exportChatBtn');
    const aboutBtn = document.getElementById('aboutBtn');
    const aboutModal = document.getElementById('aboutModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const confirmModalBtn = document.getElementById('confirmModalBtn');
    
    const indexStatusText = document.getElementById('indexStatusText');
    const toastContainer = document.getElementById('toastContainer');

    // Configure Marked.js options
    if (window.marked) {
        marked.setOptions({
            gfm: true,
            breaks: true,
        });
    }

    // --- Initialize Application ---
    init();

    async function init() {
        bindEvents();
        setupAutoResizeTextarea();
        await fetchSystemStatus();
        await loadConversations();
    }

    // --- Event Listeners ---
    function bindEvents() {
        // Mobile Sidebar
        mobileToggleBtn?.addEventListener('click', () => {
            sidebar.classList.add('open');
            sidebarOverlay.classList.add('open');
        });

        closeSidebarBtn?.addEventListener('click', closeMobileSidebar);
        sidebarOverlay?.addEventListener('click', closeMobileSidebar);

        // Conversation management
        newChatBtn?.addEventListener('click', startNewConversation);
        clearChatBtn?.addEventListener('click', clearCurrentView);
        searchConvsInput?.addEventListener('input', handleSearchConversations);

        // Question Submission
        chatForm?.addEventListener('submit', handleFormSubmit);
        questionInput?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                chatForm.dispatchEvent(new Event('submit'));
            }
        });

        // Prompt Cards (Suggested Questions)
        document.querySelectorAll('.prompt-card').forEach(card => {
            card.addEventListener('click', () => {
                const text = card.getAttribute('data-prompt');
                if (text) {
                    questionInput.value = text;
                    questionInput.focus();
                    chatForm.dispatchEvent(new Event('submit'));
                }
            });
        });

        // Utilities & Modals
        themeToggleBtn?.addEventListener('click', toggleTheme);
        exportChatBtn?.addEventListener('click', exportConversation);
        aboutBtn?.addEventListener('click', () => aboutModal.classList.remove('hidden'));
        closeModalBtn?.addEventListener('click', () => aboutModal.classList.add('hidden'));
        confirmModalBtn?.addEventListener('click', () => aboutModal.classList.add('hidden'));
        
        // Scroll bottom listener
        chatViewport?.addEventListener('scroll', () => {
            const isBottom = chatViewport.scrollHeight - chatViewport.scrollTop <= chatViewport.clientHeight + 100;
            if (isBottom) {
                scrollBottomBtn.classList.add('hidden');
            } else {
                scrollBottomBtn.classList.remove('hidden');
            }
        });

        scrollBottomBtn?.addEventListener('click', scrollToBottom);
    }

    function closeMobileSidebar() {
        sidebar.classList.remove('open');
        sidebarOverlay.classList.remove('open');
    }

    function setupAutoResizeTextarea() {
        questionInput.addEventListener('input', () => {
            questionInput.style.height = 'auto';
            questionInput.style.height = Math.min(questionInput.scrollHeight, 160) + 'px';
        });
    }

    // --- API Calls ---

    async function fetchSystemStatus() {
        try {
            const res = await fetch('/api/status/');
            if (res.ok) {
                const data = await res.json();
                indexStatusText.textContent = `${data.faiss_vector_count} Vectors Ingested`;
            }
        } catch (err) {
            indexStatusText.textContent = "Offline";
        }
    }

    async function loadConversations() {
        try {
            const res = await fetch('/api/conversations/');
            if (res.ok) {
                conversations = await res.json();
                renderConversationsList();
            }
        } catch (err) {
            showToast("Failed to load conversation history.", "error");
        }
    }

    async function loadConversationDetail(id) {
        try {
            const res = await fetch(`/api/conversations/${id}/`);
            if (res.ok) {
                const data = await res.json();
                currentConversationId = data.id;
                currentChatTitle.textContent = data.title;
                currentMessages = data.messages || [];
                renderMessages();
                highlightActiveConvItem(id);
                closeMobileSidebar();
            }
        } catch (err) {
            showToast("Failed to load conversation details.", "error");
        }
    }

    async function deleteConversation(id, e) {
        e.stopPropagation();
        if (!confirm("Are you sure you want to delete this conversation?")) return;

        try {
            const res = await fetch(`/api/conversations/${id}/`, { method: 'DELETE' });
            if (res.ok) {
                showToast("Conversation deleted.", "info");
                if (currentConversationId === id) {
                    startNewConversation();
                }
                await loadConversations();
            }
        } catch (err) {
            showToast("Error deleting conversation.", "error");
        }
    }

    async function handleFormSubmit(e) {
        e.preventDefault();
        const question = questionInput.value.trim();
        if (!question) return;

        // Reset textarea height
        questionInput.value = '';
        questionInput.style.height = 'auto';

        // Hide Empty State
        emptyState.classList.add('hidden');
        messagesContainer.classList.remove('hidden');

        // Render User Message immediately
        const userMsgObj = { role: 'user', content: question, created_at: new Date().toISOString() };
        currentMessages.push(userMsgObj);
        appendMessageRow(userMsgObj);
        scrollToBottom();

        // Show Loading Indicator
        typingIndicator.classList.remove('hidden');
        scrollToBottom();

        try {
            const response = await fetch('/api/ask/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: question,
                    conversation_id: currentConversationId
                })
            });

            const data = await response.json();
            typingIndicator.classList.add('hidden');

            if (response.ok) {
                // Update Conversation ID if newly created
                if (!currentConversationId && data.conversation_id) {
                    currentConversationId = data.conversation_id;
                    await loadConversations();
                }

                const assistantMsgObj = {
                    id: data.message_id,
                    role: 'assistant',
                    content: data.answer,
                    sources: data.sources || [],
                    domain: data.domain,
                    created_at: new Date().toISOString()
                };

                currentMessages.push(assistantMsgObj);
                appendMessageRow(assistantMsgObj);
                scrollToBottom();

                // Update sidebar list title if title changed
                await loadConversations();
            } else {
                showToast(data.error || "Failed to process question.", "error");
                appendErrorMessageRow(data.error || "An error occurred while fetching the answer.");
            }
        } catch (err) {
            typingIndicator.classList.add('hidden');
            showToast("Network error. Please check backend connection.", "error");
            appendErrorMessageRow("Unable to connect to backend server. Please verify Django server is running.");
        }
    }

    // --- Render Functions ---

    function startNewConversation() {
        currentConversationId = null;
        currentMessages = [];
        currentChatTitle.textContent = "Python & Django Knowledge Assistant";
        messagesContainer.innerHTML = '';
        messagesContainer.classList.add('hidden');
        emptyState.classList.remove('hidden');
        highlightActiveConvItem(null);
        closeMobileSidebar();
    }

    function clearCurrentView() {
        if (currentConversationId) {
            startNewConversation();
        } else {
            messagesContainer.innerHTML = '';
            messagesContainer.classList.add('hidden');
            emptyState.classList.remove('hidden');
        }
    }

    function renderConversationsList() {
        conversationsList.innerHTML = '';
        convCountBadge.textContent = conversations.length;

        if (conversations.length === 0) {
            conversationsList.innerHTML = `<div style="font-size: 0.8rem; color: var(--text-muted); padding: 0.5rem;">No history yet.</div>`;
            return;
        }

        conversations.forEach(conv => {
            const item = document.createElement('div');
            item.className = `conv-item ${conv.id === currentConversationId ? 'active' : ''}`;
            item.setAttribute('data-id', conv.id);

            item.innerHTML = `
                <i class="fa-regular fa-message" style="font-size: 0.85rem;"></i>
                <span class="conv-title">${escapeHtml(conv.title)}</span>
                <button class="conv-delete-btn" title="Delete conversation"><i class="fa-solid fa-trash"></i></button>
            `;

            item.addEventListener('click', () => loadConversationDetail(conv.id));
            item.querySelector('.conv-delete-btn').addEventListener('click', (e) => deleteConversation(conv.id, e));

            conversationsList.appendChild(item);
        });
    }

    function highlightActiveConvItem(id) {
        document.querySelectorAll('.conv-item').forEach(el => {
            if (el.getAttribute('data-id') === id) {
                el.classList.add('active');
            } else {
                el.classList.remove('active');
            }
        });
    }

    function handleSearchConversations(e) {
        const query = e.target.value.lowerCase().trim();
        document.querySelectorAll('.conv-item').forEach(el => {
            const title = el.querySelector('.conv-title').textContent.toLowerCase();
            if (title.includes(query)) {
                el.style.display = 'flex';
            } else {
                el.style.display = 'none';
            }
        });
    }

    function renderMessages() {
        emptyState.classList.add('hidden');
        messagesContainer.classList.remove('hidden');
        messagesContainer.innerHTML = '';

        currentMessages.forEach(msg => {
            appendMessageRow(msg);
        });

        scrollToBottom();
    }

    function appendMessageRow(msg) {
        const row = document.createElement('div');
        row.className = `message-row ${msg.role}`;

        const isUser = msg.role === 'user';
        const avatarIcon = isUser ? 'fa-user' : 'fa-robot';
        
        let contentHtml = '';
        if (isUser) {
            contentHtml = escapeHtml(msg.content);
        } else {
            contentHtml = formatMarkdownContent(msg.content);
        }

        let sourcesHtml = '';
        if (!isUser && msg.sources && msg.sources.length > 0) {
            sourcesHtml = `
                <div class="sources-card">
                    <div class="sources-header">
                        <i class="fa-solid fa-book-bookmark"></i> Retained Documentation Sources
                    </div>
                    <div class="sources-list">
                        ${msg.sources.map(src => `
                            <a href="${escapeHtml(src.url)}" target="_blank" rel="noopener" class="source-badge" title="${escapeHtml(src.title)} - ${escapeHtml(src.section)}">
                                <i class="fa-solid fa-link"></i> ${escapeHtml(src.title)} (${escapeHtml(src.section)})
                            </a>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        let actionsHtml = '';
        if (!isUser) {
            actionsHtml = `
                <div class="msg-actions">
                    <button class="action-btn copy-msg-btn" title="Copy Answer"><i class="fa-regular fa-copy"></i> Copy</button>
                    <button class="action-btn feedback-up-btn" title="Helpful"><i class="fa-regular fa-thumbs-up"></i></button>
                    <button class="action-btn feedback-down-btn" title="Not Helpful"><i class="fa-regular fa-thumbs-down"></i></button>
                </div>
            `;
        }

        row.innerHTML = `
            <div class="avatar"><i class="fa-solid ${avatarIcon}"></i></div>
            <div class="bubble">
                <div class="bubble-content">${contentHtml}</div>
                ${sourcesHtml}
                ${actionsHtml}
            </div>
        `;

        // Bind copy & feedback listeners
        if (!isUser) {
            const copyBtn = row.querySelector('.copy-msg-btn');
            copyBtn?.addEventListener('click', () => {
                navigator.clipboard.writeText(msg.content);
                showToast("Response copied to clipboard!", "info");
            });

            const thumbsUp = row.querySelector('.feedback-up-btn');
            thumbsUp?.addEventListener('click', () => sendFeedback(msg.id, 5, thumbsUp));

            const thumbsDown = row.querySelector('.feedback-down-btn');
            thumbsDown?.addEventListener('click', () => sendFeedback(msg.id, 1, thumbsDown));

            // Setup Code Block Copy Buttons
            row.querySelectorAll('.copy-code-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const code = btn.closest('.code-container').querySelector('code').textContent;
                    navigator.clipboard.writeText(code);
                    btn.innerHTML = `<i class="fa-solid fa-check"></i> Copied!`;
                    setTimeout(() => {
                        btn.innerHTML = `<i class="fa-regular fa-copy"></i> Copy`;
                    }, 2000);
                });
            });
        }

        messagesContainer.appendChild(row);
    }

    function appendErrorMessageRow(errorText) {
        const row = document.createElement('div');
        row.className = 'message-row assistant';
        row.innerHTML = `
            <div class="avatar" style="background: var(--danger);"><i class="fa-solid fa-triangle-exclamation"></i></div>
            <div class="bubble" style="border-color: var(--danger);">
                <p style="color: var(--danger); font-weight: 600;">Error</p>
                <p>${escapeHtml(errorText)}</p>
            </div>
        `;
        messagesContainer.appendChild(row);
        scrollToBottom();
    }

    async function sendFeedback(msgId, rating, btn) {
        try {
            await fetch('/api/feedback/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    conversation: currentConversationId,
                    message: msgId,
                    rating: rating
                })
            });
            showToast("Feedback received. Thank you!", "info");
            btn.style.color = "var(--accent-primary)";
        } catch (err) {
            console.error("Feedback error:", err);
        }
    }

    function formatMarkdownContent(rawText) {
        if (!rawText) return '';
        
        let html = marked.parse(rawText);

        // Custom code container transformation
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;

        tempDiv.querySelectorAll('pre').forEach(pre => {
            const codeEl = pre.querySelector('code');
            const codeText = codeEl ? codeEl.textContent : pre.textContent;
            
            // Detect language class
            let lang = 'python';
            if (codeEl && codeEl.className) {
                const match = codeEl.className.match(/language-(\w+)/);
                if (match) lang = match[1];
            }

            const codeContainer = document.createElement('div');
            codeContainer.className = 'code-container';
            codeContainer.innerHTML = `
                <div class="code-header">
                    <span>${lang.toUpperCase()}</span>
                    <button class="copy-code-btn"><i class="fa-regular fa-copy"></i> Copy</button>
                </div>
                <pre><code>${escapeHtml(codeText)}</code></pre>
            `;

            pre.replaceWith(codeContainer);
        });

        return tempDiv.innerHTML;
    }

    // --- Utilities ---

    function scrollToBottom() {
        chatViewport.scrollTop = chatViewport.scrollHeight;
    }

    function toggleTheme() {
        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', newTheme);
        themeToggleBtn.innerHTML = newTheme === 'dark' ? '<i class="fa-solid fa-moon"></i>' : '<i class="fa-solid fa-sun"></i>';
    }

    function exportConversation() {
        if (currentMessages.length === 0) {
            showToast("No active messages to export.", "info");
            return;
        }

        let textContent = `AI Python & Django Knowledge Assistant - Exported Conversation\n`;
        textContent += `Title: ${currentChatTitle.textContent}\n`;
        textContent += `Date: ${new Date().toLocaleString()}\n`;
        textContent += `=`.repeat(60) + `\n\n`;

        currentMessages.forEach(msg => {
            textContent += `[${msg.role.toUpperCase()}] (${new Date(msg.created_at).toLocaleTimeString()})\n`;
            textContent += `${msg.content}\n\n`;
            if (msg.sources && msg.sources.length > 0) {
                textContent += `Sources:\n`;
                msg.sources.forEach(s => textContent += `  - ${s.title} (${s.section}): ${s.url}\n`);
                textContent += `\n`;
            }
            textContent += `-`.repeat(40) + `\n\n`;
        });

        const blob = new Blob([textContent], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `conversation_${currentConversationId || 'session'}.txt`;
        a.click();
        URL.revokeObjectURL(url);

        showToast("Conversation exported successfully!", "info");
    }

    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = 'toast';
        const icon = type === 'error' ? 'fa-circle-exclamation' : 'fa-circle-info';
        toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${escapeHtml(message)}</span>`;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
