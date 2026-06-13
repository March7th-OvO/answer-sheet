# PRD：试卷及答题卡自动化生成系统 MVP

## 1. 项目名称

试卷及答题卡自动化生成系统 MVP

## 2. 项目背景

本项目目标是实现一个配置驱动的答题卡自动生成系统。

用户在前端输入考试基本信息、题型、题量、选择题选项数量、选择题排版参数等配置后，系统自动生成一份可打印的答题卡 PDF，并同步生成一份 `layout.json` 坐标文件。

`layout.json` 用于记录答题卡中每个选择题填涂点、填空题作答区域、计算题作答区域的位置，为后续 OpenCV 扫描识别和自动阅卷功能打基础。

MVP 阶段重点验证以下链路：

```text
前端配置输入 → 后端布局计算 → PDF 生成 → layout.json 导出 → 文件下载
```

MVP 阶段暂不实现扫描识别、自动阅卷、多页分页、二维码、数据库、用户系统等复杂能力。

## 3. 产品目标

MVP 的核心目标是验证答题卡自动生成的可行性。

具体目标如下：

1. 支持用户在前端配置答题卡基本信息。
2. 支持配置选择题、填空题、计算题三类题型。
3. 支持选择题自定义题量、选项内容、每行题目数、每列题目数、排列方式。
4. 支持后端根据配置自动计算题目区域坐标。
5. 支持生成标准 A4 单页 PDF 答题卡。
6. 支持 PDF 中文标题、中文字段、中文题型名称正常显示。
7. 支持同步导出 `layout.json`，记录每个题目和每个作答区域的位置。
8. 支持前端下载生成的 PDF 和 layout.json 文件。
9. 预留后续扫描识别模块的数据基础。

## 4. MVP 范围

### 4.1 本阶段需要实现

本阶段需要实现以下功能：

1. 前端答题卡配置页面。
2. 后端配置接收接口。
3. 配置参数校验。
4. 答题卡布局计算模块。
5. PDF 生成模块。
6. PDF 中文字体支持。
7. layout.json 生成模块。
8. 文件下载接口。
9. 文件下载安全校验。
10. 前后端联调所需 CORS 配置。
11. 简单的生成结果展示与下载入口。

### 4.2 本阶段暂不实现

以下功能不在 MVP 范围内：

1. 答题卡扫描识别。
2. OpenCV 填涂识别。
3. 手写文字识别。
4. 自动阅卷。
5. 数据库存储。
6. 用户登录与权限管理。
7. 多模板管理。
8. 多页答题卡。
9. 自动分页。
10. A3、B4 等复杂纸张适配。
11. 前端拖拽式编辑器。
12. 二维码。
13. 学号涂卡区。
14. 复杂美化样式。
15. Docker 部署。

MVP 阶段固定只支持 A4 单页答题卡。如果内容超出 A4 单页可用区域，后端应返回明确错误提示，不进行自动分页。

## 5. 推荐技术栈

### 5.1 前端

推荐使用：

```text
React
Vite
TypeScript
Axios
```

前端职责：

1. 提供答题卡配置表单。
2. 将配置 JSON 提交给后端。
3. 接收后端生成结果。
4. 展示生成状态。
5. 提供 PDF 和 layout.json 下载入口。

### 5.2 后端

推荐使用：

```text
Python 3.11+
FastAPI
ReportLab
Pydantic
Uvicorn
```

后端职责：

1. 接收答题卡配置。
2. 校验配置合法性。
3. 计算布局坐标。
4. 生成 PDF。
5. 生成 layout.json。
6. 返回文件下载地址。
7. 提供安全文件下载接口。

### 5.3 后续识别预留

后续可以增加：

```text
OpenCV
NumPy
Pillow
```

MVP 阶段不接入识别模块。

## 6. 核心业务流程

用户使用流程如下：

1. 用户进入前端页面。
2. 输入考试名称、答题卡标题、学生信息字段。
3. 添加题型配置。
4. 配置选择题、填空题、计算题数量。
5. 点击“生成答题卡”。
6. 前端将配置 JSON 发送到后端。
7. 后端校验配置。
8. 后端 LayoutEngine 计算坐标。
9. 后端 PdfRenderer 生成 PDF。
10. 后端 LayoutExporter 生成 layout.json。
11. 后端返回 taskId、PDF 下载地址、layout.json 下载地址。
12. 用户下载 PDF 和 layout.json。

## 7. 前端页面需求

### 7.1 页面名称

答题卡生成页面。

### 7.2 页面结构

页面分为四个区域：

1. 基础信息配置区。
2. 题型配置区。
3. 生成操作区。
4. 结果下载区。

### 7.3 基础信息配置区

需要包含以下字段：

| 字段                | 类型       | 是否必填 | 默认值      | 说明         |
| ----------------- | -------- | ---- | -------- | ---------- |
| paperTitle        | string   | 是    | 答题卡      | PDF 顶部标题   |
| examName          | string   | 否    | 空        | 考试名称       |
| pageSize          | string   | 是    | A4       | MVP 只支持 A4 |
| studentFields     | string[] | 是    | 姓名、学号、班级 | 学生信息栏字段    |
| showPositionMarks | boolean  | 否    | true     | 是否显示四角定位点  |

