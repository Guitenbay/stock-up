from typer.testing import CliRunner

from stock_up.cli import app


runner = CliRunner()


def test_scan_dragon_tiger_mock_runs(tmp_path):
    home = tmp_path / "home"
    runner.invoke(app, ["init", "--home", str(home)])
    result = runner.invoke(app, ["scan", "dragon-tiger", "--home", str(home), "--provider", "mock", "--date", "2026-05-31"])
    assert result.exit_code == 0
    assert "龙虎榜扫描完成" in result.stdout
