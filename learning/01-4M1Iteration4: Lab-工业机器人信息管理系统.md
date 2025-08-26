# 迭代4：完成查询和删除功能

现在我们将实现完整的查询功能和删除机器人功能。

## 第一步：扩展数据库功能

**database.py**（新增函数）
```python
# 添加查询机器人函数（支持多条件查询）
def search_robots(device_id=None, model=None, manufacturer=None, location=None):
    conn = sqlite3.connect('robots.db')
    cursor = conn.cursor()
    
    # 构建基础查询语句
    query = 'SELECT id, device_id, model, manufacturer, location FROM robots WHERE 1=1'
    params = []
    
    # 根据提供的参数添加查询条件
    if device_id:
        query += ' AND device_id LIKE ?'
        params.append(f'%{device_id}%')
    if model:
        query += ' AND model LIKE ?'
        params.append(f'%{model}%')
    if manufacturer:
        query += ' AND manufacturer LIKE ?'
        params.append(f'%{manufacturer}%')
    if location:
        query += ' AND location LIKE ?'
        params.append(f'%{location}%')
    
    # 执行查询
    cursor.execute(query, params)
    robots = cursor.fetchall()
    
    conn.close()
    return robots

# 添加删除机器人函数
def delete_robot(robot_id):
    conn = sqlite3.connect('robots.db')
    cursor = conn.cursor()
    
    try:
        # 删除指定ID的机器人
        cursor.execute('DELETE FROM robots WHERE id = ?', (robot_id,))
        conn.commit()
        
        # 返回是否成功删除了记录
        return cursor.rowcount > 0
    except Exception as e:
        # 处理异常
        print(f"删除数据时发生错误: {e}")
        return False
    finally:
        conn.close()

# 添加批量删除机器人函数
def delete_robots(robot_ids):
    conn = sqlite3.connect('robots.db')
    cursor = conn.cursor()
    
    try:
        # 使用IN语句批量删除
        placeholders = ','.join('?' for _ in robot_ids)
        query = f'DELETE FROM robots WHERE id IN ({placeholders})'
        
        cursor.execute(query, robot_ids)
        conn.commit()
        
        # 返回成功删除的记录数
        return cursor.rowcount
    except Exception as e:
        # 处理异常
        print(f"批量删除数据时发生错误: {e}")
        return 0
    finally:
        conn.close()
```

## 第二步：扩展服务器API

**server.py**（新增do_DELETE方法和搜索API）
```python
# 在RobotHandler类中添加do_DELETE方法
def do_DELETE(self):
    # 处理/api/robots/的DELETE请求
    if self.path.startswith('/api/robots/'):
        # 从URL路径中提取机器人ID
        robot_id = self.path.split('/')[-1]
        
        # 调用数据库函数删除机器人
        success = database.delete_robot(robot_id)
        
        if success:
            # 删除成功，返回200状态码
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.set_cors_headers()
            self.end_headers()
            response = {'message': '机器人删除成功'}
            self.wfile.write(json.dumps(response).encode())
        else:
            # 删除失败，返回404状态码
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.set_cors_headers()
            self.end_headers()
            response = {'error': '删除失败，记录不存在'}
            self.wfile.write(json.dumps(response).encode())
    else:
        # 对于其他DELETE请求返回404
        self.send_response(404)
        self.end_headers()

# 在do_GET方法中添加搜索API端点
def do_GET(self):
    ...
    # 如果请求路径是/api/robots/search，处理搜索请求
    if path.startswith('/api/robots/search'):
        # 解析查询参数
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        # 获取查询参数
        device_id = query_params.get('device_id', [None])[0]
        model = query_params.get('model', [None])[0]
        manufacturer = query_params.get('manufacturer', [None])[0]
        location = query_params.get('location', [None])[0]
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.set_cors_headers()
        self.end_headers()
        
        # 调用搜索函数
        robots = database.search_robots(device_id, model, manufacturer, location)
        robots_list = []
        for robot in robots:
            robots_list.append({
                'id': robot[0],
                'device_id': robot[1],
                'model': robot[2],
                'manufacturer': robot[3],
                'location': robot[4]
            })
        
        self.wfile.write(json.dumps(robots_list).encode())
        return
    ...

```

## 第三步：更新前端界面

**static/index.html**（替换原先的查询区域）
```html
<!-- 查询区域 -->
<section class="search-section">
    <h2>查询条件</h2>
    <div class="search-form">
        <!-- 搜索字段区域 -->
        <div class="search-fields">
            <div class="form-field">
                <label for="searchDeviceId">设备编号</label>
                <input type="text" id="searchDeviceId" placeholder="设备编号">
            </div>
            <div class="form-field">
                <label for="searchModel">型号</label>
                <input type="text" id="searchModel" placeholder="型号">
            </div>
            <div class="form-field">
                <label for="searchManufacturer">生产厂家</label>
                <input type="text" id="searchManufacturer" placeholder="生产厂家">
            </div>
            <div class="form-field">
                <label for="searchLocation">位置</label>
                <input type="text" id="searchLocation" placeholder="位置">
            </div>
        </div>
        
        <!-- 操作按钮区域 -->
        <div class="search-actions">
            <button onclick="searchRobots()">查询</button>
            <button onclick="clearSearch()" class="secondary">清空</button>
            <button onclick="loadRobots()" class="secondary">显示全部</button>
        </div>
    </div>
</section>
```

## 第四步：更新CSS样式

