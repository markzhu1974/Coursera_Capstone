# Windows 系统 Vue 3 开发环境安装手册

## 系统要求
- 操作系统：Windows 10/11（64位）
- 内存：建议 4GB 以上
- 磁盘空间：至少 2GB 可用空间

## 第一部分：安装 Node.js

### 步骤 1：下载 Node.js 安装包
1. 打开浏览器访问 [Node.js 官网](https://nodejs.org/)
2. 选择 **LTS 版本**（推荐）并下载 Windows 安装包（.msi 格式）

### 步骤 2：安装 Node.js
1. 双击下载的 `.msi` 安装包
2. 在安装向导中：
   - 勾选 **"I accept the terms..."** 接受许可协议
   - 保持默认安装路径（`C:\Program Files\nodejs\`）
   - 勾选 **"Automatically install the necessary tools..."**（自动安装必要工具）
3. 点击 **Install** 开始安装
4. 安装完成后点击 **Finish**

### 步骤 3：验证安装
1. 打开 **命令提示符**（Win + R，输入 `cmd`）
2. 执行以下命令检查版本：
   ```bash
   node -v
   npm -v
   ```
   应显示类似：
   ```
   v18.18.2
   9.8.1
   ```

## 第二部分：配置 npm（可选）

### 步骤 1：设置淘宝镜像（国内用户推荐）
```bash
npm config set registry https://registry.npmmirror.com
npm config set disturl https://npmmirror.com/mirrors/node
```

### 步骤 2：更新 npm 到最新版
```bash
npm install -g npm@latest
```

## 第三部分：安装 Vue 脚手架

### 选项 A：使用 Vite（推荐）
```bash
npm create vite@latest
```
按提示操作：
1. 输入项目名称（如 `vue3-demo`）
2. 选择框架：**Vue**
3. 选择变体：**JavaScript** 或 **TypeScript**

### 选项 B：使用 Vue CLI（传统方式）
```bash
npm install -g @vue/cli
vue create vue3-demo
```
按提示选择 **Vue 3** 预设

## 第四部分：创建并运行 Vue 3 项目

### 步骤 1：进入项目目录
```bash
cd vue3-demo
```

### 步骤 2：安装依赖
```bash
npm install
# 或使用 yarn（需先安装：npm install -g yarn）
yarn install
```

### 步骤 3：启动开发服务器
```bash
npm run dev
# 或
yarn dev
```

### 步骤 4：访问项目
在浏览器中打开：
```
http://localhost:5173
```
（Vite 默认端口为 5173，Vue CLI 默认为 8080）

## 第五部分：安装 VS Code 插件（推荐）

1. 下载安装 [VS Code](https://code.visualstudio.com/)
2. 打开扩展市场（Ctrl + Shift + X），搜索安装：
   - **Volar**（Vue 官方语言支持）
   - **ESLint**（代码质量检查）
   - **Prettier**（代码格式化）
   - **Vue Language Features (Volar)**（Vue 3 语法支持）

## 常见问题解决

### 1. 命令提示"不是内部或外部命令"
- 检查 Node.js 是否安装成功
- 重启命令提示符或 VS Code
- 手动添加 Node.js 到系统 PATH：
  1. 右键"此电脑" → 属性 → 高级系统设置 → 环境变量
  2. 在 **Path** 中添加：`C:\Program Files\nodejs\`

### 2. 安装速度慢
- 使用淘宝镜像：
  ```bash
  npm config set registry https://registry.npmmirror.com
  ```
- 或使用 yarn：
  ```bash
  npm install -g yarn
  yarn config set registry https://registry.npmmirror.com
  ```

### 3. 端口冲突
修改 `vite.config.js` 或 `vue.config.js`：
```javascript
export default defineConfig({
  server: {
    port: 3000 // 改为其他端口
  }
})
```

## 附录：常用命令速查

| 命令 | 说明 |
|------|------|
| `npm create vite@latest` | 创建 Vite 项目 |
| `vue create project-name` | 创建 Vue CLI 项目 |
| `npm run dev` | 启动开发服务器 |
| `npm run build` | 构建生产版本 |
| `npm run lint` | 代码检查 |

---

> 本手册最后更新：2023年10月  
> 适用于 Vue 3.3 及以上版本