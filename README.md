# stock-up

[![CI](https://github.com/Guitenbay/stock-up/actions/workflows/ci.yml/badge.svg)](https://github.com/Guitenbay/stock-up/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/stock-up?cacheSeconds=3600)](https://pypi.org/project/stock-up/)
[![Python versions](https://img.shields.io/pypi/pyversions/stock-up?cacheSeconds=3600)](https://pypi.org/project/stock-up/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

命令行版个人股票策略执行助手。

> AI agent / 编程助手请先阅读 [AGENTS.md](AGENTS.md)，里面有安装、使用、开发和提交约定。

## 安装

从 PyPI 安装：

```bash
python3 -m pip install stock-up
```

如果要使用 AkShare 备用数据源：

```bash
python3 -m pip install 'stock-up[akshare]'
```

验证安装：

```bash
stock-up --help
```

## 快速开始

普通使用只需要关注这几个命令：

### 1. 初始化

```bash
stock-up init
```

初始化本地配置、数据库和报告目录。

### 2. 添加持仓

```bash
stock-up hold add 300308 --name 中际旭创 --cost 120 --qty 100 --rule both
```

常用规则：

```text
wolf_swing = 狼大波段规则，偏趋势持股
hai_long   = 海指导规则，偏长线仓/时间验证
both       = 两套规则同时开启
```

### 3. 盘中检查

```bash
stock-up tick
```

更新观察池和持仓池的实时行情，并检查是否有需要动作的信号。

`stock-up` 不常驻，建议用系统定时任务在交易时间内每 20 秒调用一次。

### 4. 每日复盘

```bash
stock-up daily
```

建议每日 16:00 以后执行。默认使用 StockAPI，并自动扫描龙虎榜加入观察池，生成 Markdown 日报。

> `daily` 依赖的数据源通常在每日 16:00 以后更新；太早执行可能拿不到当天最新数据。

```text
~/.stock-up/reports/YYYY-MM-DD.md
```

### 5. 检查持仓

```bash
stock-up hold check
```

手动查看当前持仓是否触发止损、止盈、RSI 死叉或增持观察。

### 6. 卖出后关闭持仓

```bash
stock-up hold close 300308 --price 135 --reason 止盈
```

如果卖出后还想继续观察：

```bash
stock-up hold close 300308 --price 135 --reason 止盈 --watch
```

## 开发环境

```bash
git clone https://github.com/Guitenbay/stock-up.git
cd stock-up
python3 -m pip install -e '.[dev]'
pytest -q
```

如果开发时要使用 AkShare：

```bash
python3 -m pip install -e '.[dev,akshare]'
```

## 配置文件

默认配置文件位置：

```text
~/.stock-up/config.yaml
```

`stock-up init` 会自动创建默认配置、数据库和报告目录。完整参数说明见 [命令说明](docs/commands.md#配置文件)。

## 更多文档

- [命令说明与配置说明](docs/commands.md)
- [Agent 安装使用说明](AGENTS.md)
- [贡献指南](CONTRIBUTING.md)
- [许可证](LICENSE)
- [StockAPI 接口说明](docs/stockapi.md)
- [腾讯股票接口说明](docs/tencent-api.md)

## 免责声明

本工具仅用于个人复盘和策略辅助，不构成投资建议。
