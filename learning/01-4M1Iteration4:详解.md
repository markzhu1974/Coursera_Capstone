# 工业机器人信息管理系统 - 迭代4：查询和删除功能详解

## ✅ 整体架构说明

本系统采用 **前后端分离架构**，查询和删除功能涉及以下组件：

```
┌────────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌─────────────┐
│  前端 (HTML/JS)    │───▶│  server.py       │───▶│  database.py     │───▶│  SQLite     │
│  搜索 + 删除操作    │    │  GET/DELETE处理   │    │  数据查询/删除   │    │  robots.db  │
└────────────────────┘    └──────────────────┘    └──────────────────┘    └─────────────┘
```

---

## 第一步：扩展数据库功能（`database.py`）

### 1. 多条件查询机器人

```python
# 添加查询机器人函数（支持多条件查询）
def search_robots(device_id=None, model=None, manufacturer=None, location=None):
    """
    根据多个条件查询机器人信息
    参数（都可选）：
        device_id: 设备编号（模糊匹配）
        model: 型号（模糊匹配）
        manufacturer: 生产厂家（模糊匹配）
        location: 位置（模糊匹配）
    返回值：
        符合条件的机器人列表
    """
    
    # 连接SQLite数据库
    conn = sqlite3.connect('robots.db')
    
    # 创建游标对象，用于执行SQL命令
    cursor = conn.cursor()
    
    # 构建基础查询语句
    # WHERE 1=1 是一个技巧，方便后续动态添加AND条件
    query = 'SELECT id, device_id, model, manufacturer, location FROM robots WHERE 1=1'
    
    # 存储查询参数的列表
    # SQL参数化查询需要将参数单独传递
    params = []
    
    # 根据提供的参数动态添加查询条件
    if device_id:
        # 添加设备编号模糊匹配条件
        # LIKE '%xxx%' 实现模糊搜索
        query += ' AND device_id LIKE ?'
        # 在参数中添加 %xxx% 格式的数据
        params.append(f'%{device_id}%')
        
    if model:
        # 添加型号模糊匹配条件
        query += ' AND model LIKE ?'
        params.append(f'%{model}%')
        
    if manufacturer:
        # 添加生产厂家模糊匹配条件
        query += ' AND manufacturer LIKE ?'
        params.append(f'%{manufacturer}%')
        
    if location:
        # 添加位置模糊匹配条件
        query += ' AND location LIKE ?'
        params.append(f'%{location}%')
    
    # 执行查询，参数通过params传递，防止SQL注入
    cursor.execute(query, params)
    
    # 获取所有查询结果
    robots = cursor.fetchall()
    
    # 关闭数据库连接
    conn.close()
    
    # 返回查询结果
    return robots
```

### 2. 删除单个机器人

```python
# 添加删除机器人函数
def delete_robot(robot_id):
    """
    根据ID删除单个机器人
    参数：
        robot_id: 要删除的机器人ID
    返回值：
        True: 删除成功
        False: 删除失败（如记录不存在）
    """
    
    # 连接数据库
    conn = sqlite3.connect('robots.db')
    
    # 创建游标
    cursor = conn.cursor()
    
    # 使用try-except-finally确保资源正确释放
    try:
        # 执行DELETE语句删除指定ID的机器人
        # 使用?占位符防止SQL注入
        cursor.execute('DELETE FROM robots WHERE id = ?', (robot_id,))
        
        # 提交事务，使删除生效
        conn.commit()
        
        # 检查是否成功删除了记录
        # rowcount表示受影响的行数
        return cursor.rowcount > 0
        
    except Exception as e:
        # 捕获异常（如数据库连接问题）
        print(f"删除数据时发生错误: {e}")
        return False
        
    finally:
        # 无论成功或失败，都关闭数据库连接
        conn.close()
```

### 3. 批量删除机器人

