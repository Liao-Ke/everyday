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
  <div class="reading-stats">
    <div class="stat-group">
        本文大概有
      <span class="stat-item">
        {{ stats.chinese.toLocaleString() }} 个字
      </span>
      <span 
        class="stat-item"
        v-if="stats.english > 0"
      >
        {{ stats.english.toLocaleString() }} 个单词
      </span>
    </div>
    <span class="stat-item reading-time">
      阅读大概要 {{ stats.readingTime }} 分钟
    </span>
  </div>
</template>

<style>
.reading-stats {
  color: #666;
  font-size: 0.75em;
  border-top: 1px solid #eee;
  padding-top: 0.8rem;
  margin: 1.5rem 0 0;
  text-align: right;
}

/* .stat-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
} */

.stat-item {
  display: block;
  /* align-items: center; */
  /* padding: 0.2rem 0.6rem; */
  /* background: #f5f5f5;
  border-radius: 4px; */
}

/* .reading-time {
  margin-top: 0.6rem;
  display: block;
  background: none;
  padding-left: 0;
} */

/* @media (min-width: 640px) {
  .reading-stats {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .reading-time {
    margin-top: 0;
    background: #f5f5f5;
    padding: 0.2rem 0.6rem;
  }
} */
</style>