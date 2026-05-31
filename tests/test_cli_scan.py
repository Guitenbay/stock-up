from typer.testing import CliRunner

from stock_up.cli import app


runner = CliRunner()


def test_scan_limit_up_mock_runs(tmp_path):
    home = tmp_path / "home"
    runner.invoke(app, ["init", "--home", str(home)])
    result = runner.invoke(app, ["scan", "limit-up", "--home", str(home), "--provider", "mock", "--date", "2026-05-31"])
    assert result.exit_code == 0
    assert "涨停扫描完成" in result.stdout