```python
# 添加批量删除机器人函数
def delete_robots(robot_ids):
    """
    批量删除多个机器人
    参数：
        robot_ids: 要删除的机器人ID列表 [1, 2, 3]
    返回值：
        成功删除的记录数量
    """
    
    # 连接数据库
    conn = sqlite3.connect('robots.db')
    
    # 创建游标
    cursor = conn.cursor()
    
    # 使用try-except-finally确保资源正确释放
    try:
        # 动态构建IN语句的占位符
        # 如：?,?,? 对应三个ID 下面的代码遍历每个条目，_表示不取实际的值，
        # 所以有几个条目，这里只会得到几个问号。然后在通过join用逗号连接
        # 起来，就得到?,?,?这样的结果
        placeholders = ','.join('?' for _ in robot_ids)
        
        # 构建DELETE语句
        # 例如：DELETE FROM robots WHERE id IN (?, ?, ?)
        query = f'DELETE FROM robots WHERE id IN ({placeholders})'
        
        # 执行批量删除
        # robot_ids列表直接作为参数传递
        cursor.execute(query, robot_ids)
        
        # 提交事务
        conn.commit()
        
        # 返回成功删除的记录数
        return cursor.rowcount
        
    except Exception as e:
        # 捕获异常
        print(f"批量删除数据时发生错误: {e}")
        return 0
        
    finally:
        # 关闭连接
        conn.close()
```

> 💡 **安全提示**：所有SQL操作都使用参数化查询，防止SQL注入攻击。

---

## 第二步：扩展服务器API（`server.py`）

### 1. 新增`do_DELETE`方法

```python
# 处理DELETE请求（删除机器人）
def do_DELETE(self):
    """
    处理HTTP DELETE请求，用于删除机器人
    请求路径：/api/robots/{id}
    """
    
    # 只处理/api/robots/{id}格式的DELETE请求
    if self.path.startswith('/api/robots/'):
        # 从URL路径中提取机器人ID
        # 例如：/api/robots/3 → robot_id = "3"
        robot_id = self.path.split('/')[-1]
        
        # 调用数据库函数删除机器人
        success = database.delete_robot(robot_id)
        
        if success:
            # 删除成功，返回HTTP 200 OK
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.set_cors_headers()
            self.end_headers()
            response = {'message': '机器人删除成功'}
            self.wfile.write(json.dumps(response).encode())
        else:
            # 删除失败，可能是记录不存在
            self.send_response(404)  # Not Found
            self.send_header('Content-type', 'application/json')
            self.set_cors_headers()
            self.end_headers()
            response = {'error': '删除失败，记录不存在'}
            self.wfile.write(json.dumps(response).encode())
    else:
        # 不支持的DELETE路径，返回404
        self.send_response(404)
        self.end_headers()
```

### 2. 在`do_GET`中添加搜索API

```python
# 在do_GET方法中添加搜索API端点
def do_GET(self):
    """
    处理HTTP GET请求，现在支持：
    - / → 重定向
    - /api/robots → 所有机器人
    - /api/robots/{id} → 单个机器人
    - /api/robots/search → 搜索机器人
    - /static/... → 静态文件
    """
    
    # 解析URL路径
    parsed_path = urllib.parse.urlparse(self.path)
    path = parsed_path.path
    
    # ... 其他GET处理逻辑 ...
    
    # 如果请求路径以/api/robots/search开头，处理搜索请求
    if path.startswith('/api/robots/search'):
        # 解析查询参数（URL中?后面的部分）
        # 例如：?device_id=WRB&model=FANUC
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        # 获取各个查询参数
        # parse_qs返回字典，值是列表，取第一个元素
        device_id = query_params.get('device_id', [None])[0]
        model = query_params.get('model', [None])[0]
        manufacturer = query_params.get('manufacturer', [None])[0]
        location = query_params.get('location', [None])[0]
        
        # 设置响应头
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.set_cors_headers()
        self.end_headers()
        
        # 调用数据库搜索函数
        robots = database.search_robots(device_id, model, manufacturer, location)
        
        # 将结果转换为字典列表
        robots_list = []
        for robot in robots:
            robots_list.append({
                'id': robot[0],
                'device_id': robot[1],
                'model': robot[2],
                'manufacturer': robot[3],
                'location': robot[4]
            })
        
        # 发送JSON响应
        self.wfile.write(json.dumps(robots_list).encode())
        return
        
    # ... 其他路径处理 ...
```
### 注意：
在HTTP请求处理中，通过if条件判断路径时，每个分支的判断的内容，有可能会出现一个路径满足多个if条件。

