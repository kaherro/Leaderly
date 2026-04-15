import { createRouter, createWebHistory } from 'vue-router'
import Home from './views/Home.vue'
import Leaderboard from './views/Leaderboard.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    props: {
      useRouterLinks: true
    }
  },
  {
    path: '/leaderboard',
    name: 'Leaderboard',
    component: Leaderboard
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
