# stock-up 实施计划

## 原则

- 测试先行。
- 先做离线可测核心，再接真实数据源。
- 策略层不依赖 AkShare / 腾讯接口。
- CLI 只编排服务，不写业务细节。

## 阶段 1：项目骨架与核心模型

- 初始化 Python 包。
- 配置 pytest。
- 定义 Quote / DailyBar / WatchItem / Holding 等模型。
- 实现配置加载和默认配置。
- 实现 SQLite 初始化。

## 阶段 2：策略纯函数

- Fibonacci 计算。
- RSI 计算与金叉/死叉判断。
- 观察池信号。
- wolf_swing / hai_long / both 持仓规则。
- 提醒去重。

## 阶段 3：数据库仓储

- watchlist CRUD。
- holdings CRUD。
- trades 交易记录。
- alerts 提醒记录。
- quotes_daily 缓存。

## 阶段 4：CLI 命令

- init
- watch add/list/abandoned/check/set
- hold add/list/check/set/add-buy/close
- scan limit-up
- daily
- tick

## 阶段 5：数据源适配

- MarketDataProvider 接口。
- MockProvider 用于测试。
- TencentProvider 实时行情。
- AkShareProvider 涨停池、日 K、交易日历。

## 阶段 6：集成测试与真实数据 smoke test

- CLI runner 测试。
- 用 mock 数据测试 daily / tick。
- 可选真实数据 smoke test，不作为 CI 必跑。
