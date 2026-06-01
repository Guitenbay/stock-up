# stock-up 命令说明

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

## 配置文件

默认配置文件位置：

```text
~/.stock-up/config.yaml
```

如果使用 `--home` 指定目录，配置文件会放在该目录下：

```bash
stock-up init --home /tmp/stock-up-demo
# 配置文件：/tmp/stock-up-demo/config.yaml
```

默认配置示例：

```yaml
market:
  default_provider: auto
  realtime_provider: auto
  daily_provider: auto
  dragon_tiger_provider: auto
  limit_up_provider: auto
  quote_source: auto
  limit_up_source_order:
    - akshare_em
    - akshare_ths
  realtime_fallback_order:
    - qq
    - akshare

tick:
  trading_time_only: true
  min_interval_seconds: 20

limit_up:
  exclude_st: true
  exclude_bj: true
  exclude_new_stock_days: 30
  min_amount: 500000000
  include_first_board: true
  include_multi_board: true

auto_watch:
  dragon_tiger_scan_enabled: true
  hot_leader_scan_enabled: false

watch:
  initial_low_mode: same_day
  buy_382_tolerance: 0.03
  buy_618_tolerance: 0.02
  abandon_below_786: true
  abandon_below_low: true

technical:
  rsi:
    enabled: true
    short_period: 6
    long_period: 12
    min_history_days: 30
    max_updates_per_daily: 50
    watch_golden_cross: true
    holding_dead_cross: true

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
  allow_loss_add_on_618: true

alert:
  repeat_price_change_pct: 0.01

notify:
  terminal: true
  markdown_report: true

report:
  only_actionable: true
  dir: ~/.stock-up/reports
```

参数说明：

| 配置项 | 默认值 | 说明 |
|---|---:|---|
| `market.default_provider` | `auto` | 通用默认数据源 |
| `market.realtime_provider` | `auto` | 实时行情默认数据源；`auto` 会走腾讯 |
| `market.daily_provider` | `auto` | 每日复盘默认数据源；`auto` 会走 StockAPI |
| `market.dragon_tiger_provider` | `auto` | 龙虎榜默认数据源；`auto` 会走 StockAPI |
| `market.limit_up_provider` | `auto` | 涨停池默认数据源；`auto` 会走 AkShare |
| `market.quote_source` | `auto` | 兼容旧配置的行情源字段 |
| `market.limit_up_source_order` | `akshare_em`, `akshare_ths` | 涨停池数据源优先级 |
| `market.realtime_fallback_order` | `qq`, `akshare` | 实时行情备用源顺序 |
| `tick.trading_time_only` | `true` | 预留配置：是否只在交易时间检查 |
| `tick.min_interval_seconds` | `20` | 建议外部定时任务调用 `tick` 的最小间隔 |
| `limit_up.exclude_st` | `true` | 涨停扫描排除 ST |
| `limit_up.exclude_bj` | `true` | 涨停扫描排除北交所 |
| `limit_up.exclude_new_stock_days` | `30` | 涨停扫描排除上市天数过短的新股 |
| `limit_up.min_amount` | `500000000` | 涨停扫描最低成交额 |
| `limit_up.include_first_board` | `true` | 是否包含首板 |
| `limit_up.include_multi_board` | `true` | 是否包含连板 |
| `auto_watch.dragon_tiger_scan_enabled` | `true` | 每日复盘是否自动扫描龙虎榜并加入观察池 |
| `auto_watch.hot_leader_scan_enabled` | `false` | 每日复盘是否自动扫描热点板块龙头；暂不能使用，因为 StockAPI 接口需要 token，目前项目没有配置 token 的能力 |
| `watch.initial_low_mode` | `same_day` | 自动加入观察时的初始低点：`same_day` 当日低点，`recent_1d` 最近 1 日低点 |
| `watch.buy_382_tolerance` | `0.03` | 接近 0.382 回撤位的买点容忍比例 |
| `watch.buy_618_tolerance` | `0.02` | 接近 0.618 回撤位的买点容忍比例 |
| `watch.abandon_below_786` | `true` | 跌破 0.786 回撤位时废弃观察 |
| `watch.abandon_below_low` | `true` | 跌破初始低点时废弃观察 |
| `technical.rsi.enabled` | `true` | 是否启用 RSI 信号 |
| `technical.rsi.short_period` | `6` | 短 RSI 周期 |
| `technical.rsi.long_period` | `12` | 长 RSI 周期 |
| `technical.rsi.min_history_days` | `30` | 本地计算 RSI 时需要的最少历史天数 |
| `technical.rsi.max_updates_per_daily` | `50` | 每日最多更新 RSI 的股票数；先持仓，后观察 |
| `technical.rsi.watch_golden_cross` | `true` | 观察池是否提醒 RSI 金叉 |
| `technical.rsi.holding_dead_cross` | `true` | 持仓池是否提醒 RSI 死叉 |
| `holding.default_rule` | `wolf_swing` | 默认持仓规则：`wolf_swing` / `hai_long` / `both` |
| `holding.rules.wolf_swing.stop_loss_pct` | `0.07` | 狼大波段规则：成本价下跌 7% 止损 |
| `holding.rules.wolf_swing.take_profit_arm_pct` | `0.20` | 狼大波段规则：盈利 20% 后启动移动止盈 |
| `holding.rules.wolf_swing.profit_drawdown_pct` | `0.30` | 狼大波段规则：从最高盈利回撤 30% 止盈 |
| `holding.rules.hai_long.swing_low_break_pct` | `0.03` | 海指导规则：跌破波段低点 3% 视为失败 |
| `holding.rules.hai_long.validate_days` | `13` | 海指导规则：13 个交易日验证期 |
| `holding.allow_loss_add_on_618` | `true` | 未触发止损时，允许在 0.618 附近提醒亏损加仓观察 |
| `alert.repeat_price_change_pct` | `0.01` | 同类提醒价格变化超过 1% 才重复提醒 |
| `notify.terminal` | `true` | 是否输出终端提醒 |
| `notify.markdown_report` | `true` | 是否生成 Markdown 日报 |
| `report.only_actionable` | `true` | 日报是否只显示有动作建议的股票 |
| `report.dir` | `~/.stock-up/reports` | 日报目录 |

