<script setup>
import { ref, computed } from 'vue'

const variables = ref([
  { name: 'Победы', key: 'wins' },
  { name: 'Поражения', key: 'losses' },
])

const scoreFormula = ref('wins * 100 - losses * 50')

const showSettings = ref(false)

const newVariable = ref({ name: '', key: '' })

const leaderboardData = ref([
  { rank: 1, userId: 'user_1', username: 'usr1', wins: 50, losses: 5},
  { rank: 2, userId: 'user_2', username: 'usr2', wins: 45, losses: 10},
  { rank: 3, userId: 'user_3', username: 'usr3', wins: 40, losses: 15},
  { rank: 4, userId: 'user_4', username: 'usr4', wins: 35, losses: 20},
  { rank: 5, userId: 'user_5', username: 'usr5', wins: 30, losses: 25},
  { rank: 6, userId: 'user_6', username: 'usr6', wins: 25, losses: 30},
  { rank: 7, userId: 'user_7', username: 'usr7', wins: 20, losses: 35},
  { rank: 8, userId: 'user_8', username: 'usr8', wins: 15, losses: 40},
  { rank: 9, userId: 'user_9', username: 'usr9', wins: 10, losses: 45},
  { rank: 10, userId: 'user_10', username: 'usr10', wins: 5, losses: 50},
])

const availableVariableKeys = computed(() => variables.value.map((variable) => variable.key).filter(Boolean))

const normalizeVariableKey = (index) => {
  const variable = variables.value[index]
  if (!variable) return

  const normalizedKey = variable.key
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '_')
    .replace(/[^a-z0-9_]/g, '')

  if (!normalizedKey) {
    variable.key = ''
    return
  }

  const duplicateIndex = variables.value.findIndex(
    (item, itemIndex) => item.key === normalizedKey && itemIndex !== index
  )

  variable.key = duplicateIndex !== -1 ? `${normalizedKey}_${index + 1}` : normalizedKey
}

const ensureUserVariableValue = (key) => {
  leaderboardData.value = leaderboardData.value.map((user) => {
    if (Object.prototype.hasOwnProperty.call(user, key)) {
      return user
    }

    return {
      ...user,
      [key]: 0
    }
  })
}

const addVariable = () => {
  const name = newVariable.value.name.trim()
  const key = newVariable.value.key
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '_')
    .replace(/[^a-z0-9_]/g, '')

  if (name && key && !variables.value.some((variable) => variable.key === key)) {
    variables.value.push({ name, key })
    ensureUserVariableValue(key)
    newVariable.value = { name: '', key: '' }
  }
}

const removeVariable = (index) => {
  variables.value.splice(index, 1)
}

const compiledFormula = computed(() => {
  const expression = scoreFormula.value.trim()

  if (!expression) {
    return null
  }

  try {
    return new Function(...availableVariableKeys.value, `return ${expression}`)
  } catch {
    return null
  }
})

const formulaError = computed(() => {
  if (!scoreFormula.value.trim()) {
    return 'Введите формулу для подсчёта очков'
  }

  if (!compiledFormula.value) {
    return 'Формула содержит синтаксическую ошибку'
  }

  return ''
})

const calculateBaseScore = (user) => {
  if (!compiledFormula.value) {
    return 0
  }

  try {
    const values = availableVariableKeys.value.map((key) => Number(user[key] ?? 0))
    const rawScore = compiledFormula.value(...values)
    return Number.isFinite(Number(rawScore)) ? Math.round(Number(rawScore)) : 0
  } catch {
    return 0
  }
}

const leaderboardRows = computed(() => {
  const rows = leaderboardData.value.map((user) => {
    const baseScore = calculateBaseScore(user)

    return {
      ...user,
      computedScore: baseScore
    }
  })

  return rows
    .sort((firstUser, secondUser) => secondUser.computedScore - firstUser.computedScore)
    .map((user, index) => ({
      ...user,
      rank: index + 1
    }))
})


const gridColumns = computed(() => {
  const varColumns = variables.value.map(() => '120px').join(' ')
  return `100px 1fr 150px ${varColumns}`
})

</script>

