以下是在 VS Code 中创建 Vue 3 工程并实现简单数据看板的完整步骤：

---

### 第一步：创建 Vue 3 项目
1. **打开 VS Code** 并启动终端（`Ctrl+`` `或菜单 Terminal > New Terminal）
2. **创建项目**（使用 Vite，推荐方式）：
   ```bash
   npm create vite@latest vue3-dashboard --template vue

   Select a framework: 选择Vue
   Select a variant: 选JavaScript

   ```
3. **进入项目目录**：
   ```bash
   cd vue3-dashboard
   ```
4. **安装依赖**：
   ```bash
   npm install
   npm run dev
   ```
   启动web服务，用浏览器打开所显示的网页链接，能正常
   然后Ctrl-C 停止web服务
   

5. **安装额外依赖**（图表库和 axios）：
   ```bash
   npm install echarts axios
   ```

---

### 第二步：清理默认文件
1. 删除 `src/components/HelloWorld.vue`
2. 清空 `src/App.vue` 内容，替换为：
   ```vue
   <template>
     <div id="app">
       <h1>生产数据看板</h1>
       <Dashboard />
     </div>
   </template>

   <script setup>
   import Dashboard from './components/Dashboard.vue'
   </script>

   <style>
   #app {
     font-family: Avenir, Helvetica, Arial, sans-serif;
     max-width: 1200px;
     margin: 0 auto;
     padding: 20px;
   }
   </style>
   ```

---

### 第三步：创建数据看板组件
创建文件 `src/components/Dashboard.vue` ，内容：

```vue
<template>
  <div class="dashboard">
    <!-- 指标卡片 -->
    <div class="metric-cards">
      <MetricCard 
        v-for="item in metrics" 
        :key="item.title"
        :title="item.title"
        :value="item.value"
        :trend="item.trend"
      />
    </div>

    <!-- 主图表 -->
    <div class="main-chart" ref="chartEl"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'
import MetricCard from './MetricCard.vue'

// 模拟数据
const metrics = ref([
  { title: '日产量', value: '1,284', trend: 'up' },
  { title: '合格率', value: '98.6%', trend: 'up' },
  { title: '设备OEE', value: '89.2%', trend: 'down' },
  { title: '能耗指数', value: '2.4', trend: 'down' }
])

// 图表实例
const chartEl = ref(null)

// 获取生产数据（模拟API）
async function fetchData() {
  try {
    // 实际项目替换为真实API
    // const res = await axios.get('/api/production')
    const mockData = {
      xData: ['1月', '2月', '3月', '4月', '5月', '6月'],
      series: [125, 232, 101, 264, 90, 340]
    }
    initChart(mockData)
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

// 初始化图表
function initChart(data) {
  const chart = echarts.init(chartEl.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    xAxis: {
      type: 'category',
      data: data.xData
    },
    yAxis: { type: 'value' },
    series: [{
      data: data.series,
      type: 'bar',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#83bff6' },
          { offset: 0.5, color: '#188df0' },
          { offset: 1, color: '#0052d9' }
        ])
      }
    }]
  }
  chart.setOption(option)
  
  // 响应式调整
  window.addEventListener('resize', () => chart.resize())
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.metric-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
}

.main-chart {
  width: 100%;
  height: 400px;
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .metric-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
```

---

### 第四步：创建指标卡片组件
创建文件 `src/components/MetricCard.vue` ，其中内容：

```vue
<template>
  <div class="metric-card">
    <div class="title">{{ title }}</div>
    <div class="value">{{ value }}</div>
    <div class="trend" :class="trend">
      <span v-if="trend === 'up'">↑</span>
      <span v-else>↓</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  value: String,
  trend: {
    type: String,
    validator: (val) => ['up', 'down'].includes(val)
  }
})
</script>

<style scoped>
.metric-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.title {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.trend {
  position: absolute;
  right: 20px;
  bottom: 20px;
  font-size: 24px;
}

.trend.up {
  color: #52c41a;
}

.trend.down {
  color: #f5222d;
}
</style>
```

---

### 第五步：启动项目
1. 在终端运行：
   ```bash
   npm run dev
   ```
2. 浏览器访问 `http://localhost:5173`，你将看到：
   - 顶部标题
   - 4个指标卡片（带趋势箭头）
   - 一个柱状图展示月度生产数据

---

### 项目结构说明
```
vue3-dashboard/
├── src/
│   ├── components/
│   │   ├── Dashboard.vue    # 主看板
│   │   └── MetricCard.vue   # 指标卡片
│   ├── App.vue              # 根组件
│   └── main.js              # 项目入口
```

---

### 关键点说明
1. **技术栈选择**：
   - 使用 Vite 构建（比 Vue CLI 更快）
   - ECharts 实现数据可视化
   - Composition API 编写逻辑

2. **响应式设计**：
   - 卡片布局在移动端自动变为 2 列
   - 图表会随窗口大小自动调整

3. **扩展建议**：
   - 添加 `/src/api` 目录管理所有数据请求
   - 使用 Pinia 进行状态管理（当数据复杂时）
   - 增加日期选择器实现动态数据查询

---

### 效果截图
![数据看板效果](https://i.imgur.com/JQ8W5Vy.png)

这个看板可以轻松扩展为真实项目，只需：
1. 替换 `fetchData()` 中的模拟数据为真实 API 调用
2. 根据业务需求添加更多图表类型（折线图、饼图等）