## 命令速查

| 命令 | 用途 | 示例 |
|---|---|---|
| `stock-up init` | 初始化配置、数据库和报告目录 | `stock-up init` |
| `stock-up tick` | 执行一次盘中检查，由定时任务调用 | `stock-up tick` |
| `stock-up daily` | 每日 16:00 后生成复盘报告；默认自动扫描龙虎榜并加入观察池 | `stock-up daily` |
| `stock-up quote CODE` | 查看单只股票行情 | `stock-up quote 300308` |
| `stock-up watch list` | 查看观察池 | `stock-up watch list` |
| `stock-up watch check` | 检查观察池信号 | `stock-up watch check` |
| `stock-up watch abandoned` | 查看废弃观察池 | `stock-up watch abandoned` |
| `stock-up watch add CODE` | 手动加入观察池；不传 `--name` 时会尝试自动获取股票名 | `stock-up watch add 300308 --high 130 --low 110` |
| `stock-up watch set CODE` | 修正单只观察股高低点 | `stock-up watch set 300308 --high 135 --low 112` |
| `stock-up watch refresh-range` | 用 QQ 实时行情刷新观察池所有股票高低点 | `stock-up watch refresh-range` |
| `stock-up hold add CODE` | 添加持仓；不传 `--name` 时会尝试自动获取股票名 | `stock-up hold add 300308 --cost 120 --qty 100 --rule both` |
| `stock-up hold list` | 查看持仓 | `stock-up hold list` |
| `stock-up hold check` | 检查持仓信号 | `stock-up hold check` |
| `stock-up hold set CODE` | 修正持仓参数 | `stock-up hold set 300308 --highest 150 --rule hai_long` |
| `stock-up hold refresh-range` | 用 QQ 实时行情刷新持仓池所有股票高低点 | `stock-up hold refresh-range` |
| `stock-up hold add-buy CODE` | 记录加仓并更新加权平均成本 | `stock-up hold add-buy 300308 --price 125 --qty 100` |
| `stock-up hold close CODE` | 关闭持仓 | `stock-up hold close 300308 --price 135 --reason 止盈` |
| `stock-up scan dragon-tiger` | 扫描龙虎榜并加入观察池 | `stock-up scan dragon-tiger --date 2026-05-29` |
| `stock-up scan limit-up` | 扫描涨停池并加入观察池 | `stock-up scan limit-up --date 2026-05-29` |

## 观察池

手动加入观察：

```bash
stock-up watch add 300308 --high 130 --low 110 --now 120
```

不传 `--name` 时，会尝试通过实时行情接口自动获取股票名；获取失败时使用股票代码兜底。

如果想手动指定名称：

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

修正单只股票高低点：

```bash
stock-up watch set 300308 --high 135 --low 112
```

用 QQ 实时行情刷新观察池所有股票高低点：

```bash
stock-up watch refresh-range
```

这个命令会刷新观察池所有活动股票的 `high` / `low` / `now` / `avg` / `name`。如果 QQ 没返回有效高低点，会跳过该股票，不会用当前价冒充高低点。

## 持仓

添加持仓：

```bash
stock-up hold add 300308 --cost 120 --qty 100 --rule wolf_swing
```

不传 `--name` 时，会尝试通过实时行情接口自动获取股票名；获取失败时使用股票代码兜底。

如果想手动指定名称：

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