<template>
  <div class="container">
    <section class="leaderboard-section">
      <div class="leaderboard-header">
        <h1 class="leaderboard-title">🏆 Таблица лидеров</h1>
        <p class="leaderboard-description">
          Рейтинг обновляется в реальном времени
        </p>
        <button @click="showSettings = !showSettings" class="settings-btn">
          ⚙️ {{ showSettings ? 'Скрыть настройки' : 'Настройки' }}
        </button>
      </div>

      <div v-if="showSettings" class="settings-panel">
        <div class="settings-section">
          <h3 class="settings-title">Формула подсчета очков</h3>
          <input 
            v-model="scoreFormula" 
            type="text" 
            class="formula-input"
            placeholder="Например: wins * 100 - losses * 50"
          />
          <p class="settings-hint">Используйте ключи переменных из списка ниже: {{ availableVariableKeys.join(', ') || 'нет переменных' }}</p>
          <p v-if="formulaError" class="settings-error">{{ formulaError }}</p>
        </div>

        <div class="settings-section">
          <h3 class="settings-title">Переменные для подсчета</h3>
          <div class="variables-list">
            <div v-for="(variable, index) in variables" :key="index" class="variable-item">
              <input
                v-model="variable.name"
                type="text"
                class="variable-inline-input"
                placeholder="Название"
              />
              <input
                v-model="variable.key"
                type="text"
                class="variable-inline-input variable-inline-key"
                placeholder="key"
                @blur="normalizeVariableKey(index)"
              />
              <button @click="removeVariable(index)" class="remove-btn">✕</button>
            </div>
          </div>
          
          <div class="add-variable">
            <input 
              v-model="newVariable.name" 
              type="text" 
              class="variable-input"
              placeholder="Название (например: Победы)"
            />
            <input 
              v-model="newVariable.key" 
              type="text" 
              class="variable-input"
              placeholder="Ключ (например: wins)"
            />
            <button @click="addVariable" class="add-btn">+ Добавить</button>
          </div>
        </div>
      </div>

      <div class="leaderboard-container">
        <div class="leaderboard-table">
          <div class="table-header" :style="{ gridTemplateColumns: gridColumns }">
            <div class="header-cell rank-cell">Место</div>
            <div class="header-cell user-cell">Пользователь</div>
            <div class="header-cell score-cell">Очки</div>
            <div v-for="(variable, variableIndex) in variables" :key="`${variable.key}-${variableIndex}`" class="header-cell var-cell">
              {{ variable.name }}
            </div>
          </div>

          <div class="table-body">
            <div 
              v-for="user in leaderboardRows" 
              :key="user.userId"
              class="table-row"
              :class="{ 'top-three': user.rank <= 3 }"
              :style="{ gridTemplateColumns: gridColumns }"
            >
              <div class="body-cell rank-cell">
                <span class="rank-badge" :class="'rank-' + user.rank">
                  {{ user.rank }}
                </span>
              </div>
              <div class="body-cell user-cell">
                <div class="user-info">
                  <div class="user-avatar">
                    {{ user.username.charAt(0).toUpperCase() }}
                  </div>
                  <span class="username">{{ user.username }}</span>
                </div>
              </div>
              <div class="body-cell score-cell">
                <span class="score">{{ user.computedScore.toLocaleString() }}</span>
              </div>
              <div v-for="(variable, variableIndex) in variables" :key="`${variable.key}-${variableIndex}`" class="body-cell var-cell">
                <span class="var-value">{{ user[variable.key] }}</span>
              </div>
            </div>
          </div>
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

.leaderboard-section {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f1729 0%, #1a2847 100%);
  color: white;
  padding: 40px 60px;
  padding-top: 110px;
  position: relative;
  overflow: hidden;
}

.leaderboard-section::before {
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

.leaderboard-header {
  text-align: center;
  margin-bottom: 50px;
  position: relative;
  z-index: 1;
}

.leaderboard-title {
  font-size: 3rem;
  margin-bottom: 15px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.leaderboard-description {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.7);
}

.settings-btn {
  margin-top: 16px;
  border: 1px solid rgba(102, 126, 234, 0.5);
  background: rgba(102, 126, 234, 0.15);
  color: rgba(255, 255, 255, 0.95);
  padding: 10px 18px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.settings-btn:hover {
  background: rgba(102, 126, 234, 0.3);
}

.settings-panel {
  max-width: 1000px;
  margin: 0 auto 24px;
  padding: 20px;
  background: rgba(0, 0, 0, 0.28);
  border: 1px solid rgba(102, 126, 234, 0.25);
  border-radius: 12px;
  position: relative;
  z-index: 1;
}

.settings-section {
  margin-bottom: 20px;
}

.settings-section:last-child {
  margin-bottom: 0;
}

.settings-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.formula-input,
.variable-input,
.variable-inline-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(102, 126, 234, 0.35);
  border-radius: 8px;
  padding: 10px 12px;
  color: rgba(255, 255, 255, 0.95);
}

.formula-input:focus,
.variable-input:focus,
.variable-inline-input:focus {
  outline: none;
  border-color: rgba(118, 212, 212, 0.8);
}

.settings-hint {
  margin-top: 8px;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.65);
}

