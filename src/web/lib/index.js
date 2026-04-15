import Header from '../components/Header.vue'
import Home from '../views/Home.vue'
import Leaderboard from '../views/Leaderboard.vue'

const install = (app) => {
  app.component('LeaderlyHeader', Header)
  app.component('LeaderlyHome', Home)
  app.component('LeaderlyLeaderboard', Leaderboard)
}

export { Header, Home, Leaderboard, install }

export default {
  install
}
