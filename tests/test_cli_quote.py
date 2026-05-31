from typer.testing import CliRunner

from stock_up.cli import app


runner = CliRunner()


def test_quote_mock_runs():
    result = runner.invoke(app, ["quote", "300308", "--provider", "mock"])
    assert result.exit_code == 0
    assert "暂无行情" in result.stdout