用 QQ 实时行情刷新持仓池所有股票高低点：

```bash
stock-up hold refresh-range
```

这个命令会刷新持仓池所有股票的 `high` / `low` / `now` / `name`，并用 `quote.high` 上调 `highest`。如果 QQ 没返回有效高低点，会跳过该股票。

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

## 自动加入观察池

当前默认会在 `stock-up daily` 后自动扫描龙虎榜，并把龙虎榜股票加入观察池。

以下命令会把股票加入观察池：

| 命令 | 触发方式 | 说明 |
|---|---|---|
| `stock-up watch add CODE` | 手动 | 手动指定股票加入观察池 |
| `stock-up daily` | 自动入口 | 默认自动扫描龙虎榜并加入观察池；热点板块龙头策略暂不能使用，因为缺少 StockAPI token 配置 |
| `stock-up scan dragon-tiger` | 手动扫描 | 扫描龙虎榜并加入观察池 |
| `stock-up scan limit-up` | 手动扫描 | 扫描涨停池并加入观察池 |
| `stock-up hold close CODE --watch` | 手动 | 关闭持仓后重新加入观察池 |

自动加入观察池的策略状态：

| 策略 | 是否默认启用 | 当前状态 |
|---|---|---|
| 热点板块龙头 | 否 | 暂不能使用；StockAPI 接口需要 token，目前项目没有配置 token 的能力 |
| 龙虎榜 | 是 | `stock-up daily` 默认自动扫描；也可手动运行 `stock-up scan dragon-tiger` |
| 涨停池 | 否 | 可用，但需要手动运行 `stock-up scan limit-up` |

`daily` 的自动观察逻辑由配置控制：

```yaml
auto_watch:
  dragon_tiger_scan_enabled: true
  hot_leader_scan_enabled: false
```

`dragon_tiger_scan_enabled` 默认值是 `true`，所以普通执行 `stock-up daily` 时会自动扫描龙虎榜并加入观察池。

`hot_leader_scan_enabled` 默认值是 `false`。这个配置目前暂不能使用：StockAPI 热点板块龙头接口需要 token，目前项目没有配置 token 的能力。

## 数据源

当前默认：

```text
实时行情：腾讯 qt.gtimg.cn
每日复盘：StockAPI
自动加入观察：默认开启龙虎榜；热点板块龙头暂不能使用
日 K / RSI：StockAPI，失败再尝试其他源
```

数据源对命令的支持情况：

| 数据源 | 支持的命令 / 功能 | 说明 |
|---|---|---|
| `qq` | `stock-up quote`、`stock-up tick`、`watch add` / `hold add` 自动获取股票名 | 腾讯实时行情；适合盘中行情和股票名查询 |
| `stockapi` | `stock-up daily`、`stock-up scan dragon-tiger`、RSI / 日 K | 默认用于每日复盘和龙虎榜；无 token 时日 K 会按 5 天窗口分段请求 |
| `akshare` | `stock-up scan limit-up`、部分日 K / 交易日历备用 | 默认用于涨停池扫描；不支持当前龙虎榜扫描 |
| `mock` | 所有主要命令的测试场景 | 只用于测试，不访问外部网络 |
| `auto` | 按命令场景自动选择 | `quote` / `tick` 走 `qq`，`daily` / RSI 走 `stockapi`，龙虎榜走 `stockapi`，涨停池走 `akshare` |

命令行显式指定 `--provider` 时优先级最高；不指定时默认读取 `config.yaml`。

| 命令 | 默认配置项 | 默认实际数据源 | 可用 provider |
|---|---|---|---|
| `stock-up quote CODE` | `market.realtime_provider` | `auto -> qq` | `config` / `auto` / `qq` / `akshare` / `mock` |
| `stock-up tick` | `market.realtime_provider` | `auto -> qq` | `config` / `auto` / `qq` / `mock` |
| `stock-up daily` | `market.daily_provider` | `auto -> stockapi` | `config` / `auto` / `stockapi` / `mock` |
| `stock-up scan dragon-tiger` | `market.dragon_tiger_provider` | `auto -> stockapi` | `config` / `auto` / `stockapi` / `mock` |
| `stock-up scan limit-up` | `market.limit_up_provider` | `auto -> akshare` | `config` / `auto` / `akshare` / `mock` |
| `watch add` / `hold add` 自动获取股票名 | `market.realtime_provider` | `auto -> qq` | 当前内部使用实时行情 provider |

热点板块龙头自动加入观察目前默认关闭，且暂不能使用：StockAPI 龙头接口需要 token，目前项目没有配置 token 的能力。

```yaml
auto_watch:
  dragon_tiger_scan_enabled: true
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

建议每日 16:00 以后执行：

```bash
stock-up daily
```

`daily` 依赖的数据源通常在每日 16:00 以后更新；太早执行可能拿不到当天最新数据。

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
