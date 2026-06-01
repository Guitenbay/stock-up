# 腾讯股票接口说明

## 1. 实时行情

接口：

```text
https://qt.gtimg.cn/q=sz000858
```

多个股票用英文逗号分隔：

```text
https://qt.gtimg.cn/q=sz000858,sh600519
```

返回示例：

```text
v_sz000858="51~五粮液~000858~27.78~27.60~27.70~...";
```

常用字段，下标从 0 开始：

| 下标 | 含义 |
|---:|---|
| 1 | 名称 |
| 2 | 代码 |
| 3 | 当前价 |
| 4 | 昨收 |
| 5 | 今开 |
| 31 | 涨跌额 |
| 32 | 涨跌幅 |
| 33 | 最高 |
| 34 | 最低 |
| 35 | 价格/成交量/成交额 |
| 36 | 成交量，手 |
| 37 | 成交额，万 |
| 38 | 换手率 |
| 43 | 振幅 |
| 47 | 涨停价 |
| 48 | 跌停价 |
| 51 | 分时均价，部分接口返回 |
| 57 | 成交额，万，部分接口返回 |

`stock-up` 用该接口作为默认实时行情源。

---

## 2. 资金流向

接口：

```text
https://qt.gtimg.cn/q=ff_sz000858
```

字段：

| 下标 | 含义 |
|---:|---|
| 0 | 代码 |
| 1 | 主力流入 |
| 2 | 主力流出 |
| 3 | 主力净流入 |
| 4 | 主力净流入占比 |
| 5 | 散户流入 |
| 6 | 散户流出 |
| 7 | 散户净流入 |
| 8 | 散户净流入占比 |
| 9 | 资金流入流出总和 |
| 12 | 名称 |
| 13 | 日期 |

MVP 暂不使用。

---

## 3. 盘口分析

接口：

```text
https://qt.gtimg.cn/q=s_pksz000858
```

字段：

| 下标 | 含义 |
|---:|---|
| 0 | 买盘大单 |
| 1 | 买盘小单 |
| 2 | 卖盘大单 |
| 3 | 卖盘小单 |

MVP 暂不使用。

---

## 4. 简要行情

接口：

```text
https://qt.gtimg.cn/q=s_sz000858
```

字段：

| 下标 | 含义 |
|---:|---|
| 1 | 名称 |
| 2 | 代码 |
| 3 | 当前价 |
| 4 | 涨跌额 |
| 5 | 涨跌幅 |
| 6 | 成交量，手 |
| 7 | 成交额，万 |
| 9 | 总市值 |

MVP 暂不使用。

---

## 5. K 线数据

### 日 K

接口格式：

```text
http://data.gtimg.cn/flashdata/hushen/daily/{yy}/{code}.js
```

例子：

```text
http://data.gtimg.cn/flashdata/hushen/daily/26/sz000858.js
```

其中：

```text
26 = 年份后两位，即 2026 年
```

旧资料中示例：

```text
http://data.gtimg.cn/flashdata/hushen/daily/13/sz000858.js
```

表示 2013 年日 K。

### 周 K

接口格式：

```text
http://data.gtimg.cn/flashdata/hushen/weekly/{code}.js
```

例子：

```text
http://data.gtimg.cn/flashdata/hushen/weekly/sz000858.js
```

### stock-up 使用方式

`stock-up` 目前主要使用腾讯接口获取实时行情和股票名。日 K / RSI 优先使用 StockAPI；腾讯日 K 文档保留为接口参考。

腾讯日 K 会按年份请求最近若干年的 daily 文件，然后解析为统一 `DailyBar`：

```text
code
trade_date
open
high
low
close
volume
amount
```
