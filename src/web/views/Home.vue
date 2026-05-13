<script setup>
const props = defineProps({
  useRouterLinks: {
    type: Boolean,
    default: false
  },
  leaderboardLink: {
    type: String,
    default: '/leaderboard'
  },
  docsLink: {
    type: String,
    default: 'https://github.com/kaherro/Leaderly/blob/dev/README.md'
  }
})
</script>

<template>
  <div class="container">
    <section id="home" class="hero">
      <div class="hero-left">
        <h1 class="hero-title">Лидерборд в реальном времени</h1>
        <p class="hero-description">
          Leaderly - бесплатная open-source библиотека на Python, которая позволяет разработчикам создать систему рейтинга в реальном времени.
        </p>

        <div class="buttons">
          <component
            :is="props.useRouterLinks ? 'router-link' : 'a'"
            :to="props.useRouterLinks ? props.leaderboardLink : undefined"
            :href="props.useRouterLinks ? undefined : props.leaderboardLink"
            class="btn btn-primary"
          >
            🏆 Перейти в лидерборд
          </component>
          <a :href="props.docsLink" class="btn btn-secondary">📚 Документация</a>
        </div>
      </div>

      <div class="hero-right">
        <div class="code-block">
          <div class="code-header">
            <span class="code-title">leaderboard.py</span>
          </div>
          <pre><code v-pre><span class="keyword">from</span> <span class="module">src.leaderboard</span> <span class="keyword">import</span> <span class="class-name">LeaderboardClient</span>

<span class="comment"># Создание клиента с параметрами по умолчанию</span>
<span class="var">lb</span> = <span class="class-name">LeaderboardClient</span>()

<span class="comment"># Добавление игроков</span>
<span class="var">lb</span>.<span class="method">update_score</span>(<span class="string">"alice"</span>, <span class="number">1500</span>)
<span class="var">lb</span>.<span class="method">update_score</span>(<span class="string">"bob"</span>, <span class="number">2300</span>)
<span class="var">lb</span>.<span class="method">update_score</span>(<span class="string">"charlie"</span>, <span class="number">1800</span>)
<span class="var">lb</span>.<span class="method">update_score</span>(<span class="string">"diana"</span>, <span class="number">3200</span>)

<span class="comment"># Получение счета конкретного игрока</span>
<span class="var">score</span> = <span class="var">lb</span>.<span class="method">get_score</span>(<span class="string">"alice"</span>)
<span class="method">print</span>(<span class="string">f&quot;Счет Alice: {score}&quot;</span>)  <span class="comment"># Счет Alice: 1500</span>

<span class="comment"># Получение топ-3 игроков</span>
<span class="var">top3</span> = <span class="var">lb</span>.<span class="method">get_leaderboard</span>(<span class="number">3</span>)
<span class="keyword">for</span> <span class="var">rank</span>, (<span class="var">key</span>, <span class="var">score</span>, <span class="var">tags</span>) <span class="keyword">in</span> <span class="method">enumerate</span>(<span class="var">top3</span>, <span class="number">1</span>):
    <span class="method">print</span>(<span class="string">f&quot;{rank}. {key}: {score} очков&quot;</span>)
<span class="comment"># 1. diana: 3200 очков</span>
<span class="comment"># 2. bob: 2300 очков</span>
<span class="comment"># 3. charlie: 1800 очков</span>

<span class="comment"># Обновление счета</span>
<span class="var">lb</span>.<span class="method">update_score</span>(<span class="string">"alice"</span>, <span class="number">3500</span>)  <span class="comment"># Alice теперь лидер</span>

<span class="comment"># Удаление игрока</span>
<span class="var">lb</span>.<span class="method">delete_object</span>(<span class="string">"charlie"</span>)</code></pre>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.container {
  width: 100%;
}

.hero {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f1729 0%, #1a2847 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 40px 60px;
  padding-top: 110px;
  position: relative;
  overflow: hidden;
  gap: 80px;
}

.hero::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

.hero-left {
  flex: 1;
  position: relative;
  z-index: 1;
  max-width: 800px;
  padding-left: 100px;
}

.hero-right {
  flex: 1;
  position: relative;
  z-index: 1;
  padding-left: 100px;
  padding-right: 100px;
}

.hero-title {
  font-size: 3.2rem;
  margin-bottom: 25px;
  font-weight: 700;
  line-height: 1.2;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 1.15rem;
  color: #ffffffbf;
  margin-bottom: 40px;
  line-height: 1.7;
}

.code-block {
  background: #0000004d;
  border: 1px solid #667eea4d;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px #0000004d;
}

.code-header {
  background: #667eea1a;
  padding: 12px 20px;
  border-bottom: 1px solid #667eea33;
  display: flex;
  align-items: center;
  gap: 10px;
}

.code-title {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  font-weight: 500;
  font-family: 'Courier New', monospace;
}

.code-block pre {
  padding: 20px;
  margin: 0;
  overflow-x: auto;
  font-size: 0.85rem;
  line-height: 1.6;
}

.code-block code {
  color: rgba(255, 255, 255, 0.8);
  font-family: 'Courier New', monospace;
  white-space: pre;
}

.keyword {
  color: #8fb3ff;
  font-weight: 700;
}

.module {
  color: #8be9fd;
}

.class-name {
  color: #d7aefb;
  font-weight: 700;
}

.var {
  color: #f8c98d;
}

.method {
  color: #7ee787;
}

.string {
  color: #7ee787;
}

.number {
  color: #ffb86b;
}

.comment {
  color: rgba(255, 255, 255, 0.45);
  font-style: italic;
}

.buttons {
  display: flex;
  gap: 20px;
  justify-content: flex-start;
  flex-wrap: wrap;
}

.btn {
  padding: 15px 35px;
  font-size: 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  display: inline-block;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 4px 15px #667eea66;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px #667eea99;
}

.btn-secondary {
  background: #667eea33;
  color: white;
  border: 1px solid #667eea80;
}

.btn-secondary:hover {
  background: #667eea4d;
}

@media (max-width: 1100px) {
  .hero {
    flex-direction: column;
    gap: 40px;
    padding-left: 24px;
    padding-right: 24px;
  }

  .hero-left,
  .hero-right {
    padding-left: 0;
    padding-right: 0;
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.3rem;
  }

  .hero-description {
    font-size: 1rem;
  }
}
</style>