MVP 阶段不提供二维码配置字段。

### 7.4 题型配置区

用户可以添加多个题型区块。

MVP 支持三种题型：

1. 选择题。
2. 填空题。
3. 计算题。

### 7.5 选择题配置字段

| 字段                 | 类型       | 是否必填 | 默认值          | 说明     |
| ------------------ | -------- | ---- | ------------ | ------ |
| type               | string   | 是    | choice       | 题型     |
| title              | string   | 是    | 一、选择题        | 分区标题   |
| questionCount      | number   | 是    | 20           | 选择题数量  |
| optionCount        | number   | 是    | 4            | 选项数量   |
| options            | string[] | 是    | A,B,C,D      | 选项文本   |
| questionsPerRow    | number   | 是    | 4            | 每行几个题目 |
| questionsPerColumn | number   | 是    | 10           | 每列几个题目 |
| fillOrder          | string   | 是    | column_first | 排列方式   |

`fillOrder` 可选值：

```text
row_first
column_first
```

MVP 默认使用：

```text
column_first
```

MVP 阶段固定使用圆形填涂框，不提供 `bubbleShape` 字段。后续模板扩展阶段可以增加填涂框形状配置。

### 7.6 填空题配置字段

| 字段               | 类型     | 是否必填 | 默认值   | 说明     |
| ---------------- | ------ | ---- | ----- | ------ |
| type             | string | 是    | blank | 题型     |
| title            | string | 是    | 二、填空题 | 分区标题   |
| questionCount    | number | 是    | 5     | 填空题数量  |
| linesPerQuestion | number | 是    | 1     | 每题横线数量 |

### 7.7 计算题配置字段

| 字段                | 类型     | 是否必填 | 默认值         | 说明            |
| ----------------- | ------ | ---- | ----------- | ------------- |
| type              | string | 是    | calculation | 题型            |
| title             | string | 是    | 三、计算题       | 分区标题          |
| questionCount     | number | 是    | 3           | 计算题数量         |
| heightPerQuestion | number | 是    | 35          | 每题作答区高度，单位 mm |

## 8. 请求数据结构

前端提交给后端的 JSON 示例：

```json
{
  "paperTitle": "软件工程期末考试答题卡",
  "examName": "2026年春季学期期末考试",
  "pageSize": "A4",
  "studentFields": ["姓名", "学号", "班级"],
  "showPositionMarks": true,
  "sections": [
    {
      "type": "choice",
      "title": "一、选择题",
      "questionCount": 40,
      "optionCount": 4,
      "options": ["A", "B", "C", "D"],
      "questionsPerRow": 4,
      "questionsPerColumn": 10,
      "fillOrder": "column_first"
    },
    {
      "type": "blank",
      "title": "二、填空题",
      "questionCount": 3,
      "linesPerQuestion": 1
    },
    {
      "type": "calculation",
      "title": "三、计算题",
      "questionCount": 2,
      "heightPerQuestion": 25
    }
  ]
}
```

说明：

1. `options` 为主字段。
2. `optionCount` 可以保留用于前端表单展示，但后端必须校验 `optionCount === options.length`。
3. MVP 阶段不接收 `showQRCode`。
4. MVP 阶段不接收 `bubbleShape`。

## 9. 响应数据结构

### 9.1 成功响应

```json
{
  "success": true,
  "taskId": "sheet_20260613_001",
  "pdfUrl": "/api/files/sheet_20260613_001.pdf",
  "layoutJsonUrl": "/api/files/sheet_20260613_001_layout.json",
  "message": "答题卡生成成功"
}
```

### 9.2 失败响应

失败响应必须包含 `errorCode`，前端不应依赖 `message` 字符串判断错误类型。

```json
{
  "success": false,
  "errorCode": "PAGE_HEIGHT_EXCEEDED",
  "message": "答题卡内容超出 A4 单页可用高度，请减少题量或调整排版参数"
}
```

### 9.3 错误码列表

MVP 阶段至少支持以下错误码：

| errorCode                     | 含义                               |
| ----------------------------- | -------------------------------- |
| INVALID_REQUEST               | 请求参数不合法                          |
| UNSUPPORTED_PAGE_SIZE         | 不支持的纸张大小                         |
| OPTION_COUNT_MISMATCH         | optionCount 与 options.length 不一致 |
| CHOICE_GRID_CAPACITY_EXCEEDED | 选择题数量超过当前选择题网格容量                 |
| PAGE_WIDTH_EXCEEDED           | 内容超出 A4 单页可用宽度                   |
| PAGE_HEIGHT_EXCEEDED          | 内容超出 A4 单页可用高度                   |
| FONT_NOT_FOUND                | 未找到可用中文字体                        |
| INVALID_FILE_NAME             | 文件名非法                            |
| FILE_NOT_FOUND                | 文件不存在                            |
| INTERNAL_ERROR                | 服务内部错误                           |

## 10. layout.json 结构

layout.json 用于记录答题卡中所有可识别区域的坐标。

### 10.1 坐标系说明

layout.json 中所有坐标均采用 PDF 逻辑坐标系。

规则如下：

```text
单位：mm
原点：页面左下角
x 轴：向右递增
y 轴：向上递增
```