.settings-error {
  margin-top: 8px;
  font-size: 0.85rem;
  color: #ff8b8b;
}

.variables-list {
  display: grid;
  gap: 10px;
  margin-bottom: 12px;
}

.variable-item {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 10px;
}

.add-variable {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 10px;
}

.add-btn,
.remove-btn {
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  color: white;
}

.add-btn {
  background: rgba(102, 126, 234, 0.8);
  padding: 0 14px;
}

.remove-btn {
  background: rgba(255, 107, 107, 0.8);
  width: 38px;
}

.leaderboard-container {
  max-width: 1000px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.leaderboard-table {
  --table-scrollbar-width: 8px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  margin-bottom: 30px;
}

.table-header {
  display: grid;
  grid-template-columns: 100px 1fr 150px 120px;
  gap: 20px;
  padding: 20px calc(30px + var(--table-scrollbar-width)) 20px 30px;
  background: rgba(102, 126, 234, 0.1);
  border-bottom: 1px solid rgba(102, 126, 234, 0.2);
}

.header-cell {
  font-weight: 600;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.9);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.table-body {
  max-height: 600px;
  overflow-y: auto;
  scrollbar-gutter: stable;
}

.table-row {
  display: grid;
  grid-template-columns: 100px 1fr 150px 120px;
  gap: 20px;
  padding: 20px 30px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
  transition: background 0.3s ease;
}

.table-row:hover {
  background: rgba(102, 126, 234, 0.05);
}

.table-row.top-three {
  background: rgba(102, 126, 234, 0.08);
}

.table-row:last-child {
  border-bottom: none;
}

.body-cell {
  display: flex;
  align-items: center;
  color: rgba(255, 255, 255, 0.8);
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-weight: 700;
  font-size: 1rem;
  background: rgba(102, 126, 234, 0.2);
  color: white;
}

.rank-badge.rank-1 {
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #0f1729;
}

.rank-badge.rank-2 {
  background: linear-gradient(135deg, #c0c0c0, #e8e8e8);
  color: #0f1729;
}

.rank-badge.rank-3 {
  background: linear-gradient(135deg, #cd7f32, #e8a87c);
  color: #0f1729;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
}

.username {
  font-weight: 500;
  font-size: 1rem;
}

.score {
  font-weight: 700;
  font-size: 1.2rem;
  color: #76d4d4;
}

.change-badge {
  padding: 5px 12px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.9rem;
}

.change-badge.positive {
  background: rgba(118, 212, 127, 0.2);
  color: #76d47f;
}

.change-badge.negative {
  background: rgba(255, 107, 107, 0.2);
  color: #ff6b6b;
}

.change-badge.neutral {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
}

.info-card {
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  padding: 20px 25px;
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.info-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.info-content {
  flex: 1;
}

.info-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.9);
}

.info-text {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
}

.table-body::-webkit-scrollbar {
  width: 8px;
}

.table-body::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
}

.table-body::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 4px;
}

.table-body::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
}

@media (max-width: 768px) {
  .leaderboard-section {
    padding: 80px 20px 40px;
  }

  .leaderboard-title {
    font-size: 2rem;
  }

  .table-header,
  .table-row {
    grid-template-columns: 60px 1fr 100px 80px;
    gap: 10px;
    padding: 15px 15px;
  }

  .table-header {
    padding-right: calc(15px + var(--table-scrollbar-width));
  }

  .header-cell {
    font-size: 0.75rem;
  }

  .rank-badge {
    width: 35px;
    height: 35px;
    font-size: 0.9rem;
  }

  .user-avatar {
    width: 35px;
    height: 35px;
    font-size: 1rem;
  }

  .username {
    font-size: 0.9rem;
  }

  .score {
    font-size: 1rem;
  }

  .variable-item,
  .add-variable {
    grid-template-columns: 1fr;
  }

  .change-badge {
    padding: 4px 8px;
    font-size: 0.8rem;
  }
}
</style>
