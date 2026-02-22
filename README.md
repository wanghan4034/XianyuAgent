# 咸鱼商品抓取 Agent

一个轻量 Python Agent，用于**快速抓取咸鱼（goofish/xianyu）搜索结果页商品信息**。

> ⚠️ 说明：请确保你的抓取行为符合平台服务条款与当地法律法规。若页面反爬严格，可能需要登录态、代理、指纹或限速策略。

## 功能

- 按关键词抓取商品列表
- 输出结构化字段：标题、价格、地区、链接、卖家、商品ID
- 优先解析 Next.js 内嵌 JSON，失败时回退到 DOM 解析
- 提供命令行工具，方便快速调用
- 支持 Docker 一键运行

## 本地快速开始

### 1) 安装依赖

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 2) 运行

```bash
python -m xianyu_agent.cli "iPhone 15" --max-items 10
```

## Docker / Docker Compose 快速开始

### 1) 构建镜像

```bash
docker build -t xianyu-agent:latest .
```

### 2) 运行容器（直接传递关键词和参数）

```bash
docker run --rm xianyu-agent:latest "iPhone 15" --max-items 10
```

> 镜像默认入口为 `python -m xianyu_agent.cli`，因此 `docker run` 后追加的参数会直接传给 CLI。

### 3) 使用 Docker Compose 运行

```bash
# 使用默认参数（KEYWORD=iPhone 15, MAX_ITEMS=10）
docker compose up --build

# 自定义关键词与抓取数量
KEYWORD="MacBook Pro" MAX_ITEMS=5 docker compose up --build
```

`docker-compose.yml` 会读取环境变量 `KEYWORD` 和 `MAX_ITEMS`，并传递给 CLI。

示例输出：

```json
[
  {
    "title": "iPhone 15 国行",
    "price": 3999.0,
    "location": "杭州",
    "item_url": "https://www.goofish.com/item?id=xxxx",
    "seller": "某某卖家",
    "item_id": "xxxx"
  }
]
```

## 项目结构

- `xianyu_agent/agent.py`：浏览器抓取流程
- `xianyu_agent/parsers.py`：页面结构化解析
- `xianyu_agent/models.py`：数据模型
- `xianyu_agent/cli.py`：命令行入口
- `tests/test_parsers.py`：解析逻辑测试
- `Dockerfile`：容器化运行定义
- `docker-compose.yml`：Compose 编排配置

## 注意事项（实战建议）

- 控制抓取频率（随机 sleep / 限流）
- 需要更多字段时，优先从 `__NEXT_DATA__` 中提取
- 如遇风控，考虑账号登录态 + 稳定指纹 + 代理池
