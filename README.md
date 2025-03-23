# 📖 每日故事 | Everyday Story Generator
**🌠 用AI为金山每日一句编织奇幻物语**  
*"每个金句都值得被赋予生命"——欢迎来到文学与AI的奇妙交汇点*

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/Liao-Ke/everyday?tab=MIT-1-ov-file)
[![每日故事在线预览](https://img.shields.io/badge/🌏%20在线体验-点击访问-ff69b4)](https://story.maozi.io/)

## ✨ 项目特色
- **智能续写引擎**：基于DeepSeek/智谱清言双AI引擎，将金句拓展成跌宕起伏的微型小说
- **时空胶囊式存储**：采用`年/月/日`三维归档系统，自动生成时光隧道般的故事索引
- **沉浸式文档站点**：内置精美Vitepress知识库，支持实时故事画廊浏览（[在线预览](https://story.maozi.io/)）
- **云端自动化**：GitHub Actions每日定时生成故事，打造永不间断的文学瀑布流

## 🚀 快速开始
### 获取故事宝箱
```bash
git clone https://github.com/Liao-Ke/everyday.git && cd everyday
```

### 激活魔法药剂（Python环境）
```bash
conda create -n storygen python=3.11 && conda activate storygen
pip install -r requirements.txt
```

### 配置魔法密钥
1. 获取AI通行证：
   - [DeepSeek API密钥](https://platform.deepseek.com/api_keys)
   - [智谱清言API密钥](https://bigmodel.cn/usercenter/proj-mgmt/apikeys)
   - [Kimi API密钥](https://platform.moonshot.cn/console/api-keys)

2. 创建魔法卷轴（.env文件）：
```env
API_KEY=您的智谱密钥
API_KEY_DS=您的DeepSeek密钥
API_KEY_KIMI=您的Kimi密钥
```

### 启动故事熔炉
```bash
python main.py  # 见证金句蜕变为完整故事的奇迹时刻！
```

## 🌌 故事宇宙管理台
### 启动时空观测站
```bash
npm install && npm run docs:dev
```
在[http://localhost:5173](http://localhost:5173)穿越故事维度

### 构建永恒档案馆
```bash
npm run docs:build && npm run docs:preview
```

## 📂 时空档案库结构
```
everyday/
├── story/
│   ├── 2025年/                # 时间维度
│   │   ├── 01月/              # 空间维度
│   │   │   └── 05日/          # 故事发生的精确坐标
│   ├── images/                # 视觉记忆博物馆
│   └── .vitepress/            # 故事展示魔方
└── .github/workflows/         # 自动化时光机器
```
*提示：完整时空拓扑图请查阅[三维目录结构](#)*

## 🤝 成为故事编织者
我们欢迎所有形式的艺术共创：
- 提交新的[故事生成算法](https://github.com/Liao-Ke/everyday/issues)
- 优化[时空档案馆主题](story/.vitepress/theme)
- 创作[配套视觉元素](story/images/)

## 📜 智慧传承协议
本项目遵循[MIT开放公约](https://github.com/Liao-Ke/everyday?tab=MIT-1-ov-file)，您可自由使用、修改和分享这些故事结晶，唯需保留原创魔法印记。

---

**🌌 特别鸣谢**
- 智慧之源：[金山词霸每日一句](https://open.iciba.com/index.php?c=wiki)
- 灵感催化剂：[DeepSeek](https://platform.deepseek.com) & [智谱AI](https://bigmodel.cn) & [Kimi](https://platform.moonshot.cn)
- 时空建筑师：[Vitepress](https://vitepress.dev)
- 自动化工程师：[GitHub Actions](https://github.com/features/actions)
- 魔法绽放平台：[帽子云](https://maoziyun.com/)

*让每个平凡的日子，都有不平凡的故事✨*
