import { defineConfig } from 'vitepress'
import { generateSidebar } from 'vitepress-sidebar';
import {
  GitChangelog,
  GitChangelogMarkdownSection,
} from '@nolebase/vitepress-plugin-git-changelog/vite'
// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "每日故事",
  description: "根据金山每日一句使用AI生成的小故事",
  lang: 'zh-CN',
  lastUpdated: true,
  cleanUrls: false,
  vite: {
    plugins: [
      GitChangelog({
        // 填写在此处填写您的仓库链接
        repoURL: () => 'https://github.com/Liao-Ke/everyday',
      }),
      GitChangelogMarkdownSection({
        sections: {
          disableContributors: true
        }
      }),
    ],
  },
  themeConfig: {
    search: {
      provider: 'local',
      options: {
        locales: {
          root: {
            translations: {
              button: {
                buttonText: '搜索文档',
                buttonAriaLabel: '搜索文档'
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


    sidebar: generateSidebar({
      // VitePress Sidebar's options here...
      documentRootPath: '/story',
      useTitleFromFileHeading: true,
      collapsed: true,
    }),

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