因此，视觉上的 `top_left` 定位点会具有较大的 y 值。

后续如果将 PDF 或扫描图转换为图片进行 OpenCV 识别，图片坐标系通常是左上角为原点，需要进行坐标转换。

转换公式：

```text
image_y = page_height - pdf_y
```

如果需要转换一个矩形区域，还需要考虑矩形高度：

```text
image_rect_y = page_height - pdf_rect_y - rect_height
```

### 10.2 layout.json 示例

```json
{
  "sheetId": "sheet_20260613_001",
  "paperTitle": "软件工程期末考试答题卡",
  "pageSize": "A4",
  "unit": "mm",
  "coordinateSystem": "pdf_bottom_left",
  "pages": [
    {
      "pageIndex": 1,
      "width": 210,
      "height": 297,
      "positionMarks": [
        {
          "name": "top_left",
          "x": 10,
          "y": 281,
          "width": 6,
          "height": 6
        },
        {
          "name": "top_right",
          "x": 194,
          "y": 281,
          "width": 6,
          "height": 6
        },
        {
          "name": "bottom_left",
          "x": 10,
          "y": 10,
          "width": 6,
          "height": 6
        },
        {
          "name": "bottom_right",
          "x": 194,
          "y": 10,
          "width": 6,
          "height": 6
        }
      ],
      "sections": [
        {
          "type": "choice",
          "title": "一、选择题",
          "questions": [
            {
              "questionNo": 1,
              "type": "choice",
              "options": [
                {
                  "option": "A",
                  "x": 32,
                  "y": 220,
                  "radius": 2.0
                },
                {
                  "option": "B",
                  "x": 40,
                  "y": 220,
                  "radius": 2.0
                },
                {
                  "option": "C",
                  "x": 48,
                  "y": 220,
                  "radius": 2.0
                },
                {
                  "option": "D",
                  "x": 56,
                  "y": 220,
                  "radius": 2.0
                }
              ]
            }
          ]
        },
        {
          "type": "blank",
          "title": "二、填空题",
          "questions": [
            {
              "questionNo": 1,
              "type": "blank",
              "x": 20,
              "y": 130,
              "width": 170,
              "height": 8
            }
          ]
        },
        {
          "type": "calculation",
          "title": "三、计算题",
          "questions": [
            {
              "questionNo": 1,
              "type": "calculation",
              "x": 20,
              "y": 80,
              "width": 170,
              "height": 35
            }
          ]
        }
      ]
    }
  ]
}
```

### 10.3 选择题 option 坐标说明

MVP 阶段选择题填涂框固定为圆形，option 对象使用 `radius` 字段。

示例：

```json
{
  "option": "A",
  "x": 32,
  "y": 220,
  "radius": 2.0
}
```

说明：

```text
x、y 表示圆心坐标，单位 mm，采用 PDF 坐标系。
radius 表示圆形填涂框半径，单位 mm。
```

后续如果支持方形或矩形填涂框，可以扩展为：

```json
{
  "shape": "rect",
  "x": 32,
  "y": 220,
  "width": 4,
  "height": 4
}
```

但 MVP 阶段不实现该扩展。

## 11. 坐标单位与 ReportLab 渲染要求

系统内部布局引擎统一使用 mm 作为逻辑单位。

ReportLab 默认绘图单位是 point，而不是 mm。1 point 等于 1/72 英寸，约等于 0.3528 mm。

因此：

1. `layout_engine` 输出的坐标单位必须是 mm。
2. `layout.json` 保存的坐标单位必须是 mm。
3. `pdf_renderer` 调用 ReportLab 绘图时，必须将 mm 转换为 point。
4. 禁止在 `pdf_renderer` 中直接把 mm 数值当作 ReportLab 坐标使用。

推荐转换方式：

```python
from reportlab.lib.units import mm

def to_pt(value_mm: float) -> float:
    return value_mm * mm
```

示例：

```python
c.drawString(to_pt(x_mm), to_pt(y_mm), text)
c.circle(to_pt(x_mm), to_pt(y_mm), to_pt(radius_mm))
c.rect(to_pt(x_mm), to_pt(y_mm), to_pt(width_mm), to_pt(height_mm))
```

## 12. 后端模块设计

建议后端目录结构如下：

```text
backend/
├── app/
│   ├── main.py
│   ├── models/
│   │   └── paper_config.py
│   ├── services/
│   │   ├── layout_engine.py
│   │   ├── pdf_renderer.py
│   │   ├── layout_exporter.py
│   │   └── file_service.py
│   ├── routers/
│   │   └── answer_sheet.py
│   ├── assets/
│   │   └── fonts/
│   └── output/
│       ├── pdf/
│       └── json/
├── requirements.txt
└── README.md
```

### 12.1 main.py

负责启动 FastAPI 应用，并配置 CORS。

MVP 开发阶段需要允许前端开发服务器访问后端，例如：

```text
http://localhost:5173
```

FastAPI 需要添加 CORS 中间件：

```python
from fastapi.middleware.cors import CORSMiddleware
```

MVP 阶段可以允许以下 origin：

```text
http://localhost:5173
http://127.0.0.1:5173
```

### 12.2 paper_config.py

负责定义 Pydantic 数据模型，包括：

