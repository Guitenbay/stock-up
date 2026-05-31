# StockAPI 接口说明

## 1. 日 K 接口

`stock-up` 可使用 StockAPI 获取日 K，但现在 RSI 优先使用 StockAPI 的专用 RSI 接口。

### 接口

```text
GET https://www.stockapi.com.cn/v1/base/day
```

### 请求参数

| 参数 | 类型 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| code | string | 是 | 股票/板块/概念代码，股票不带市场前缀 | 600004 |
| startDate | string | 是 | 开始日期 | 2021-11-09 |
| endDate | string | 是 | 结束日期 | 2021-11-09 |
| calculationCycle | string | 是 | 周期：100=日，101=周，102=月 | 100 |

### 示例

```text
https://www.stockapi.com.cn/v1/base/day?code=600004&startDate=2021-11-09&endDate=2021-11-09&calculationCycle=100
```

### 文档响应格式

```json
{
  "msg": "success",
  "code": 20000,
  "data": {
    "turnoverRatio": [],
    "amount": [],
    "high": [],
    "low": [],
    "close": [],
    "open": [],
    "volume": []
  }
}
```

### 实测响应格式

实际无 token 请求返回的 `data` 是列表：

```json
{
  "code": 20000,
  "msg": "success",
  "data": [
    {
      "code": "000858.SZ",
      "time": "2026-05-27",
      "open": "83",
      "high": "86.25",
      "low": "81.7",
      "close": "83.89",
      "volume": "60380066",
      "amount": "5045124428"
    }
  ]
}
```

`stock-up` 同时兼容文档格式和实测格式。

---

## 2. RSI 指标接口

`stock-up` 优先使用该接口获取 RSI，避免消耗日 K 数据和本地重复计算。

### 接口

```text
GET https://www.stockapi.com.cn/v1/quota/rsi2
```

### 请求参数

| 参数 | 类型 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| code | string | 是 | 股票/板块/概念代码，股票不带市场前缀 | 601088 |
| cycle1 | int | 是 | RSI 周期 1 | 6 |
| cycle2 | int | 是 | RSI 周期 2 | 12 |
| cycle3 | int | 是 | RSI 周期 3 | 24 |
| startDate | string | 是 | 开始日期 | 2021-10-22 |
| endDate | string | 是 | 结束日期 | 2021-10-22 |
| calculationCycle | string | 是 | 周期：100=日，101=周，102=月 | 100 |

### 示例

```text
https://www.stockapi.com.cn/v1/quota/rsi2?code=000858&cycle1=6&cycle2=12&cycle3=24&startDate=2026-05-27&endDate=2026-05-31&calculationCycle=100
```

### 文档响应格式

```json
{
  "msg": "success",
  "code": 20000,
  "data": [
    {
      "date": "2021-10-10",
      "api_code": "600004.SH",
      "rsi1": 29.770992366412,
      "rsi2": 29.770992366412,
      "rsi3": 29.770992366412
    }
  ]
}
```

### 实测响应格式

实际无 token 请求返回的 `data` 是对象，内部字段为数组：

```json
{
  "code": 20000,
  "msg": "success",
  "data": {
    "api_code": "000858",
    "date": ["2026-05-27", "2026-05-28", "2026-05-29"],
    "rsi1": [17.3427562, 10.3375101, 46.8554589],
    "rsi2": [14.9932074, 11.8127786, 33.5977683],
    "rsi3": [22.3205055, 19.9314922, 30.8708651]
  }
}
```

`stock-up` 同时兼容：

1. 文档格式：`data` 为 `list[dict]`
2. 实测格式：`data` 为对象，`date/rsi1/rsi2/rsi3` 为数组

`stock-up` 使用：

```text
rsi1 -> rsi_short，默认 RSI6
rsi2 -> rsi_long，默认 RSI12
```

---

## 3. 无 token 限制

实测无 token 时，单次请求时间跨度不能超过 5 天：

```json
{
  "msg": "无token用户起始时间和结束时间间隔不能超过5天,地址:https://www.stockapi.com.cn",
  "code": 60038
}
```

因此 `stock-up` 对 StockAPI 请求采用 5 天窗口分段请求，再合并结果。

---

## 4. 热点板块接口

`stock-up daily` 的观察池自动加入策略使用热点板块龙头，而不是涨停池。

接口：

```text
GET https://www.stockapi.com.cn/v1/hotBkJlrDr
```

请求参数：

| 参数 | 必填 | 说明 | 示例 |
|---|---|---|---|
| date | 是 | 日期 | 2025-11-14 |

响应字段：

| 字段 | 含义 |
|---|---|
| bkCode | 板块代码 |
| bkName | 板块名称 |
| qjzf | 涨幅 |
| qjje | 净额 |
| jlrts | 资金净流入天数 |
| qiangdu | 板块强度 |
| time | 时间 |

---

## 5. 热点板块龙头股接口

接口：

```text
GET https://www.stockapi.com.cn/v1/hotBkJlrLongTou
```

请求参数：

| 参数 | 必填 | 说明 | 示例 |
|---|---|---|---|
| date | 是 | 日期 | 2025-11-14 |
| plateId | 是 | 板块 id / 板块代码 | 801004 |

响应字段：

| 字段 | 含义 |
|---|---|
| code | 股票代码 |
| name | 股票名称 |
| bkCode | 板块代码 |
| bk | 所属板块 |
| qjzf | 5 日区间涨幅 |
| jlrts | 资金净流入天数 |
| time | 时间 |

`stock-up` 会将龙头股加入观察池，原因格式：

```text
热点板块龙头: <板块名> / <股票所属板块>
```

---

## 6. 数据源优先级建议

```yaml
market:
  daily_bar_source_order:
    - stockapi
    - akshare
    - qq
```

RSI 优先级：

```text
StockAPI RSI 专用接口 -> 本地日 K 计算 fallback
```

观察池自动加入：

```text
StockAPI 热点板块 -> StockAPI 热点板块龙头股
```