例如，我们看下面这两个条件：

if path.startswith('/api/robots/') 和
if path.startswith('/api/robots/search') 这两个条件

实际请求的path如果是/api/robots/search的时候，这两个条件都满足。而实际上，我们只希望程序进入第二个条件分支，而不执行第一个条件分支里的代码。

因此需要注意path和各个if判断的代码逻辑。通过在进入条件后print一些信息可以用作调试时判断。路径的判断最好通过严格的条件来区分，或者通过一些方法，例如末尾的return语句确保一旦匹配成功并处理完成，函数立即退出，避免后续条件被重复执行。还有，可以从具体到通用的顺序排列条件，如先处理/api/robots/search，再处理/api/robots/{id}，防止路径覆盖。使用return实现“短路退出”，结合合理排序，可确保每个请求仅被正确处理一次，避免逻辑冲突和重复执行。

---

## 第三步：更新前端界面（`static/index.html`）
**static/index.html**（替换原先的查询区域）
```html
<!-- 查询区域 -->
<section class="search-section">
    <h2>查询条件</h2>
    <div class="search-form">
        <!-- 搜索字段区域 -->
        <div class="search-fields">
            <!-- 设备编号搜索字段 -->
            <div class="form-field">
                <label for="searchDeviceId">设备编号</label>
                <!-- placeholder提供输入提示 -->
                <input type="text" id="searchDeviceId" placeholder="设备编号">
            </div>
            
            <!-- 型号搜索字段 -->
            <div class="form-field">
                <label for="searchModel">型号</label>
                <input type="text" id="searchModel" placeholder="型号">
            </div>
            
            <!-- 生产厂家搜索字段 -->
            <div class="form-field">
                <label for="searchManufacturer">生产厂家</label>
                <input type="text" id="searchManufacturer" placeholder="生产厂家">
            </div>
            
            <!-- 位置搜索字段 -->
            <div class="form-field">
                <label for="searchLocation">位置</label>
                <input type="text" id="searchLocation" placeholder="位置">
            </div>
        </div>
        
        <!-- 操作按钮区域 -->
        <div class="search-actions">
            <!-- 查询按钮 -->
            <button onclick="searchRobots()">查询</button>
            
            <!-- 清空按钮，重置搜索条件 -->
            <button onclick="clearSearch()" class="secondary">清空</button>
            
            <!-- 显示全部按钮，重载所有数据 -->
            <button onclick="loadRobots()" class="secondary">显示全部</button>
        </div>
    </div>
</section>
```

> 💡 **设计亮点**：
> - 单行布局，节省空间
> - 多字段并行搜索
> - 提供"清空"和"显示全部"快捷操作

---

## 第四步：更新CSS样式（`static/style.css`）

```css
/* 更新搜索区域样式 - 单行布局 */
.search-section {
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
}

/* 搜索表单整体样式 */
.search-form {
    display: flex;
    align-items: flex-end; /* 底部对齐，使按钮与输入框底部对齐 */
    gap: 10px;
    flex-wrap: nowrap; /* 不换行 */
}

/* 搜索字段容器 */
.search-fields {
    display: flex;
    gap: 10px;
    flex: 1; /* 占据剩余空间 */
    flex-wrap: nowrap;
}

/* 每个表单字段的样式 */
.form-field {
    display: flex;
    flex-direction: column; /* 垂直布局：标签在上，输入框在下 */
    min-width: 120px; /* 最小宽度 */
}

/* 标签样式 */
.form-field label {
    margin-bottom: 5px;
    font-size: 12px;
    color: #666;
    font-weight: bold;
}

/* 输入框样式 */
.form-field input {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    width: 100%;
    min-width: 120px;
}

/* 操作按钮容器 */
.search-actions {
    display: flex;
    gap: 10px;
    align-items: flex-end; /* 底部对齐 */
}

/* 按钮通用样式 */
.search-actions button {
    padding: 10px 15px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    white-space: nowrap; /* 文字不换行 */
    height: 40px; /* 固定高度，与输入框对齐 */
}

/* 主要按钮（查询） */
.search-actions button:first-child {
    background-color: #3498db; /* 蓝色 */
    color: white;
}

/* 次要按钮（清空、显示全部） */
.search-actions button.secondary {
    background-color: #95a5a6; /* 灰色 */
    color: white;
}

/* 按钮悬停效果 */
.search-actions button:hover {
    opacity: 0.9;
}

/* 响应式设计：小屏幕下换行 */
@media (max-width: 768px) {
    .search-form {
        flex-wrap: wrap; /* 换行 */
    }
    
    .search-fields {
        flex-wrap: wrap;
    }
    
    .form-field {
        min-width: 100px;
    }
}

/* 删除确认对话框样式 */
.confirm-dialog {
    display: none; /* 默认隐藏 */
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5); /* 半透明遮罩 */
}

/* 确认对话框内容 */
.confirm-content {
    background-color: white;
    margin: 20% auto;
    padding: 20px;
    width: 300px;
    border-radius: 8px;
    text-align: center;
}

/* 确认按钮容器 */
.confirm-buttons {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-top: 20px;
}

/* 确认按钮样式 */
.confirm-buttons button {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

/* 确认删除按钮（红色） */
.confirm-buttons button:first-child {
    background-color: #e74c3c;
    color: white;
}

/* 取消按钮（灰色） */
.confirm-buttons button:last-child {
    background-color: #95a5a6;
    color: white;
}
```