1. PaperConfig。
2. ChoiceSectionConfig。
3. BlankSectionConfig。
4. CalculationSectionConfig。

### 12.3 layout_engine.py

负责根据配置计算所有题区坐标。

主要职责：

1. 计算基础信息区域坐标。
2. 计算定位点坐标。
3. 计算选择题区域坐标。
4. 计算填空题区域坐标。
5. 计算计算题区域坐标。
6. 检查网格容量是否足够。
7. 检查内容是否超出 A4 单页可用宽度。
8. 检查内容是否超出 A4 单页可用高度。
9. 输出标准布局对象，坐标单位为 mm。

### 12.4 pdf_renderer.py

负责根据布局对象生成 PDF。

主要职责：

1. 注册中文字体。
2. 将 mm 坐标转换为 point 坐标。
3. 绘制标题。
4. 绘制考试名称。
5. 绘制学生信息栏。
6. 绘制定位点。
7. 绘制选择题填涂区。
8. 绘制填空题横线。
9. 绘制计算题作答框。
10. 保存 PDF 文件。

### 12.5 layout_exporter.py

负责将布局对象导出为 JSON 文件。

### 12.6 file_service.py

负责文件下载安全校验。

文件下载接口必须防止路径遍历攻击。

## 13. 接口设计

### 13.1 生成答题卡接口

接口：

```http
POST /api/answer-sheet/generate
```

请求体示例（注意：sections 不允许为空，以下为完整有效示例）：

```json
{
  "paperTitle": "软件工程期末考试答题卡",
  "examName": "2026年春季学期期末考试",
  "pageSize": "A4",
  "studentFields": ["姓名", "学号", "班级"],
  "showPositionMarks": true,
  "sections": [
    {
      "type": "choice",
      "title": "一、选择题",
      "questionCount": 40,
      "optionCount": 4,
      "options": ["A", "B", "C", "D"],
      "questionsPerRow": 4,
      "questionsPerColumn": 10,
      "fillOrder": "column_first"
    },
    {
      "type": "blank",
      "title": "二、填空题",
      "questionCount": 3,
      "linesPerQuestion": 1
    },
    {
      "type": "calculation",
      "title": "三、计算题",
      "questionCount": 2,
      "heightPerQuestion": 25
    }
  ]
}
```

成功响应：

```json
{
  "success": true,
  "taskId": "sheet_20260613_001",
  "pdfUrl": "/api/files/sheet_20260613_001.pdf",
  "layoutJsonUrl": "/api/files/sheet_20260613_001_layout.json",
  "message": "答题卡生成成功"
}
```

失败响应：

```json
{
  "success": false,
  "errorCode": "INVALID_REQUEST",
  "message": "请求参数不合法"
}
```

### 13.2 文件下载接口

接口：

```http
GET /api/files/{filename}
```

功能：

根据文件名下载 PDF 或 JSON 文件。

Content-Type 要求：

文件下载接口必须根据文件扩展名返回正确的 Content-Type：

```text
.pdf  → Content-Type: application/pdf
.json → Content-Type: application/json; charset=utf-8
```

如果文件扩展名不是 `.pdf` 或 `.json`，返回：

```json
{
  "success": false,
  "errorCode": "INVALID_FILE_NAME",
  "message": "只允许下载 PDF 或 JSON 文件"
}
```

安全要求：

1. 只允许下载系统生成的 `.pdf` 和 `.json` 文件。
2. 文件名不允许包含 `../`、`..\\`、`/`、`\\` 等路径分隔符。
3. 文件名不允许为空。
4. 后端必须使用安全路径拼接。
5. 后端必须校验最终路径仍位于 output 目录内。
6. 如果文件名非法，返回 `INVALID_FILE_NAME`。
7. 如果文件不存在，返回 `FILE_NOT_FOUND`。

## 14. 前端模块设计

建议前端目录结构如下：

```text
frontend/
├── src/
│   ├── api/
│   │   └── answerSheetApi.ts
│   ├── components/
│   │   ├── BasicConfigForm.tsx
│   │   ├── SectionConfigList.tsx
│   │   ├── ChoiceSectionForm.tsx
│   │   ├── BlankSectionForm.tsx
│   │   └── CalculationSectionForm.tsx
│   ├── pages/
│   │   └── AnswerSheetGeneratorPage.tsx
│   ├── types/
│   │   └── answerSheet.ts
│   ├── App.tsx
│   └── main.tsx
├── package.json
└── vite.config.ts
```

## 15. 前端交互要求

页面初始状态默认提供一个选择题区块：

```json
{
  "type": "choice",
  "title": "一、选择题",
  "questionCount": 40,
  "optionCount": 4,
  "options": ["A", "B", "C", "D"],
  "questionsPerRow": 4,
  "questionsPerColumn": 10,
  "fillOrder": "column_first"
}
```

用户可以：

1. 修改答题卡标题。
2. 修改考试名称。
3. 修改学生信息字段。
4. 添加选择题区块。
5. 添加填空题区块。
6. 添加计算题区块。
7. 删除题型区块。
8. 点击生成按钮。
9. 查看生成结果。
10. 下载 PDF。
11. 下载 layout.json。

