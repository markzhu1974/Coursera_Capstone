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

// 查询机器人函数
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



// 删除机器人
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

// 更新addRobot函数，打开模态窗口
function addRobot() {
    const modal = document.getElementById('addModal');
    modal.style.display = 'block';
    
    // 清空表单
    document.getElementById('addForm').reset();
}


// 更新editRobot函数，打开编辑模态窗口
function editRobot() {
    // 获取选中的机器人
    const selectedRobot = getSelectedRobot();
    if (!selectedRobot) {
        alert('请先选择一个机器人');
        return;
    }
    
    // 获取机器人详细信息
    fetch(`/api/robots/${selectedRobot}`)
        .then(response => response.json())
        .then(robot => {
            if (robot.error) {
                alert(robot.error);
                return;
            }
            
            // 填充表单数据
            document.getElementById('edit_id').value = robot.id;
            document.getElementById('edit_device_id').value = robot.device_id;
            document.getElementById('edit_model').value = robot.model;
            document.getElementById('edit_manufacturer').value = robot.manufacturer;
            document.getElementById('edit_location').value = robot.location;
            
            // 显示编辑模态窗口
            const modal = document.getElementById('editModal');
            modal.style.display = 'block';
        })
        .catch(error => {
            console.error('获取机器人信息失败:', error);
            alert('获取机器人信息失败');
        });
}

// 关闭新增模态窗口
function closeAddModal() {
    const modal = document.getElementById('addModal');
    modal.style.display = 'none';
}

// 关闭编辑模态窗口
function closeEditModal() {
    const modal = document.getElementById('editModal');
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

// 提交编辑表单
function submitEditForm(event) {
    event.preventDefault(); // 阻止表单默认提交行为
    
    // 获取表单数据
    const formData = {
        device_id: document.getElementById('edit_device_id').value,
        model: document.getElementById('edit_model').value,
        manufacturer: document.getElementById('edit_manufacturer').value,
        location: document.getElementById('edit_location').value
    };
    
    const robotId = document.getElementById('edit_id').value;
    
    // 发送PUT请求到服务器
    fetch(`/api/robots/${robotId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (response.status === 200) {
            // 更新成功
            alert('机器人信息更新成功！');
            closeEditModal();
            loadRobots(); // 重新加载数据
        } else if (response.status === 400) {
            // 更新失败，显示错误信息
            return response.json().then(data => {
                alert('更新失败: ' + data.error);
            });
        }
    })
    .catch(error => {
        console.error('更新机器人信息时发生错误:', error);
        alert('更新失败，请检查网络连接');
    });
}

// 获取选中的机器人ID（单个）
function getSelectedRobot() {
    const checkboxes = document.querySelectorAll('#robotTable tbody input[type="checkbox"]:checked');
    if (checkboxes.length === 0) {
        return null;
    }
    if (checkboxes.length > 1) {
        alert('请只选择一个机器人');
        return null;
    }
    return checkboxes[0].dataset.id;
}

// 获取选中的机器人ID（多个）
function getSelectedRobots() {
    const checkboxes = document.querySelectorAll('#robotTable tbody input[type="checkbox"]:checked');
    if (checkboxes.length === 0) {
        return null;
    }
    return Array.from(checkboxes).map(checkbox => checkbox.dataset.id);
}


// 更新window.onclick函数，支持关闭编辑模态窗口
window.onclick = function(event) {
    const addModal = document.getElementById('addModal');
    const editModal = document.getElementById('editModal');
    
    if (event.target === addModal) {
        closeAddModal();
    }
    if (event.target === editModal) {
        closeEditModal();
    }
};

