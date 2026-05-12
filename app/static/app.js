document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    
    const chatContainer = document.getElementById('chat-container');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const welcomeMsg = document.getElementById('welcome-msg');

    // at-resize text area
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = userInput.scrollHeight + 'px';
    });

    const addMessage = (content, isUser = false, usage = null) => {
        if (welcomeMsg) welcomeMsg.style.display = 'none';

        const msgDiv = document.createElement('div');
        msgDiv.className = `flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`;
        
        const innerContent = `
            <div class="max-w-[85%] ${isUser ? 'bg-indigo-600 text-white rounded-2xl rounded-tr-sm' : 'bg-[#1e1e24] border border-slate-800 text-slate-200 rounded-2xl rounded-tl-sm'} p-4 shadow-lg">
                <div class="markdown-content text-sm leading-relaxed">
                    ${content.replace(/\n/g, '<br>')}
                </div>
                ${usage ? `
                    <div class="mt-3 pt-2 border-t border-slate-700/50 flex gap-4 text-[10px] text-slate-400">
                        <span><i data-lucide="coins" class="inline w-3 h-3"></i> $${usage.total_cost.toFixed(4)}</span>
                        <span><i data-lucide="Zap" class="inline w-3 h-3"></i> ${usage.total_tokens} tokens</span>
                    </div>
                ` : ''}
            </div>
        `;
        
        msgDiv.innerHTML = innerContent;
        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        lucide.createIcons();
    };

    const showThinking = () => {
        const thinkingDiv = document.createElement('div');
        thinkingDiv.id = 'thinking-indicator';
        thinkingDiv.className = 'flex justify-start animate-fade-in';
        thinkingDiv.innerHTML = `
            <div class="bg-[#1e1e24] border border-slate-800 p-4 rounded-2xl rounded-tl-sm flex items-center gap-2">
                <div class="thinking-dot"></div>
                <div class="thinking-dot"></div>
                <div class="thinking-dot"></div>
            </div>
        `;
        chatContainer.appendChild(thinkingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    };

    const removeThinking = () => {
        const indicator = document.getElementById('thinking-indicator');
        if (indicator) indicator.remove();
    };

    const sendMessage = async () => {
        const text = userInput.value.trim();
        if (!text) return;

        userInput.value = '';
        userInput.style.height = 'auto';
        addMessage(text, true);
        
        showThinking();
        sendBtn.disabled = true;

        try {
            const threadId = sessionStorage.getItem('thread_id') || 'session-' + Math.random().toString(36).substring(7);
            sessionStorage.setItem('thread_id', threadId);

            const response = await fetch('/api/v1/ask', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-API-KEY': 'monks-secret-key-2026' // chave 
                },
                body: JSON.stringify({ 
                    question: text,
                    thread_id: threadId
                })
            });

            const data = await response.json();
            removeThinking();

            if (data.status === 'ok') {
                addMessage(data.answer, false, data.usage);
            } else {
                addMessage(`Erro: ${data.detail || 'Não foi possível processar a resposta.'}`, false);
            }
        } catch (error) {
            removeThinking();
            addMessage('Erro de conexão com o servidor.', false);
        } finally {
            sendBtn.disabled = false;
        }
    };

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});
