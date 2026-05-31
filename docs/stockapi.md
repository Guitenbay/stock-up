# StockAPI 日 K 接口说明

## 用途

`stock-up` 使用 StockAPI 作为日 K 数据源之一，用于计算 RSI。

适用：

- A 股日 K
- 周 K
- 月 K
- 板块 / 概念 K 线

## 接口

```text
GET https://www.stockapi.com.cn/v1/base/day
```

## 请求参数

| 参数 | 类型 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| code | string | 是 | 股票/板块/概念代码，股票不带市场前缀 | 600004 |
| startDate | string | 是 | 开始日期 | 2021-11-09 |
| endDate | string | 是 | 结束日期 | 2021-11-09 |
| calculationCycle | string | 是 | 周期：100=日，101=周，102=月 | 100 |

## 示例

```text
https://www.stockapi.com.cn/v1/base/day?code=600004&startDate=2021-11-09&endDate=2021-11-09&calculationCycle=100
```

## 响应

```json
{
  "msg": "success",
  "code": 20000,
  "data": {
    "turnoverRatio": [],
    "amount": [],
    "totalCapital": [],
    "avgPrice": [],
    "change": [],
    "totalShares": [],
    "volume": [],
    "pb": [],
    "pcf": [],
    "high": [],
    "preClose": [],
    "pe": [],
    "low": [],
    "transactionAmount": [],
    "changeRatio": [],
    "pe_ttm": [],
    "close": [],
    "open": []
  }
}
```

## stock-up 映射

`StockApiProvider.get_daily_bars()` 将接口数据转换成统一模型：

```text
DailyBar:
  code
  trade_date
  open
  high
  low
  close
  volume
  amount
```

## 注意

文档示例没有明确日期字段。实际实现会兼容两种结构：

1. 数组元素为对象，包含日期和值。
2. 响应里有单独日期数组。

如果接口没有日期信息，`stock-up` 会返回空列表，避免错误对齐。

## 数据源优先级建议

```yaml
market:
  daily_bar_source_order:
    - stockapi
    - akshare
    - qq
```
