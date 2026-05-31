from pathlib import Path

from stock_up.config import AppConfig, load_config, write_default_config


def test_default_config_values():
    cfg = AppConfig()
    assert cfg.market.quote_source == "akshare"
    assert cfg.tick.min_interval_seconds == 20
    assert cfg.holding.default_rule == "wolf_swing"
    assert cfg.auto_watch.dragon_tiger_scan_enabled is True
    assert cfg.auto_watch.hot_leader_scan_enabled is False


def test_write_and_load_default_config(tmp_path: Path):
    path = tmp_path / "config.yaml"
    write_default_config(path)
    cfg = load_config(path)
    assert cfg.watch.initial_low_mode == "same_day"
    assert cfg.technical.rsi.short_period == 6
