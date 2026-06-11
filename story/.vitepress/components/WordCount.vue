<script setup>
import { ref } from 'vue'
import { onContentUpdated } from 'vitepress'

const stats = ref({
    chinese: 0,
    english: 0,
    readingTime: 0
})

const READING_SPEED = {
    chinese: 400,  // 中文每分钟阅读字数
    english: 250   // 英文每分钟阅读单词数
}

const calculateStats = () => {
    const contentEl = document.querySelector('.vp-doc')
    if (!contentEl) return

    const text = contentEl.textContent

    // 中文统计（汉字 + 中文标点）
    const chineseChars = text.match(/[\u4E00-\u9FA5\u3000-\u303F\uFF00-\uFFEF]/g) || []
    // 英文单词统计（排除纯数字）
    const englishWords = text.match(/\b[a-zA-Z]+\b/g) || []

    // 计算阅读时间
    const chineseTime = chineseChars.length / READING_SPEED.chinese
    const englishTime = englishWords.length / READING_SPEED.english
    const totalTime = chineseTime + englishTime

    stats.value = {
        chinese: chineseChars.length,
        english: englishWords.length,
        readingTime: Math.ceil(totalTime || 1)  // 至少显示1分钟
    }
}

onContentUpdated(() => {
    calculateStats()
})
</script>

<template>
    <div class="stats-wrapper">
        <div class="reading-stats">
            <span class="stat-item">
                <svg class="icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/><line x1="8" y1="7" x2="16" y2="7"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
                {{ stats.chinese.toLocaleString() }} 字
            </span>
            <span class="stat-item" v-if="stats.english > 0">
                <svg class="icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="4 7 4 4 20 4 20 7"/><line x1="9" y1="20" x2="15" y2="20"/><line x1="12" y1="4" x2="12" y2="20"/></svg>
                {{ stats.english.toLocaleString() }} 词
            </span>
            <span class="stat-item reading-time">
                <svg class="icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                {{ stats.readingTime }} 分钟
            </span>
        </div>
    </div>
</template>

<style scoped>
.stats-wrapper {
    width: 100%;
    display: flex;
    justify-content: flex-end;
}

.reading-stats {
    font-size: 0.75em;
    display: inline-flex;
    gap: 0.75rem;
    align-items: center;
    color: var(--vp-c-text-2);
    padding: 7px 14px;
    border-radius: 10px;
    background-color: var(--vp-c-bg-soft);
    border: 1px solid var(--vp-c-divider-light);
}

.stat-item {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    line-height: 1;
}

.icon {
    opacity: 0.7;
    flex-shrink: 0;
}

.reading-time {
    color: var(--vp-c-brand);
}

@media (max-width: 640px) {
    .reading-stats {
        font-size: 0.7em;
        gap: 0.5rem;
        padding: 5px 10px;
    }
}
</style>