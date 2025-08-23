import { defineConfig } from 'vitepress'
import { generateSidebar } from 'vitepress-sidebar';
import viteCompression from "vite-plugin-compression";

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: '每日 AI 小故事',
  description: '根据金山每日一句使用AI生成的小故事，每日更新，提供独特阅读体验，用户可分享互动，共同打造故事社区。',
  lang: 'zh-CN',
  lastUpdated: true,
  cleanUrls: false,
  srcExclude:["故事/2025年/08月/23日/星期六_07-19-59.6e8.md"],
  sitemap: {
    hostname: 'https://story-aii.pages.dev',
    xslUrl: '/sitemap.xsl',
    xmlns: { // 修剪 XML 命名空间
      news: false, // 设为 false 可省略新闻的 XML 命名空间
      xhtml: true,
      image: false,
      video: false
    }
  },
  head: [
    ['meta', { property: 'og:title', content: '每日AI生成小故事 - 基于金山每日一句' }],
    ['meta', { property: 'og:description', content: '根据金山每日一句使用AI生成的小故事，每日更新，提供独特阅读体验，用户可分享互动，共同打造故事社区。' }],
    ['link', { rel: 'shortcut icon', href: '/favicon.ico' }],
    // ['meta', { property: 'og:image', content: 'path/to/social-media-image.jpg' }],
    // ['meta', { name: 'twitter:card', content: 'summary_large_image' }],
    ['meta', { name: 'twitter:title', content: '每日AI生成小故事 - 基于金山每日一句' }],
    ['meta', { name: 'twitter:description', content: '根据金山每日一句使用AI生成的小故事，每日更新，提供独特阅读体验，用户可分享互动，共同打造故事社区。' }],
    // ['meta', { name: 'twitter:image', content: 'path/to/social-media-image.jpg' }]
  ],
  vite: {
    plugins: [
      viteCompression({
        verbose: true,
        disable: false,
        threshold: 10240,
        algorithm: "gzip",
        ext: ".gz",
      }),
      viteCompression({
        verbose: true,
        disable: false,
        threshold: 10240,
        algorithm: "brotliCompress",
        ext: ".br",
      }),
    ],
  },
  transformHead({ assets }) {
    // 相应地调整正则表达式以匹配字体
    const myFontFile = assets.find(file => /jinkai\.\w+\.ttf/.test(file))
    if (myFontFile) {
      return [
        [
          'link',
          {
            rel: 'preload',
            href: myFontFile,
            as: 'font',
            type: 'font/ttf',
            crossorigin: ''
          }
        ]
      ]
    }
  },
  themeConfig: {
    nav:[
      {text: '神奇小故事', link: 'https://ruozhi.pages.dev/' },
    ],
    editLink: {
      "text":"编辑此页",
      pattern: 'https://github.com/Liao-Ke/everyday/edit/master/story/:path'
    },
    search: {
      provider: 'local',
      options: {
        locales: {
          root: {
            translations: {
              button: {
                buttonText: '搜索',
                buttonAriaLabel: '搜索'
              },
              modal: {
                noResultsText: '无法找到相关结果',
                resetButtonTitle: '清除查询条件',
                displayDetails: '显示详细信息',
                footer: {
                  selectText: '选择',
                  navigateText: '切换',
                  closeText: '取消'
                }
              }
            }
          }
        }
      }
    },
    outline: {
      label: '大纲',
      level: 'deep'
    },
    docFooter: {
      prev: '上一页',
      next: '下一页'
    },
    lastUpdated: {
      text: '最后更新时间'
    },
    darkModeSwitchLabel: '切换主题',
    lightModeSwitchTitle: '浅色模式',
    darkModeSwitchTitle: '深色模式',
    sidebarMenuLabel: '目录',
    returnToTopLabel: '返回顶部',
    // https://vitepress.dev/reference/default-theme-config


    sidebar: generateSidebar([{
      // VitePress Sidebar's options here...
      documentRootPath: '/story',
      scanStartPath:"词云",
      resolvePath:"/词云/",
      basePath:"/词云/",
      useTitleFromFileHeading: true,
      useTitleFromFrontmatter:true,
      collapsed: true,
    },{
      // VitePress Sidebar's options here...
      documentRootPath: '/story',
      scanStartPath:"故事",
      resolvePath:"/故事/",
      basePath:"/故事/",
      useTitleFromFileHeading: true,
      useTitleFromFrontmatter:true,
      collapsed: true,
      excludeByGlobPattern:["**/星期六_07-19-59.6e8.md"]
    }]),

    socialLinks: [
      { icon: 'github', link: 'https://github.com/Liao-Ke/everyday' }
    ]
  },
  markdown: {
    math: false,
    container: {
      tipLabel: '提示',
      warningLabel: '警告',
      dangerLabel: '危险',
      infoLabel: '信息',
      detailsLabel: '详细信息'
    }
  },
})