**static/style.css**（新增样式）
```css
/* 更新搜索区域样式 - 单行布局 */
.search-section {
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
}

.search-form {
    display: flex;
    align-items: flex-end; /* 底部对齐 */
    gap: 10px;
    flex-wrap: nowrap; /* 确保不换行 */
}

.search-fields {
    display: flex;
    gap: 10px;
    flex: 1; /* 占据剩余空间 */
    flex-wrap: nowrap;
}

/* 每个表单组的样式 */
.form-field {
    display: flex;
    flex-direction: column;
    min-width: 120px; /* 最小宽度 */
}

.form-field label {
    margin-bottom: 5px;
    font-size: 12px;
    color: #666;
    font-weight: bold;
}

.form-field input {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    width: 100%;
    min-width: 120px; /* 输入框最小宽度 */
}

.search-actions {
    display: flex;
    gap: 10px;
    align-items: flex-end; /* 底部对齐 */
}

/* 按钮样式 */
.search-actions button {
    padding: 10px 15px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    white-space: nowrap; /* 按钮文字不换行 */
    height: 40px; /* 固定高度与输入框对齐 */
}

.search-actions button:first-child {
    background-color: #3498db; /* 蓝色查询按钮 */
    color: white;
}

.search-actions button.secondary {
    background-color: #95a5a6; /* 灰色按钮 */
    color: white;
}

.search-actions button:hover {
    opacity: 0.9;
}

/* 响应式设计：在小屏幕上换行 */
@media (max-width: 768px) {
    .search-form {
        flex-wrap: wrap;
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
    display: none;
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
}

.confirm-content {
    background-color: white;
    margin: 20% auto;
    padding: 20px;
    width: 300px;
    border-radius: 8px;
    text-align: center;
}

.confirm-buttons {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-top: 20px;
}

.confirm-buttons button {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.confirm-buttons button:first-child {
    background-color: #e74c3c;
    color: white;
}

.confirm-buttons button:last-child {
    background-color: #95a5a6;
    color: white;
}
```

## 第五步：更新JavaScript功能

**static/script.js**（增加更的处理函数）
```javascript


// 查询机器人函数，替换原来的searchRobots（）函数
function searchRobots() {
    // 获取搜索条件
    const deviceId = document.getElementById('searchDeviceId').value;
    const model = document.getElementById('searchModel').value;
    const manufacturer = document.getElementById('searchManufacturer').value;
    const location = document.getElementById('searchLocation').value;
    
    // 构建查询参数
    const params = new URLSearchParams();
    if (deviceId) params.append('device_id', deviceId);
    if (model) params.append('model', model);
    if (manufacturer) params.append('manufacturer', manufacturer);
    if (location) params.append('location', location);
    
    // 发送搜索请求
    fetch(`/api/robots/search?${params}`)
        .then(response => response.json())
        .then(data => {
            // 确保data是数组格式
            const robotsArray = Array.isArray(data) ? data : [data];
            populateTable(robotsArray);
        })
        .catch(error => {
            console.error('搜索失败:', error);
            alert('搜索失败');
        });
}

// 清空搜索条件
function clearSearch() {
    document.getElementById('searchDeviceId').value = '';
    document.getElementById('searchModel').value = '';
    document.getElementById('searchManufacturer').value = '';
    document.getElementById('searchLocation').value = '';
    loadRobots();
}

// 删除机器人，替换原来的待实现的deleteRobot()
function deleteRobot() {
    const selectedRobots = getSelectedRobots();
    if (!selectedRobots || selectedRobots.length === 0) {
        alert('请至少选择一个机器人');
        return;
    }
    
    // 显示确认对话框
    if (confirm(`确定要删除选中的 ${selectedRobots.length} 个机器人吗？此操作不可撤销。`)) {
        // 逐个删除选中的机器人
        const deletePromises = selectedRobots.map(robotId => 
            fetch(`/api/robots/${robotId}`, {
                method: 'DELETE'
            })
        );
        
        // 等待所有删除操作完成
        Promise.all(deletePromises)
            .then(responses => {
                const successCount = responses.filter(response => response.status === 200).length;
                alert(`成功删除 ${successCount} 个机器人`);
                loadRobots(); // 重新加载数据
            })
            .catch(error => {
                console.error('删除机器人时发生错误:', error);
                alert('删除失败，请检查网络连接');
            });
    }
}


// 获取选中的机器人ID（多个）
function getSelectedRobots() {
    const checkboxes = document.querySelectorAll('#robotTable tbody input[type="checkbox"]:checked');
    if (checkboxes.length === 0) {
        return null;
    }
    return Array.from(checkboxes).map(checkbox => checkbox.dataset.id);
}


```

## 第六步：测试完整功能

1. 重启服务器：`python server.py`
2. 访问：`http://localhost:8000/`
3. 测试所有功能：
   - 查询功能：使用不同的搜索条件
   - 新增功能：添加新的机器人
   - 修改功能：编辑现有机器人信息
   - 删除功能：删除选中的机器人

## 功能说明

现在你已完成迭代4，实现了完整的CRUD功能：

1. **数据库层**：
   - 添加了`search_robots`函数支持多条件查询
   - 添加了`delete_robot`和`delete_robots`函数支持删除操作

2. **服务器层**：
   - 添加了`do_DELETE`方法处理HTTP DELETE请求
   - 扩展了`do_GET`方法支持搜索API

3. **前端层**：
   - 完善了搜索界面，支持多条件查询
   - 实现了批量删除功能
   - 添加了确认对话框防止误操作
   - 增强了用户体验和错误处理

**关键特性：**
- 支持多条件组合查询
- 支持批量删除操作
- 操作前确认防止误操作
- 完整的错误处理和用户反馈
- 响应式界面设计

现在工业机器人信息管理系统的第一个里程碑已经完成！系统支持完整的增删改查功能。

请测试所有功能，确保一切正常工作，然后我们可以继续Milestone 2的内容。

------

代码参考 [code/01-4_Lab/M1Iteration4](code/01-4_Lab/M1Iteration4)
