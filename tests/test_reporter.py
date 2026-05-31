from stock_up.services.reporter import DailyReport, render_daily_report


def test_render_daily_report_contains_sections():
    report = DailyReport(
        trade_date="2026-05-31",
        new_watch=["300308 中际旭创"],
        watch_actions=["300308 建议可小仓试错"],
        holding_actions=["600000 建议止损"],
        trades=["买入 300308 100股 @120"],
    )
    text = render_daily_report(report)
    assert "# stock-up 每日报告 2026-05-31" in text
    assert "## 新增观察" in text
    assert "## 今日交易" in text
    assert "免责声明" in text
