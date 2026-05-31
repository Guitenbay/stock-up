# stock-up

[![CI](https://github.com/Guitenbay/stock-up/actions/workflows/ci.yml/badge.svg)](https://github.com/Guitenbay/stock-up/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/stock-up.svg)](https://pypi.org/project/stock-up/)
[![Python versions](https://img.shields.io/pypi/pyversions/stock-up.svg)](https://pypi.org/project/stock-up/)

命令行版个人股票策略执行助手。

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

## 初始化

```bash
stock-up init
```

默认创建：

```text
~/.stock-up/config.yaml
~/.stock-up/data.db
~/.stock-up/reports/
```

测试时可以指定目录：

```bash
stock-up init --home /tmp/stock-up-demo
```

## 观察池

手动加入观察：

```bash
stock-up watch add 300308 --name 中际旭创 --high 130 --low 110 --now 120
```

查看观察池：

```bash
stock-up watch list
```

检查观察信号：

```bash
stock-up watch check
```

查看废弃观察：

```bash
stock-up watch abandoned
```

修正高低点：

```bash
stock-up watch set 300308 --high 135 --low 112
```

## 持仓

添加持仓：

```bash
stock-up hold add 300308 --name 中际旭创 --cost 120 --qty 100 --rule wolf_swing
```

规则支持：

```text
wolf_swing = 狼大波段规则
hai_long   = 海指导规则
both       = 两套规则同时开启
```

加仓：

```bash
stock-up hold add-buy 300308 --price 125 --qty 100
```

检查持仓：

```bash
stock-up hold check
```

关闭持仓：

```bash
stock-up hold close 300308 --price 135 --reason 止盈
```

关闭后重新加入观察：

```bash
stock-up hold close 300308 --price 135 --reason 止盈 --watch
```

## 盘中 tick

`stock-up` 不常驻。盘中由外部定时任务反复调用：

```bash
stock-up tick
```

默认使用腾讯实时行情。测试可用：

```bash
stock-up tick --provider mock
```

建议外部定时任务每 20 秒调用一次。

## 数据源

当前默认：

```text
实时行情：腾讯 qt.gtimg.cn
自动加入观察：默认关闭
日 K / RSI：StockAPI，失败再尝试其他源
```

热点板块龙头自动加入观察目前默认关闭，因为 StockAPI 龙头接口需要 token：

```yaml
auto_watch:
  hot_leader_scan_enabled: false
```

StockAPI 无 token 时会按 5 天窗口分段请求，以满足免费接口限制。

RSI 日 K 数据很宝贵，`daily` 更新 RSI 时遵循：

```text
先更新持仓池
再更新观察池
达到 max_updates_per_daily 后停止
```

配置项：

```yaml
technical:
  rsi:
    max_updates_per_daily: 50
```

## 涨停扫描

```bash
stock-up scan limit-up
```

默认使用 AkShare。测试可用：

```bash
stock-up scan limit-up --provider mock --date 2026-05-31
```

初始低点模式：

```bash
stock-up scan limit-up --low-mode same_day
stock-up scan limit-up --low-mode recent_1d
```

## 每日报告

```bash
stock-up daily
```

测试：

```bash
stock-up daily --provider mock --date 2026-05-31
```

报告输出到：

```text
~/.stock-up/reports/YYYY-MM-DD.md
```

## 测试

```bash
pytest -q
```

## 免责声明

本工具仅用于个人复盘和策略辅助，不构成投资建议。
