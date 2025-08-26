let currentPage = 1;
const recordsPerPage = 10;
let conversationHistory = []; // 存储对话历史
let currentDevice = null; // 当前设备信息

// 页面加载时获取维修记录
document.addEventListener('DOMContentLoaded', function() {
    loadMaintenanceRecords();
    
    // 设置日期默认值为今天
    document.getElementById('maintenance_date').valueAsDate = new Date();
    
    // 分页按钮事件
    document.getElementById('prevPage').addEventListener('click', function() {
        if (currentPage > 1) {
            currentPage--;
            loadMaintenanceRecords();
        }
    });
    
    document.getElementById('nextPage').addEventListener('click', function() {
        currentPage++;
        loadMaintenanceRecords();
    });
});


// // 加载维修记录
// function loadMaintenanceRecords() {
//     fetch(`/api/maintenance?page=${currentPage}&per_page=${recordsPerPage}`)
//         .then(response => response.json())
//         .then(data => {
//             populateTable(data.records);
//             updatePagination(data.total_records);
//         })
//         .catch(error => {
//             console.error('获取维修记录失败:', error);
//             alert('获取维修记录失败');
//         });
// }

// 更新加载函数，支持从URL参数过滤
function loadMaintenanceRecords() {
    const urlParams = new URLSearchParams(window.location.search);
    const deviceId = urlParams.get('device_id');
    
    let apiUrl = `/api/maintenance?page=${currentPage}&per_page=${recordsPerPage}`;
    if (deviceId) {
        console.log('按设备ID过滤:', deviceId);
        apiUrl = `/api/maintenance/search?device_id=${deviceId}`;
    }else{
        console.log('加载所有维修记录');
    }
    
    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            if (deviceId) {
                // 处理搜索结果的格式
                populateTable(data.records);
                document.getElementById('prevPage').disabled = true;
                document.getElementById('nextPage').disabled = true;
                document.getElementById('pageInfo').textContent = `设备 ${deviceId} 的维修记录`;
            } else {
                populateTable(data.records);
                updatePagination(data.total_records);
            }
        })
        .catch(error => {
            console.error('获取维修记录失败:', error);
            alert('获取维修记录失败');
        });
}


