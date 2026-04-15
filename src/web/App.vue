<script setup>
import Header from './components/Header.vue'
</script>

<template>
  <Header :use-router-links="true" />
  <div id="app">
    <router-view />
  </div>
</template>

<style>
html, body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Source Sans Pro',
    'Helvetica Neue', sans-serif;
  background: #0f1729;
}

#app {
  margin: 0;
  padding: 0;
}
</style>
