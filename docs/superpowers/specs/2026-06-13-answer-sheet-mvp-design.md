# 答题卡生成系统 MVP 设计说明

## 目标

基于 [PRD](E:/MyCodexProjects/answer-sheet/docs/PRD.md) 实现一个配置驱动的答题卡生成 MVP：前端输入答题卡参数，后端生成可打印的 A4 单页 PDF 和对应的 `layout.json`，并提供安全下载。

本阶段优先目标是打通最小可用闭环，而不是追求模板系统、多页排版或识别能力。

## 范围

本次实现包含：

1. FastAPI 后端脚手架与生成接口
2. 配置模型与参数校验
3. A4 单页布局计算
4. PDF 生成与中文字体检查
5. `layout.json` 导出
6. 生成文件本地存储与安全下载
7. React + Vite + TypeScript 前端配置页面
8. 前后端联调与最小交互
9. 覆盖核心行为的自动化测试

本次实现不包含：

1. 多页分页
2. OMR / OpenCV 识别
3. 用户系统、数据库、模板管理
4. 二维码、学号涂卡区、拖拽排版
5. Docker 部署

## 实现路径

采用“后端优先、前端后接入”的方式推进。

推荐原因：

1. 项目核心价值链在后端：布局计算、PDF 生成、`layout.json` 导出、错误码返回
2. 先稳定后端契约可以减少前端反复改接口
3. 当前仓库是空白起步，后端先落测试和接口更容易控制范围

## 总体架构

系统分为两个子项目：

1. `backend/`：负责配置接收、校验、布局计算、文件生成、文件下载
2. `frontend/`：负责表单输入、调用生成接口、展示结果、下载文件

运行方式：

1. 前端通过 HTTP 调用后端 `/api/answer-sheet/generate`
2. 后端返回 `taskId`、`pdfUrl`、`layoutJsonUrl`
3. 前端展示链接并允许下载

## 后端设计

### 目录结构

计划采用如下结构：

```text
backend/
├─ app/
│  ├─ main.py
│  ├─ models/
│  │  └─ paper_config.py
│  ├─ routers/
│  │  └─ answer_sheet.py
│  ├─ services/
│  │  ├─ font_service.py
│  │  ├─ layout_engine.py
│  │  ├─ layout_exporter.py
│  │  ├─ pdf_renderer.py
│  │  └─ file_service.py
│  ├─ core/
│  │  ├─ constants.py
│  │  └─ errors.py
│  └─ output/
│     ├─ pdf/
│     └─ json/
├─ assets/
│  └─ fonts/
├─ tests/
│  ├─ test_api.py
│  ├─ test_layout_engine.py
│  ├─ test_file_service.py
│  └─ test_pdf_renderer.py
└─ requirements.txt
```

### 模块职责

`main.py`

1. 创建 FastAPI 应用
2. 注册 CORS
3. 挂载路由
4. 启动时记录中文字体状态

`paper_config.py`

1. 定义 Pydantic 请求模型
2. 表达三类 section 配置
3. 做基础字段级校验

`layout_engine.py`

1. 统一使用 `mm` 作为布局单位
2. 计算页面内容区、标题区、学生信息区、定位点
3. 计算 choice / blank / calculation 各 section 坐标
4. 执行容量、宽度、高度校验
5. 输出供 PDF 和 `layout.json` 共用的布局对象

`pdf_renderer.py`

1. 检查并注册中文字体
2. 将 `mm` 转换为 ReportLab 的 `point`
3. 基于布局对象绘制 PDF
4. 不负责布局计算，只负责渲染

`layout_exporter.py`

1. 将布局对象转换为 PRD 规定的 `layout.json` 结构
2. 保证导出单位为 `mm`
3. 保证坐标系为 `pdf_bottom_left`

`file_service.py`

1. 生成唯一 `taskId`
2. 保存 PDF / JSON 文件
3. 校验下载文件名合法性
4. 限制只下载系统输出目录中的 `.pdf` 和 `.json`

