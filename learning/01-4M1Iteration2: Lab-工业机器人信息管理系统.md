# 迭代2：完成机器人创建功能

现在我们将实现新增机器人的功能，包括前端表单和后端API。

## 第一步：扩展数据库功能

**database.py**（新增函数）
```python
# 添加新增机器人函数
def add_robot(device_id, model, manufacturer, location):
    conn = sqlite3.connect('robots.db')
    cursor = conn.cursor()
    
    try:
        # 插入新的机器人记录
        cursor.execute(
            'INSERT INTO robots (device_id, model, manufacturer, location) VALUES (?, ?, ?, ?)',
            (device_id, model, manufacturer, location)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # 处理唯一性约束错误（设备编号重复）
        print(f"错误：设备编号 {device_id} 已存在")
        return False
    except Exception as e:
        # 处理其他异常
        print(f"插入数据时发生错误: {e}")
        return False
    finally:
        conn.close()
```

## 第二步：扩展服务器API

**server.py**（新增do_POST方法）
```python
# 在RobotHandler类中添加do_POST方法
def do_POST(self):
    # 只处理/api/robots的POST请求
    if self.path == '/api/robots':
        # 获取请求内容长度
        content_length = int(self.headers['Content-Length'])
        # 读取请求体数据
        post_data = self.rfile.read(content_length)
        
        try:
            # 解析JSON数据
            data = json.loads(post_data.decode('utf-8'))
            
            # 调用数据库函数添加机器人
            success = database.add_robot(
                data['device_id'],
                data['model'],
                data['manufacturer'],
                data['location']
            )
            
            if success:
                # 添加成功，返回201状态码
                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self.set_cors_headers()
                self.end_headers()
                response = {'message': '机器人添加成功'}
                self.wfile.write(json.dumps(response).encode())
            else:
                # 添加失败，返回400状态码
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.set_cors_headers()
                self.end_headers()
                response = {'error': '添加失败，设备编号可能已存在'}
                self.wfile.write(json.dumps(response).encode())
                
        except json.JSONDecodeError:
            # JSON解析错误
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.set_cors_headers()
            self.end_headers()
            response = {'error': '无效的JSON数据'}
            self.wfile.write(json.dumps(response).encode())
        except KeyError as e:
            # 缺少必要字段
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.set_cors_headers()
            self.end_headers()
            response = {'error': f'缺少必要字段: {e}'}
            self.wfile.write(json.dumps(response).encode())
    else:
        # 对于其他POST请求返回404
        self.send_response(404)
        self.end_headers()
```

## 第三步：创建新增机器人模态窗口

模态窗口的意思就是，它会在当前页面上弹出一个窗口，用于和用户与交互，填写信息，然后或者保存或者提交，或者取消，窗口才会小时，然后才能继续操作主页面

**static/index.html**（在body末尾添加）
```html
<!-- 新增机器人模态窗口 -->
<div id="addModal" class="modal">
    <div class="modal-content">
        <span class="close" onclick="closeAddModal()">&times;</span>
        <h2>新增机器人</h2>
        <form id="addForm" onsubmit="submitAddForm(event)">
            <div class="form-group">
                <label for="device_id">设备编号:</label>
                <input type="text" id="device_id" name="device_id" required>
            </div>
            <div class="form-group">
                <label for="model">型号:</label>
                <input type="text" id="model" name="model" required>
            </div>
            <div class="form-group">
                <label for="manufacturer">生产厂家:</label>
                <input type="text" id="manufacturer" name="manufacturer" required>
            </div>
            <div class="form-group">
                <label for="location">位置:</label>
                <input type="text" id="location" name="location" required>
            </div>
            <div class="form-buttons">
                <button type="submit">提交</button>
                <button type="button" onclick="closeAddModal()">取消</button>
            </div>
        </form>
    </div>
</div>
```

## 第四步：添加模态窗口样式

**static/style.css**（新增样式）
```css
/* 模态窗口样式 */
.modal {
    display: none; /* 默认隐藏 */
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5); /* 半透明背景 */
}

.modal-content {
    background-color: white;
    margin: 10% auto;
    padding: 20px;
    width: 50%;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    position: relative;
}

.close {
    color: #aaa;
    float: right;
    font-size: 28px;
    font-weight: bold;
    cursor: pointer;
}

.close:hover {
    color: black;
}

/* 表单样式 */
.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

.form-group input {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.form-buttons {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
    margin-top: 20px;
}

.form-buttons button {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.form-buttons button[type="submit"] {
    background-color: #27ae60;
    color: white;
}

.form-buttons button[type="button"] {
    background-color: #95a5a6;
    color: white;
}

.form-buttons button:hover {
    opacity: 0.9;
}
```

## 第五步：实现前端新增功能

**static/script.js**（更新和新增函数）
```javascript
// 更新addRobot函数，打开模态窗口
function addRobot() {
    const modal = document.getElementById('addModal');
    modal.style.display = 'block';
    
    // 清空表单
    document.getElementById('addForm').reset();
}

// 关闭新增模态窗口
function closeAddModal() {
    const modal = document.getElementById('addModal');
    modal.style.display = 'none';
}

// 提交新增表单
function submitAddForm(event) {
    event.preventDefault(); // 阻止表单默认提交行为
    
    // 获取表单数据
    const formData = {
        device_id: document.getElementById('device_id').value,
        model: document.getElementById('model').value,
        manufacturer: document.getElementById('manufacturer').value,
        location: document.getElementById('location').value
    };
    
    // 发送POST请求到服务器
    fetch('/api/robots', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (response.status === 201) {
            // 添加成功
            alert('机器人添加成功！');
            closeAddModal();
            loadRobots(); // 重新加载数据
        } else if (response.status === 400) {
            // 添加失败，显示错误信息
            return response.json().then(data => {
                alert('添加失败: ' + data.error);
            });
        }
    })
    .catch(error => {
        console.error('添加机器人时发生错误:', error);
        alert('添加失败，请检查网络连接');
    });
}

// 点击模态窗口外部关闭窗口
window.onclick = function(event) {
    const modal = document.getElementById('addModal');
    if (event.target === modal) {
        closeAddModal();
    }
};
```
#### 注意，addrRobot()函数原来代码中已有定义，说明是待实现。新加了上面的代码后要把下面的内容删除。

```javascript
// 新增机器人函数（待实现）
function addRobot() {
    alert('新增功能将在迭代2实现');
}
```

## 第六步：测试新增功能

1. 删除robots.sb文件，启动服务器：`python server.py`
2. 访问：`http://localhost:8000/`
3. 点击"新增"按钮，填写表单并提交
4. 检查数据是否成功添加到列表
5. 打开robots.db，看提交的内容是否已经保存到数据库

## 功能说明

现在你已完成迭代2，实现了以下功能：

1. **数据库层**：添加了`add_robot`函数来处理数据插入
2. **服务器层**：添加了`do_POST`方法来处理HTTP POST请求
3. **前端层**：
   - 创建了模态窗口用于输入新机器人信息
   - 实现了表单提交逻辑
   - 添加了错误处理和用户反馈

**关键特性：**
- 设备编号唯一性验证
- 表单数据验证
- 友好的用户反馈
- 模态窗口交互
- 自动刷新数据列表

现在用户可以通过点击"新增"按钮，填写表单并成功添加新的机器人记录到数据库中。

请测试这个功能，确保一切正常工作，然后输入"继续"我将提供迭代3的内容。