# 依赖安装命令汇总

本文档**仅汇总需在本机手动执行的命令**；不在自动化脚本中替你执行。  
请先按项目规划创建 **`backend/`**、**`frontend/`** 目录与基础工程文件后再运行；若目录尚不存在，需先自行创建或先初始化脚手架。

---

## 前置环境

- **Conda**：Miniconda 或 Anaconda（用于**创建并管理 Python 环境**）。
- **Python**：由 conda 环境提供，建议 **3.11+**（与 FastAPI / Pydantic v2 兼容）。
- **Node.js**：建议 **20 LTS** 或 **18+**（用于 Vite / React）。
- **npm**：下文以 **npm** 为例；若使用 **pnpm** / **yarn**，将 `npm install` 换成对应命令即可。

---

## 后端（Python / FastAPI）

**约定**：使用 **conda** 管理 Python 环境；包安装在**已激活的环境**内。下列与主计划一致：**元数据使用 SQLite**，故 **`sqlalchemy`、`aiosqlite` 为必选**（不再标为可选）。

### 1. 创建并激活 conda 环境

环境名示例：`zerodrive`，可按需修改。

**Windows（PowerShell）：**

```powershell
conda create -n zerodrive python=3.11 -y
conda activate zerodrive
python -m pip install -U pip
```

若首次使用 conda 且无法 `activate`，先执行一次：`conda init powershell` 后重开终端，或按 Anaconda 文档初始化。

**Linux / macOS（Bash）：**

```bash
conda create -n zerodrive python=3.11 -y
conda activate zerodrive
python -m pip install -U pip
```

### 2. 进入后端目录（按需）

```powershell
cd backend
```

（路径请换成你本机 `ZeroDrive\backend`。）

### 3. 必选依赖（一行安装）

在**已执行 `conda activate zerodrive`** 的前提下运行：

**Windows / Linux / macOS 相同：**

```bash
pip install "fastapi" "uvicorn[standard]" "python-multipart" "pydantic-settings" "passlib[bcrypt]" "python-jose[cryptography]" "sqlalchemy" "aiosqlite"
```

说明：

- **`sqlalchemy`、`aiosqlite`**：与计划中文档「SQLite 存元数据、AsyncSession」一致。
- 其余为 Web、配置、表单上传与鉴权常用栈。

### 4. 可选：开发与接口测试

```bash
pip install "httpx" "pytest" "pytest-asyncio"
```

### 5. 可选：表结构迁移（表稳定后）

```bash
pip install "alembic"
```

---

## 前端（React + Vite + Mantine + DnD）

在仓库根目录进入 `frontend`（需已存在包含 `package.json` 的工程；若尚无，请先用 Vite 创建 React+TS 项目再执行下列命令）。

### 生产依赖（运行时）

**npm：**

```powershell
cd frontend
npm install react react-dom react-router-dom axios @mantine/core @mantine/hooks @mantine/notifications @mantine/modals @tabler/icons-react @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities
```

（Linux / macOS 将 `cd frontend` 与上面相同，其余一致。）

### 开发依赖（构建、类型、Mantine 样式）

```powershell
npm install -D vite @vitejs/plugin-react typescript @types/react @types/react-dom postcss postcss-preset-mantine postcss-simple-vars
```

---

## 若从零创建前端工程后再装依赖（可选）

仅在 **`frontend/` 尚不存在**时，可在仓库根目录执行一次：

```powershell
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

然后再执行上文「生产依赖」与「开发依赖」中的 `npm install` 命令；若 `create vite` 已包含部分包，可自行删减重复项。

---

## 与计划文档的对应关系

- **数据库**：元数据 **SQLite**（**SQLAlchemy + aiosqlite**），文件体在 **`DATA_ROOT`**，见 Cursor 计划：`网盘_mvp_功能设计_*.plan.md`（路径以本机 `.cursor/plans` 为准）。
- **API**：JSON 统一信封 **`{ code, msg, data }`**；**下载**成功为流式，不套该信封。
- **栈**：FastAPI、React + Vite、Mantine、@dnd-kit、单用户鉴权等以计划文档为准。
