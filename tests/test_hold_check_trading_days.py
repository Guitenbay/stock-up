from typer.testing import CliRunner

from stock_up.cli import app


runner = CliRunner()


def test_hold_check_uses_trading_days_for_hai_long(tmp_path):
    home = tmp_path / "home"
    runner.invoke(app, ["init", "--home", str(home)])
    runner.invoke(app, [
        "hold", "add", "300308", "--home", str(home), "--cost", "100", "--qty", "100",
        "--date", "2026-05-01", "--rule", "hai_long", "--ref-high", "120", "--swing-low", "95",
        "--high", "100", "--low", "90"
    ])
    result = runner.invoke(app, ["hold", "check", "--home", str(home), "--today", "2026-05-31"])
    assert result.exit_code == 0
    assert "未创新高" in result.stdout
