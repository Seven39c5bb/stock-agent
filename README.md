# Stock Intel Agent (股票智能分析助手)

这是一个基于产品设计文档开发的股票分析助手原型。它提供了一个 Vue 前端界面和 FastAPI 后端，通过大模型联网搜索获取股票数据，计算相关指标并返回结构化分析。

## 项目结构
- **frontend**: Vue 3 + Vite + Tailwind (用户交互界面)
- **backend**: FastAPI + LLM Web Search (数据处理与分析)

## 快速启动指南 (Windows)

### 一键启动（推荐）
在项目根目录执行：
```powershell
.\start.ps1
```

或直接双击：
```text
start.bat
```

说明：
- 脚本会自动检查并创建 `backend/.venv`。
- 默认会安装/更新后端依赖，并在前端首次运行时安装 `node_modules`。
- 脚本会分别打开两个 PowerShell 窗口启动前后端服务。
- 若你已安装好依赖，可用以下命令跳过安装步骤：
   ```powershell
   .\start.ps1 -SkipInstall
   ```
- 如需先查看将执行的命令（不实际启动服务）：
   ```powershell
   .\start.ps1 -SkipInstall -DryRun
   ```

### 1. 后端设置 (Backend)
1) **创建并激活虚拟环境**:
   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

2) **安装依赖**:
   ```powershell
   pip install -r requirements.txt
   ```

3) **配置文件**:
   - 确保 `backend/.env` 文件存在。
   - 必须配置 `LLM_API_KEY` 以便进行联网数据检索和分析。
   - 如需“分析模型”和“联网搜索模型”分离，可额外配置：
     - `LLM_ANALYSIS_MODEL`（文本分析）
     - `LLM_SEARCH_MODEL`（Responses + Web Search）
     - 以及对应的 `LLM_ANALYSIS_*` / `LLM_SEARCH_*` 地址、密钥、温度、超时
   - 若未配置上述专用变量，系统会自动回退到 `LLM_*`。
   - 检查 `CORS_ORIGINS` 是否包含前端运行的地址 (例如 `http://localhost:5173`)。

4) **启动 API 服务**:
   ```powershell
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### 2. 前端设置 (Frontend)
1) **安装依赖**:
   ```powershell
   cd frontend
   npm install
   ```

2) **配置文件**:
   - 确保 `frontend/.env` 中的 `VITE_API_BASE` 指向后端地址（默认 `http://localhost:8000`）。

3) **启动开发服务器**:
   ```powershell
   npm run dev
   ```

## 注意事项
- **数据非实时**: 界面显示的数据仅供参考，不构成投资建议。
- **联网搜索**: 后端高度依赖大模型的联网能力进行市场数据和历史信息的检索。
- **跨域问题**: 如果前端启动端口不是 5173，请在后端 `.env` 的 `CORS_ORIGINS` 中添加对应的地址。

---
## 调试建议
- 访问 `http://localhost:8000/docs` 可以查看后端的 Swagger API 文档。
- 如果请求失败，请检查浏览器控制台 (F12) 是否出现 CORS 报错。
