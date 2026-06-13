# answer-sheet

一个配置驱动的答题卡生成 MVP。

当前阶段已经实现：

1. FastAPI 后端配置接收、布局计算、PDF 生成、`layout.json` 导出、文件下载
2. React 前端基础配置页面、生成操作、结果下载展示
3. 选择题 / 填空题 / 计算题三类题型
4. A4 单页容量校验、下载安全校验、基础自动化测试

## 目录

```text
backend/   FastAPI + ReportLab
frontend/  React + Vite + TypeScript
```

## 后端启动

建议使用 Python 3.11+。

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

默认地址：

```text
http://127.0.0.1:8000
```

## 前端启动

```powershell
cd frontend
npm install
npm run dev
```

默认地址：

```text
http://127.0.0.1:5173
```

## 中文字体配置

如果你要生成包含中文标题、中文考试名称或中文学生字段的 PDF，需要在下面目录放入一个可用中文字体文件：

```text
backend/assets/fonts/NotoSansCJKsc-Regular.otf
```

当前后端会优先检查这个路径。

如果缺少中文字体：

1. 纯英文配置仍可使用内置字体生成 PDF
2. 含中文内容时会返回 `FONT_NOT_FOUND`

## 测试

后端：

```powershell
pytest backend/tests -q
```

前端：

```powershell
cd frontend
npm run test
```

## 当前限制

1. 仅支持 A4 单页
2. 不支持自动分页
3. 不包含 OMR / OpenCV 识别
4. 不包含数据库、登录、二维码、模板管理