// 填充表格数据
function populateTable(records) {
    console.log('populateTable records:', records);

    const tbody = document.querySelector('#maintenanceTable tbody');
    tbody.innerHTML = '';
    
    if (records.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="6" style="text-align:center;">没有找到维修记录</td>';
        tbody.appendChild(row);
        return;
    }
    
    records.forEach(record => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${record.device_id}</td>
            <td>${record.maintenance_date}</td>
            <td>${record.fault_code || '-'}</td>
            <td>${record.fault_phenomenon ? record.fault_phenomenon.substring(0, 20) + (record.fault_phenomenon.length > 20 ? '...' : '') : '-'}</td>
            <td>${record.maintenance_personnel || '-'}</td>
            <td>
                <button class="detail-btn" onclick="viewDetail(${record.id})">详情</button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// 更新分页状态
function updatePagination(totalRecords) {
    const totalPages = Math.ceil(totalRecords / recordsPerPage);
    document.getElementById('pageInfo').textContent = `第 ${currentPage} 页 / 共 ${totalPages} 页`;
    
    document.getElementById('prevPage').disabled = currentPage <= 1;
    document.getElementById('nextPage').disabled = currentPage >= totalPages;
}

// 查询记录
function searchRecords() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) {
        loadMaintenanceRecords();
        return;
    }
    
    fetch(`/api/maintenance/search?device_id=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            console.log('searchRecords data:', data);

            populateTable(data.records);
            document.getElementById('prevPage').disabled = true;
            document.getElementById('nextPage').disabled = true;
            document.getElementById('pageInfo').textContent = `找到 ${data.length} 条记录`;
        })
        .catch(error => {
            console.error('搜索失败:', error);
            alert('搜索失败');
        });
}

// 重置查询
function resetSearch() {
    document.getElementById('searchInput').value = '';
    currentPage = 1;
    loadMaintenanceRecords();
}

// 显示新增表单
function showAddForm() {
    document.getElementById('addForm').style.display = 'block';
}

// 隐藏新增表单
function hideAddForm() {
    document.getElementById('addForm').style.display = 'none';
}

// 提交新增表单
function submitForm(event) {
    event.preventDefault();
    
    const formData = {
        device_id: document.getElementById('device_id').value,
        maintenance_date: document.getElementById('maintenance_date').value,
        fault_code: document.getElementById('fault_code').value,
        fault_phenomenon: document.getElementById('fault_phenomenon').value,
        maintenance_personnel: document.getElementById('maintenance_personnel').value
    };
    
    fetch('/api/mradd', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (response.ok) {
            alert('维修记录添加成功');
            hideAddForm();
            loadMaintenanceRecords();
        } else {
            alert('添加失败');
        }
    })
    .catch(error => {
        console.error('添加失败:', error);
        alert('添加失败');
    });
}

// 查看详情
function viewDetail(recordId) {
    fetch(`/api/mrdetail/${recordId}`)
        .then(response => response.json())
        .then(record => {
            alert(`维修记录详情：
设备编号: ${record.device_id}
维护日期: ${record.maintenance_date}
故障代码: ${record.fault_code || '无'}
故障现象: ${record.fault_phenomenon || '无'}
原因分析: ${record.cause_analysis || '无'}
采取措施: ${record.measures_taken || '无'}
更换部件: ${record.replaced_parts || '无'}
耗时(小时): ${record.time_consumed || '无'}
维修人员: ${record.maintenance_personnel || '无'}`);
        })
        .catch(error => {
            console.error('获取详情失败:', error);
            alert('获取详情失败');
        });
}


// 初始化聊天界面
function initChat() {
    // 从URL获取设备ID
    const params = new URLSearchParams(window.location.search);
    currentDevice = params.get('device_id');
    
    if (currentDevice) {
        // 显示欢迎消息
        addMessage('ai', `您好！我是${currentDevice}设备的AI维修助手。请问有什么可以帮您？`);
        
        // 加载设备维护历史
        loadDeviceHistory(currentDevice);
    } else {
        addMessage('ai', '请先选择要咨询的设备。');
    }
    
    // 设置输入框事件监听
    setupInputEvents();
}

// 加载设备维护历史
function loadDeviceHistory(deviceId) {
    fetch(`/api/device_history?device_id=${deviceId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('获取历史失败');
            }
            return response.json();
        })
        .then(data => {
            // 显示设备信息和历史记录
            let historyMessage = `设备型号: ${data.model}\n`;
            historyMessage += `生产厂家: ${data.manufacturer}\n`;
            historyMessage += `安装位置: ${data.location}\n\n`;
            
            if (data.history.length > 0) {
                historyMessage += `最近维护记录:\n`;
                data.history.forEach(record => {
                    historyMessage += `${record.date} - ${record.code}: ${record.phenomenon}\n`;
                });
            } else {
                historyMessage += `暂无维护记录`;
            }
            
            addMessage('ai', historyMessage);
        })
        .catch(error => {
            console.error('加载历史失败:', error);
            addMessage('ai', '加载设备历史记录失败');
        });
}

// 设置输入框事件
function setupInputEvents() {
    const input = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendButton');
    
    // Enter键发送消息 (Shift+Enter换行)
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendToDeepSeek();
        }
    });
    
    // 发送按钮点击事件
    sendBtn.addEventListener('click', sendToDeepSeek);
}

// 发送消息到DeepSeek
async function sendToDeepSeek() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (!message) return;
    if (!currentDevice) {
        alert('请先选择设备');
        return;
    }
    
    // 添加用户消息到界面
    addMessage('user', message);
    input.value = ''; // 清空输入框
    
    try {
        // 显示"思考中"状态
        const thinkingId = addThinkingMessage();
        
        // 构建请求数据
        const requestData = {
            device_id: currentDevice,
            message: message,
            conversation: conversationHistory
        };
        
        // 调用后端API
        const response = await fetch('/api/deepseek_chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || '请求失败');
        }
        
        // 移除"思考中"消息
        removeMessage(thinkingId);
        
        // 添加AI回复
        addMessage('ai', data.response);
        
        // 更新对话历史
        updateConversationHistory(message, data.response);
        
    } catch (error) {
        //removeThinkingMessage();
        addMessage('ai', `错误: ${error.message}`);
        console.error('API调用失败:', error);
    }
}

// 添加消息到聊天界面
function addMessage(role, content) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    
    // 生成唯一ID用于后续操作
    const messageId = 'msg-' + Date.now();
    
    messageDiv.id = messageId;
    messageDiv.className = `message ${role}-message`;
    messageDiv.textContent = content;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight; // 滚动到底部
    
    return messageId;
}

// 添加"思考中"消息
function addThinkingMessage() {
    return addMessage('ai', '思考中...');
}

// 移除消息
function removeMessage(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

// 更新对话历史
function updateConversationHistory(userMessage, aiResponse) {
    // 保留最近10轮对话
    if (conversationHistory.length > 20) {
        conversationHistory = conversationHistory.slice(-20);
    }
    
    // 添加新对话
    conversationHistory.push(
        { role: 'user', content: userMessage },
        { role: 'assistant', content: aiResponse }
    );
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', initChat);