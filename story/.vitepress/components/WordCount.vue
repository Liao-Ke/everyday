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
                <span class="icon">📝</span>
                {{ stats.chinese.toLocaleString() }} 个字
            </span>
            <span class="stat-item" v-if="stats.english > 0">
                <span class="icon">🔠</span>
                {{ stats.english.toLocaleString() }} 个单词
            </span>
            <span class="stat-item reading-time">
                <span class="icon">⏱️</span>
                {{ stats.readingTime }}分钟
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
    font-size: 0.9em;
    opacity: 0.8;
}

.reading-time {
    color: var(--vp-c-brand);
}

/* 移动端适配 */
/* @media (max-width: 640px) {
  .reading-stats {
    font-size: 0.8em;
    gap: 0.5rem;
    padding: 0.2rem 0.4rem;
  }
  
  .icon {
    font-size: 0.85em;
  }
} */
</style>