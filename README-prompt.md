根据提供的内容，写一份 Github 仓库的 自述文件 。要生动有趣（保证专业性）并使用合理的结构（格式），可以适当补充细节或调整内容。


项目名称：everyday 每日故事
项目介绍：根据金山每日一句，借助人工智能技术生成了一个小故事。这个小故事的诞生源于对金山每日一句的深入思考和创意发挥。通过 AI 的强大能力，将金山每日一句中的智慧和情感进行了拓展和延伸，从而打造出了一个生动有趣、富有内涵的小故事。
项目主页：https://story.maozi.io/
项目许可：[MIT 许可证](https://github.com/Liao-Ke/everyday?tab=MIT-1-ov-file)
项目部分目录结构：
├── .env
├── .gitattributes
├── .github
│   └── workflows
│       └── main.yml
├── .gitignore
├── LICENSE
├── main.py
├── package.json
├── package-lock.json
├── README.md
├── README-special.md
├── requirements.txt
├── story
│   ├── 2025年
│   │   ├── 01月
│   │   │   ├── 05日
│   │   │   │   └── 星期日 17:09:31.md
│   │   │   ├── 06日
│   │   │   │   └── 星期一 07:16:59.md
│   │   │   ├── 07日
│   │   │   │   └── 星期二 07:18:01.md
│   │   │   ├── 08日
│   │   │   │   └── 星期三 07:17:17.md
│   │   │   ├── 09日
│   │   │   │   └── 星期四 07:17:28.md
│   │   │   ├── 10日
│   │   │   │   └── 星期五 07:18:33.md
│   │   │   ├── 11日
│   │   │   │   └── 星期六 07:19:45.md
│   │   │   ├── 12日
│   │   │   │   └── 星期日 07:19:08.md
│   │   │   ├── 13日
│   │   │   │   └── 星期一 07:16:43.md
│   │   │   ├── 14日
│   │   │   │   └── 星期二 07:16:54.md
│   │   │   ├── 15日
│   │   │   │   └── 星期三 07:16:48.md
│   │   │   ├── 16日
│   │   │   │   └── 星期四 07:17:20.md
│   │   │   ├── 17日
│   │   │   │   └── 星期五 07:18:39.md
│   │   │   ├── 18日
│   │   │   │   └── 星期六 07:17:32.md
│   │   │   ├── 19日
│   │   │   │   └── 星期日 07:16:32.md
│   │   │   ├── 20日
│   │   │   │   └── 星期一 07:18:14.md
│   │   │   ├── 21日
│   │   │   │   └── 星期二 07:16:26.md
│   │   │   ├── 22日
│   │   │   │   └── 星期三 07:19:06.md
│   │   │   ├── 23日
│   │   │   │   └── 星期四 07:19:29.md
│   │   │   ├── 24日
│   │   │   │   └── 星期五 07:17:32.md
│   │   │   ├── 25日
│   │   │   │   └── 星期六 07:19:24.md
│   │   │   ├── 26日
│   │   │   │   └── 星期日 07:17:17.md
│   │   │   ├── 27日
│   │   │   │   └── 星期一 07:16:11.md
│   │   │   ├── 28日
│   │   │   │   └── 星期二 07:16:59.md
│   │   │   ├── 29日
│   │   │   │   └── 星期三 07:16:48.md
│   │   │   ├── 30日
│   │   │   │   └── 星期四 07:16:55.md
│   │   │   └── 31日
│   │   │       └── 星期五 07:20:29.md
│   │   └── 02月
│   │       ├── 01日
│   │       │   └── 星期六 07:16:21.md
│   │       ├── 02日
│   │       │   └── 星期日 08:07:40.md
│   │       ├── 03日
│   │       │   └── 星期一 07:15:54.md
│   │       ├── 04日
│   │       │   └── 星期二 07:16:49.md
│   │       ├── 05日
│   │       │   └── 星期三 07:17:09.md
│   │       ├── 06日
│   │       │   └── 星期四 07:19:54.md
│   │       ├── 07日
│   │       │   └── 星期五 07:22:05.md
│   │       ├── 08日
│   │       │   ├── 星期六 07:20:37.md
│   │       │   └── 星期六 07:21:32.md
│   │       ├── 09日
│   │       │   ├── 星期日 07:18:22.md
│   │       │   └── 星期日 07:19:18.md
│   │       ├── 10日
│   │       │   ├── 星期一 07:17:54.md
│   │       │   └── 星期一 07:19:01.md
│   │       ├── 11日
│   │       │   ├── 星期二 07:18:33.md
│   │       │   └── 星期二 07:19:44.md
│   │       ├── 12日
│   │       │   ├── 星期三 07:18:16.md
│   │       │   └── 星期三 07:19:25.md
│   │       ├── 13日
│   │       │   ├── 星期四 07:16:48.md
│   │       │   └── 星期四 07:17:54.md
│   │       ├── 14日
│   │       │   ├── 星期五 07:18:21.md
│   │       │   └── 星期五 07:19:28.md
│   │       └── 15日
│   │           ├── 星期六 07:17:38.md
│   │           └── 星期六 07:18:40.md
│   ├── images
│   │   ├── 0263205a43104d25821992b6e37f6356.jpg
│   │   ├── 03b39cbf79094bd4bc25688cc2ecbc3a.jpg
│   │   ├── 0964520cf6d345ac8d4124b8f468d179.jpg
│   │   ├── 0ce04ffcb8e745839299243345229978.jpg
│   │   ├── 0f047b7b2b4e45409d355a5961be0889.jpg
│   │   ├── 15867735f0454bb284038724ec522055.jpg
│   │   ├── 15d82c44d84e40f88fc9f0627fa3ad47.jpg
│   │   ├── 1f1e84a31f554254aaf4569aff2736c6.jpg
│   │   ├── 207c2a15c005494fb135465f65e55776.jpg
│   │   ├── 2194c57a872b4b98a575b48b1bbf9c99.jpg
│   │   ├── 26fd85158954482cbd70440d4a50b7a9.jpg
│   │   ├── 2c59bdcd49ad41a8911f0779adbfffa1.jpg
│   │   ├── 2d0b1fb0a193485ab3fb2b0f87725472.jpg
│   │   ├── 386f647794434e588e959a7bb4a4e5aa.jpg
│   │   ├── 3b5b92e6db7f4ec2b9c31b4547bc8b9e.jpg
│   │   ├── 3f819ea7cd464413a1fd5879a4d384fc.jpg
│   │   ├── 415f2f9f8bce429c8bb30fbef8db6f26.jpg
│   │   ├── 4a824156fbef41bab3c7e6f7301e383a.jpg
│   │   ├── 4d21e8ee347d43f6a358b31c054046cf.jpg
│   │   ├── 587400a1f06e4ca281909b6f7c269030.jpg
│   │   ├── 5aa9f1ed3bf9491181207615fcfd56a1.jpg
│   │   ├── 5f5b488a130b4d21951bf159d6249cb5.jpg
│   │   ├── 622001ae151e4cc880857cb000496bfa.jpg
│   │   ├── 697c35c822c642708f51554b336fae7f.jpg
│   │   ├── 76801ce0ffc24283bdc8bcda69a13fda.jpg
│   │   ├── 81ff42861f0b4aec86adf189adaa5548.jpg
│   │   ├── 8435332904474ea897f12ffca2c0b486.jpg
│   │   ├── 898ddcbd3fbb47208c28fb12e32ec88f.jpg
│   │   ├── 9ad36cc3e57b46f6812d7978411cdf82.jpg
│   │   ├── 9ba1d27bb7df4db78dbb117528a3adf4.jpg
│   │   ├── 9c357fd49a5248df8739521bc9e917da.jpg
│   │   ├── a7504210cbdb4d68af1d327068065588.jpg
│   │   ├── b708100c55274974b9eb6c237eb76ac8.jpg
│   │   ├── bd3b6282937d497297fbfb8db75e1af6.jpg
│   │   ├── d9c3d2d10f364c2c85cc44d047a9d607.jpg
│   │   ├── db6b86eb44be4f488d09a16a4ec56e1d.jpg
│   │   ├── dba44462b3df4ec79ce757add49253fe.jpg
│   │   ├── df6d6bffff9d4621aaa0745be0969f15.jpg
│   │   ├── e08ab0f05b4047c8b2a2d5eb40f3fb50.jpg
│   │   ├── e640d24d24144f39a51ea5882e846ddc.jpg
│   │   ├── f4ee3ff27d0940eb96205017077f02cf.jpg
│   │   └── f53bec6e683e4efbb24106bc6d3e5a15.jpg
│   ├── index.md
│   └── .vitepress
│       ├── components
│       │   └── ReasoningChainRenderer.vue
│       ├── config.mts
│       └── theme
│           ├── fonts
│           │   └── jinkai.ttf
│           ├── index.ts
│           ├── Layout.vue
│           ├── MyLayout.vue
│           └── styles
│               └── my.css
└── tsconfig.json
金山每日一句：https://open.iciba.com/index.php?c=wiki

克隆仓库：
git clone https://github.com/Liao-Ke/everyday.git

使用Python虚拟环境（可选）：
conda create -n everyday python=3.11
conda activate everyday

安装Python依赖：
python install -r requirements.txt

获取 AI API密钥：
DeepSeek：https://platform.deepseek.com/api_keys
智谱清言：https://bigmodel.cn/usercenter/proj-mgmt/apikeys
创建.env文件：
API_KEY=<智谱清言 API Key>
API_KEY_DS=<DeepSeek API Key>

生成故事：
python main.py

预览故事：

安装 依赖 ：
npm install

开发预览：
npm run docs:dev

构建：
npm run docs:build

构建预览：
npm run docs:preview