# GaAutoBuilds - AI 自动编译修复系统

> GitHub Actions + LLM 实现自动检测编译错误并智能修复

## 项目概述

一个通用的自动化修复系统，可以自动检测编译错误、调用 LLM 分析并修复代码。

## 当前进度

- **Step 1 (完成)**: 获取编译错误并保存到本地文件
- **Step 2 (计划中)**: 调用 LLM 分析错误 → 自动修复 → 自动提交

## 技术栈

- Python 3.11
- PyGithub
- GitHub Actions

## 文件结构

```
GaAutoBuilds/
├── .github/workflows/
│   └── step1-fetch-error.yml   # Step 1: 获取错误
├── scripts/
│   └── fetch_build_error.py    # 核心脚本
├── requirements.txt
├── README.md
└── PLAN.md
```

## 使用方式

触发 Workflow 获取目标仓库的编译错误：

```bash
gh workflow run step1-fetch-error.yml \
  -f target_repo=owner/project \
  -f commit_sha=abc123
```

## 常用路径

- 错误日志输出: `build_errors/`
- Workflow 配置: `.github/workflows/`
- 核心脚本: `scripts/`

## 下一步任务

1. 将错误日志发送给 LLM 分析
2. LLM 生成修复方案
3. 自动提交修复
4. 循环直到成功
