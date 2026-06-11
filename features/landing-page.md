# 落地页制作

## 目标

为 everyday 项目制作一个产品落地页，中英文双语，部署到 GitHub Pages。

## 修改范围

- 新增 `docs/index.html`（中文版落地页）
- 新增 `docs/en/index.html`（英文版落地页）
- 新增 `docs/images/` 目录及 3 张站点截图

## 核心实现

使用 Kami 设计系统的 landing-page 模板，基于 parchment + ink-blue 配色方案、TsangerJinKai02 中文字体 / Charter 英文字体。

### 页面结构

| 区段 | 内容 |
|------|------|
| Hero | 大字标题 + tagline + 项目指标 + GitHub/在线预览 CTA + 语言切换 |
| Gallery | 截图轮播（首页 / 故事正文 / 词云），支持自动轮播、悬停暂停、左右点击切换 |
| Features | 6 个核心特性两列排布：多模型并行、插件配置、惰性加载、流水线架构、词云洞察、自动运维 |
| Principles | 6 条设计原则网格：简单稳定、零侵入、纯函数式、可观测、零配置、自动化 |
| Manifesto | 项目哲学陈述 + 4 个关键指标数据卡片 |
| FAQ | 5 个常见问题：上手、添加模型、存储位置、本地预览、代码质量 |
| Footer | 品牌标记 + GitHub/预览/许可链接 + 收尾语 |

### 多语言

- `docs/index.html`（中文，lang=zh-CN）
- `docs/en/index.html`（英文，lang=en）
- 右上角语言切换按钮：中文版显示「EN」→ `/en/`，英文版显示「中文」→ `/`
- hreflang + og:locale 多语言 SEO 标签

## 影响范围

- 新文件只影响 `docs/` 目录，不修改任何现有代码
- Cloudflare Pages（`story/` 目录）不受影响
- GitHub Pages 需在仓库 Settings → Pages → Source 选择 `docs/`

## 验证方式

- HTML 语法解析通过
- 所有图片路径解析正确（CN: `images/xxx`，EN: `../images/xxx`）
- 响应式断点 880px / 480px 覆盖
- prefers-reduced-motion 无障碍支持

## 已知限制

- 截图文件较大（homepage 108K / story 968K / wordcloud 468K），首次加载可能较慢
- 无自定义 logo，使用纯文字品牌标记
