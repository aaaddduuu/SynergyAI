// Global state
let currentSessionId = null;
let currentTeamId = null;
let currentProjectId = null;
let selectedAgent = null;
let ws = null;
let wsConnected = false;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
let typingTimeout = null;
let isCreatingSession = false;
let allTeams = [];
let allProjects = [];

const agentNames = {
    'hr': 'HR',
    'pm': '项目经理',
    'ba': '业务分析师',
    'dev': '开发工程师',
    'qa': '测试工程师',
    'architect': '架构师',
    'system': '系统'
};

const agentColors = {
    'hr': '#e91e63',
    'pm': '#2196f3',
    'ba': '#9c27b0',
    'dev': '#4caf50',
    'qa': '#ff9800',
    'architect': '#607d8b',
    'system': '#666',
    'user': '#667aea'
};

const taskStateColors = {
    'pending': { bg: 'bg-slate-50', border: 'border-slate-300', text: 'text-slate-400' },
    'in_progress': { bg: 'bg-blue-50', border: 'border-primary', text: 'text-primary' },
    'review': { bg: 'bg-amber-50', border: 'border-amber-400', text: 'text-amber-600' },
    'done': { bg: 'bg-emerald-50', border: 'border-emerald-400', text: 'text-emerald-600' }
};

const taskStateLabels = {
    'pending': '待处理',
    'in_progress': '进行中',
    'review': '审核中',
    'done': '已完成'
};

// ==================== WebSocket Functions ====================
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/chat`;

    console.log('Connecting to WebSocket:', wsUrl);

    try {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('WebSocket connected');
            wsConnected = true;
            reconnectAttempts = 0;
            updateWsStatus(true);
            showToast('success', '连接成功', 'WebSocket连接已建立');
        };

        ws.onclose = (event) => {
            console.log('WebSocket disconnected, code:', event.code, 'reason:', event.reason);
            wsConnected = false;
            updateWsStatus(false);

            if (reconnectAttempts < maxReconnectAttempts) {
                reconnectAttempts++;
                const delay = 2000 * reconnectAttempts;
                console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts}/${maxReconnectAttempts})`);
                showToast('warning', '连接断开', `将在 ${delay/1000} 秒后重连...`);
                setTimeout(connectWebSocket, delay);
            } else {
                showToast('error', '连接失败', 'WebSocket 重连失败，请刷新页面');
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            showToast('error', '连接错误', 'WebSocket 连接出错');
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                handleWsMessage(data);
            } catch (e) {
                console.error('Failed to parse WS message:', e);
            }
        };
    } catch (error) {
        console.error('Failed to create WebSocket:', error);
        showToast('error', '连接失败', '无法创建 WebSocket 连接');
    }
}

function handleWsMessage(data) {
    switch (data.type) {
        case 'connected':
            console.log('WS:', data.message);
            break;

        case 'message':
            addMessage('agent', data.sender, data.content);
            hideTyping();
            resetSendButton();
            break;

        case 'turn_update':
            document.getElementById('turnCount').textContent = data.turn_count;
            break;

        case 'session_created':
            isCreatingSession = false;
            hideLoadingOverlay();
            currentSessionId = data.session_id;
            document.getElementById('emptyState').classList.add('hidden');
            const messagesDiv = document.getElementById('messages');
            messagesDiv.innerHTML = `
                <div class="flex justify-center my-4">
                    <div class="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800/50 px-6 py-2 rounded-full flex items-center gap-2">
                        <span class="text-emerald-500 text-[18px]">✅</span>
                        <span class="text-xs text-emerald-700 dark:text-emerald-400 font-medium">${data.message}</span>
                    </div>
                </div>
            `;
            updateSessionStatus(true);
            loadTasks();
            showToast('success', '成功', '新项目创建成功！');
            break;

        case 'session_end':
            updateSessionStatus(false);
            addMessage('system', '系统', '📋 Session已结束\n\n' + (data.handover_doc || '无交接文档'));
            break;

        case 'task_created':
            loadTasks();
            updateProgress();
            addActivity('task', `新任务: ${data.task.title}`);
            break;

        case 'task_updated':
            loadTasks();
            updateProgress();
            addActivity('task', `任务状态更新: ${data.task.title} → ${data.new_state}`);
            break;

        case 'task_deleted':
            loadTasks();
            updateProgress();
            break;

        case 'error':
            isCreatingSession = false;
            hideLoadingOverlay();
            showToast('error', '错误', data.message);
            break;

        case 'pong':
            break;
    }
}

function updateWsStatus(connected) {
    const statusEl = document.getElementById('wsStatus');
    if (connected) {
        statusEl.innerHTML = `
            <span class="w-2 h-2 rounded-full bg-green-500"></span>
            <span>在线</span>
        `;
    } else {
        statusEl.innerHTML = `
            <span class="w-2 h-2 rounded-full bg-red-500"></span>
            <span>离线</span>
        `;
    }
}

function sendWsMessage(data) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(data));
    } else {
        console.warn('WebSocket not connected');
    }
}

// ==================== UI Functions ====================
const agentRoleNames = {
    'hr': { name: 'HR', color: '#e91e63' },
    'pm': { name: '产品经理', color: '#2196f3' },
    'ba': { name: '业务分析师', color: '#9c27b0' },
    'dev': { name: '开发工程师', color: '#4caf50' },
    'qa': { name: '测试工程师', color: '#ff9800' },
    'architect': { name: '架构师', color: '#607d8b' }
};

const modelOptions = {
    'openai': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    'anthropic': ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
    'zhipu': ['glm-4', 'glm-4-plus', 'glm-4-flash', 'glm-4-air', 'glm-4-airx', 'glm-3-turbo'],
    'custom': ['custom']
};

let currentConfig = null;

function updateModelOptions() {
    const provider = document.getElementById('providerSelect').value;
    const modelSelect = document.getElementById('modelSelect');
    const models = modelOptions[provider] || [];

    modelSelect.innerHTML = models.map(m => `<option value="${m}">${m}</option>`).join('');
}

function showConfigModal() {
    loadConfig();
    document.getElementById('configModal').classList.remove('hidden');
}

async function loadConfig() {
    try {
        const res = await fetch('/api/config');
        if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
        }
        const data = await res.json();

        const defaultCfg = (data && data.default) ? data.default : { provider: 'openai', model: 'gpt-4o', base_url: '' };
        const agentsCfg = (data && data.agents) ? data.agents : {};

        currentConfig = data;

        document.getElementById('providerSelect').value = defaultCfg.provider || 'openai';
        updateModelOptions();
        document.getElementById('modelSelect').value = defaultCfg.model || 'gpt-4o';
        document.getElementById('apiKeyInput').value = '';
        document.getElementById('baseUrlInput').value = defaultCfg.base_url || '';

        renderAgentConfigs(agentsCfg);
    } catch (e) {
        console.error('Failed to load config:', e);
        currentConfig = {
            default: { provider: 'openai', model: 'gpt-4o', base_url: '' },
            agents: {}
        };
        document.getElementById('providerSelect').value = 'openai';
        updateModelOptions();
        document.getElementById('modelSelect').value = 'gpt-4o';
        renderAgentConfigs({});
    }
}

