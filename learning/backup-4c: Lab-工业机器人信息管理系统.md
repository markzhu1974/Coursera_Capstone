
### 里程碑三：调用ChatGPT的API给出维修指导

在这个里程碑中，我们将为系统注入“智能”。当维修人员输入故障代码和现象时，系统将调用OpenAI的ChatGPT API，获取专业的维修建议，并将其展示在前端界面上。

#### 步骤 1: 注册OpenAI API并获取密钥

要使用ChatGPT的功能，你必须先拥有一个OpenAI的API密钥。

1.  **访问OpenAI平台**: 打开浏览器，访问 [https://platform.openai.com/](https://platform.openai.com/)。
2.  **注册或登录**: 如果你没有账户，需要创建一个新账户（可能需要邮箱和手机号验证）。如果已有账户，请直接登录。
3.  **创建API密钥**:
      * 登录后，点击页面右上角的你的头像或组织名称，选择 "View API keys"。
      * 在API keys页面，点击 "**Create new secret key**" 按钮。
      * 给你的密钥起一个名字（例如 `IRIMS-Project`），然后点击 "Create secret key"。
      * **立即复制并保存你的密钥！** OpenAI只会显示这一次完整的密钥，关闭弹窗后你将无法再次看到它。请将它保存在一个安全的地方，比如密码管理器或一个私密的文本文件中。

**重要提示**:

  * **API密钥非常重要，等同于你的密码，绝对不要分享给他人或提交到公共代码仓库（如GitHub）中。**
  * OpenAI API是付费服务。新用户通常会获得一定的免费额度，足够完成本教程的学习。你可以在 "Usage" 页面查看你的余额。

#### 步骤 2: 后端集成 (`server.py`)

现在，我们将修改后端服务器，使其能够与OpenAI API通信。

**A. 安装OpenAI Python库**

首先，我们需要安装官方的 `openai` Python库。打开你的终端（确保你的Python服务器已停止，按 `Ctrl+C`），然后运行以下命令：

```bash
pip install openai
```

**B. 安全地配置API密钥**

为了不将密钥硬编码在代码中，我们使用环境变量来存储它。这是一种更安全、更灵活的做法。

  * **在 Windows 上设置:**
    ```bash
    set OPENAI_API_KEY="你的密钥粘贴在这里"
    ```
    (注意: 这种方式只在当前终端窗口有效。要永久设置，请搜索“编辑系统环境变量”)
  * **在 macOS 或 Linux 上设置:**
    ```bash
    export OPENAI_API_KEY="你的密钥粘贴在这里"
    ```
    (这种方式也只在当前终端窗口有效。要永久设置，可以将其添加到 `~/.bashrc` 或 `~/.zshrc` 文件中)

**C. 修改 `server.py`**

我们将添加一个新的API端点 `/api/suggestion`，它接收故障信息，调用OpenAI，然后返回建议。

```python
# 导入所需模块 (在顶部添加 openai)
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sqlite3
import os
from urllib.parse import urlparse, parse_qs
import openai # <-- 新增导入

# --- 安全地加载API密钥 ---
# 从环境变量中获取API密钥
# 如果找不到环境变量，则设置为None，这样程序会报错而不是暴露问题
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    # 如果没有设置环境变量，打印错误信息并退出
    print("错误: 请设置 OPENAI_API_KEY 环境变量。")
    # exit() # 在生产环境中，你可能希望直接退出

# --- 数据库操作函数 (全部保持不变) ---
# ... get_all_robots, add_robot, 等函数 ...

# --- 新增的ChatGPT调用函数 ---
def get_chatgpt_suggestion(fault_code, phenomenon):
    # 检查API密钥是否已配置
    if not openai.api_key:
        return "错误: OpenAI API 密钥未配置。"

    try:
        # 创建一个OpenAI客户端实例
        client = openai.OpenAI()

        # --- 精心设计的Prompt ---
        # 这是调用AI最关键的部分。一个好的Prompt能让AI更好地理解你的意图。
        prompt_message = f"""
        作为一个资深的工业机器人维修专家，请根据以下信息提供维修建议。

        **故障信息:**
        - 故障代码: {fault_code}
        - 故障现象: {phenomenon}

        **请按照以下格式，用中文清晰地回答:**

        **1. 可能的原因分析:**
        [请在这里列出1-3个最可能导致此故障的原因]

        **2. 推荐的排查步骤:**
        [请在这里提供一步步的诊断和排查指南]

        **3. 建议的解决措施:**
        [请在这里给出具体的维修或更换建议]

        请确保你的回答专业、严谨且易于理解。
        """

        # 调用OpenAI的Chat Completions API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 使用性价比高的 gpt-3.5-turbo 模型
            messages=[
                {"role": "system", "content": "你是一个工业机器人维修专家。"}, # 给AI设定一个角色
                {"role": "user", "content": prompt_message} # 用户提出的具体问题
            ],
            temperature=0.5, # 设置温度，较低的值使输出更确定和一致
        )
        
        # 从响应中提取AI生成的文本内容
        suggestion = response.choices[0].message.content
        return suggestion

    except Exception as e:
        # 捕获并返回任何可能发生的错误（如网络问题、认证失败等）
        print(f"调用OpenAI API时发生错误: {e}")
        return f"无法获取AI建议，发生错误: {e}"


# --- HTTP请求处理类 (RequestHandler) ---
class RequestHandler(BaseHTTPRequestHandler):
    
    # do_GET 方法保持不变
    def do_GET(self):
        # ... (代码不变) ...

    # 修改 do_POST 方法以处理新的API请求
    def do_POST(self):
        # API请求：添加新机器人
        if self.path == '/api/robots':
            # ... (代码不变) ...
        
        # API请求：添加新维修记录
        elif self.path == '/api/maintenance':
            # ... (代码不变) ...

        # --- 新增代码开始 ---
        # API请求：获取ChatGPT维修建议
        elif self.path == '/api/suggestion':
            content_length = int(self.headers['Content-Length']) # 获取请求体长度
            post_data = self.rfile.read(content_length) # 读取数据
            data = json.loads(post_data) # 解析JSON
            
            # 从请求数据中获取故障代码和现象
            fault_code = data.get('fault_code')
            phenomenon = data.get('phenomenon')
            
            # 调用函数获取AI建议
            suggestion = get_chatgpt_suggestion(fault_code, phenomenon)
            
            # 准备返回给前端的JSON数据
            response_data = {'suggestion': suggestion}
            
            self.send_response(200) # 发送200 OK
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8')) # 返回建议
        # --- 新增代码结束 ---
        
    # do_PUT 和 do_DELETE 方法保持不变
    def do_PUT(self):
        # ... (代码不变) ...

    def do_DELETE(self):
        # ... (代码不变) ...

# --- 启动服务器 (保持不变) ---
# ... run() and __main__ block ...
```

#### 步骤 3: 前端集成 (`web/index.html` 和 `web/style.css`)

最后，我们在前端界面上添加一个按钮来触发AI建议功能，并添加一个区域来显示结果。

**A. 修改 `web/index.html`:**

```html
<div id="maintenance-view" style="display: none;">
    <h1 id="maintenance-title">维修记录</h1>
    <button onclick="showRobotView()">返回机器人列表</button>

    <h2>添加新维修记录</h2>
    <div class="form-container">
        <form id="maintenance-form">
            <input type="hidden" id="maint-robot-device-id">
            <input type="date" id="maintenance_date" required>
            <input type="text" id="technician" placeholder="维修人员" required>
            
            <div class="input-group">
                <input type="text" id="fault_code" placeholder="故障代码 (例如 ERR-105)">
                <button type="button" id="get-suggestion-btn" onclick="fetchAiSuggestion()">获取AI建议</button>
            </div>

            <input type="number" id="duration" placeholder="耗时(小时)" step="0.1">
            <textarea id="phenomenon" placeholder="故障现象 (例如 机器人2轴异响)"></textarea>
            
            <div id="ai-suggestion-container" style="display: none;">
                <h3>AI 维修建议 <span id="loading-indicator" style="display: none;">正在思考中...</span></h3>
                <pre id="ai-suggestion-box"></pre> </div>
            <textarea id="analysis" placeholder="原因分析"></textarea>
            <textarea id="measures" placeholder="采取措施"></textarea>
            <textarea id="parts_replaced" placeholder="更换部件"></textarea>
            <button type="submit">保存记录</button>
        </form>
    </div>

    </div>

<script>
// ... (DOMContentLoaded 和大部分函数保持不变) ...

// --- 新增的AI建议相关函数 ---

// 异步函数：获取AI建议
async function fetchAiSuggestion() {
    // 从表单获取故障代码和现象
    const fault_code = document.getElementById('fault_code').value;
    const phenomenon = document.getElementById('phenomenon').value;

    // 简单验证
    if (!fault_code || !phenomenon) {
        alert('请输入故障代码和故障现象以获取AI建议。');
        return;
    }
    
    // 获取相关元素
    const suggestionContainer = document.getElementById('ai-suggestion-container');
    const suggestionBox = document.getElementById('ai-suggestion-box');
    const loadingIndicator = document.getElementById('loading-indicator');
    const getBtn = document.getElementById('get-suggestion-btn');

    // 显示加载状态
    suggestionContainer.style.display = 'block';
    suggestionBox.textContent = ''; // 清空旧内容
    loadingIndicator.style.display = 'inline';
    getBtn.disabled = true; // 禁用按钮防止重复点击
    getBtn.textContent = '正在获取...';

    try {
        // 向后端发送POST请求
        const response = await fetch('/api/suggestion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fault_code, phenomenon }), // 发送数据
        });

        if (response.ok) {
            const data = await response.json();
            // 将返回的建议显示在pre标签中
            suggestionBox.textContent = data.suggestion;
        } else {
            // 如果请求失败，显示错误信息
            suggestionBox.textContent = '获取建议失败，请检查服务器日志。';
        }
    } catch (error) {
        // 捕获网络等错误
        console.error('获取AI建议时出错:', error);
        suggestionBox.textContent = '无法连接到服务器。';
    } finally {
        // 无论成功与否，都隐藏加载状态并恢复按钮
        loadingIndicator.style.display = 'none';
        getBtn.disabled = false;
        getBtn.textContent = '获取AI建议';
    }
}
// ... (其他JS函数保持不变) ...
</script>
```

**B. 修改 `web/style.css`:**

最后，添加一些样式来美化新的UI元素。在 `style.css` 文件末尾添加：

```css
/* ... (之前的CSS代码保持不变) ... */

/* 用于包裹输入框和按钮的组 */
.input-group {
    display: flex; /* 使用flex布局 */
    margin-bottom: 10px;
}
.input-group input {
    flex-grow: 1; /* 输入框占据剩余空间 */
    margin-bottom: 0; /* 移除单独的下外边距 */
}
.input-group button {
    width: auto; /* 按钮宽度自适应内容 */
    margin-left: 10px; /* 和输入框留出间距 */
    white-space: nowrap; /* 防止按钮文字换行 */
}

/* AI建议按钮的特定样式 */
#get-suggestion-btn {
    background-color: #28a745; /* 绿色 */
}
#get-suggestion-btn:hover {
    background-color: #218838;
}
#get-suggestion-btn:disabled {
    background-color: #aaa; /* 禁用时的颜色 */
    cursor: not-allowed;
}

/* AI建议显示容器的样式 */
#ai-suggestion-container {
    margin-top: 15px;
    margin-bottom: 15px;
}
#ai-suggestion-container h3 {
    margin-bottom: 5px;
    color: #0056b3;
}

/* AI建议文本框的样式 */
#ai-suggestion-box {
    background-color: #e9ecef;
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 15px;
    white-space: pre-wrap; /* 关键：保留换行和空格 */
    word-wrap: break-word; /* 自动换行 */
    min-height: 100px;
    font-family: Consolas, 'Courier New', monospace; /* 使用等宽字体，看起来更像代码 */
    color: #333;
}

/* 加载指示器样式 */
#loading-indicator {
    color: #666;
    font-style: italic;
    font-size: 0.9em;
    margin-left: 10px;
}
```

#### 步骤 4: 最终运行和测试

1.  **停止旧服务器**: 如果正在运行，按 `Ctrl + C` 停止。
2.  **设置环境变量**: 确保你已经在终端中设置了 `OPENAI_API_KEY`。
3.  **启动服务器**:
    ```bash
    python server.py
    ```
4.  **访问和测试**:
      * 在浏览器刷新 `http://localhost:8000`。
      * 进入任意一个机器人的“查看维修记录”页面。
      * 在“故障代码”输入框中输入一个虚构但合理的代码，例如 `ERR-050-COMM`。
      * 在“故障现象”输入框中输入描述，例如 `机器人无法与控制器建立通讯，示教器屏幕显示连接超时`。
      * 点击绿色的“获取AI建议”按钮。
      * 你应该会看到按钮变为“正在获取...”，并且旁边出现“正在思考中...”的提示。
      * 几秒钟后，下方的AI建议框中应该会出现由ChatGPT生成的、格式化的维修建议！
      * 你可以将AI给出的建议作为参考，填写到“原因分析”和“采取措施”的文本框中，然后保存整个维修记录。

**恭喜你！你已经成功完成了整个工业机器人信息管理系统的开发！**

你从零开始，用最基础的前端和后端技术，不仅搭建了一个功能完善的CRUD应用，还成功地集成了一流的AI服务，为你的应用赋予了强大的智能。

-----

### 总结与展望

通过这三个里程碑，你学习了：

  * 如何使用Python原生`http.server`处理GET, POST, PUT, DELETE请求，构建RESTful API。
  * 如何使用HTML, CSS, 和原生JavaScript构建动态的前端界面，并通过`fetch`与后端交互。
  * 如何使用SQLite作为轻量级数据库，并用Python进行数据操作。
  * 如何将多个视图整合到一个单页面应用(SPA)中。
  * **如何安全地调用强大的外部API（如OpenAI），并将AI能力集成到你的项目中。**

**下一步可以探索的方向:**

  * **用户认证**: 添加登录和注册功能。
  * **部署**: 将你的应用部署到云服务器上，让任何人都可以访问。
  * **前端框架**: 尝试使用Vue, React或Angular等现代前端框架来重构前端，以管理更复杂的应用状态。
  * **后端框架**: 学习Flask或Django等Python Web框架，它们能极大地简化后端开发。
  * **功能扩展**: 增加数据可视化图表、备件库存管理、定期保养提醒等更多高级功能。
