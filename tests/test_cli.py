from typer.testing import CliRunner

from stock_up.cli import app


runner = CliRunner()


def test_init_command(tmp_path):
    home = tmp_path / "home"
    result = runner.invoke(app, ["init", "--home", str(home)])
    assert result.exit_code == 0
    assert (home / "config.yaml").exists()
    assert (home / "data.db").exists()


def test_watch_add_and_list_with_manual_values(tmp_path):
    home = tmp_path / "home"
    runner.invoke(app, ["init", "--home", str(home)])
    result = runner.invoke(app, ["watch", "add", "300308", "--home", str(home), "--name", "中际旭创", "--high", "130", "--low", "110"])
    assert result.exit_code == 0

    result = runner.invoke(app, ["watch", "list", "--home", str(home)])
    assert result.exit_code == 0
    assert "300308" in result.stdout
    assert "中际旭创" in result.stdout


def test_hold_add_buy_close(tmp_path):
    home = tmp_path / "home"
    runner.invoke(app, ["init", "--home", str(home)])
    result = runner.invoke(app, ["hold", "add", "300308", "--home", str(home), "--name", "中际旭创", "--cost", "100", "--qty", "100"])
    assert result.exit_code == 0

    result = runner.invoke(app, ["hold", "add-buy", "300308", "--home", str(home), "--price", "120", "--qty", "100"])
    assert result.exit_code == 0
    assert "110" in result.stdout

    result = runner.invoke(app, ["hold", "close", "300308", "--home", str(home), "--price", "130", "--reason", "止盈"])
    assert result.exit_code == 0
    assert "4000" in result.stdout
