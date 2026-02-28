# 咸鱼商品抓取 Agent

一个轻量 Python Agent，用于**快速抓取咸鱼（goofish/xianyu）商品信息并生成行情估价报告**，支持关键词搜索与图片搜索，并提供 Web 页面上传图片。

> ⚠️ 说明：请确保你的抓取行为符合平台服务条款与当地法律法规。若页面反爬严格，可能需要登录态、代理、指纹或限速策略。

## 功能

- 按关键词抓取商品列表
- 上传本地图片执行以图搜（支持拖拽上传与预览）
- 支持关键词搜索与网页端以图搜能力探测
- 输出结构化字段：标题、价格、地区、链接、卖家、商品ID
- 返回价格统计：最低价/中位价/最高价
- 提供 CLI、Web 页面、Docker、Docker Compose 运行方式


## 典型业务流程（客户来货估价）

1. 上传客户实物照片（或输入准确关键词）
2. 获取闲鱼同类商品样本价格
3. 自动生成建议定价区间（Q1-Q3）与中位价
4. 查看可比商品列表并导出 JSON 报告留档

## 本地快速开始

### 1) 安装依赖

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 2) CLI 运行

关键词搜索：

```bash
python -m xianyu_agent.cli "iPhone 15" --max-items 10
```

图片搜索：

```bash
python -m xianyu_agent.cli --image /path/to/item.jpg --max-items 10
```


网页端能力探测（是否支持以图搜入口）：

```bash
python -m xianyu_agent.cli --check-image-search
```

### 3) 启动 Web 页面

```bash
python -m xianyu_agent.web
```

浏览器访问：`http://127.0.0.1:8090`，直接上传图片查询。


### Web 页面新增体验优化

- 双模式：图片搜索 / 关键词搜索一键切换
- 能力探测按钮：快速判断当前网页版本是否存在以图搜入口
- 图片拖拽上传 + 预览
- 估价卡片（样本数/建议低价/建议高价/中位价）
- 可比商品列表（便于人工复核）
- 一键下载估价报告 JSON

## Docker / Docker Compose 快速开始

### 1) 构建镜像

```bash
docker build -t xianyu-agent:latest .
```

### 2) Docker 运行（CLI）

```bash
docker run --rm xianyu-agent:latest "iPhone 15" --max-items 10
```

### 3) Docker Compose 运行（CLI）

```bash
# 使用默认参数（KEYWORD=iPhone 15, MAX_ITEMS=10）
docker compose up --build xianyu-agent

# 自定义关键词与抓取数量
KEYWORD="MacBook Pro" MAX_ITEMS=5 docker compose up --build xianyu-agent
```

### 4) Docker Compose 运行（Web 上传页）

```bash
docker compose up --build xianyu-web
```

打开：`http://127.0.0.1:8090`

> `docker-compose.yml` 中 `xianyu-web` 将 `./uploads` 挂载到容器 `/app/uploads`，用于保存上传图片。

## 项目结构

- `xianyu_agent/agent.py`：浏览器抓取流程（关键词/图片）
- `xianyu_agent/parsers.py`：页面结构化解析
- `xianyu_agent/models.py`：数据模型
- `xianyu_agent/service.py`：价格统计逻辑
- `xianyu_agent/cli.py`：命令行入口
- `xianyu_agent/web.py`：Flask Web 上传页与 API
- `xianyu_agent/templates/index.html`：Web 页面模板
- `tests/test_parsers.py`：解析逻辑测试
- `Dockerfile`：容器化运行定义
- `docker-compose.yml`：Compose 编排配置

## 注意事项（实战建议）

- 闲鱼网页端以图搜入口可能随版本变化，如页面找不到上传控件会报错提示。
- 控制抓取频率（随机 sleep / 限流）
- 需要更多字段时，优先从 `__NEXT_DATA__` 中提取
- 如遇风控，考虑账号登录态 + 稳定指纹 + 代理池


## 常见问题

- 报错：`未在页面找到图片上传控件...`
  - 新版本已增加两层上传策略（直接查找文件输入框 + 点击“以图搜/拍照搜”触发文件选择器）。
  - 若仍失败，通常是网页端当前账号/地区未开放以图搜，建议先使用关键词估价模式。
