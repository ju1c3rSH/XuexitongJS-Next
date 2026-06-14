# Security Policy

## 报告安全漏洞

如发现安全漏洞或潜在风险，请**不要在公开 Issue 或 Pull Request 中披露**，通过以下方式私下报告：

- 在 GitHub 上发起 [Security Advisory](https://github.com/ju1c3rSH/XuexitongJS-Next/security/advisories/new)
- 或通过 Issues 页面说明需要私密报告，我们会提供联系方式

请在报告中包含：

- 漏洞描述及影响范围
- 复现步骤或相关代码片段
- 建议的修复方案（可选）

我们会在收到报告后尽快回复，并在修复后致谢（如你同意）。

---

## 安全最佳实践

- **API Key**：在 GUI 中配置后存储在 `config.toml`，该文件已加入 `.gitignore`，不会提交到仓库
- **浏览器驱动**：Selenium 使用的 WebDriver 请从官方渠道获取
- **网络通信**：WebSocket 服务仅绑定 `localhost:8765`，不对外暴露
- **依赖管理**：请勿随意升级依赖库，所有依赖变更需经过 Review
- **敏感信息**：不要在代码、配置或日志中提交 API Key、密码等敏感信息

---

## 免责声明

本项目仅供学习使用。使用本项目造成的任何安全问题或账号封禁，开发者不承担任何责任。

---

## 参考

- [GitHub Security Advisories](https://docs.github.com/en/code-security/security-advisories)
- [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)
