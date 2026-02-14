# GAutoBuilds - Step 1

> 获取目标仓库的编译错误并保存到本地文件

## 当前进度: Step 1 ✅

### 功能
- 触发目标仓库的 CI 构建
- 等待构建完成（或直接获取已有构建结果）
- 获取构建日志
- 保存到本地文件 (`build_errors/` 目录)

## 使用方法

### 1. 触发 Workflow

#### 通过 GitHub Web UI
1. 进入 GAutoBuilds 仓库
2. 点击 Actions → Step 1 - Fetch Build Error
3. 点击 "Run workflow"
4. 填写参数：
   - `target_repo`: 目标仓库 (如 `your-org/your-project`)
   - `target_branch`: 分支名 (默认 `main`)
   - `commit_sha`: 提交 SHA
   - `workflow_file`: CI 配置文件名 (默认 `ci.yml`)
   - `wait_for_build`: 是否等待构建完成

#### 通过 GitHub CLI
```bash
gh workflow run step1-fetch-error.yml \
  -f target_repo=owner/project \
  -f target_branch=main \
  -f commit_sha=abc123 \
  -f workflow_file=ci.yml
```

#### 通过 curl
```bash
curl -X POST https://api.github.com/repos/YOUR_USERNAME/ga-auto-builds/dispatches \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.versions+json" \
  -d '{
    "event_type": "fetch-error",
    "client_payload": {
      "target_repo": "owner/project",
      "target_branch": "main",
      "commit_sha": "abc123",
      "workflow_file": "ci.yml"
    }
  }'
```

### 2. 本地运行

```bash
# 安装依赖
pip install PyGithub

# 设置 token
export GITHUB_TOKEN=ghp_your_token

# 运行
python scripts/fetch_build_error.py \
  --target-repo "owner/project" \
  --branch "main" \
  --commit-sha "abc123" \
  --workflow-file "ci.yml" \
  --wait
```

## 输出文件

错误日志会保存到 `build_errors/` 目录，文件名格式：
```
{repo_name}_{commit_sha}_{timestamp}.log
```

文件内容包含：
- 仓库、分支、提交信息
- 构建结论 (success/failure)
- 构建日志

## 下一步 (Step 2)

- [ ] 将错误日志发送给 LLM 分析
- [ ] LLM 生成修复方案
- [ ] 自动提交修复
- [ ] 循环直到成功
