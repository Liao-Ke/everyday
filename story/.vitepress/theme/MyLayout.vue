<!--.vitepress/theme/MyLayout.vue-->
<script setup>
// import DefaultTheme from 'vitepress/theme'
import { useData } from 'vitepress'
import { withBase } from 'vitepress'
// import { useLangs } from 'vitepress'

const { theme } = useData()
// const { currentLang } = useLangs()

// const { Layout } = DefaultTheme
</script>

<template>
      <div class="NotFound">
    <p class="code">{{ theme.notFound?.code ?? '404' }}</p>
    <h1 class="title">{{ theme.notFound?.title ?? '找不到网页' }}</h1>
    <div class="divider" />
    <blockquote class="quote">
      {{
        theme.notFound?.quote ??
        "但如果你不改变方向，如果你继续寻找，你最终可能会回到原来的位置。"
      }}
    </blockquote>

    <div class="action">
      <a
        class="link"
        :href="withBase('/')"
        :aria-label="theme.notFound?.linkLabel ?? '回家'"
      >
        {{ theme.notFound?.linkText ?? '带我回家' }}
      </a>
    </div>
  </div>
</template>

<style scoped>

.NotFound {
  padding: 64px 24px 96px;
  text-align: center;
}

@media (min-width: 768px) {
  .NotFound {
    padding: 96px 32px 168px;
  }
}

.code {
  line-height: 64px;
  font-size: 64px;
  font-weight: 600;
}

.title {
  padding-top: 12px;
  letter-spacing: 2px;
  line-height: 20px;
  font-size: 20px;
  font-weight: 700;
}

.divider {
  margin: 24px auto 18px;
  width: 64px;
  height: 1px;
  background-color: var(--vp-c-divider);
}

.quote {
  margin: 0 auto;
  max-width: 256px;
  font-size: 14px;
  font-weight: 500;
  color: var(--vp-c-text-2);
}

.action {
  padding-top: 20px;
}

.link {
  display: inline-block;
  border: 1px solid var(--vp-c-brand-1);
  border-radius: 16px;
  padding: 3px 16px;
  font-size: 14px;
  font-weight: 500;
  color: var(--vp-c-brand-1);
  transition:
    border-color 0.25s,
    color 0.25s;
}

.link:hover {
  border-color: var(--vp-c-brand-2);
  color: var(--vp-c-brand-2);
}
</style>
