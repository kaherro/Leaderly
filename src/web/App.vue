<script setup>
import { ref } from 'vue'

const message = ref('Welcome to Leaderly!')
</script>

<template>
  <div id="app">
    <h1>{{ message }}</h1>
    <p>vue project is ready!</p>
  </div>
</template>

<style scoped>
h1 {
  color: #42b983;
}
</style>
