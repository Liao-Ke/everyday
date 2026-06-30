import { defineConfig } from 'vitepress'
import { generateSidebar } from 'vitepress-sidebar';
import viteCompression from "vite-plugin-compression";

export default defineConfig({
    title: '每日 AI 小故事',
    description: '根据金山每日一句使用AI生成的小故事，每日更新，提供独特阅读体验。',
    lang: 'zh-CN',
    lastUpdated: true,
    cleanUrls: false,
    srcExclude: ["故事/2025年/08月/23日/星期六_07-19-59.6e8.md", "故事/2025年/08月/24日/星期日_07-20-05.c9a.md"],
    sitemap: {
        hostname: 'https://story-aii.pages.dev',
        xslUrl: '/sitemap.xsl',
        xmlns: {
            news: false,
            xhtml: true,
            image: false,
            video: false
        }
    },
    head: [
        ['meta', { property: 'og:title', content: '每日AI生成小故事 - 基于金山每日一句' }],
        ['meta', { property: 'og:description', content: '根据金山每日一句使用AI生成的小故事，每日更新，提供独特阅读体验。' }],
        ['meta', { property: 'og:image', content: '/favicon.ico' }],
        ['link', { rel: 'shortcut icon', href: '/favicon.ico' }],
        ['meta', { name: 'twitter:title', content: '每日AI生成小故事 - 基于金山每日一句' }],
        ['meta', { name: 'twitter:description', content: '根据金山每日一句使用AI生成的小故事，每日更新，提供独特阅读体验。' }],
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
        nav: [
            { text: '神奇小故事', link: 'https://ruozhi.pages.dev/' },
        ],
        editLink: {
            "text": "编辑此页",
            pattern: 'https://github.com/Liao-Ke/everyday/edit/master/story/:path'
        },
        search: {
            provider: 'algolia',
            options: {
                appId: process.env.ALGOLIA_APP_ID || '',
                apiKey: process.env.ALGOLIA_API_KEY || '',
                indexName: process.env.ALGOLIA_INDEX_NAME || '',
                locales: {
                    zh: {
                        placeholder: '搜索文档',
                        translations: {
                            button: {
                                buttonText: '搜索',
                                buttonAriaLabel: '搜索'
                            },
                            modal: {
                                searchBox: {
                                    resetButtonTitle: '清除查询条件',
                                    cancelButtonText: '取消'
                                },
                                startScreen: {
                                    recentSearchesTitle: '搜索历史',
                                    noRecentSearchesText: '没有搜索历史'
                                },
                                errorScreen: {
                                    titleText: '无法获取结果',
                                    helpText: '你可能需要检查你的网络连接。'
                                },
                                footer: {
                                    selectText: '选择',
                                    navigateText: '切换',
                                    closeText: '关闭'
                                },
                                noResultsScreen: {
                                    noResultsText: '无法找到相关结果'
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

        sidebar: generateSidebar([{
            documentRootPath: '/story',
            scanStartPath: "词云",
            resolvePath: "/词云/",
            basePath: "/词云/",
            useTitleFromFileHeading: true,
            useTitleFromFrontmatter: true,
            collapsed: true,
        }, {
            documentRootPath: '/story',
            scanStartPath: "故事",
            resolvePath: "/故事/",
            basePath: "/故事/",
            useTitleFromFileHeading: true,
            useTitleFromFrontmatter: true,
            collapsed: true,
            excludeByGlobPattern: ["**/星期六_07-19-59.6e8.md", "**/星期日_07-20-05.c9a.md"]
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