`answer_sheet.py`

1. 暴露生成接口
2. 暴露下载接口
3. 将领域错误映射成统一响应结构

### 后端数据流

```text
请求 JSON
→ Pydantic 校验
→ LayoutEngine 生成布局
→ PdfRenderer 生成 PDF
→ LayoutExporter 生成 JSON
→ FileService 保存文件
→ 返回下载地址
```

### 错误处理

后端统一返回：

```json
{
  "success": false,
  "errorCode": "SOME_CODE",
  "message": "可读错误信息"
}
```

优先覆盖这些错误码：

1. `INVALID_REQUEST`
2. `UNSUPPORTED_PAGE_SIZE`
3. `OPTION_COUNT_MISMATCH`
4. `CHOICE_GRID_CAPACITY_EXCEEDED`
5. `PAGE_WIDTH_EXCEEDED`
6. `PAGE_HEIGHT_EXCEEDED`
7. `FONT_NOT_FOUND`
8. `INVALID_FILE_NAME`
9. `FILE_NOT_FOUND`
10. `INTERNAL_ERROR`

## 前端设计

### 目录结构

```text
frontend/
├─ src/
│  ├─ api/
│  │  └─ answerSheet.ts
│  ├─ components/
│  │  ├─ BasicInfoForm.tsx
│  │  ├─ SectionList.tsx
│  │  ├─ SectionEditor.tsx
│  │  └─ ResultPanel.tsx
│  ├─ types/
│  │  └─ answerSheet.ts
│  ├─ App.tsx
│  ├─ main.tsx
│  └─ styles.css
├─ tests/
└─ package.json
```

### 前端职责

1. 编辑基础信息：标题、考试名称、学生字段、是否显示定位点
2. 动态添加三类题型 section
3. 对表单做最小前端校验
4. 提交配置到后端
5. 展示生成中、成功、失败三类状态
6. 展示 PDF 与 `layout.json` 下载链接

### 前端边界

前端不做复杂排版预览，不复刻后端布局逻辑；只做输入和结果展示。页面保持简单清晰，避免超范围设计。

## 测试策略

实现阶段采用 TDD，先写失败测试，再补最小实现。

后端重点测试：

1. 请求模型与错误码映射
2. `optionCount !== options.length`
3. 选择题网格容量超限
4. 页面高度超限
5. 下载文件名非法
6. `layout.json` 单位与字段结构
7. 字体缺失时返回 `FONT_NOT_FOUND`

前端重点测试：

1. 默认表单值渲染
2. 提交配置触发接口调用
3. 接口失败时显示错误信息
4. 成功后展示两个下载入口

## 交付顺序

第一阶段先完成后端 MVP 闭环：

1. FastAPI 脚手架
2. 数据模型
3. 布局引擎
4. JSON 导出
5. PDF 生成
6. 文件下载
7. 后端测试通过

第二阶段接入前端：

1. Vite React 脚手架
2. 基础表单
3. section 编辑
4. 结果展示与下载
5. 联调

第三阶段补齐文档与验证：

1. README
2. 字体配置说明
3. 手工联调验证
4. PRD 验收项对照检查

## 风险与约束

1. 当前工作区不是 Git 仓库，无法按流程提交设计文档 commit
2. 中文字体文件默认不会随实现自动提供，需要用户后续放入 `backend/assets/fonts/`
3. ReportLab 渲染与布局单位转换必须严格隔离，否则容易造成 PDF 与 `layout.json` 坐标不一致
4. 单页限制是本次 MVP 的核心边界，任何自动分页需求都应明确拒绝进入本轮实现

## 验收基线

本次实现完成时，至少应满足：

1. 可通过前端提交一份有效配置
2. 后端返回 `taskId` 和两个下载地址
3. 下载的 PDF 可正常打开，中文可正常显示
4. 下载的 `layout.json` 结构与 PRD 一致
5. 超限和非法下载请求能返回正确错误码
6. 前后端本地可按 README 独立启动
