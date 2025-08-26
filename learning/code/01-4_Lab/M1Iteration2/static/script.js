// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 加载机器人数据
    loadRobots();
});

// 加载机器人数据函数
function loadRobots() {
    // 发送GET请求到服务器API
    fetch('/api/robots')
        .then(response => response.json())  // 解析响应为JSON
        .then(data => {
            // 调用函数填充表格数据
            populateTable(data);
        })
        .catch(error => {
            // 错误处理
            console.error('获取数据失败:', error);
        });
}


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


// 填充表格数据函数
function populateTable(robots) {
    // 获取表格tbody元素
    const tbody = document.querySelector('#robotTable tbody');
    // 清空现有内容
    tbody.innerHTML = '';
    
    // 遍历机器人数据
    robots.forEach(robot => {
        // 创建表格行
        const row = document.createElement('tr');
        
        // 创建选择复选框单元格
        const selectCell = document.createElement('td');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.dataset.id = robot.id;  // 存储机器人ID
        selectCell.appendChild(checkbox);
        
        // 创建设备编号单元格
        const deviceIdCell = document.createElement('td');
        deviceIdCell.textContent = robot.device_id;
        
        // 创建型号单元格
        const modelCell = document.createElement('td');
        modelCell.textContent = robot.model;
        
        // 创建生产厂家单元格
        const manufacturerCell = document.createElement('td');
        manufacturerCell.textContent = robot.manufacturer;
        
        // 创建位置单元格
        const locationCell = document.createElement('td');
        locationCell.textContent = robot.location;
        
        // 将所有单元格添加到行
        row.appendChild(selectCell);
        row.appendChild(deviceIdCell);
        row.appendChild(modelCell);
        row.appendChild(manufacturerCell);
        row.appendChild(locationCell);
        
        // 将行添加到表格
        tbody.appendChild(row);
    });
}

// 查询机器人函数
function searchRobots() {
    // 获取搜索输入值
    const searchValue = document.getElementById('searchInput').value.toLowerCase();
    
    // 发送GET请求到服务器API
    fetch('/api/robots')
        .then(response => response.json())
        .then(data => {
            // 过滤数据
            const filteredData = data.filter(robot => 
                robot.device_id.toLowerCase().includes(searchValue) || 
                robot.model.toLowerCase().includes(searchValue)
            );
            // 填充过滤后的数据
            populateTable(filteredData);
        })
        .catch(error => {
            console.error('搜索失败:', error);
        });
}


// 修改机器人函数（待实现）
function editRobot() {
    alert('修改功能将在迭代3实现');
}

// 删除机器人函数（待实现）
function deleteRobot() {
    alert('删除功能将在迭代4实现');
}