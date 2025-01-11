import DefaultTheme from  'vitepress/theme-without-fonts'


import MyLayout from './MyLayout.vue'
import type { Theme as ThemeConfig } from 'vitepress'
import { h } from 'vue'

import mediumZoom from 'medium-zoom';
import { onMounted, watch, nextTick } from 'vue';
import { useRoute } from 'vitepress';
import "./styles/my.css"

import { 
  NolebaseGitChangelogPlugin 
} from '@nolebase/vitepress-plugin-git-changelog/client'
import '@nolebase/vitepress-plugin-git-changelog/client/style.css'
export const Theme: ThemeConfig = {
  extends: DefaultTheme,
  setup() {
    const route = useRoute();
    const initZoom = () => {
      // mediumZoom('[data-zoomable]', { background: 'var(--vp-c-bg)' }); // 默认
      mediumZoom(".main p img", { background: "var(--vp-c-bg)" }); // 不显式添加{data-zoomable}的情况下为所有图像启用此功能
      // mediumZoom(".main img")
    };
    onMounted(() => {
      initZoom(); 
    }); 
    watch(  
      () => route.path,
      () => nextTick(() => initZoom())
    );
  },
  Layout: () => {
    return h(DefaultTheme.Layout, null, {
      // 其他的配置...
      'not-found':()=>h(MyLayout)
    })
  },
  enhanceApp({ app }) {
    app.use(NolebaseGitChangelogPlugin,{
      commitsRelativeTime: true
    })  
  },
}
export default Theme