function renderAgentConfigs(agentConfigs) {
    const container = document.getElementById('agentConfigList');
    const roles = Object.keys(agentRoleNames);

    if (!agentConfigs || Object.keys(agentConfigs).length === 0) {
        container.innerHTML = `
            <div class="text-center py-4 text-slate-400 text-sm">
                <p>点击下方角色可展开独立配置</p>
                <p class="text-xs mt-1">不配置则使用默认模型</p>
            </div>
        `;
        roles.forEach(role => {
            const roleInfo = agentRoleNames[role];
            container.innerHTML += `
                <div class="bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
                    <div onclick="toggleAgentConfig('${role}')" class="flex items-center justify-between p-3 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                        <div class="flex items-center gap-2">
                            <div class="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold" style="background: ${roleInfo.color}">
                                ${role.toUpperCase()}
                            </div>
                            <span class="text-sm font-medium">${roleInfo.name}</span>
                            <span class="text-xs text-slate-400">(使用默认)</span>
                        </div>
                        <span class="text-slate-400 text-[18px] transition-transform" id="arrow-${role}">▼</span>
                    </div>
                    <div id="agent-${role}" class="hidden p-3 pt-0 grid grid-cols-2 gap-3">
                        <div class="col-span-2">
                            <label class="text-xs text-slate-500 flex items-center">
                                <input type="checkbox" id="use-default-${role}" checked
                                    onchange="toggleAgentUseDefault('${role}')" class="mr-2"/>
                                使用默认配置
                            </label>
                        </div>
                        <div>
                            <label class="text-xs text-slate-500">供应商</label>
                            <select id="agent-provider-${role}" class="w-full h-9 text-sm rounded border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900" onchange="updateAgentModels('${role}')">
                                <option value="openai">OpenAI</option>
                                <option value="anthropic">Anthropic</option>
                                <option value="zhipu">智谱AI</option>
                                <option value="custom">自定义</option>
                            </select>
                        </div>
                        <div>
                            <label class="text-xs text-slate-500">模型</label>
                            <select id="agent-model-${role}" class="w-full h-9 text-sm rounded border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
                                ${modelOptions['openai'].map(m => `<option value="${m}">${m}</option>`).join('')}
                            </select>
                        </div>
                        <div class="col-span-2">
                            <label class="text-xs text-slate-500">API Key <span class="text-slate-400">(可选)</span></label>
                            <input id="agent-apikey-${role}" type="password" class="w-full h-9 text-sm rounded border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3" placeholder="留空使用默认配置"/>
                        </div>
                    </div>
                </div>
            `;
        });
        return;
    }

    container.innerHTML = roles.map(role => {
        const config = agentConfigs[role] || {};
        const roleInfo = agentRoleNames[role];

        return `
            <div class="bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
                <div onclick="toggleAgentConfig('${role}')" class="flex items-center justify-between p-3 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                    <div class="flex items-center gap-2">
                        <div class="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold" style="background: ${roleInfo.color}">
                            ${role.toUpperCase()}
                        </div>
                        <span class="text-sm font-medium">${roleInfo.name}</span>
                        ${config.model ? `<span class="text-xs text-primary">${config.provider}/${config.model}</span>` : '<span class="text-xs text-slate-400">(使用默认)</span>'}
                    </div>
                    <span class="text-slate-400 text-[18px] transition-transform" id="arrow-${role}">▼</span>
                </div>
                <div id="agent-${role}" class="hidden p-3 pt-0 grid grid-cols-2 gap-3">
                    <div class="col-span-2">
                        <label class="text-xs text-slate-500 flex items-center">
                            <input type="checkbox" id="use-default-${role}" ${!config.model ? 'checked' : ''}
                                onchange="toggleAgentUseDefault('${role}')" class="mr-2"/>
                            使用默认配置
                        </label>
                    </div>
                    <div>
                        <label class="text-xs text-slate-500">供应商</label>
                        <select id="agent-provider-${role}" class="w-full h-9 text-sm rounded border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900" onchange="updateAgentModels('${role}')">
                            <option value="openai" ${config.provider === 'openai' ? 'selected' : ''}>OpenAI</option>
                            <option value="anthropic" ${config.provider === 'anthropic' ? 'selected' : ''}>Anthropic</option>
                            <option value="zhipu" ${config.provider === 'zhipu' ? 'selected' : ''}>智谱AI</option>
                            <option value="custom" ${config.provider === 'custom' ? 'selected' : ''}>自定义</option>
                        </select>
                    </div>
                    <div>
                        <label class="text-xs text-slate-500">模型</label>
                        <select id="agent-model-${role}" class="w-full h-9 text-sm rounded border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
                            ${(modelOptions[config.provider] || modelOptions['openai']).map(m =>
                                `<option value="${m}" ${config.model === m ? 'selected' : ''}>${m}</option>`
                            ).join('')}
                        </select>
                    </div>
                    <div class="col-span-2">
                        <label class="text-xs text-slate-500">API Key <span class="text-slate-400">(可选)</span></label>
                        <input id="agent-apikey-${role}" type="password" class="w-full h-9 text-sm rounded border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3" placeholder="留空使用默认配置" value=""/>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function toggleAgentConfig(role) {
    const el = document.getElementById(`agent-${role}`);
    const arrow = document.getElementById(`arrow-${role}`);
    if (el.classList.contains('hidden')) {
        el.classList.remove('hidden');
        arrow.style.transform = 'rotate(180deg)';
    } else {
        el.classList.add('hidden');
        arrow.style.transform = 'rotate(0deg)';
    }
}

function toggleAgentUseDefault(role) {
    const checkbox = document.getElementById(`use-default-${role}`);
    const fields = document.getElementById(`agent-${role}`).querySelectorAll('select, input:not([type="checkbox"])');
    fields.forEach(f => f.disabled = checkbox.checked);
}

function updateAgentModels(role) {
    const provider = document.getElementById(`agent-provider-${role}`).value;
    const modelSelect = document.getElementById(`agent-model-${role}`);
    modelSelect.innerHTML = (modelOptions[provider] || []).map(m => `<option value="${m}">${m}</option>`).join('');
}

function expandAllAgents() {
    console.log('expandAllAgents called');
    try {
        Object.keys(agentRoleNames).forEach(role => {
            console.log('Expanding agent:', role);
            const el = document.getElementById(`agent-${role}`);
            const arrow = document.getElementById(`arrow-${role}`);
            if (el) {
                el.classList.remove('hidden');
            }
            if (arrow) {
                arrow.style.transform = 'rotate(180deg)';
            }
        });
    } catch (e) {
        console.error('expandAllAgents error:', e);
    }
}

async function saveAllConfig() {
    const provider = document.getElementById('providerSelect').value;
    const model = document.getElementById('modelSelect').value;
    const apiKey = document.getElementById('apiKeyInput').value;
    const baseUrl = document.getElementById('baseUrlInput').value;

    try {
        const res = await fetch('/api/config', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                provider,
                model,
                api_key: apiKey || null,
                base_url: baseUrl || null
            })
        });

        if (!res.ok) {
            const err = await res.json();
            showToast('error', '保存失败', err.detail);
            return;
        }

        const configs = [];
        for (const role of Object.keys(agentRoleNames)) {
            const useDefault = document.getElementById(`use-default-${role}`)?.checked;
            if (useDefault) continue;

            const agentProvider = document.getElementById(`agent-provider-${role}`)?.value || provider;
            const agentModel = document.getElementById(`agent-model-${role}`)?.value || model;
            const agentApiKey = document.getElementById(`agent-apikey-${role}`)?.value;

            configs.push({
                role,
                provider: agentProvider,
                model: agentModel,
                api_key: agentApiKey || null,
                base_url: null
            });
        }

        if (configs.length > 0) {
            await fetch('/api/config/agents', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ configs })
            });
        }

        hideConfigModal();
        showToast('success', '配置成功', '模型配置已保存');
    } catch (e) {
        showToast('error', '保存失败', e.message);
    }
}

function hideConfigModal() {
    document.getElementById('configModal').classList.add('hidden');
}

function showAddTaskModal() {
    if (!currentSessionId) {
        showToast('warning', '提示', '请先创建项目');
        return;
    }
    document.getElementById('addTaskModal').classList.remove('hidden');

    document.querySelectorAll('.priority-option').forEach(el => {
        el.onclick = function() {
            const label = this.parentElement;
            const radio = label.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;
                document.querySelectorAll('.priority-option').forEach(opt => {
                    opt.className = 'priority-option flex items-center justify-center py-2 px-3 border border-slate-200 dark:border-slate-700 rounded-lg text-sm bg-slate-50 dark:bg-slate-800 transition-all';
                });
                this.className = 'priority-option flex items-center justify-center py-2 px-3 border border-primary dark:border-primary rounded-lg text-sm bg-primary/10 text-primary font-medium';
            }
        };
    });
}

function hideAddTaskModal() {
    document.getElementById('addTaskModal').classList.add('hidden');
}

function selectAgent(agent) {
    selectedAgent = agent;
    document.getElementById('messageInput').focus();
}

async function saveConfig() {
    const model = document.getElementById('modelSelect').value;
    const apiKey = document.getElementById('apiKeyInput').value;
    const baseUrl = document.getElementById('baseUrlInput').value;

    try {
        const res = await fetch('/api/config', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({model, api_key: apiKey, base_url: baseUrl})
        });

        if (res.ok) {
            hideConfigModal();
            showToast('success', '配置成功', 'LLM已配置完成');
        } else {
            const err = await res.json();
            showToast('error', '配置失败', err.detail);
        }
    } catch (e) {
        showToast('error', '配置失败', e.message);
    }
}

function createSession() {
    if (isCreatingSession) {
        showToast('warning', '提示', '正在创建项目，请稍候...');
        return;
    }

    if (!wsConnected) {
        showToast('warning', '提示', 'WebSocket 未连接，正在尝试重连...');

        if (reconnectAttempts >= maxReconnectAttempts) {
            reconnectAttempts = 0;
        }

        connectWebSocket();

        setTimeout(() => {
            if (wsConnected) {
                createSession();
            } else {
                showToast('error', '连接失败', 'WebSocket 连接失败，请刷新页面重试');
            }
        }, 3000);
        return;
    }

    isCreatingSession = true;
    showLoadingOverlay('正在创建新项目...');

    sendWsMessage({ type: 'create_session' });

    setTimeout(() => {
        if (isCreatingSession) {
            isCreatingSession = false;
            hideLoadingOverlay();
            showToast('warning', '提示', '创建超时，请重试');
        }
    }, 10000);
}

function sendMessage() {
    const input = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const sendIcon = document.getElementById('sendIcon');
    const sendText = document.getElementById('sendText');
    let message = input.value.trim();

    if (!message) return;
    if (!currentSessionId) {
        showToast('warning', '提示', '请先创建项目');
        return;
    }

    sendBtn.disabled = true;
    sendIcon.textContent = '⏳';
    sendText.textContent = '处理中';

    if (selectedAgent) {
        message = `[${agentNames[selectedAgent]}] ${message}`;
        selectedAgent = null;
    }

    addMessage('user', '我', message);
    input.value = '';
    showTyping();

    sendWsMessage({ type: 'chat', message: message });

    setTimeout(() => {
        sendBtn.disabled = false;
        sendIcon.textContent = 'send';
        sendText.textContent = '发送';
    }, 3000);
}

function handleTyping() {
    if (typingTimeout) clearTimeout(typingTimeout);
    sendWsMessage({ type: 'typing', sender: 'user' });
}

function showTyping() {
    document.getElementById('typingIndicator').classList.remove('hidden');
    const messagesDiv = document.getElementById('messages');
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function hideTyping() {
    document.getElementById('typingIndicator').classList.add('hidden');
}

function addMessage(type, sender, content) {
    const messagesDiv = document.getElementById('messages');

    const emptyState = document.getElementById('emptyState');
    if (emptyState) {
        emptyState.classList.add('hidden');
    }

    const color = agentColors[type === 'user' ? 'user' : sender] || agentColors['system'];

    let renderedContent = content;
    if (typeof marked !== 'undefined' && typeof hljs !== 'undefined') {
        try {
            renderedContent = marked.parse(content, { breaks: true });
        } catch (e) {
            renderedContent = content.replace(/\n/g, '<br>');
        }
    } else {
        renderedContent = content.replace(/\n/g, '<br>');
    }

    const div = document.createElement('div');
    if (type === 'user') {
        div.className = 'flex flex-row-reverse items-start gap-4 max-w-[85%] ml-auto';
        div.innerHTML = `
            <div class="w-10 h-10 rounded-full bg-primary/20 flex-shrink-0 flex items-center justify-center border border-primary/30 shadow-sm overflow-hidden">
                <span class="text-primary">👤</span>
            </div>
            <div class="flex flex-col items-end gap-1">
                <span class="text-xs font-bold text-slate-400 mr-1">${sender}</span>
                <div class="bg-gradient-to-br from-primary to-secondary p-4 rounded-2xl rounded-tr-none shadow-md">
                    <div class="text-sm text-white leading-relaxed font-medium message-content">${renderedContent}</div>
                </div>
            </div>
        `;
    } else if (type === 'system') {
        div.className = 'flex justify-center my-4';
        div.innerHTML = `
            <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/50 px-6 py-3 rounded-full flex items-start gap-2 max-w-[80%]">
                <span class="text-amber-500 text-[18px] mt-0.5">⚠️</span>
                <p class="text-xs text-amber-700 dark:text-amber-400 font-medium whitespace-pre-line">${content}</p>
            </div>
        `;
    } else {
        div.className = 'flex items-start gap-4 max-w-[85%]';
        div.innerHTML = `
            <div class="w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center border shadow-sm" style="background: ${color}20; border-color: ${color}30;">
                <span style="color: ${color}">🤖</span>
            </div>
            <div class="flex flex-col gap-1">
                <span class="text-xs font-bold text-slate-400 ml-1">${sender}</span>
                <div class="bg-white dark:bg-slate-800 p-4 rounded-2xl rounded-tl-none shadow-sm border border-slate-200 dark:border-slate-700">
                    <div class="text-sm leading-relaxed message-content">${renderedContent}</div>
                </div>
            </div>
        `;
    }

    messagesDiv.appendChild(div);

    if (typeof hljs !== 'undefined') {
        div.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }

    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function loadTasks() {
    showTaskListSkeleton();
    try {
        const res = await fetch('/api/tasks');
        const data = await res.json();

        const container = document.getElementById('taskList');

        if (!data.tasks || data.tasks.length === 0) {
            container.innerHTML = '<div class="text-center py-4 text-slate-400 text-sm">暂无任务</div>';
            hideTaskListSkeleton();
            return;
        }

        container.innerHTML = data.tasks.map(task => {
            const colors = taskStateColors[task.state] || taskStateColors['pending'];
            const priorityLabels = { 'low': '低', 'medium': '中', 'high': '高' };
            const roleLabels = { 'dev': '开发', 'qa': '测试', 'ba': 'BA', 'architect': '架构师', 'pm': 'PM', 'hr': 'HR' };
            return `
                <div onclick="showTaskDetail('${task.id}')" class="${colors.bg} dark:bg-slate-800/50 p-3 rounded-lg border-l-4 ${colors.border} shadow-sm cursor-pointer hover:opacity-80 transition-opacity">
                    <div class="flex items-center justify-between mb-1">
                        <span class="text-xs font-bold ${colors.text}">${taskStateLabels[task.state] || '待处理'}</span>
                        <span class="text-[10px] text-slate-400">${priorityLabels[task.priority] || '中'}</span>
                    </div>
                    <p class="text-sm font-medium leading-tight">${task.title}</p>
                    ${task.assignee_role ? `<p class="text-[10px] text-slate-400 mt-1">负责人: ${roleLabels[task.assignee_role] || task.assignee_role}</p>` : ''}
                </div>
            `;
        }).join('');
        hideTaskListSkeleton();
    } catch (e) {
        console.error('加载任务失败:', e);
        hideTaskListSkeleton();
    }
}

function showTaskDetail(taskId) {
    console.log('Task clicked:', taskId);
}

async function loadSessionList() {
    try {
        const res = await fetch('/api/sessions');
        const data = await res.json();

        const container = document.getElementById('sessionList');

        if (!data.sessions || data.sessions.length === 0) {
            container.innerHTML = '<div class="text-center py-4 text-slate-400 text-xs">暂无历史会话</div>';
            return;
        }

        container.innerHTML = data.sessions.slice(0, 10).map(session => {
            const date = new Date(session.created_at);
            const dateStr = date.toLocaleDateString('zh-CN');
            const timeStr = date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
            return `
                <div onclick="loadSession('${session.id}')" class="flex items-center gap-2 p-2 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg cursor-pointer transition-colors">
                    <span class="text-slate-400 text-[16px]">💬</span>
                    <div class="flex-1 min-w-0">
                        <p class="text-xs font-medium truncate">${dateStr} ${timeStr}</p>
                    </div>
                </div>
            `;
        }).join('');
    } catch (e) {
        console.error('加载会话列表失败:', e);
    }
}

async function loadSession(sessionId) {
    showLoadingOverlay('加载会话中...');
    try {
        const res = await fetch(`/api/sessions/${sessionId}/load`, { method: 'POST' });
        if (!res.ok) {
            const err = await res.json();
            hideLoadingOverlay();
            showToast('error', '加载失败', err.detail || '无法加载会话');
            return;
        }
        const data = await res.json();
        hideLoadingOverlay();
        showToast('success', '加载成功', `已加载会话，包含 ${data.message_count} 条消息`);
        loadSessionList();
        loadTasks();
    } catch (e) {
        hideLoadingOverlay();
        showToast('error', '加载失败', e.message);
    }
}

async function addTask() {
    const title = document.getElementById('taskTitle').value.trim();
    const description = document.getElementById('taskDesc').value.trim();
    const assigneeRole = document.getElementById('taskAssignee').value;

    const priorityEl = document.querySelector('input[name="priority"]:checked');
    const priority = priorityEl ? priorityEl.value : 'medium';

    console.log('Adding task:', { title, description, assigneeRole, priority });

    if (!title) {
        showToast('warning', '提示', '请输入任务标题');
        return;
    }

    showProgressModal('创建任务', 10);

    try {
        updateProgress(30, '正在验证数据...');

        const res = await fetch('/api/tasks', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                title,
                description,
                assignee_role: assigneeRole,
                priority
            })
        });

        console.log('Add task response:', res.status, res.ok);

        updateProgress(60, '正在保存任务...');

        if (res.ok) {
            const data = await res.json();
            console.log('Task created:', data);

            updateProgress(90, '正在刷新列表...');

            hideAddTaskModal();
            await loadTasks();
            updateProgress();

            updateProgress(100, '任务创建完成');
            autoHideProgressModal(300);

            showToast('success', '成功', `任务 "${title}" 已创建`);
            document.getElementById('taskTitle').value = '';
            document.getElementById('taskDesc').value = '';
            document.getElementById('taskAssignee').value = '';
        } else {
            const err = await res.json();
            console.error('Error:', err);
            hideProgressModal();
            showToast('error', '添加失败', err.detail || '未知错误');
        }
    } catch (e) {
        console.error('Exception:', e);
        hideProgressModal();
        showToast('error', '添加失败', e.message);
    }
}

function updateSessionStatus(active) {
    const status = document.getElementById('sessionStatus');
    if (active) {
        status.innerHTML = `
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            进行中
        `;
        status.className = 'bg-emerald-500/20 text-emerald-100 text-xs px-2 py-1 rounded-full border border-emerald-500/30 flex items-center gap-1';
    } else {
        status.innerHTML = `
            <span class="w-1.5 h-1.5 rounded-full bg-red-400"></span>
            已结束
        `;
        status.className = 'bg-red-500/20 text-red-100 text-xs px-2 py-1 rounded-full border border-red-500/30 flex items-center gap-1';
    }
}

function updateProgress() {
    fetch('/api/tasks')
        .then(res => res.json())
        .then(data => {
            const tasks = data.tasks || [];
            if (tasks.length === 0) {
                document.getElementById('progressBar').style.width = '0%';
                document.getElementById('progressText').textContent = '0% 完成';
                return;
            }
            const done = tasks.filter(t => t.state === 'done').length;
            const percent = Math.round((done / tasks.length) * 100);
            document.getElementById('progressBar').style.width = percent + '%';
            document.getElementById('progressText').textContent = percent + '% 完成';
        });
}

function addActivity(type, text) {
    const container = document.getElementById('activityList');
    const time = new Date().toLocaleTimeString();

    const colorMap = {
        'task': 'bg-primary',
        'message': 'bg-blue-500',
        'session': 'bg-emerald-500'
    };

    const html = `
        <div class="flex gap-3 relative animate-slide-in">
            <div class="w-2 h-2 rounded-full ${colorMap[type] || 'bg-primary'} mt-1.5 shrink-0 z-10"></div>
            <div>
                <p class="text-xs font-bold">${text}</p>
                <p class="text-[10px] text-slate-400">${time}</p>
            </div>
        </div>
    `;

    container.insertAdjacentHTML('afterbegin', html);

    const activities = container.querySelectorAll('.relative');
    if (activities.length > 10) {
        activities[activities.length - 1].remove();
    }
}

function showToast(type, title, message) {
    const container = document.getElementById('toastContainer');

    const toastIcons = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    };

    const colors = {
        'success': 'bg-emerald-500/10 border-emerald-500/20 text-emerald-600',
        'error': 'bg-red-500/10 border-red-500/20 text-red-600',
        'warning': 'bg-amber-500/10 border-amber-500/20 text-amber-600',
        'info': 'bg-blue-500/10 border-blue-500/20 text-blue-600'
    };

    const id = 'toast-' + Date.now();

    const html = `
        <div id="${id}" class="flex items-start gap-3 p-4 rounded-xl border ${colors[type]} animate-slide-in">
            <span>${toastIcons[type]}</span>
            <div>
                <p class="font-semibold text-sm">${title}</p>
                <p class="text-xs opacity-80">${message}</p>
            </div>
        </div>
    `;

    container.insertAdjacentHTML('afterbegin', html);

    setTimeout(() => {
        const el = document.getElementById(id);
        if (el) el.remove();
    }, 5000);
}

function resetSendButton() {
    const sendBtn = document.getElementById('sendBtn');
    const sendIcon = document.getElementById('sendIcon');
    const sendText = document.getElementById('sendText');
    if (sendBtn && sendIcon && sendText) {
        sendBtn.disabled = false;
        sendIcon.textContent = 'send';
        sendText.textContent = '发送';
    }
}

function handleKeyPress(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
}

// ==================== Loading State Functions ====================

function showLoadingOverlay(text = '加载中...') {
    const overlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    loadingText.textContent = text;
    overlay.classList.remove('hidden');
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.classList.add('hidden');
}

function showInlineLoading(containerId = 'inlineLoading') {
    const loading = document.getElementById(containerId);
    if (loading) {
        loading.classList.remove('hidden');
        loading.classList.add('flex');
    }
}

function hideInlineLoading(containerId = 'inlineLoading') {
    const loading = document.getElementById(containerId);
    if (loading) {
        loading.classList.add('hidden');
        loading.classList.remove('flex');
    }
}

function showTaskListSkeleton() {
    document.getElementById('taskList').classList.add('hidden');
    document.getElementById('taskListSkeleton').classList.remove('hidden');
}

function hideTaskListSkeleton() {
    document.getElementById('taskListSkeleton').classList.add('hidden');
    document.getElementById('taskList').classList.remove('hidden');
}

function showMessageListSkeleton() {
    document.getElementById('emptyState')?.classList.add('hidden');
    document.getElementById('messageListSkeleton').classList.remove('hidden');
}

function hideMessageListSkeleton() {
    document.getElementById('messageListSkeleton').classList.add('hidden');
}

let progressModalTimeout = null;

function showProgressModal(title = '处理中', initialPercent = 0) {
    const modal = document.getElementById('progressModal');
    document.getElementById('progressTitle').textContent = title;
    document.getElementById('progressPercent').textContent = initialPercent + '%';
    document.getElementById('progressBarFill').style.width = initialPercent + '%';
    document.getElementById('progressStatus').textContent = '正在处理...';
    modal.classList.remove('hidden');
}

function updateProgress(percent, status = null) {
    const progressBarFill = document.getElementById('progressBarFill');
    const progressPercent = document.getElementById('progressPercent');
    const progressStatus = document.getElementById('progressStatus');

    progressBarFill.style.width = Math.min(100, Math.max(0, percent)) + '%';
    progressPercent.textContent = Math.round(Math.min(100, Math.max(0, percent))) + '%';

    if (status) {
        progressStatus.textContent = status;
    }
}

function hideProgressModal() {
    const modal = document.getElementById('progressModal');
    modal.classList.add('hidden');
    if (progressModalTimeout) {
        clearTimeout(progressModalTimeout);
        progressModalTimeout = null;
    }
}

function autoHideProgressModal(delay = 500) {
    if (progressModalTimeout) {
        clearTimeout(progressModalTimeout);
    }
    progressModalTimeout = setTimeout(() => {
        hideProgressModal();
    }, delay);
}

// ==================== User Menu Functions ====================

function toggleUserMenu() {
    const menu = document.getElementById('userMenu');
    if (!menu) {
        console.error('userMenu element not found');
        return;
    }

    if (!menu.innerHTML.trim() || menu.innerHTML.includes('will be dynamically updated')) {
        console.log('Menu is empty, calling updateUserUI()');
        updateUserUI();
    }

    menu.classList.toggle('hidden');
}

document.addEventListener('click', (e) => {
    const menu = document.getElementById('userMenu');
    const avatar = document.getElementById('userAvatar');
    if (menu && avatar && !menu.contains(e.target) && !avatar.contains(e.target)) {
        menu.classList.add('hidden');
    }
});

function showLoginModal() {
    document.getElementById('userMenu').classList.add('hidden');
    showToast('info', '提示', '登录功能开发中，敬请期待！');
}

function showSettingsModal() {
    document.getElementById('userMenu').classList.add('hidden');
    showConfigModal();
}

function toggleDarkMode() {
    document.getElementById('userMenu').classList.add('hidden');
    document.documentElement.classList.toggle('dark');

    const isDark = document.documentElement.classList.contains('dark');
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');

    if (isDark) {
        themeIcon.textContent = '☀️';
        themeText.textContent = '浅色模式';
        localStorage.setItem('theme', 'dark');
        showToast('success', '主题切换', '已切换到深色模式');
    } else {
        themeIcon.textContent = '🌙';
        themeText.textContent = '深色模式';
        localStorage.setItem('theme', 'light');
        showToast('success', '主题切换', '已切换到浅色模式');
    }
}

function showAboutModal() {
    document.getElementById('userMenu').classList.add('hidden');
    showToast('info', '关于', 'AI 协作团队 v1.0.0 - 多智能体协作系统');
}

function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');

    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark');
        themeIcon.textContent = '☀️';
        themeText.textContent = '浅色模式';
    } else {
        document.documentElement.classList.remove('dark');
        themeIcon.textContent = '🌙';
        themeText.textContent = '深色模式';
    }
}

initTheme();

// ==================== Authentication Functions ====================

let currentUser = null;
let authToken = null;

const TokenManager = {
    getToken() {
        return localStorage.getItem('auth_token');
    },

    setToken(token) {
        localStorage.setItem('auth_token', token);
        authToken = token;
    },

    removeToken() {
        localStorage.removeItem('auth_token');
        authToken = null;
    },

    getUser() {
        const userStr = localStorage.getItem('current_user');
        return userStr ? JSON.parse(userStr) : null;
    },

    setUser(user) {
        localStorage.setItem('current_user', JSON.stringify(user));
        currentUser = user;
    },

    removeUser() {
        localStorage.removeItem('current_user');
        currentUser = null;
    },

    isAuthenticated() {
        return !!this.getToken() && !!this.getUser();
    }
};

async function login(username, password) {
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '登录失败');
        }

        const data = await response.json();
        TokenManager.setToken(data.access_token);
        TokenManager.setUser(data.user);

        return data;
    } catch (error) {
        throw error;
    }
}

async function register(username, email, password) {
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                username,
                email,
                password,
                role: 'user'
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '注册失败');
        }

        return await response.json();
    } catch (error) {
        throw error;
    }
}

async function fetchCurrentUser() {
    const token = TokenManager.getToken();
    if (!token) return null;

    try {
        const response = await fetch('/api/auth/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            TokenManager.removeToken();
            TokenManager.removeUser();
            return null;
        }

        const user = await response.json();
        TokenManager.setUser(user);
        return user;
    } catch (error) {
        console.error('Failed to fetch user:', error);
        return null;
    }
}

function logout() {
    TokenManager.removeToken();
    TokenManager.removeUser();
    currentUser = null;
    authToken = null;
    updateUserUI();
    showToast('success', '已登出', '期待您的再次回来！');
}

function showAuthModal() {
    document.getElementById('authModal').classList.remove('hidden');
    document.getElementById('userMenu').classList.add('hidden');
}

function hideAuthModal() {
    document.getElementById('authModal').classList.add('hidden');
    document.getElementById('loginForm').reset();
    document.getElementById('registerForm').reset();
}

function showLoginForm() {
    document.getElementById('loginForm').classList.remove('hidden');
    document.getElementById('registerForm').classList.add('hidden');
    document.getElementById('authModalTitle').innerHTML = '<span class="text-primary">🔐</span> 登录';
}

function showRegisterForm() {
    document.getElementById('loginForm').classList.add('hidden');
    document.getElementById('registerForm').classList.remove('hidden');
    document.getElementById('authModalTitle').innerHTML = '<span class="text-primary">📝</span> 注册';
}

function updateUserUI() {
    const user = TokenManager.getUser();
    const userMenu = document.getElementById('userMenu');

    if (!userMenu) {
        console.error('userMenu element not found');
        return;
    }

    console.log('updateUserUI called, user:', user ? user.username : 'null');

    if (user) {
        const roleLabels = {
            'admin': '管理员',
            'user': '普通用户',
            'guest': '访客'
        };

        userMenu.innerHTML = `
            <div class="p-4 border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-primary text-lg">
                        ${user.username.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <p class="font-semibold text-slate-900 dark:text-white text-sm">${user.username}</p>
                        <p class="text-xs text-slate-500 dark:text-slate-400">${roleLabels[user.role] || user.role}</p>
                    </div>
                </div>
            </div>

            <div class="p-2 bg-white dark:bg-slate-800">
                <button onclick="showSettingsModal()" class="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
                    <span>⚙️</span>
                    <span>个人设置</span>
                </button>

                <button onclick="toggleDarkMode()" class="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
                    <span>🌙</span>
                    <span>深色模式</span>
                </button>

                <button onclick="openPluginManagementModal()" class="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
                    <span>🧩</span>
                    <span>插件管理</span>
                </button>
            </div>

            <div class="p-2 border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
                <button onclick="showAboutModal()" class="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
                    <span>ℹ️</span>
                    <span>关于</span>
                </button>

                <a href="https://github.com/aaaddduuu/SynergyAI" target="_blank" class="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
                    <span>📦</span>
                    <span>GitHub 仓库</span>
                </a>

                <button onclick="logout()" class="w-full flex items-center gap-3 px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors">
                    <span>🚪</span>
                    <span>退出登录</span>
                </button>
            </div>
        `;
    } else {
        userMenu.innerHTML = `
            <div class="p-4 border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-primary text-lg">
                        👤
                    </div>
                    <div>
                        <p class="font-semibold text-slate-900 dark:text-white text-sm">访客用户</p>
                        <p class="text-xs text-slate-500 dark:text-slate-400">未登录</p>
                    </div>
                </div>
            </div>

            <div class="p-2 bg-white dark:bg-slate-800">
                <button onclick="showAuthModal()" class="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
                    <span>🔐</span>
                    <span>登录 / 注册</span>
                </button>

                <button onclick="showSettingsModal()" class="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
                    <span>⚙️</span>
                    <span>个人设置</span>
                </button>

                <button onclick="toggleDarkMode()" class="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
                    <span>🌙</span>
                    <span>深色模式</span>
                </button>
            </div>

            <div class="p-2 border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
                <button onclick="showAboutModal()" class="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
                    <span>ℹ️</span>
                    <span>关于</span>
                </button>

                <a href="https://github.com/aaaddduuu/SynergyAI" target="_blank" class="w-full flex items-center gap-3 px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
                    <span>📦</span>
                    <span>GitHub 仓库</span>
                </a>
            </div>
        `;
    }
}

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!username || !password) {
        showToast('error', '错误', '请填写用户名和密码');
        return;
    }

    showLoadingOverlay('登录中...');

    try {
        const data = await login(username, password);
        hideAuthModal();
        hideLoadingOverlay();
        updateUserUI();
        showToast('success', '登录成功', `欢迎回来，${data.user.username}！`);
    } catch (error) {
        hideLoadingOverlay();
        showToast('error', '登录失败', error.message);
    }
});

document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('registerUsername').value.trim();
    const email = document.getElementById('registerEmail').value.trim();
    const password = document.getElementById('registerPassword').value;
    const passwordConfirm = document.getElementById('registerPasswordConfirm').value;

    if (!username || !email || !password) {
        showToast('error', '错误', '请填写所有必填项');
        return;
    }

    if (password !== passwordConfirm) {
        showToast('error', '错误', '两次输入的密码不一致');
        return;
    }

    if (password.length < 6) {
        showToast('error', '错误', '密码长度至少为6个字符');
        return;
    }

    showLoadingOverlay('注册中...');

    try {
        await register(username, email, password);
        hideLoadingOverlay();

        showToast('success', '注册成功', '请使用新账号登录');
        showLoginForm();
        document.getElementById('loginUsername').value = username;
    } catch (error) {
        hideLoadingOverlay();
        showToast('error', '注册失败', error.message);
    }
});

async function initAuth() {
    try {
        const token = TokenManager.getToken();
        console.log('initAuth: token exists?', !!token);

        if (token) {
            await fetchCurrentUser();
        }
        updateUserUI();
    } catch (error) {
        console.error('initAuth error:', error);
        updateUserUI();
    }
}

function hasPermission(requiredRole) {
    const user = TokenManager.getUser();
    if (!user) return false;

    const roleHierarchy = {
        'admin': 3,
        'user': 2,
        'guest': 1
    };

    const userLevel = roleHierarchy[user.role] || 0;
    const requiredLevel = roleHierarchy[requiredRole] || 0;

    return userLevel >= requiredLevel;
}

function requireAuth(callback) {
    if (!TokenManager.isAuthenticated()) {
        showToast('warning', '需要登录', '请先登录后再执行此操作');
        showAuthModal();
        return;
    }

    if (callback) callback();
}

function requireAdmin(callback) {
    if (!TokenManager.isAuthenticated()) {
        showToast('warning', '需要登录', '请先登录后再执行此操作');
        showAuthModal();
        return;
    }

    if (!hasPermission('admin')) {
        showToast('error', '权限不足', '此操作需要管理员权限');
        return;
    }

    if (callback) callback();
}

async function authFetch(url, options = {}) {
    const token = TokenManager.getToken();

    if (!token) {
        throw new Error('未登录');
    }

    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };

    const response = await fetch(url, {
        ...options,
        headers
    });

    if (response.status === 401) {
        TokenManager.removeToken();
        TokenManager.removeUser();
        updateUserUI();
        showToast('warning', '登录已过期', '请重新登录');
        showAuthModal();
        throw new Error('登录已过期');
    }

    return response;
}

// ==================== Team & Project Management ====================

async function loadTeams() {
    try {
        const response = await authFetch('/api/teams');
        if (!response.ok) throw new Error('获取团队列表失败');

        const data = await response.json();
        allTeams = data.teams || [];
        return allTeams;
    } catch (error) {
        console.error('Failed to load teams:', error);
        showToast('error', '错误', error.message);
        return [];
    }
}

async function loadProjects(teamId = null) {
    try {
        const url = teamId ? `/api/projects?team_id=${teamId}` : '/api/projects';
        const response = await authFetch(url);
        if (!response.ok) throw new Error('获取项目列表失败');

        const data = await response.json();
        allProjects = data.projects || [];
        return allProjects;
    } catch (error) {
        console.error('Failed to load projects:', error);
        showToast('error', '错误', error.message);
        return [];
    }
}

async function createTeam(name, description) {
    try {
        const response = await authFetch('/api/teams', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, description })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '创建团队失败');
        }

        const data = await response.json();
        await loadTeams();
        showToast('success', '成功', data.message);
        return data.team;
    } catch (error) {
        console.error('Failed to create team:', error);
        showToast('error', '错误', error.message);
        return null;
    }
}

async function createProject(teamId, name, description) {
    try {
        const response = await authFetch('/api/projects', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ team_id: teamId, name, description })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '创建项目失败');
        }

        const data = await response.json();
        await loadProjects(teamId);
        showToast('success', '成功', data.message);
        return data.project;
    } catch (error) {
        console.error('Failed to create project:', error);
        showToast('error', '错误', error.message);
        return null;
    }
}

async function switchTeam(teamId) {
    currentTeamId = teamId;
    await loadProjects(teamId);
    updateTeamProjectUI();
    showToast('success', '成功', `已切换到团队: ${teamId}`);
}

async function switchProject(projectId) {
    currentProjectId = projectId;
    const project = allProjects.find(p => p.id === projectId);
    if (project) {
        showToast('success', '成功', `已选择项目: ${project.name}`);
    }
}

function updateTeamProjectUI() {
    const teamSelect = document.getElementById('teamSelect');
    const projectSelect = document.getElementById('projectSelect');

    if (teamSelect) {
        teamSelect.innerHTML = '<option value="">选择团队...</option>' +
            allTeams.map(team =>
                `<option value="${team.id}" ${team.id === currentTeamId ? 'selected' : ''}>
                    ${team.name}
                </option>`
            ).join('');
    }

    if (projectSelect) {
        projectSelect.innerHTML = '<option value="">选择项目...</option>' +
            allProjects.map(project =>
                `<option value="${project.id}" ${project.id === currentProjectId ? 'selected' : ''}>
                    ${project.name}
                </option>`
            ).join('');
    }
}

// Enhanced create session with team/project context
function createSessionWithTeamProject(teamId, projectId) {
    currentTeamId = teamId;
    currentProjectId = projectId;

    sendWsMessage({
        type: 'create_session',
        team_id: teamId,
        project_id: projectId
    });
}

window.addEventListener('DOMContentLoaded', () => {
    console.log('Page loaded, initializing...');
    connectWebSocket();
    initAuth().catch(error => console.error('initAuth failed:', error));

    setInterval(() => {
        if (!wsConnected && reconnectAttempts < maxReconnectAttempts) {
            console.log('WebSocket not connected, attempting to reconnect...');
            connectWebSocket();
        }
    }, 30000);
});

// ============ 插件管理功能 ============

let allPlugins = [];
let pluginModalElement = null;

// 加载插件列表
async function loadPlugins() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/plugins', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('加载插件失败');
        }

        const data = await response.json();
        allPlugins = data.plugins || [];
        return allPlugins;
    } catch (error) {
        console.error('加载插件失败:', error);
        showToast('error', '错误', '加载插件列表失败');
        return [];
    }
}

// 渲染插件列表
function renderPlugins(plugins) {
    const container = document.getElementById('pluginsContainer');
    if (!container) return;

    if (plugins.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
                <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">暂无插件</h3>
                <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">创建您的第一个自定义智能体插件</p>
            </div>
        `;
        return;
    }

    container.innerHTML = plugins.map(plugin => `
        <div class="plugin-card bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div class="flex items-start justify-between">
                <div class="flex-1">
                    <div class="flex items-center gap-2">
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                            ${plugin.display_name}
                        </h3>
                        <span class="plugin-status-badge ${plugin.enabled ? 'plugin-status-enabled' : 'plugin-status-disabled'}">
                            ${plugin.enabled ? '已启用' : '已禁用'}
                        </span>
                    </div>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        ${plugin.description}
                    </p>
                    <div class="mt-3">
                        <span class="text-xs text-gray-500 dark:text-gray-500">角色: ${plugin.role}</span>
                    </div>
                    <div class="mt-2 flex flex-wrap gap-1">
                        ${plugin.capabilities.map(cap => `
                            <span class="plugin-capability-badge">${cap}</span>
                        `).join('')}
                    </div>
                    ${plugin.tags && plugin.tags.length > 0 ? `
                        <div class="mt-2 flex flex-wrap gap-1">
                            ${plugin.tags.map(tag => `
                                <span class="text-xs text-gray-500 dark:text-gray-500">#${tag}</span>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
                <div class="flex gap-2 ml-4">
                    <button onclick="editPlugin('${plugin.id}')" class="p-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-gray-700 rounded" title="编辑">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                    </button>
                    <button onclick="togglePlugin('${plugin.id}', ${!plugin.enabled})" class="p-2 ${plugin.enabled ? 'text-yellow-600' : 'text-green-600'} hover:bg-gray-50 dark:hover:bg-gray-700 rounded" title="${plugin.enabled ? '禁用' : '启用'}">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            ${plugin.enabled ?
                                '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />' :
                                '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />'
                            }
                        </svg>
                    </button>
                    <button onclick="exportPlugin('${plugin.id}')" class="p-2 text-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 rounded" title="导出">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                    </button>
                    <button onclick="deletePlugin('${plugin.id}')" class="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-gray-700 rounded" title="删除">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// 显示插件创建/编辑模态框
async function showPluginModal(pluginId = null) {
    const plugin = pluginId ? allPlugins.find(p => p.id === pluginId) : null;

    const modalHtml = `
        <div id="pluginModal" class="plugin-modal-overlay">
            <div class="plugin-modal-content">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100">
                        ${plugin ? '编辑插件' : '创建插件'}
                    </h2>
                    <button onclick="closePluginModal()" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <form id="pluginForm" onsubmit="savePlugin(event, '${pluginId || ''}')">
                    <div class="plugin-form-group">
                        <label class="plugin-form-label">插件名称 *</label>
                        <input type="text" name="name" class="plugin-form-input" value="${plugin?.name || ''}" required>
                    </div>

                    <div class="plugin-form-group">
                        <label class="plugin-form-label">显示名称 *</label>
                        <input type="text" name="display_name" class="plugin-form-input" value="${plugin?.display_name || ''}" required>
                    </div>

                    <div class="plugin-form-group">
                        <label class="plugin-form-label">角色标识符 *</label>
                        <input type="text" name="role" class="plugin-form-input" value="${plugin?.role || ''}" pattern="[a-z0-9_]+" title="只能包含小写字母、数字和下划线" required>
                        <p class="text-xs text-gray-500 mt-1">只能包含小写字母、数字和下划线</p>
                    </div>

                    <div class="plugin-form-group">
                        <label class="plugin-form-label">描述 *</label>
                        <textarea name="description" class="plugin-form-textarea" required>${plugin?.description || ''}</textarea>
                    </div>

                    <div class="plugin-form-group">
                        <label class="plugin-form-label">系统提示词 *</label>
                        <textarea name="system_prompt" class="plugin-form-textarea" style="min-height: 200px;" required>${plugin?.system_prompt || ''}</textarea>
                    </div>

                    <div class="plugin-form-group">
                        <label class="plugin-form-label">能力列表 *（每行一个能力）</label>
                        <textarea name="capabilities" class="plugin-form-textarea" required>${plugin?.capabilities?.join('\n') || ''}</textarea>
                    </div>

                    <div class="plugin-form-group">
                        <label class="plugin-form-label">标签（逗号分隔）</label>
                        <input type="text" name="tags" class="plugin-form-input" value="${plugin?.tags?.join(', ') || ''}">
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                        <div class="plugin-form-group">
                            <label class="plugin-form-label">温度</label>
                            <input type="number" name="temperature" class="plugin-form-input" value="${plugin?.temperature || 0.7}" min="0" max="2" step="0.1">
                        </div>

                        <div class="plugin-form-group">
                            <label class="plugin-form-label">最大 Token 数</label>
                            <input type="number" name="max_tokens" class="plugin-form-input" value="${plugin?.max_tokens || 2000}" min="100" max="8000">
                        </div>
                    </div>

                    <div class="flex justify-end gap-2 mt-6">
                        <button type="button" onclick="closePluginModal()" class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                            取消
                        </button>
                        <button type="submit" class="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded">
                            ${plugin ? '更新' : '创建'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);
    pluginModalElement = document.getElementById('pluginModal');
}

// 关闭插件模态框
function closePluginModal() {
    if (pluginModalElement) {
        pluginModalElement.remove();
        pluginModalElement = null;
    }
}

// 保存插件
async function savePlugin(event, pluginId) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    const pluginData = {
        name: formData.get('name'),
        display_name: formData.get('display_name'),
        role: formData.get('role'),
        description: formData.get('description'),
        system_prompt: formData.get('system_prompt'),
        capabilities: formData.get('capabilities').split('\n').filter(c => c.trim()),
        tags: formData.get('tags').split(',').map(t => t.trim()).filter(t => t),
        temperature: parseFloat(formData.get('temperature')),
        max_tokens: parseInt(formData.get('max_tokens'))
    };

    try {
        const token = localStorage.getItem('token');
        const url = pluginId ? `/api/plugins/${pluginId}` : '/api/plugins';
        const method = pluginId ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(pluginData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '保存失败');
        }

        showToast('success', '成功', pluginId ? '插件更新成功' : '插件创建成功');
        closePluginModal();
        await loadAndRenderPlugins();
    } catch (error) {
        console.error('保存插件失败:', error);
        showToast('error', '错误', error.message);
    }
}

// 编辑插件
async function editPlugin(pluginId) {
    await showPluginModal(pluginId);
}

// 切换插件启用状态
async function togglePlugin(pluginId, enable) {
    try {
        const token = localStorage.getItem('token');
        const url = `/api/plugins/${pluginId}/${enable ? 'enable' : 'disable'}`;

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('操作失败');
        }

        showToast('success', '成功', enable ? '插件已启用' : '插件已禁用');
        await loadAndRenderPlugins();
    } catch (error) {
        console.error('切换插件状态失败:', error);
        showToast('error', '错误', '操作失败');
    }
}

// 删除插件
async function deletePlugin(pluginId) {
    if (!confirm('确定要删除这个插件吗？')) {
        return;
    }

    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/plugins/${pluginId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('删除失败');
        }

        showToast('success', '成功', '插件已删除');
        await loadAndRenderPlugins();
    } catch (error) {
        console.error('删除插件失败:', error);
        showToast('error', '错误', '删除失败');
    }
}

// 导出插件
async function exportPlugin(pluginId) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/plugins/${pluginId}/export`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('导出失败');
        }

        const data = await response.json();
        const jsonStr = JSON.stringify(data.plugin, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `plugin_${data.plugin.role}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        showToast('success', '成功', '插件已导出');
    } catch (error) {
        console.error('导出插件失败:', error);
        showToast('error', '错误', '导出失败');
    }
}