MVP 可以不做实时 PDF 预览。生成后提供 PDF 下载链接即可。

## 16. 版式规则

### 16.1 页面基础规则

MVP 默认使用 A4 纵向页面。

页面尺寸：

```text
宽度：210 mm
高度：297 mm
```

建议页边距：

```text
左边距：15 mm
右边距：15 mm
上边距：15 mm
下边距：15 mm
```

可用内容区域：

```text
content_width = 210 - 15 - 15 = 180 mm
content_height = 297 - 15 - 15 = 267 mm
```

### 16.2 标题区域

标题居中显示，字号较大。

示例：

```text
软件工程期末考试答题卡
```

标题下方显示考试名称。

建议高度：

```text
标题区高度：16 mm
```

### 16.3 学生信息区域

学生信息区域显示：

```text
姓名：__________
学号：__________
班级：__________
```

字段由前端配置。

建议高度：

```text
学生信息区高度：24 mm
```

### 16.4 定位点

如果 `showPositionMarks = true`，则在页面四角绘制黑色定位点。

定位点参数：

```text
定位点尺寸：6 mm × 6 mm
定位点距离页面外边缘：10 mm
```

四个定位点坐标采用 PDF 坐标系，单位为 mm，坐标表示矩形左下角位置：

```text
top_left:
x = 10
y = 297 - 10 - 6 = 281

top_right:
x = 210 - 10 - 6 = 194
y = 281

bottom_left:
x = 10
y = 10

bottom_right:
x = 194
y = 10
```

### 16.5 题型区块统一间距语义

所有题型区块统一使用以下版式参数：

```text
sectionTitleHeight = 8 mm
titleToContentGap = 4 mm
sectionGap = 4 mm
```

说明：

```text
sectionTitleHeight 表示题型标题自身占用高度。
titleToContentGap 表示题型标题与本区块第一行内容之间的距离。
sectionGap 表示当前题型区块结束后，到下一个题型标题之间的额外距离。
```

MVP 阶段不再单独使用 `sectionBottomGap`，避免与 `sectionGap` 语义重复。

`sectionGap` 仅在当前 section 后面还有 section 时才由 LayoutEngine 追加。最后一个 section 之后不追加 sectionGap。

### 16.6 选择题区域

选择题以圆形填涂框形式展示。

示例：

```text
01. ○A ○B ○C ○D
```

选择题布局支持两种排列方式。

#### column_first

列优先排列：

```text
01  11  21  31
02  12  22  32
03  13  23  33
...
10  20  30  40
```

#### row_first

行优先排列：

```text
01  02  03  04
05  06  07  08
09  10  11  12
...
```

MVP 默认使用 `column_first`。

选择题默认布局参数：

```text
questionNoWidth = 8 mm
optionBlockWidth = 8 mm
questionInnerPadding = 4 mm
choiceQuestionRowHeight = 6 mm
bubbleRadius = 2.0 mm
```

选择题单题宽度计算公式（动态，随选项数量变化）：

```text
choiceQuestionWidth = questionNoWidth + optionCount × optionBlockWidth + questionInnerPadding
```

示例：

```text
4 选项题：
choiceQuestionWidth = 8 + 4 × 8 + 4 = 44 mm

5 选项题：
choiceQuestionWidth = 8 + 5 × 8 + 4 = 52 mm
```

选择题区域物理宽度计算：

```text
choice_section_width = questionsPerRow × choiceQuestionWidth
```

选择题区域宽度必须满足：

```text
choice_section_width <= content_width
```

如果不满足，返回：

```json
{
  "success": false,
  "errorCode": "PAGE_WIDTH_EXCEEDED",
  "message": "选择题区域超出 A4 单页可用宽度，请减少每行题目数量或减少选项数量"
}
```

选择题区域物理高度计算：

```text
choice_section_height = sectionTitleHeight + titleToContentGap + questionsPerColumn × choiceQuestionRowHeight
```

其中：

```text
sectionTitleHeight = 8 mm
titleToContentGap = 4 mm
choiceQuestionRowHeight = 6 mm
```

如果该选择题区块后面还有其他 section，则 LayoutEngine 额外追加 sectionGap：

```text
sectionGap = 4 mm
```

### 16.7 填空题区域

填空题按照题号绘制横线。

示例：

```text
1. ______________________________
2. ______________________________
```

每题横线数量由 `linesPerQuestion` 控制。

填空题默认布局参数：

```text
sectionTitleHeight = 8 mm
titleToContentGap = 4 mm
blankLineHeight = 6 mm
blankQuestionGap = 3 mm
```

填空题区域高度计算公式：

```text
blank_section_height = sectionTitleHeight
                     + titleToContentGap
                     + questionCount × linesPerQuestion × blankLineHeight
                     + (questionCount - 1) × blankQuestionGap
```

如果该填空题区块后面还有其他 section，则 LayoutEngine 额外追加 sectionGap：

```text
sectionGap = 4 mm
```

示例：

```text
questionCount = 3
linesPerQuestion = 1

blank_section_height = 8 + 4 + 3 × 1 × 6 + 2 × 3 = 36 mm
```

### 16.8 计算题区域

计算题绘制作答框。

示例：

```text
1.
┌──────────────────────────────┐
│                              │
│                              │
└──────────────────────────────┘
```

