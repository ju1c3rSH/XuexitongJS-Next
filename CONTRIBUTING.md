# Contributing to XueXiTong-Helper

欢迎提交 Issue、Pull Request 或提出建议。请遵循以下贡献指南。

---

## 环境准备

1. **克隆仓库**

   ```sh
   git clone https://github.com/ju1c3rSH/XuexitongJS-Next.git
   cd XuexitongJS-Next
   ```

2. **创建并激活虚拟环境**

   - Windows:
     ```sh
     python -m venv venv
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```sh
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **安装依赖**

   ```sh
   pip install -r requirements.txt
   ```

---

## 代码规范

### Python

- 遵循 [PEP8](https://pep8.org/) 代码风格
- 使用 [Ruff](https://docs.astral.sh/ruff/) 进行代码检查和格式化，配置见 `pyproject.toml`
- 文件编码统一为 UTF-8
- 资源路径统一使用 `static_path()` 和 `writable_path()`（定义在 `src/app/utils/file_path.py`）

### JavaScript

- 代码位于 `src/main_script/modules/` 目录，按模块分为 `core`、`nav`、`video`、`pdf`、`quiz`、`main`
- 构建使用 `node src/main_script/build.js`，按顺序拼接模块生成 `script.js`
- 顶层全局变量使用 `var`（脚本可能被重复注入，`let` 会抛出重新声明错误）

---

## 提交规范

- **分支命名**：`feature/xxx`、`bugfix/xxx`、`docs/xxx`
- **Commit 信息**：简明描述变更内容，中英文均可
  ```
  feat: 新增答题重试机制
  fix: 修复 iframe 遍历超时问题
  docs: 更新 README 快速开始部分
  ```
- **PR 说明**：请描述变更内容、影响范围和测试方式

---

## Issue 反馈

- 提交前请先搜索是否已存在类似问题
- 提供复现步骤、环境信息（操作系统、Python 版本）、报错日志
- Bug 报告请尽量附带截图或日志

---

## Pull Request 流程

1. Fork 本仓库并新建分支
2. 按规范进行开发和提交
3. 确保本地运行正常后提交 PR
4. 等待维护者 Review 并合并

---

## 打包说明

- 使用 `build.ps1` 进行 PyInstaller 打包
- 打包配置见 `build.spec`，隐式导入和排除项已在此文件中声明
- 调试构建：`.\build.ps1 -Debug`

---

## 其他

- 遵守 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- 本项目基于 CC BY-NC 4.0 协议，禁止商业使用
- 联系方式：通过 GitHub Issues 或 Discussions 沟通

感谢你的贡献！