// 导入插件
async function importPlugin() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';

    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
            const text = await file.text();
            const pluginData = JSON.parse(text);

            const token = localStorage.getItem('token');
            const response = await fetch('/api/plugins/import', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(pluginData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || '导入失败');
            }

            showToast('success', '成功', '插件已导入');
            await loadAndRenderPlugins();
        } catch (error) {
            console.error('导入插件失败:', error);
            showToast('error', '错误', error.message);
        }
    };

    input.click();
}

// 加载并渲染插件
async function loadAndRenderPlugins() {
    const plugins = await loadPlugins();
    renderPlugins(plugins);
}

// 搜索插件
function searchPlugins(keyword) {
    if (!keyword) {
        renderPlugins(allPlugins);
        return;
    }

    const filtered = allPlugins.filter(p =>
        p.name.toLowerCase().includes(keyword.toLowerCase()) ||
        p.description.toLowerCase().includes(keyword.toLowerCase()) ||
        p.role.toLowerCase().includes(keyword.toLowerCase()) ||
        p.tags.some(tag => tag.toLowerCase().includes(keyword.toLowerCase()))
    );

    renderPlugins(filtered);
}

// 打开插件管理模态框
function openPluginManagementModal() {
    const modal = document.getElementById('pluginManagementModal');
    if (modal) {
        modal.classList.remove('hidden');
        loadAndRenderPlugins();
    }
}