每题区域高度由 `heightPerQuestion` 控制，单位 mm。

建议参数：

```text
sectionTitleHeight = 8 mm
titleToContentGap = 4 mm
calculationQuestionNoHeight = 5 mm
calculationQuestionGap = 4 mm
```

计算题区域高度计算公式：

```text
calculation_section_height = sectionTitleHeight
                           + titleToContentGap
                           + questionCount × (calculationQuestionNoHeight + heightPerQuestion)
                           + (questionCount - 1) × calculationQuestionGap
```

如果该计算题区块后面还有其他 section，则 LayoutEngine 额外追加 sectionGap：

```text
sectionGap = 4 mm
```

示例：

```text
questionCount = 2
heightPerQuestion = 25

calculation_section_height = 8 + 4 + 2 × (5 + 25) + 1 × 4 = 76 mm
```

## 17. 校验规则

后端需要做以下校验：

1. `paperTitle` 不能为空。
2. `pageSize` MVP 阶段只能为 A4。
3. `sections` 至少包含一个题型。
4. `studentFields` 至少包含一个字段。
5. 选择题 `questionCount` 必须大于 0。
6. 选择题 `optionCount` 必须大于等于 2。
7. 选择题 `options.length` 必须等于 `optionCount`。
8. 选择题 `questionsPerRow` 必须大于 0。
9. 选择题 `questionsPerColumn` 必须大于 0。
10. 选择题 `fillOrder` 只能为 `row_first` 或 `column_first`。
11. 选择题必须满足网格容量校验：

```text
questionCount <= questionsPerRow × questionsPerColumn
```

如果不满足，返回：

```json
{
  "success": false,
  "errorCode": "CHOICE_GRID_CAPACITY_EXCEEDED",
  "message": "选择题数量超过当前选择题网格容量"
}
```

12. 选择题必须满足物理宽度校验：

```text
choice_section_width <= content_width
```

如果不满足，返回：

```json
{
  "success": false,
  "errorCode": "PAGE_WIDTH_EXCEEDED",
  "message": "选择题区域超出 A4 单页可用宽度，请减少每行题目数量或减少选项数量"
}
```

13. 选择题必须满足物理高度校验：

```text
choice_section_height <= remaining_page_height
```

如果不满足，返回：

```json
{
  "success": false,
  "errorCode": "PAGE_HEIGHT_EXCEEDED",
  "message": "选择题区域超出 A4 单页可用高度，请减少每列题目数量或调整排版参数"
}
```

14. 填空题 `questionCount` 必须大于 0。
15. 填空题 `linesPerQuestion` 必须大于 0。
16. 计算题 `questionCount` 必须大于 0。
17. 计算题 `heightPerQuestion` 必须大于 0。
18. 所有题型区域合计高度不能超过 A4 单页可用高度。
19. 如果超出页面，返回：

```json
{
  "success": false,
  "errorCode": "PAGE_HEIGHT_EXCEEDED",
  "message": "答题卡内容超出 A4 单页可用高度，请减少题量或调整排版参数"
}
```

20. 文件下载接口必须校验文件名，防止路径遍历。
21. 文件下载接口只允许下载系统生成的 `.pdf` 和 `.json` 文件。

## 18. PDF 中文字体要求

PDF 中文字体支持是 P0 必须实现项。

ReportLab 默认字体不支持中文，因此后端必须注册中文字体后再绘制中文文本。

实现要求：

1. 后端必须支持中文标题、中文考试名称、中文学生字段、中文题型标题正常显示。
2. 不允许生成中文乱码或方块字 PDF。
3. 不应强依赖某个固定操作系统字体路径。
4. 推荐在 `backend/assets/fonts/` 目录放置中文字体文件。
5. README 必须说明中文字体文件的配置方式。
6. 如果找不到中文字体，后端应返回 `FONT_NOT_FOUND`，而不是生成乱码 PDF。

字体检测时机：

后端应在两个阶段检查中文字体：

1. **服务启动时**：检查字体文件是否存在，并在日志中输出检查结果。
2. **生成 PDF 前**：再次检查字体是否可用，不可用时返回错误。

启动检查失败不应阻止服务启动，但应输出警告日志。生成 PDF 时如果字体不可用，必须返回：

```json
{
  "success": false,
  "errorCode": "FONT_NOT_FOUND",
  "message": "未找到可用中文字体，请在 backend/assets/fonts/ 目录下配置中文字体文件"
}
```

推荐字体路径：

```text
backend/assets/fonts/NotoSansCJKsc-Regular.otf
```

推荐配置方式：

```text
backend/assets/fonts/NotoSansCJKsc-Regular.otf
```

后端可以优先读取项目内字体路径：

```text
backend/assets/fonts/
```

如果用户没有放置字体，启动或生成 PDF 时应给出明确错误提示。

## 19. 文件存储策略

MVP 阶段生成的 PDF 和 layout.json 文件保存在后端本地 `output` 目录中。

推荐结构：

```text
backend/app/output/
├── pdf/
│   └── sheet_20260613_001.pdf
└── json/
    └── sheet_20260613_001_layout.json
```

MVP 阶段暂不实现自动清理机制。

