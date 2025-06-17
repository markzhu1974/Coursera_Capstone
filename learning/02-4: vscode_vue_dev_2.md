在上一节的 VS Code 项目中替换一下文件和内容：

---

1. 文件 src/App.vue内容，替换为：
```vue
<template>
  <OeeDashboard />
</template>

<script setup>
import OeeDashboard from './components/OeeDashboard.vue'
</script>
```
---

2. 文件 `src/components/OeeDashboard.vue` ，内容：

```vue
<template>
  <div style="display: flex; justify-content: space-around;">
    <div v-for="item in gauges" :key="item.title" style="width: 200px; height: 200px;">
      <div ref="charts" :id="item.id" style="width: 100%; height: 100%;"></div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import * as echarts from 'echarts'

const gauges = [
  { id: 'oee', title: 'OEE', value: 85 },
  { id: 'avail', title: '开动率', value: 90 },
  { id: 'perf', title: '性能开动率', value: 88 },
  { id: 'qual', title: '合格品率', value: 95 },
]

onMounted(() => {
  gauges.forEach(item => {
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
          offsetCenter: [0, '50%']  // 数值向下移
        },
        title: {
          fontSize: 16,
          offsetCenter: [0, '80%'] // 标题再往下移
        },
        data: [{ value: item.value, name: item.title }]
      }]
    })
  })
})
</script>

```

作业：
在上面的面板中如何增加一个第一个例子中的直方图的图表？