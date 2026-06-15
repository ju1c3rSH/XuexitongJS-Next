# uXueXiTongX

视频更稳，答题更准，使用更省心

超星学习通全自动学习工具。支持视频自动播放、PDF 自动翻阅、AI 智能答题，基于 Selenium 与 WebSocket 实现浏览器自动化操作，无需手动干预。

本项目源于：

- **[@chaolucky18](https://github.com/chaolucky18)** 的 [xuexitongScript](https://github.com/chaolucky18/xuexitongScript) —— 原始 JS 自动化脚本
- **[@unraous](https://github.com/unraous)** 的 [uXuexitongJS](https://github.com/unraous/uXuexitongJS) —— 加入 Python 后端与 AI 答题能力

感谢两位前作者的贡献。本项目在以上基础上全面重写并修复大量问题，作为独立项目维护。

---

## 特性

### JS 自动化

- 三层 iframe 嵌套遍历，自动识别视频、PDF、作业三种内容类型
- 锁与冷却机制协调多任务并发
- 页面刷新后脚本自动重连并恢复运行
- 双速存活监视器，脚本异常退出后自动重新注入

### AI 答题

- 字体反混淆：基于 ddddocr 对混淆字体进行字形识别，替代哈希方案
- 兼容任意 OpenAI 兼容 API，用户可选择不同模型
- 答题失败时自动重试，重试达最大次数后回退到默认答案
- 可选 DuckDuckGo 联网搜索，为 AI 提供题目相关上下文
- 可选视觉模型模式，将题目截图发送给 AI 分析

### 题目获取

- 从页面中提取结构化 JSON 题目数据
- 图片自动下载并 OCR 识别，公式图片亦做处理
- 修补模式加入历史记忆，避免重复尝试已证错误的选项

### 稳定性

- 多线程竞态处理机制
- WebSocket 断线自动重连
- Cookie 持久化，减少重复登录
- iframe 加载超时及跨域异常处理

### 图形界面

- 基于 PyQt5 与 qfluentwidgets 构建
- 实时日志面板、配置管理、主题切换

---

## AI 答题流程

```
浏览器端 JS 提取题目数据 → WebSocket 发送至 Python 后端
Python 保存字体 → ddddocr 反混淆 → 解码题目文本
调用 AI 接口（可选联网搜索和视觉模式）
AI 返回答案 JSON → WebSocket 回传浏览器 → 自动填写并提交
```

---

## 快速开始

### 快速使用（推荐）

1. 在 API 配置页填写 API Key 和接口地址（推荐使用 deepseek-v4-flash）
2. 点击**启动浏览器**，初次启动可能稍慢
3. 在打开的浏览器中登录学习通，进入课程页面
4. 点击**注入脚本**
5. 点击**鼠标模拟**，脚本开始自动运行

遇到 Bug 欢迎提交 Issue，我们会尽快排查修复。

### 下载 Release

从 [Releases](https://github.com/ju1c3rSH/uXueXiTongX/releases) 下载 Windows 打包版本，解压后运行。

### 源码运行

```bash
git clone https://github.com/ju1c3rSH/uXueXiTongX.git
cd uXueXiTongX

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux

pip install -r requirements.txt
python src/main.py
```

> **注意：** 程序中的高级设置项如无需要，请勿更改。

### 纯 JS 模式

若不需要 AI 答题功能，可将 `src/main_script/script.js` 的内容复制至浏览器控制台执行。

---

## 项目结构

```
src/
├── main.py
├── app/
│   ├── _driver_manager.py
│   ├── _config_manager.py
│   └── auto_answer/
│       ├── _create_map.py
│       ├── _depry_question.py
│       ├── _core_of_answer.py
│       ├── _prompt_builder.py
│       ├── _image_processor.py
│       ├── _web_search.py
│       └── _extract_html.py
├── main_script/
│   ├── modules/
│   │   ├── core.js
│   │   ├── nav.js
│   │   ├── video.js
│   │   ├── pdf.js
│   │   ├── quiz.js
│   │   └── main.js
│   └── build.js
├── gui_fluent/
└── resources/
```

---

## 许可证与免责声明

本项目基于 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) 协议授权。

使用时须署名原作者（@chaolucky18、@unraous、@ju1c3rSH）并标注修改。

本软件仅供学习使用，不得用于商业盈利。请合理使用，滥用脚本可能会导致不良后果。

如涉及版权或侵犯了您的合法权益，请在 Issues 页提出，我们收到后会尽快核实并处理。
