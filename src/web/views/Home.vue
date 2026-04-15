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
    default: '#docs'
  }
})
</script>

<template>
  <div class="container">
    <section id="home" class="hero">
      <div class="hero-left">
        <h1 class="hero-title">Лидербоард в реальном времени</h1>
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
            <span class="code-title">leaderly.py</span>
          </div>
          <pre><code></code></pre>
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
}

.code-block .keyword {
  color: #667eea;
  font-weight: 600;
}

.code-block .class {
  color: #b8a4ff;
}

.code-block .var {
  color: #e8d4ff;
}

.code-block .param {
  color: #eaa7ff;
}

.code-block .string {
  color: #76d47f;
}

.code-block .number {
  color: #ffa878;
}

.code-block .method {
  color: #76d4d4;
}

.code-block .property {
  color: #ffc371;
}

.stats {
  display: flex;
  gap: 30px;
  margin-top: 50px;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-number {
  font-size: 1.4rem;
  font-weight: 700;
  color: #667eea;
}

.stat-label {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
}

.tagline {
  font-size: 1.3rem;
  margin-bottom: 40px;
  opacity: 0.95;
  font-weight: 300;
  line-height: 1.6;
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
  background: rgba(102, 126, 234, 0.3);
  border-color: rgba(102, 126, 234, 0.8);
  transform: translateY(-2px);
}

.scroll-indicator {
  margin-top: 60px;
  animation: bounce 2s infinite;
}

.scroll-button {
  color: white;
  text-decoration: none;
  font-size: 0.9rem;
  opacity: 0.8;
  transition: opacity 0.3s ease;
  display: inline-block;
}

.scroll-button:hover {
  opacity: 1;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@media (max-width: 1200px) {
  .hero {
    flex-direction: column;
    gap: 40px;
    padding: 40px 30px;
    padding-top: 110px;
  }

  .hero-left {
    max-width: 100%;
    padding-left: 0;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .code-block {
    max-width: 100%;
  }

  .hero-right {
    padding-left: 0;
  }
}
</style>
