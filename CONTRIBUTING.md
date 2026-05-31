# Contributing

感谢你关注 `stock-up`。

## 开发环境

```bash
git clone https://github.com/Guitenbay/stock-up.git
cd stock-up
python3 -m pip install -e '.[dev]'
```

如果需要 AkShare 数据源：

```bash
python3 -m pip install -e '.[dev,akshare]'
```

## 运行测试

```bash
pytest -q
```

提交代码前请尽量保证测试通过。

## 本地验证 CLI

```bash
stock-up --help
stock-up init --home /tmp/stock-up-demo
stock-up daily --home /tmp/stock-up-demo --provider mock --date 2026-05-31
```

## 提交规范

commit message 使用 Conventional Commits：

```text
feat: add new command
fix: correct daily provider
perf: speed up quote parsing
docs: update command guide
refactor: simplify scanner
ci: add workflow
build: bump version
```

## Pull Request

PR 建议包含：

- 变更摘要
- 关联 issue，例如 `Closes #1`
- 测试结果，例如 `pytest -q`
- 如果改了命令或配置，请同步更新：
  - `README.md`
  - `AGENTS.md`
  - `docs/commands.md`

## 发布流程

发布到 PyPI 前需要升级版本号，因为 PyPI 不允许覆盖同一版本：

```bash
# 修改 pyproject.toml version
pytest -q
rm -rf dist build
python3 -m build
python3 -m twine check dist/*
python3 -m twine upload dist/*
```

然后创建 GitHub Release，并上传 `dist/` 中的 wheel 和 sdist。

## 安全注意

不要把 token、密钥、cookie 写入代码、测试或文档。

如果 token 已经出现在 issue、PR、commit 或聊天记录中，请立刻 revoke。

## 免责声明

本项目仅用于个人复盘和策略辅助，不构成投资建议，也不会自动交易。