// 关闭插件管理模态框
function closePluginManagementModal() {
    const modal = document.getElementById('pluginManagementModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// ==================== Mobile Support Functions ====================

// 切换移动端侧边栏
function toggleMobileSidebar() {
    const sidebar = document.getElementById('leftSidebar');
    const overlay = document.getElementById('mobileSidebarOverlay');

    if (sidebar && overlay) {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('open');
    }
}

// 关闭移动端侧边栏
function closeMobileSidebar() {
    const sidebar = document.getElementById('leftSidebar');
    const overlay = document.getElementById('mobileSidebarOverlay');

    if (sidebar && overlay) {
        sidebar.classList.remove('open');
        overlay.classList.remove('open');
    }
}

// 检测设备是否为触摸设备
function isTouchDevice() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
}

// 优化触摸事件 - 防止双击缩放
function initTouchOptimization() {
    if (!isTouchDevice()) return;

    // 为所有按钮添加触摸优化
    const buttons = document.querySelectorAll('button, .agent-item, .mobile-touch-btn');
    buttons.forEach(btn => {
        btn.addEventListener('touchstart', function() {
            this.classList.add('touching');
        }, { passive: true });

        btn.addEventListener('touchend', function() {
            this.classList.remove('touching');
        }, { passive: true });

        btn.addEventListener('touchcancel', function() {
            this.classList.remove('touching');
        }, { passive: true });
    });

    // 防止双击缩放和长按选择
    document.addEventListener('touchstart', function(event) {
        if (event.touches.length > 1) {
            event.preventDefault();
        }
    }, { passive: false });

    // 优化表单输入
    const inputs = document.querySelectorAll('input, textarea');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            // 输入框获得焦点时关闭侧边栏
            closeMobileSidebar();
        });
    });
}

