<script setup>
import logoImage from '../assets/logo/logo.png'
</script>

<template>
  <header class="header">
    <div class="header-content">
      <div class="logo">
        <img :src="logoImage" alt="Leaderly logo" class="logo-image" />
        <h1 class="logo-title">Leaderly</h1>
      </div>
      
      <nav class="nav">
        <router-link to="/" class="nav-link">Главная</router-link>
        <router-link to="/leaderboard" class="nav-link">Лидерборд</router-link>
        <a href="#docs" class="nav-link">Документация</a>
        <a href="https://github.com/kaherro/Leaderly/tree/main" target="_blank" class="nav-link">GitHub</a>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: #0f172afa;
  color: white;
  padding-top: 0;
  padding-bottom: 1px;
  z-index: 1000;
  box-shadow: 0 2px 15px #0000004d;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0px;
  margin-right: auto;
  margin-left: -185px;
}

.logo-image {
  width: 72px;
  height: 72px;
  object-fit: contain;
  display: block;
}

.logo-title {
  margin: 0;
  font-size: 2.5rem;
  font-weight: 620;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav {
  display: flex;
  gap: 30px;
  align-items: center;
}

.nav-link {
  color: #ffffffcc;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.3s ease;
  font-weight: 500;
}

.nav-link:hover {
  color: white;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 15px;
  }

  .nav {
    flex-wrap: wrap;
    gap: 15px;
    justify-content: center;
  }

  .nav-link {
    font-size: 0.9rem;
  }

  .logo-image {
    width: 64px;
    height: 64px;
  }

  .logo-title {
    font-size: 1.4rem;
  }
}
</style>
