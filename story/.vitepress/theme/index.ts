import DefaultTheme from 'vitepress/theme-without-fonts'

import type { Theme as ThemeConfig } from 'vitepress'

import mediumZoom from 'medium-zoom';
import { onMounted, watch, nextTick } from 'vue';
import { useRoute } from 'vitepress';
import "./styles/my.css"
import Layout from './Layout.vue';

import ReasoningChainRenderer from '../components/ReasoningChainRenderer.vue'
import WordCount from '../components/WordCount.vue'

export const Theme: ThemeConfig = {
    extends: DefaultTheme,
    setup() {
        const route = useRoute();
        const initZoom = () => {
            mediumZoom(".main p img", { background: "var(--vp-c-bg)" });
        };
        onMounted(() => {
            initZoom();
        });
        watch(
            () => route.path,
            () => nextTick(() => initZoom())
        );
    },
    Layout: Layout,

    enhanceApp({ app }) {
        app.component('ReasoningChainRenderer', ReasoningChainRenderer)
        app.component('WordCount', WordCount)
    },
}
export default Theme