// 监听窗口大小变化
function handleResize() {
    const width = window.innerWidth;

    // 当窗口宽度大于1024px时，确保侧边栏关闭
    if (width >= 1024) {
        closeMobileSidebar();
    }
}

// 初始化移动端支持
function initMobileSupport() {
    // 添加窗口大小变化监听
    window.addEventListener('resize', handleResize);

    // 初始化触摸优化
    initTouchOptimization();

    // 点击模态框外部关闭模态框（移动端）
    const modals = document.querySelectorAll('[id$="Modal"]');
    modals.forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this && isTouchDevice()) {
                this.classList.add('hidden');
            }
        });
    });

    // 优化滚动性能
    if (isTouchDevice()) {
        const scrollContainers = document.querySelectorAll('.mobile-scroll');
        scrollContainers.forEach(container => {
            container.style.webkitOverflowScrolling = 'touch';
        });
    }

    console.log('Mobile support initialized');
}

// 页面加载完成后初始化移动端支持
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMobileSupport);
} else {
    initMobileSupport();
}

// 添加触摸设备CSS样式
const touchStyles = document.createElement('style');
touchStyles.textContent = `
    .touching {
        opacity: 0.7 !important;
        transform: scale(0.98) !important;
    }
`;
document.head.appendChild(touchStyles);

});
