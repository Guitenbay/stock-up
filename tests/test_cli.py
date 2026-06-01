from typer.testing import CliRunner

from stock_up.cli import app
from stock_up.models import Quote, WatchItem
from stock_up.repositories import HoldingRepository, WatchRepository


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
    item = WatchRepository(home / "data.db").get("sz300308")
    assert item is not None
    assert item.name == "中际旭创"


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


def test_watch_add_fetches_name_when_name_missing(tmp_path):
    home = tmp_path / "home"
    runner.invoke(app, ["init", "--home", str(home)])
    result = runner.invoke(app, ["watch", "add", "300308", "--home", str(home), "--high", "130", "--low", "110"])
    assert result.exit_code == 0
    item = WatchRepository(home / "data.db").get("sz300308")
    assert item is not None
    assert item.name
    assert item.name != "sz300308"


def test_hold_add_fetches_name_when_name_missing(tmp_path):
    home = tmp_path / "home"
    runner.invoke(app, ["init", "--home", str(home)])
    result = runner.invoke(app, ["hold", "add", "300308", "--home", str(home), "--cost", "100", "--qty", "100"])
    assert result.exit_code == 0
    item = HoldingRepository(home / "data.db").get("sz300308")
    assert item is not None
    assert item.name
    assert item.name != "sz300308"


def test_watch_list_handles_invalid_range(tmp_path):
    home = tmp_path / "home"
    runner.invoke(app, ["init", "--home", str(home)])
    WatchRepository(home / "data.db").upsert(WatchItem(code="sz300308", name="中际旭创", high=0, low=0, now=120))

    result = runner.invoke(app, ["watch", "list", "--home", str(home)])

    assert result.exit_code == 0


def test_watch_add_uses_qq_range_when_high_low_missing(tmp_path, monkeypatch):
    home = tmp_path / "home"
    runner.invoke(app, ["init", "--home", str(home)])
    monkeypatch.setattr("stock_up.cli._get_realtime_quote", lambda code, provider="qq": Quote(
        code="sz300308",
        name="中际旭创",
        now=120,
        high=126,
        low=118,
    ))

    result = runner.invoke(app, ["watch", "add", "300308", "--home", str(home)])

    assert result.exit_code == 0
    item = WatchRepository(home / "data.db").get("sz300308")
    assert item is not None
    assert item.name == "中际旭创"
    assert item.now == 120
    assert item.high == 126
    assert item.low == 118


def test_hold_add_uses_qq_range_when_high_low_missing(tmp_path, monkeypatch):
    home = tmp_path / "home"
    runner.invoke(app, ["init", "--home", str(home)])
    monkeypatch.setattr("stock_up.cli._get_realtime_quote", lambda code, provider="qq": Quote(
        code="sz300308",
        name="中际旭创",
        now=120,
        high=126,
        low=118,
    ))

    result = runner.invoke(app, ["hold", "add", "300308", "--home", str(home), "--cost", "100", "--qty", "100"])

    assert result.exit_code == 0
    item = HoldingRepository(home / "data.db").get("sz300308")
    assert item is not None
    assert item.name == "中际旭创"
    assert item.high == 126
    assert item.low == 118
