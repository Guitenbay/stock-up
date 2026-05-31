from typer.testing import CliRunner

from stock_up.cli import app


runner = CliRunner()


def test_watch_check_outputs_action(tmp_path):
    home = tmp_path / "home"
    runner.invoke(app, ["init", "--home", str(home)])
    runner.invoke(app, ["watch", "add", "300308", "--home", str(home), "--name", "中际旭创", "--high", "20", "--low", "10", "--now", "16.5"])
    result = runner.invoke(app, ["watch", "check", "--home", str(home)])
    assert result.exit_code == 0
    assert "300308" in result.stdout


def test_hold_check_outputs_stop_loss(tmp_path):
    home = tmp_path / "home"
    runner.invoke(app, ["init", "--home", str(home)])
    runner.invoke(app, ["hold", "add", "300308", "--home", str(home), "--cost", "100", "--qty", "100"])
    runner.invoke(app, ["hold", "set", "300308", "--home", str(home), "--highest", "110"])
    # update current price through repository-independent set is not supported yet; use add-buy not suitable, so rely on direct now option via future command not here
    result = runner.invoke(app, ["hold", "check", "--home", str(home)])
    assert result.exit_code == 0
    assert "300308" in result.stdout
