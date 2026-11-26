# CI/CD 说明文档

本文档说明本项目使用的 GitHub Actions 工作流，以及你需要手动完成的步骤。

## 已添加的文件

- `.github/workflows/ci-cd.yml`：GitHub Actions 工作流
- `.gitignore`：忽略本地运行时产生的临时文件

## 工作流做什么

### CI（持续集成）

在 `push` 或 `pull_request` 到 `main` / `master` 分支时自动运行，检查：

1. 检出代码
2. 安装 Python
3. 用 `py_compile` 检查 `app.py` 和 `serve.py` 语法
4. 确认 `index.html` 存在且包含文字 `Have a nice day!`
5. 启动本地 HTTP 服务，并用 `curl` 确认页面能返回 200

### CD（持续部署）

当代码被推送到 `main` 或 `master` 分支，并且 CI 通过后：

1. 只把 `index.html` 复制到 `site/` 目录作为发布内容
2. 使用官方 `actions/configure-pages`、`actions/upload-pages-artifact`、`actions/deploy-pages` 发布到 GitHub Pages
3. 部署成功后，Actions 页面会输出 Pages 访问地址

你也可以在项目根目录的 Actions 标签页中手动点击 **Run workflow** 触发一次。

## 你需要手动完成的操作

当前这台机器还没有 Git 仓库、GitHub 远程仓库和 GitHub 登录凭据，所以我只能先在本地提交，不能替你推送到 GitHub。请你按下面步骤操作：

### 1. 在 GitHub 上创建仓库

登录 GitHub，点击 **New repository**，例如命名为：

```text
have-a-nice-day-web
```

创建时不要勾选初始化 README / .gitignore / license，保持空仓库即可（如果已经勾选，也没关系，后面按提示处理冲突即可）。

### 2. 在本地关联远程仓库

在本项目目录打开终端，执行（把 URL 换成你自己的）：

```powershell
git remote add origin https://github.com/<你的用户名>/have-a-nice-day-web.git
```

如果你习惯用 SSH，并且已经配置好 SSH key，可以用：

```powershell
git remote set-url origin git@github.com:<你的用户名>/have-a-nice-day-web.git
```

### 3. 配置 GitHub 认证

任选一种：

- **GitHub CLI（推荐）**
  ```powershell
  winget install --id GitHub.cli
  gh auth login
  ```
- **HTTPS + Personal Access Token**：在 GitHub → Settings → Developer settings → Personal access tokens 生成带 `repo` 和 `workflow` 权限的 token，推送时用它作为密码。
- **SSH key**：生成并添加公钥到 GitHub → Settings → SSH and GPG keys，然后信任主机：
  ```powershell
  ssh-keyscan github.com >> "$env:USERPROFILE\.ssh\known_hosts"
  ```

> 我不会在对话中索要你的密码、token 或私钥。

### 4. 推送代码

```powershell
git push -u origin main
```

### 5. 启用 GitHub Pages

进入仓库页面：

1. 点击 **Settings**
2. 左侧选择 **Pages**
3. **Build and deployment → Source** 选择 **GitHub Actions**

### 6. 查看结果

- 打开仓库的 **Actions** 标签页，确认工作流是绿色 successful
- 部署成功后，访问地址格式为：
  ```text
  https://<你的用户名>.github.io/have-a-nice-day-web/
  ```
  具体地址以 Actions 中 `deploy` 作业输出的 `page_url` 为准。

## 常见问题

- **CI 失败，提示端口被占用**：工作流里用的是 GitHub 临时 runner，不会有本机端口冲突；如果仍失败，请把 Actions 日志发给我。
- **Pages 404**：确认第 5 步 Source 已选成 GitHub Actions，并且 `main` 分支的 workflow 已成功运行。
- **推送被拒绝**：通常是认证失败或远程仓库不是空的；按终端提示处理，或把错误信息发给我。
