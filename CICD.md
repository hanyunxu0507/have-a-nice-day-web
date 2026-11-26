# CI/CD 说明文档

本项目包含两个阶段的成果：

1. 初始静态网页 `index.html`（`Have a nice day!`），由 `.github/workflows/ci-cd.yml` 验证并发布到 GitHub Pages。
2. 当前 application：Flask 前端 + SQLite 后端，数据放在 `data/` 文件夹，由 `.github/workflows/data-update.yml` 自动更新数据库。

## 当前 application 的 CI/CD 工作流

工作流文件：`/.github/workflows/data-update.yml`

### Trigger

工作流在以下情况下触发：

- 有文件被推送到 `data/` 文件夹下的任意路径（`data/**`）
- 在 Actions 页面手动点击 **Run workflow**（`workflow_dispatch`）

### Actions / Steps

工作流运行在 `ubuntu-latest`，步骤如下：

1. **Checkout**：检出仓库代码。
2. **Set up Python 3.11**：使用 `actions/setup-python@v5` 安装 Python 3.11。
3. **Install dependencies**：升级 pip，并根据 `requirements.txt` 安装 `Flask` 和 `pandas`。`sqlite3` 是 Python 标准库，不需要额外安装，工作流中仅验证可导入。
4. **Run clean_and_merge**：执行 `python clean_and_merge.py`，读取 `data/orders.csv` 和 `data/customers.csv`，去重、换算 `amount_cny`、按 `customer_id` 合并，并重建 `merged_data.db`。
5. **Commit updated database**：配置 bot 身份，把更新后的 `merged_data.db` 提交并推送回仓库；如果数据库没有变化，则跳过提交。

因为提交的是 `merged_data.db`，路径不匹配 `data/**`，所以不会造成无限循环触发。

### Flask 前端

- 入口：`app.py`
- 主页 `/`：展示 `merged_orders` 表和 `region_summary` 表
- 接口 `/api/data`：返回两张表的 JSON 数据
- 页面每 3 秒通过 JavaScript `fetch('/api/data')` 自动刷新，数据库变化后前端会自动更新

本地运行：

```powershell
cd "c:\Users\26430\CodeBuddy\20261126153955"
python clean_and_merge.py
python app.py
```

然后访问 `http://127.0.0.1:5000/`。

## 可直接填写到作业里的英文描述

### Trigger

The workflow is triggered when any file under the `data/` folder is pushed to the repository. It can also be triggered manually from the GitHub Actions tab using `workflow_dispatch`.

### Actions / Main steps

1. Check out the repository.
2. Set up Python 3.11.
3. Install the required packages from `requirements.txt` (`Flask` and `pandas`); `sqlite3` is part of the Python standard library and is verified by import.
4. Run `clean_and_merge.py` to clean duplicates, convert amounts to CNY, merge orders with customers on `customer_id`, and rebuild `merged_data.db`.
5. Commit and push the updated `merged_data.db` back to GitHub if it changed.

The Flask frontend connects to the same SQLite database. Its main page shows the merged orders table and the average `amount_cny` per region, and it refreshes automatically every 3 seconds by calling `/api/data`.

## 初始静态网页工作流（保留）

文件：`.github/workflows/ci-cd.yml`

- Trigger：`push` / `pull_request` 到 `main` 或 `master`，以及手动触发
- CI：检查 Python 语法、验证 `index.html` 内容、冒烟测试本地 HTTP 服务
- CD：把 `index.html` 发布到 GitHub Pages

## 当前 Git 状态

- 远程仓库：`https://github.com/hanyunxu0507/have-a-nice-day-web.git`
- 分支：`main`
- 已启用 GitHub Pages（Source = GitHub Actions）
