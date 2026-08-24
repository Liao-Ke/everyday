# 修复 9 条 Dependabot npm 依赖漏洞告警

## 目标

修复 GitHub Dependabot 报告的 9 条 open 状态 npm 依赖漏洞告警（#32–#44），涉及 4 个传递依赖包。

## 背景

所有告警均为 **npm 开发依赖**（devDependencies）中的传递依赖漏洞，引入链：

| 漏洞包 | 原版本 | 引入链 |
|--------|--------|--------|
| vite | 5.4.21 | vitepress@1.6.4、vite-plugin-compression@0.5.1 |
| postcss | 8.5.10 | vitepress@1.6.4 直接依赖 |
| js-yaml | 3.14.2 | vitepress-sidebar@1.33.1 → gray-matter@4.0.3 |
| brace-expansion | 5.0.5 | vitepress-sidebar@1.33.1 → glob@11.1.0 → minimatch@10.2.5 |

vite 5.x 已停止维护（EOL），修复版本仅存在于 6.4.3+；vitepress 1.6.4（当前最新）仍锁定 vite ^5.4.14，因此采用 npm overrides 强制升级。

## 修改范围

- `package.json` — 新增 `overrides` 字段：postcss ^8.5.23、js-yaml ^3.15.1、brace-expansion ^5.0.9、vite ^6.4.3
- `package-lock.json` — npm install 重新解析

## 核心实现

```json
"overrides": {
  "postcss": "^8.5.23",
  "js-yaml": "^3.15.1",
  "brace-expansion": "^5.0.9",
  "vite": "^6.4.3"
}
```

升级后版本：vite 6.4.3、postcss 8.5.26、js-yaml 3.15.1、brace-expansion 5.0.9。

## 影响范围

- 9 条告警覆盖的包全部升级到修复版本（postcss×3、js-yaml×3、brace-expansion×1、vite×2）
- vite 5 → 6 为主版本升级，但已验证 vitepress 1.6.4 兼容（见验证方式）

## 验证方式

1. `npm audit` → found 0 vulnerabilities
2. 小站点冒烟测试：vite 6.4.3 + vitepress 1.6.4 构建通过（build complete in 1.93s）
3. 真实项目 `npm run docs:build` 构建验证（bundle 阶段通过；rendering 阶段耗时是项目 3219 页面的既有情况，与升级无关，vite 5/6 表现一致）

## 已知限制

- vite 升级依赖 overrides 强制，vitepress 官方支持 vite 6 前需保持该配置；后续 vitepress 升级到支持 vite 6 的版本后可移除
- 真实项目全量构建耗时很长（3219 个页面），属既有问题，不在本次修复范围