---

## 第五步：更新JavaScript功能（`static/script.js`）

### 1. 多条件查询

```javascript
// 查询机器人函数
function searchRobots() {
    // 获取各个搜索条件的输入值
    const deviceId = document.getElementById('searchDeviceId').value;
    const model = document.getElementById('searchModel').value;
    const manufacturer = document.getElementById('searchManufacturer').value;
    const location = document.getElementById('searchLocation').value;
    
    // 使用URLSearchParams构建查询字符串
    // 这样可以自动处理特殊字符编码
    const params = new URLSearchParams();
    
    // 只有当输入值存在时才添加到查询参数
    if (deviceId) params.append('device_id', deviceId);
    if (model) params.append('model', model);
    if (manufacturer) params.append('manufacturer', manufacturer);
    if (location) params.append('location', location);
    
    // 发送搜索请求
    // URL: /api/robots/search?device_id=WRB&model=FANUC
    fetch(`/api/robots/search?${params}`)
        .then(response => response.json())
        .then(data => {
            // 确保data是数组格式，防止后端返回单个对象
            const robotsArray = Array.isArray(data) ? data : [data];
            // 填充表格
            populateTable(robotsArray);
        })
        .catch(error => {
            console.error('搜索失败:', error);
            alert('搜索失败');
        });
}
```

### 思考：在Iteration 1 的代码中，也有查询的功能。和这里实现的查询功能有什么不同？


---

### 2. 清空搜索

```javascript
// 清空搜索条件
function clearSearch() {
    // 将所有搜索输入框清空
    document.getElementById('searchDeviceId').value = '';
    document.getElementById('searchModel').value = '';
    document.getElementById('searchManufacturer').value = '';
    document.getElementById('searchLocation').value = '';
    
    // 重新加载所有机器人数据
    loadRobots();
}
```

### 3. 删除机器人

```javascript
// 删除机器人
function deleteRobot() {
    // 获取选中的机器人ID列表
    const selectedRobots = getSelectedRobots();
    
    // 如果没有选择任何机器人
    if (!selectedRobots || selectedRobots.length === 0) {
        alert('请至少选择一个机器人');
        return;
    }
    
    // 显示浏览器内置的确认对话框
    if (confirm(`确定要删除选中的 ${selectedRobots.length} 个机器人吗？此操作不可撤销。`)) {
        // 为每个选中的机器人创建一个删除请求
        const deletePromises = selectedRobots.map(robotId => 
            fetch(`/api/robots/${robotId}`, {
                method: 'DELETE'  // HTTP DELETE请求
            })
        );
        
        // 等待所有删除请求完成
        Promise.all(deletePromises)
            .then(responses => {
                // 统计成功删除的数量
                const successCount = responses.filter(response => response.status === 200).length;
                alert(`成功删除 ${successCount} 个机器人`);
                // 重新加载数据
                loadRobots();
            })
            .catch(error => {
                console.error('删除机器人时发生错误:', error);
                alert('删除失败，请检查网络连接');
            });
    }
}
```

