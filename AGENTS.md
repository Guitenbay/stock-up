# AGENTS.md

面向 AI agent / 编程助手的 stock-up 安装与使用说明。

## 项目定位

`stock-up` 是一个 Python CLI，用于个人股票策略辅助：

- 维护观察池和持仓池。
- 盘中通过 `tick` 更新实时行情并提示动作。
- 收盘后通过 `daily` 生成 Markdown 日报。
- 支持 RSI 金叉/死叉提醒。
- 支持 `wolf_swing`、`hai_long`、`both` 三种持仓规则。

注意：这是投资辅助工具，不做自动交易，不构成投资建议。

## 环境要求

- Python `>=3.10`
- 推荐命令使用 `python3`
- 包管理直接用 `pip`

## 安装方式

### 从 PyPI 安装

```bash
python3 -m pip install stock-up
```

如需 AkShare 备用数据源：

```bash
python3 -m pip install 'stock-up[akshare]'
```

验证：

```bash
stock-up --help
```

### 从源码开发安装

```bash
git clone https://github.com/Guitenbay/stock-up.git
cd stock-up
python3 -m pip install -e '.[dev]'
```

如开发时需要 AkShare：

```bash
python3 -m pip install -e '.[dev,akshare]'
```

运行测试：

```bash
pytest -q
```

## 初始化

首次使用：

```bash
stock-up init
```

默认创建：

```text
~/.stock-up/config.yaml
~/.stock-up/data.db
~/.stock-up/reports/
```

如果需要隔离测试目录，使用 `--home`：

```bash
stock-up init --home /tmp/stock-up-demo
```

此时文件位于：

```text
/tmp/stock-up-demo/config.yaml
/tmp/stock-up-demo/data.db
/tmp/stock-up-demo/reports/
```

## 最小使用流程

### 1. 初始化

```bash
stock-up init
```

### 2. 添加持仓

```bash
stock-up hold add 300308 --name 中际旭创 --cost 120 --qty 100 --rule both
```

规则：

```text
wolf_swing = 狼大波段规则，偏趋势持股
hai_long   = 海指导规则，偏长线仓/时间验证
both       = 两套规则同时开启
```

### 3. 盘中检查

```bash
stock-up tick
```

`stock-up` 不常驻。外部定时任务可以在交易时间内每 20 秒调用一次：

```bash
stock-up tick
```

### 4. 收盘复盘

```bash
stock-up daily
```

`daily` 是普通用户主要依赖的自动入口，默认使用 StockAPI，自动扫描龙虎榜并把股票加入观察池。

建议每日 16:00 以后执行 `stock-up daily`。它依赖的数据源通常在 16:00 以后更新；太早执行可能拿不到当天最新数据。

当前自动加入观察池的策略状态：

- 默认自动加入：龙虎榜，配置项是 `auto_watch.dragon_tiger_scan_enabled: true`。
- 热点板块龙头：配置项是 `auto_watch.hot_leader_scan_enabled`，默认 `false`，且暂不能使用；StockAPI 热点板块龙头接口需要 token，目前项目没有配置 token 的能力。
- 手动扫描加入：`stock-up scan dragon-tiger` 也可以手动把龙虎榜股票加入观察池。
- 手动扫描加入：`stock-up scan limit-up` 会把涨停池股票加入观察池。
- 手动加入：`stock-up watch add CODE`。
- 卖出后重新观察：`stock-up hold close CODE --watch`。

日报输出：

```text
~/.stock-up/reports/YYYY-MM-DD.md
```

### 5. 手动检查持仓

```bash
stock-up hold check
```

### 6. 卖出后关闭持仓

```bash
stock-up hold close 300308 --price 135 --reason 止盈
```

如果卖出后继续观察：

```bash
stock-up hold close 300308 --price 135 --reason 止盈 --watch
```

## 常用命令

| 命令 | 用途 |
|---|---|
| `stock-up init` | 初始化配置、数据库、报告目录 |
| `stock-up quote CODE` | 查看单只股票实时行情 |
| `stock-up tick` | 执行一次盘中检查 |
| `stock-up daily` | 执行每日复盘并生成报告；默认使用 StockAPI 扫描龙虎榜并加入观察池 |
| `stock-up watch add CODE` | 手动加入观察池；不传 `--name` 时会尝试自动获取股票名 |
| `stock-up watch list` | 查看观察池 |
| `stock-up watch check` | 检查观察池信号 |
| `stock-up watch abandoned` | 查看废弃观察池 |
| `stock-up watch set CODE` | 修正观察股高低点 |
| `stock-up hold add CODE` | 添加持仓；不传 `--name` 时会尝试自动获取股票名 |
| `stock-up hold list` | 查看持仓 |
| `stock-up hold check` | 检查持仓信号 |
| `stock-up hold set CODE` | 修正持仓参数 |
| `stock-up hold add-buy CODE` | 记录加仓并更新加权平均成本 |
| `stock-up hold close CODE` | 关闭持仓 |
| `stock-up scan dragon-tiger` | 扫描龙虎榜并加入观察池 |
| `stock-up scan limit-up` | 扫描涨停池并加入观察池 |

## 配置文件

默认位置：

```text
~/.stock-up/config.yaml
```

使用 `--home` 后位置为：

```text
<home>/config.yaml
```

关键配置：

```yaml
market:
  default_provider: auto
  realtime_provider: auto
  daily_provider: auto
  dragon_tiger_provider: auto
  limit_up_provider: auto

technical:
  rsi:
    enabled: true
    short_period: 6
    long_period: 12
    max_updates_per_daily: 50

holding:
  default_rule: wolf_swing
  rules:
    wolf_swing:
      stop_loss_pct: 0.07
      take_profit_arm_pct: 0.20
      profit_drawdown_pct: 0.30
    hai_long:
      swing_low_break_pct: 0.03
      validate_days: 13

auto_watch:
  dragon_tiger_scan_enabled: true
  hot_leader_scan_enabled: false

alert:
  repeat_price_change_pct: 0.01

report:
  only_actionable: true
  dir: ~/.stock-up/reports
```

完整配置说明见：

```text
docs/commands.md#配置文件
```

## 数据源说明

默认使用：

```text
实时行情：腾讯 qt.gtimg.cn
RSI / 日 K：StockAPI 优先
涨停池：AkShare
龙虎榜：StockAPI
```

热点板块龙头自动加入观察默认关闭，且暂不能使用：StockAPI 龙头接口需要 token，目前项目没有配置 token 的能力。

```yaml
auto_watch:
  dragon_tiger_scan_enabled: true
  hot_leader_scan_enabled: false
```

## Agent 修改项目时的约定

- 用户偏好短回复。
- 每完成一个实现步骤要提交一次代码。
- commit message 使用 Conventional Commits，例如：
  - `feat: add xxx`
  - `fix: correct xxx`
  - `docs: update xxx`
  - `refactor: simplify xxx`
  - `ci: add xxx`
- 文档修改不需要跑测试，除非用户明确要求。
- 代码修改应优先测试先行，并运行相关测试。
- 不要自动交易，只做提醒和报告。
- 不要把 token、密钥写入仓库或文档。
- PyPI 已发布过 `0.1.0`；如果要重新发布当前代码，需要先升级版本号。

## 更多文档

- `README.md`：用户版快速开始。
- `docs/commands.md`：完整命令与配置说明。
- `docs/stockapi.md`：StockAPI 接口说明。
- `docs/tencent-api.md`：腾讯接口说明。