文件默认永久保留，后续版本再增加以下能力：

1. 定时清理。
2. 按 taskId 删除。
3. 对象存储迁移。
4. 文件过期时间。
5. 任务记录数据库化。

## 20. 最小可行实现优先级

### P0：必须实现

1. FastAPI 后端服务。
2. React 前端配置页面。
3. 后端 CORS 配置。
4. 选择题配置。
5. 填空题配置。
6. 计算题配置。
7. 配置参数校验。
8. 单页容量校验。
9. PDF 生成。
10. PDF 中文字体支持。
11. mm 到 point 的 ReportLab 渲染转换。
12. layout.json 生成。
13. 文件下载。
14. 文件下载安全校验。
15. 错误响应 errorCode。

### P1：建议实现

1. 四角定位点。
2. 选择题 column_first / row_first 切换。
3. 生成结果展示。
4. 更友好的前端表单校验。
5. README 运行说明。

### P2：暂缓实现

1. 实时 PDF 预览。
2. 多页答题卡。
3. 自动分页。
4. 二维码。
5. 学号涂卡区。
6. OMR 识别。
7. 模板保存。
8. 用户系统。
9. 数据库。
10. Docker 部署。

## 21. 开发顺序建议

建议按以下顺序开发：

1. 搭建 FastAPI 项目。
2. 配置 CORS。
3. 定义 Pydantic 请求模型。
4. 实现中文字体加载逻辑。
5. 编写固定配置 PDF 生成 Demo。
6. 加入 mm 到 point 的坐标转换。
7. 将固定配置改造成 JSON 配置驱动。
8. 实现选择题布局计算。
9. 实现选择题网格容量校验。
10. 实现选择题物理宽度和高度校验。
11. 实现 layout.json 导出。
12. 实现填空题区域。
13. 实现计算题区域。
14. 实现安全文件下载接口。
15. 搭建 React 前端页面。
16. 前端调用后端生成接口。
17. 实现 PDF 和 JSON 下载。
18. 清理代码结构和 README。

## 22. Codex 实现要求

请 Codex 按照以下要求实现：

1. 先实现 MVP，不要过度设计。
2. 后端使用 FastAPI。
3. PDF 生成使用 ReportLab。
4. 前端使用 React + Vite + TypeScript。
5. 后端需要支持中文标题和中文字段。
6. 后端必须注册中文字体。
7. 后端必须实现 mm 到 point 的 ReportLab 坐标转换。
8. 后端内部布局坐标统一使用 mm。
9. layout.json 中坐标统一使用 mm。
10. 生成文件保存到后端本地 output 目录。
11. 每次生成使用唯一 taskId。
12. PDF 文件名格式：

```text
{taskId}.pdf
```

13. layout.json 文件名格式：

```text
{taskId}_layout.json
```

14. 后端接口返回文件下载 URL。
15. 文件下载接口必须防止路径遍历。
16. 前端页面能完整提交配置并下载文件。
17. 暂时不需要数据库。
18. 暂时不需要登录。
19. 暂时不需要 Docker。
20. 暂时不需要二维码。
21. 暂时不需要自动分页。
22. 暂时不需要 OMR 识别。
23. 代码需要有清晰目录结构。
24. README 需要说明如何启动前后端。
25. README 需要说明中文字体文件如何配置。

## 23. 验收标准

MVP 完成后，应满足以下条件：

1. 启动后端服务成功。
2. 启动前端页面成功。
3. 前端能够正常请求后端，不被 CORS 阻止。
4. 用户可以在前端输入答题卡配置。
5. 用户点击生成后，后端成功返回 PDF 和 JSON 下载地址。
6. 下载的 PDF 能正常打开。
7. PDF 中中文标题、中文考试名称、中文字段正常显示。
8. PDF 中包含标题、学生信息区、选择题区、填空题区、计算题区。
9. PDF 中四角定位点位置正确。
10. 选择题数量和选项数量与前端配置一致。
11. 选择题排列方式符合配置。
12. layout.json 中包含选择题每个选项的坐标。
13. layout.json 中包含填空题和计算题区域坐标。
14. layout.json 坐标单位为 mm。
15. ReportLab 渲染位置与 layout.json 坐标一致。
16. 如果选择题数量超过网格容量，返回 `CHOICE_GRID_CAPACITY_EXCEEDED`。
17. 如果内容超出 A4 单页宽度，返回 `PAGE_WIDTH_EXCEEDED`。
18. 如果内容超出 A4 单页高度，返回 `PAGE_HEIGHT_EXCEEDED`。
19. 文件下载接口不能通过路径遍历访问 output 目录外的文件。
20. 文件下载接口返回正确的 Content-Type（.pdf → application/pdf，.json → application/json）。
21. 后端启动时检查并记录中文字体状态。
22. 项目 README 可以指导用户本地运行。
23. 项目 README 可以指导用户配置中文字体。

## 24. 示例测试用例

### 测试用例 1：标准答题卡

输入：