### 4. 获取选中的机器人

```javascript
// 获取选中的机器人ID（多个）
function getSelectedRobots() {
    // 查找所有被选中的复选框
    const checkboxes = document.querySelectorAll('#robotTable tbody input[type="checkbox"]:checked');
    
    // 如果没有选中任何机器人
    if (checkboxes.length === 0) {
        return null;
    }
    
    // 将NodeList转换为数组，并提取每个复选框的data-id
    return Array.from(checkboxes).map(checkbox => checkbox.dataset.id);
}
```

---

## 第六步：测试完整功能

### 测试步骤：
1. **启动服务器**：`python server.py`
2. **访问系统**：`http://localhost:8000/`
3. **测试查询功能**：
   - 输入设备编号搜索
   - 输入型号搜索
   - 组合多个条件搜索
   - 点击"清空"和"显示全部"
4. **测试删除功能**：
   - 勾选一个或多个机器人
   - 点击"删除"
   - 确认删除
   - 验证数据是否消失

### 预期结果：
- **查询功能**：
  - 支持单字段和多字段组合搜索
  - 模糊匹配（包含即可）
  - "清空"按钮重置搜索条件
  - "显示全部"按钮重载所有数据
- **删除功能**：
  - 必须先选择机器人
  - 删除前有确认提示
  - 批量删除时统计成功数量
  - 删除后自动刷新列表

---

## 数据流图（多条件查询）

```text
前端 (HTML/JavaScript)           后端 (server.py)                           后端 (database.py)                      数据库 (SQLite)
    │                                    │                                        │                                      │
    │    输入搜索条件                     │                                        │                                      │
    │    点击【查询】按钮                 │                                        │                                      │
    │    searchRobots()                  │                                        │                                      │
    │    构建查询参数                     │                                        │                                      │
    │── fetch(`/api/robots/search?...`)->│  do_GET:search_robots(device_id, ...)  │                                      │
    │                                    │───────────────────────────────────────>│                                      │
    │                                    │                                        │  SELECT * FROM robots WHERE ...      │
    │                                    │                                        │─────────────────────────────────────>│
    │                                    │                                        │  返回查询结果                         │
    │                                    │                                        │<─────────────────────────────────────│
    │                                    │<───────────────────────────────────────│                                      │
    │<───── 返回匹配的机器人列表 ───────── │                                        │                                      │
    │    populateTable(data)             │                                        │                                      │
```

---

## 数据流图（删除机器人）

```text
前端 (HTML/JavaScript)                  后端 (server.py)        后端 (database.py)                      数据库 (SQLite)
    │                                      │                             │                                     │
    │  勾选机器人并点击【删除】                                            │                                     │
    │    confirm("确定删除吗？")            │                             │                                     │
    │    是 → 继续                         │                             │                                     │
    │    deleteRobot()                     │                             │                                     │
    │    为每个选中的ID创建fetch请求                                       │                                     │
    │────fetch(`/api/robots/5`, DELETE) ──>│ do_DELETE: delete_robot(5)  │                                     │
    │                                      │────────────────────────────>│                                     │
    │                                      │                             │    DELETE FROM robots WHERE id = 5  │
    │                                      │                             │────────────────────────────────────>│
    │                                      │                             │   返回DELETE结果                     │
    │                                      │                             │<────────────────────────────────────│
    │                                      │<────────────────────────────│                                     │
    │<───── 200 OK ────────────────────────│                             │                                     │
    │    Promise.all() 收集所有响应         │                             │                                     │
    │    统计成功数量                       │                             │                                     │
    │    alert("成功删除X个机器人")         │                             │                                     │
    │    loadRobots()                      │                             │                                     │

现在工业机器人信息管理系统的第一个里程碑已经完成！系统支持完整的增删改查功能。请测试所有功能，确保一切正常工作，然后我们可以继续Milestone 2的内容。

------

代码参考 [code/01-4_Lab/M1Iteration4](code/01-4_Lab/M1Iteration4)
