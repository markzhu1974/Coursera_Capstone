# Vue3 + Flask 项目改造方案

将之前的 Vue3 仪表盘项目与 Flask 后端集成：

## 1. 后端 Flask 代码

首先创建一个 Flask 后端 API 来提供数据：

```python
# app.py
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域请求

@app.route('/api/oee-metrics', methods=['GET'])
def get_oee_metrics():
    # 这里可以从数据库或其他数据源获取实际数据
    metrics = [
        {"id": "oee", "title": "OEE", "value": 85},
        {"id": "avail", "title": "开动率", "value": 90},
        {"id": "perf", "title": "性能开动率", "value": 88},
        {"id": "qual", "title": "合格品率", "value": 95}
    ]
    return jsonify(metrics)

if __name__ == '__main__':
    app.run(debug=True)
```

## 2. 前端 Vue3 组件改造

修改 Vue 组件以从 API 获取数据：

```vue
<template>
  <div v-if="loading" class="loading">加载中...</div>
  <div v-else-if="error" class="error">加载数据失败: {{ error }}</div>
  <div v-else style="display: flex; justify-content: space-around;">
    <div v-for="item in gauges" :key="item.title" style="width: 200px; height: 200px;">
      <div ref="charts" :id="item.id" style="width: 100%; height: 100%;"></div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import * as echarts from 'echarts'

const gauges = ref([])
const loading = ref(true)
const error = ref(null)

// 从API获取数据
const fetchData = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/oee-metrics')
    if (!response.ok) {
      throw new Error('网络响应不正常')
    }
    gauges.value = await response.json()
  } catch (err) {
    error.value = err.message
    console.error('获取数据失败:', err)
  } finally {
    loading.value = false
  }
}

// 初始化图表
const initCharts = () => {
  gauges.value.forEach(item => {
    const chart = echarts.init(document.getElementById(item.id))
    chart.setOption({
      series: [{
        type: 'gauge',
        progress: { show: true, width: 18 },
        axisLine: { lineStyle: { width: 18 } },
        axisTick: { show: false },
        splitLine: { length: 15, lineStyle: { width: 2 } },
        axisLabel: { distance: 20 },
        detail: { 
          valueAnimation: true, 
          formatter: '{value}%', 
          fontSize: 20,
          offsetCenter: [0, '50%']
        },
        title: {
          fontSize: 16,
          offsetCenter: [0, '80%']
        },
        data: [{ value: item.value, name: item.title }]
      }]
    })
  })
}

onMounted(async () => {
  await fetchData()
  if (!error.value) {
    initCharts()
  }
})
</script>

<style>
.loading, .error {
  text-align: center;
  padding: 20px;
  font-size: 18px;
}
.error {
  color: red;
}
</style>
```

## 3. 项目结构建议

```
project/
├── backend/          # Flask后端
│   ├── app.py        # Flask主应用
│   ├── requirements.txt
│   └── ...
├── frontend/         # Vue3前端
│   ├── src/
│   │   ├── components/
│   │   │   └── OeeDashboard.vue
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── ...
└── README.md
```

## 4. 运行项目

1. 启动 Flask 后端：
   ```bash
   cd backend
   pip install -r requirements.txt
   python app.py
   ```

2. 启动 Vue 前端：
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 5. 进一步改进建议

1. **环境变量**：将 API URL 存储在环境变量中，便于不同环境配置
2. **数据刷新**：可以添加定时刷新功能，定期获取最新数据
3. **错误处理**：增强错误处理和重试机制
4. **状态管理**：对于大型应用，可以考虑使用 Pinia 进行状态管理
5. **API 文档**：使用 Swagger 或类似工具为 Flask API 生成文档

这样改造后，你的 Vue3 仪表盘将从 Flask 后端动态获取数据，而不是使用硬编码的值。