from typer.testing import CliRunner

from stock_up.cli import app


runner = CliRunner()


def test_tick_command_runs_without_data(tmp_path):
    home = tmp_path / "home"
    runner.invoke(app, ["init", "--home", str(home)])
    result = runner.invoke(app, ["tick", "--home", str(home), "--provider", "mock"])
    assert result.exit_code == 0
    assert "tick完成" in result.stdout
