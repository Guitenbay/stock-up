from typer.testing import CliRunner

from stock_up.cli import app
from stock_up.db import init_db
from stock_up.market.mock import MockProvider
from stock_up.models import Holding, Quote
from stock_up.repositories import HoldingRepository
from stock_up.services.tick import TickSignal, run_tick


runner = CliRunner()


def test_tick_command_runs_without_data(tmp_path):
    home = tmp_path / "home"
    runner.invoke(app, ["init", "--home", str(home)])
    result = runner.invoke(app, ["tick", "--home", str(home), "--provider", "mock"])
    assert result.exit_code == 0
    assert "tick完成" in result.stdout


def test_tick_summary_contains_holding_signal(tmp_path):
    db_path = tmp_path / "data.db"
    init_db(db_path)
    HoldingRepository(db_path).upsert(Holding(code="600000", name="浦发银行", cost=10, quantity=100, now=10, highest=10, high=11, low=9))
    provider = MockProvider(quotes={
        "600000": Quote(code="600000", name="浦发银行", now=9.2, high=9.3, low=9.1, avg=9.2),
    })

    summary = run_tick(db_path, provider, trade_date="2026-05-31")

    assert summary.holding_signals
    assert summary.holding_signals[0].title == "建议止损/退出"


def test_tick_grouped_signal_output(capsys):
    from stock_up.cli import _print_grouped_signals

    _print_grouped_signals("持仓", [
        TickSignal(code="600000", name="浦发银行", title="建议止损/退出", reasons=["跌破止损线"]),
        TickSignal(code="300308", name="中际旭创", title="建议止损/退出", reasons=["跌破止损线"]),
        TickSignal(code="000858", name="五粮液", title="建议止盈", reasons=["触发回撤止盈"]),
    ])

    output = capsys.readouterr().out
    assert output.index("持仓｜建议止损/退出") < output.index("持仓｜建议止盈")
    assert output.count("持仓｜建议止损/退出") == 1
    assert "600000 浦发银行" in output
    assert "300308 中际旭创" in output
    assert "000858 五粮液" in output


def test_tick_signal_output_merges_same_stock_before_grouping(capsys):
    from stock_up.cli import _print_grouped_signals

    _print_grouped_signals("持仓", [
        TickSignal(code="600000", name="浦发银行", title="建议止损/退出", reasons=["跌破止损线"]),
        TickSignal(code="600000", name="浦发银行", title="RSI 死叉", reasons=["短 RSI 下穿长 RSI"]),
        TickSignal(code="300308", name="中际旭创", title="建议止损/退出", reasons=["跌破止损线"]),
    ])

    output = capsys.readouterr().out
    assert "持仓｜建议止损/退出 / RSI 死叉" in output
    assert "600000 浦发银行: 跌破止损线; 短 RSI 下穿长 RSI" in output
    assert output.count("600000 浦发银行") == 1
    assert "持仓｜建议止损/退出\n" in output
    assert "300308 中际旭创" in output
