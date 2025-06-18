# 包含React前端（3D仪表盘）和Spring Boot后端的完整代码，实现每5秒自动更新数据。

### 一、Spring Boot 后端实现

#### 1. 创建Spring Boot项目结构
```
src/
├── main/
│   ├── java/com/example/oee/
│   │   ├── OeeApplication.java
│   │   ├── controller/
│   │   │   └── OeeController.java
│   │   └── service/
│   │       └── OeeService.java
│   └── resources/
│       └── application.properties
```

#### 2. OeeController.java
```java
package com.example.oee.controller;

import com.example.oee.service.OeeService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/oee")
public class OeeController {
    
    private final OeeService oeeService;

    public OeeController(OeeService oeeService) {
        this.oeeService = oeeService;
    }

    @GetMapping
    public OeeData getOeeData() {
        return oeeService.generateOeeData();
    }
}

record OeeData(double oee, double availability, double performance, double quality) {}
```

#### 3. OeeService.java
```java
package com.example.oee.service;

import com.example.oee.controller.OeeData;
import org.springframework.stereotype.Service;

import java.util.Random;

@Service
public class OeeService {
    private final Random random = new Random();

    public OeeData generateOeeData() {
        return new OeeData(
            random.nextDouble() * 20 + 70,  // OEE 70-90%
            random.nextDouble() * 20 + 75,  // 时间开动率 75-95%
            random.nextDouble() * 20 + 80,  // 性能开动率 80-100%
            random.nextDouble() * 10 + 85   // 合格品率 85-95%
        );
    }
}
```

#### 4. application.properties
```properties
server.port=8080
spring.application.name=oee-backend
```

### 二、React 前端实现

#### 1. 创建React项目结构
```
src/
├── components/
│   ├── ThreeDGauge.jsx
│   └── ThreeDGauge.css
├── App.js
├── App.css
└── index.js
```

#### 2. ThreeDGauge.jsx
```jsx
import React from 'react';
import './ThreeDGauge.css';

const ThreeDGauge = ({ value, size = 180 }) => {
    const rotation = (value / 100) * 180 - 90;
    
    return (
        <div className="gauge-container" style={{ width: size, height: size }}>
            <div className="gauge-body">
                <div className="gauge-face">
                    <div className="gauge-marks">
                        {[...Array(11)].map((_, i) => (
                            <div key={i} className="gauge-mark" 
                                 style={{ transform: `rotate(${i * 18 - 90}deg)` }} />
                        ))}
                    </div>
                    <div className="gauge-needle" style={{ transform: `rotate(${rotation}deg)` }} />
                    <div className="gauge-center" />
                </div>
                <div className="gauge-value">{value.toFixed(1)}%</div>
            </div>
        </div>
    );
};

export default ThreeDGauge;
```

#### 3. ThreeDGauge.css
```css
.gauge-container {
    position: relative;
    margin: 0 20px;
}

.gauge-body {
    width: 100%;
    height: 100%;
    position: relative;
}

.gauge-face {
    width: 100%;
    height: 100%;
    background: linear-gradient(145deg, #4CAF50, #388E3C);
    border-radius: 50%;
    position: relative;
    box-shadow: 
        inset 0 0 15px rgba(0, 0, 0, 0.2),
        0 5px 15px rgba(0, 0, 0, 0.2);
    border: 5px solid #2E7D32;
    overflow: hidden;
}

.gauge-marks {
    position: absolute;
    width: 100%;
    height: 100%;
}

.gauge-mark {
    position: absolute;
    width: 2px;
    height: 15px;
    background: rgba(255, 255, 255, 0.7);
    left: 50%;
    top: 10px;
    transform-origin: 50% calc(100% - 10px);
}

.gauge-needle {
    position: absolute;
    width: 3px;
    height: 45%;
    background: #333;
    left: 50%;
    top: 50%;
    transform-origin: 50% 0;
    z-index: 10;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
    transition: transform 0.5s ease-out;
}

.gauge-center {
    position: absolute;
    width: 12%;
    height: 12%;
    background: #333;
    border-radius: 50%;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    z-index: 11;
    box-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
}

.gauge-value {
    position: absolute;
    top: 60%;
    left: 0;
    right: 0;
    font-size: 24px;
    font-weight: bold;
    color: #333;
    text-align: center;
    text-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
}
```

#### 4. App.js
```jsx
import React, { useState, useEffect } from 'react';
import ThreeDGauge from './components/ThreeDGauge';
import './App.css';

function App() {
    const [oeeData, setOeeData] = useState({
        oee: 0,
        availability: 0,
        performance: 0,
        quality: 0
    });
    const [loading, setLoading] = useState(true);

    const fetchOeeData = async () => {
        try {
            const response = await fetch('http://localhost:8080/api/oee');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            setOeeData({
                oee: data.oee,
                availability: data.availability,
                performance: data.performance,
                quality: data.quality
            });
        } catch (error) {
            console.error('Error fetching OEE data:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchOeeData();
        const interval = setInterval(fetchOeeData, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="App">
            <header className="App-header">
                <h1>设备OEE看板</h1>
                {loading ? (
                    <div className="loading">加载中...</div>
                ) : (
                    <div className="gauges-container">
                        <ThreeDGauge value={oeeData.oee} />
                        <ThreeDGauge value={oeeData.availability} />
                        <ThreeDGauge value={oeeData.performance} />
                        <ThreeDGauge value={oeeData.quality} />
                    </div>
                )}
            </header>
        </div>
    );
}

export default App;
```

#### 5. App.css
```css
.App {
    text-align: center;
    background-color: white;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: Arial, sans-serif;
}

.App-header {
    padding: 20px;
    max-width: 900px;
    margin: 0 auto;
}

h1 {
    color: #333;
    margin-bottom: 40px;
}

.loading {
    font-size: 20px;
    color: #333;
}

.gauges-container {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 20px;
}

@media (max-width: 768px) {
    .gauges-container {
        flex-direction: column;
        align-items: center;
    }
    
    h1 {
        font-size: 24px;
        margin-bottom: 20px;
    }
}
```

### 三、系统运行说明

1. **启动后端**：
   ```bash
   cd oee-backend
   ./mvnw spring-boot:run
   ```

2. **启动前端**：
   ```bash
   cd oee-frontend
   npm start
   ```

3. **访问应用**：
   - 打开浏览器访问 `http://localhost:3000`
   - 每5秒会自动从后端获取最新数据并更新仪表盘

### 四、功能特点

1. **3D仪表盘效果**：
   - 半圆形绿色渐变设计
   - 平滑的指针动画
   - 精确的刻度显示

2. **动态数据更新**：
   - 每5秒自动请求后端API
   - 平滑过渡动画

3. **响应式布局**：
   - 桌面端横向排列
   - 移动端自动垂直排列

4. **完整前后端分离架构**：
   - Spring Boot提供REST API
   - React前端独立部署

这个解决方案可以直接复制使用，您可以根据实际需求调整样式或数据生成逻辑。