```json
{
  "paperTitle": "软件工程期末考试答题卡",
  "examName": "2026年春季学期期末考试",
  "pageSize": "A4",
  "studentFields": ["姓名", "学号", "班级"],
  "showPositionMarks": true,
  "sections": [
    {
      "type": "choice",
      "title": "一、选择题",
      "questionCount": 40,
      "optionCount": 4,
      "options": ["A", "B", "C", "D"],
      "questionsPerRow": 4,
      "questionsPerColumn": 10,
      "fillOrder": "column_first"
    },
    {
      "type": "blank",
      "title": "二、填空题",
      "questionCount": 3,
      "linesPerQuestion": 1
    },
    {
      "type": "calculation",
      "title": "三、计算题",
      "questionCount": 2,
      "heightPerQuestion": 25
    }
  ]
}
```

预期结果：

1. 生成 PDF 成功。
2. PDF 中文正常显示。
3. PDF 中显示 40 道选择题。
4. 每道选择题有 A、B、C、D 四个选项。
5. PDF 中显示 3 道填空题。
6. PDF 中显示 2 道计算题。
7. layout.json 正常生成。
8. layout.json 坐标单位为 mm。

### 测试用例 2：五选项选择题

输入：

```json
{
  "paperTitle": "英语考试答题卡",
  "examName": "阅读理解专项训练",
  "pageSize": "A4",
  "studentFields": ["姓名", "学号"],
  "showPositionMarks": true,
  "sections": [
    {
      "type": "choice",
      "title": "一、阅读理解",
      "questionCount": 30,
      "optionCount": 5,
      "options": ["A", "B", "C", "D", "E"],
      "questionsPerRow": 3,
      "questionsPerColumn": 10,
      "fillOrder": "column_first"
    }
  ]
}
```

预期结果：

1. 生成 PDF 成功。
2. 每题显示 A、B、C、D、E 五个选项。
3. layout.json 中每题有 5 个 option 坐标。

### 测试用例 3：选择题网格容量不足

输入：

```json
{
  "paperTitle": "测试答题卡",
  "examName": "容量测试",
  "pageSize": "A4",
  "studentFields": ["姓名", "学号"],
  "showPositionMarks": true,
  "sections": [
    {
      "type": "choice",
      "title": "一、选择题",
      "questionCount": 50,
      "optionCount": 4,
      "options": ["A", "B", "C", "D"],
      "questionsPerRow": 4,
      "questionsPerColumn": 10,
      "fillOrder": "column_first"
    }
  ]
}
```

预期结果：

```json
{
  "success": false,
  "errorCode": "CHOICE_GRID_CAPACITY_EXCEEDED",
  "message": "选择题数量超过当前选择题网格容量"
}
```

### 测试用例 4：页面高度超出

输入：

```json
{
  "paperTitle": "测试答题卡",
  "examName": "高度测试",
  "pageSize": "A4",
  "studentFields": ["姓名", "学号", "班级"],
  "showPositionMarks": true,
  "sections": [
    {
      "type": "choice",
      "title": "一、选择题",
      "questionCount": 40,
      "optionCount": 4,
      "options": ["A", "B", "C", "D"],
      "questionsPerRow": 4,
      "questionsPerColumn": 10,
      "fillOrder": "column_first"
    },
    {
      "type": "calculation",
      "title": "二、计算题",
      "questionCount": 8,
      "heightPerQuestion": 35
    }
  ]
}
```

预期结果：

```json
{
  "success": false,
  "errorCode": "PAGE_HEIGHT_EXCEEDED",
  "message": "答题卡内容超出 A4 单页可用高度，请减少题量或调整排版参数"
}
```

### 测试用例 5：optionCount 与 options.length 不一致

输入：

```json
{
  "paperTitle": "测试答题卡",
  "examName": "选项测试",
  "pageSize": "A4",
  "studentFields": ["姓名", "学号"],
  "showPositionMarks": true,
  "sections": [
    {
      "type": "choice",
      "title": "一、选择题",
      "questionCount": 10,
      "optionCount": 4,
      "options": ["A", "B", "C"],
      "questionsPerRow": 2,
      "questionsPerColumn": 5,
      "fillOrder": "column_first"
    }
  ]
}
```

预期结果：

```json
{
  "success": false,
  "errorCode": "OPTION_COUNT_MISMATCH",
  "message": "optionCount 必须等于 options.length"
}
```

### 测试用例 6：非法文件名下载

请求：

```http
GET /api/files/../../etc/passwd
```

预期结果：

```json
{
  "success": false,
  "errorCode": "INVALID_FILE_NAME",
  "message": "文件名非法"
}
```

## 25. 后续扩展方向

MVP 验证完成后，可以继续扩展：

1. 增加多页答题卡支持。
2. 增加自动分页。
3. 增加二维码，绑定 paperId。
4. 增加学号涂卡区。
5. 增加答题卡模板保存。
6. 增加 OpenCV 扫描识别。
7. 增加客观题自动判分。
8. 增加主观题教师阅卷入口。
9. 增加数据库。
10. 增加考试管理。
11. 增加试卷生成模块。
12. 增加前端可视化拖拽排版。
13. 增加导出 Word 或图片版本。
14. 增加 Docker 部署。
15. 增加对象存储。

## 26. MVP 一句话目标

实现一个配置驱动的 A4 单页答题卡生成器：前端输入题型和排版参数，后端自动生成可打印 PDF 答题卡，并同步导出可用于后续识别的 layout.json。
