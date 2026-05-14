<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const variables = ref([
  { name: 'Параметр 1', key: 'param_1' },
  { name: 'Параметр 2', key: 'param_2' },
  { name: 'Параметр 3', key: 'param_3' }
])

const scoreFormula = ref('score')
const showSettings = ref(false)
const showEditModal = ref(false)
const showUserModal = ref(false)
const draftMode = ref('edit')
const newVariable = ref({ name: '', key: '' })
const tagDraftValues = ref({})
const editDraftBaseline = ref({
  score: '0',
  tags: {}
})

const leaderboardData = ref([])
const connectionState = ref('connecting')
const statusMessage = ref('Подключение к серверу...')
const socketError = ref('')

const editDraft = ref({
  key: '',
  score: '0',
  tags: ''
})

let subscriptionSocket = null
let reconnectTimer = null
let reconnectEnabled = true

const wsBaseUrl = (() => {
  const configuredUrl = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'

  if (configuredUrl.startsWith('ws://') || configuredUrl.startsWith('wss://')) {
    return configuredUrl.replace(/\/$/, '')
  }

  if (configuredUrl.startsWith('https://')) {
    return configuredUrl.replace(/^https:\/\//, 'wss://').replace(/\/$/, '')
  }

  return configuredUrl.replace(/^http:\/\//, 'ws://').replace(/\/$/, '')
})()

const availableVariableKeys = computed(() => {
  return ['score', ...variables.value.map((item) => item.key).filter(Boolean)]
})

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

  const duplicateIndex = variables.value.findIndex((item, itemIndex) => item.key === normalizedKey && itemIndex !== index)
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

const buildTagDraftValues = (source = {}) => {
  return variables.value.reduce((accumulator, variable) => {
    const normalizedValue = Number(source[variable.key] ?? 0)
    accumulator[variable.key] = Number.isFinite(normalizedValue) ? String(normalizedValue) : '0'
    return accumulator
  }, {})
}

const addVariable = () => {
  const name = newVariable.value.name.trim()
  const key = newVariable.value.key
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '_')
    .replace(/[^a-z0-9_]/g, '')

  if (name && key && !variables.value.some((item) => item.key === key)) {
    variables.value.push({ name, key })
    ensureUserVariableValue(key)
    tagDraftValues.value = {
      ...tagDraftValues.value,
      [key]: '0'
    }
    newVariable.value = { name: '', key: '' }
  }
}

const removeVariable = (index) => {
  const variable = variables.value[index]
  variables.value.splice(index, 1)

  if (!variable?.key) {
    return
  }

  leaderboardData.value = leaderboardData.value.map((user) => {
    const { [variable.key]: _, ...rest } = user
    return rest
  })

  const { [variable.key]: _, ...restDraftValues } = tagDraftValues.value
  tagDraftValues.value = restDraftValues
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
    return 'Введите формулу для подсчета очков'
  }

  if (!compiledFormula.value) {
    return 'Формула содержит синтаксическую ошибку'
  }

  return ''
})

const calculateBaseScore = (user) => {
  if (!compiledFormula.value) {
    return Number(user.score ?? 0)
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
  const rows = leaderboardData.value.map((user) => ({
    ...user,
    computedScore: calculateBaseScore(user)
  }))

  return rows
    .sort((firstUser, secondUser) => secondUser.computedScore - firstUser.computedScore)
    .map((user, index) => ({
      ...user,
      rank: index + 1
    }))
})

const connectionBadgeClass = computed(() => {
  if (connectionState.value === 'connected') return 'badge-connected'
  if (connectionState.value === 'error') return 'badge-error'
  return 'badge-connecting'
})

const gridColumns = computed(() => {
  const varColumns = variables.value.map(() => '120px').join(' ')
  return `100px 1fr 150px ${varColumns}`
})

const normalizeKey = (value) => value.trim()

const applyLeaderboardData = (data) => {
  if (!Array.isArray(data)) {
    return
  }

  const maxTagsCount = data.reduce((maxCount, entry) => {
    const tagsCount = Array.isArray(entry.tags) ? entry.tags.length : 0
    return Math.max(maxCount, tagsCount)
  }, 0)

  if (maxTagsCount > variables.value.length) {
    for (let index = variables.value.length + 1; index <= maxTagsCount; index += 1) {
      variables.value.push({
        name: `Параметр ${index}`,
        key: `param_${index}`
      })
    }
  }

  leaderboardData.value = data.map((entry) => {
    const key = String(entry.key ?? '')
    const score = Number(entry.score ?? 0)
    const tags = Array.isArray(entry.tags)
      ? entry.tags.map((tag) => Number(tag)).filter((tag) => Number.isFinite(tag))
      : []

    const dynamicValues = {}
    variables.value.forEach((variable, index) => {
      dynamicValues[variable.key] = Number(tags[index] ?? 0)
    })

    return {
      key,
      userId: key,
      username: key,
      score,
      ...dynamicValues
    }
  })
}

const buildSocketUrl = (action, path = '') => {
  const safePath = path ? `/${path}` : ''
  return `${wsBaseUrl}/ws/${action}${safePath}`
}

const sendSocketAction = (action, path = '') => {
  return new Promise((resolve, reject) => {
    const actionSocket = new WebSocket(buildSocketUrl(action, path))
    let settled = false

    const finish = (handler, value) => {
      if (settled) {
        return
      }

      settled = true

      try {
        actionSocket.close()
      } catch {
        // Ignore close errors during request teardown.
      }

      handler(value)
    }

    actionSocket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data)

        if (payload?.type === 'error') {
          finish(reject, new Error(payload.message || 'Не удалось выполнить операцию'))
          return
        }

        finish(resolve, payload)
      } catch {
        finish(reject, new Error('Сервер вернул некорректный ответ'))
      }
    }

    actionSocket.onerror = () => {
      finish(reject, new Error('Ошибка websocket-запроса'))
    }

    actionSocket.onclose = () => {
      if (!settled) {
        finish(reject, new Error('Соединение закрылось до ответа сервера'))
      }
    }
  })
}

const selectEntry = (entry) => {
  draftMode.value = 'edit'
  const score = String(entry.score ?? 0)
  const tags = buildTagDraftValues(entry)

  editDraft.value = {
    key: entry.key,
    score
  }
  editDraftBaseline.value = {
    score,
    tags: { ...tags }
  }
  tagDraftValues.value = tags

  showEditModal.value = true
  socketError.value = ''
}

const closeEditModal = () => {
  showEditModal.value = false
  socketError.value = ''
}

const openCreateUserModal = () => {
  draftMode.value = 'create'
  resetDraft()
  showUserModal.value = true
  socketError.value = ''
}

const closeUserModal = () => {
  showUserModal.value = false
  draftMode.value = 'edit'
  socketError.value = ''
}

const resetDraft = () => {
  editDraft.value = {
    key: '',
    score: '0'
  }
  tagDraftValues.value = buildTagDraftValues()
}

const resetEditDraft = () => {
  editDraft.value.score = editDraftBaseline.value.score
  tagDraftValues.value = { ...editDraftBaseline.value.tags }
  socketError.value = ''
}

const refreshLeaderboard = async () => {
  try {
    socketError.value = ''
    const payload = await sendSocketAction('get_leaderboard', '0')

    if (Array.isArray(payload?.data)) {
      applyLeaderboardData(payload.data)
    }
  } catch (error) {
    socketError.value = error instanceof Error ? error.message : 'Не удалось обновить таблицу'
  }
}

const saveEntry = async () => {
  const key = normalizeKey(editDraft.value.key)

  if (!key) {
    socketError.value = draftMode.value === 'create'
      ? 'Введите имя пользователя'
      : 'Выберите пользователя для редактирования'
    return
  }

  const score = Number(editDraft.value.score)

  if (!Number.isFinite(score)) {
    socketError.value = 'Очки должны быть числом'
    return
  }

  try {
    socketError.value = ''
    statusMessage.value = draftMode.value === 'create' ? 'Добавляем пользователя...' : 'Сохраняем изменения...'

    await sendSocketAction('update_score', `${encodeURIComponent(key)}/${encodeURIComponent(String(score))}`)

    const tags = variables.value.map((variable) => {
      const parsedValue = Number(tagDraftValues.value[variable.key] ?? 0)
      return Number.isFinite(parsedValue) ? parsedValue : 0
    })
    await sendSocketAction('update_tags', `${encodeURIComponent(key)}/${encodeURIComponent(tags.join(','))}`)

    statusMessage.value = draftMode.value === 'create' ? 'Пользователь добавлен' : 'Изменения отправлены'
    if (draftMode.value === 'create') {
      showUserModal.value = false
    } else {
      showEditModal.value = false
    }
    draftMode.value = 'edit'
  } catch (error) {
    socketError.value = error instanceof Error ? error.message : 'Не удалось сохранить запись'
    statusMessage.value = draftMode.value === 'create' ? 'Ошибка при добавлении' : 'Ошибка при сохранении'
  }
}

const deleteEntry = async (keyOverride = '') => {
  const key = normalizeKey(keyOverride || editDraft.value.key)

  if (!key) {
    socketError.value = 'Выберите пользователя для удаления'
    return
  }

  try {
    socketError.value = ''
    statusMessage.value = 'Удаляем запись...'
    await sendSocketAction('delete_object', encodeURIComponent(key))
    resetDraft()
    showEditModal.value = false
    statusMessage.value = 'Запись удалена'
  } catch (error) {
    socketError.value = error instanceof Error ? error.message : 'Не удалось удалить запись'
    statusMessage.value = 'Ошибка при удалении'
  }
}

const handleSubscriptionMessage = (event) => {
  try {
    const payload = JSON.parse(event.data)

    if (Array.isArray(payload?.data)) {
      applyLeaderboardData(payload.data)
    }

    if (payload?.type === 'Connection (successful)') {
      connectionState.value = 'connected'
      statusMessage.value = 'Подключение установлено'
      socketError.value = ''
      return
    }

    if (payload?.type === 'leaderboard_update') {
      statusMessage.value = 'Лидерборд обновлён'
      socketError.value = ''
      return
    }

    if (payload?.type === 'error') {
      connectionState.value = 'error'
      socketError.value = payload.message || 'Ошибка websocket'
    }
  } catch {
    socketError.value = 'Не удалось разобрать сообщение от сервера'
  }
}

const scheduleReconnect = () => {
  if (!reconnectEnabled) {
    return
  }

  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
  }

  reconnectTimer = setTimeout(() => {
    connectSubscription()
  }, 2000)
}

const connectSubscription = () => {
  if (subscriptionSocket) {
    try {
      subscriptionSocket.close()
    } catch {
      // Ignore close errors when reconnecting.
    }
  }

  connectionState.value = 'connecting'
  statusMessage.value = 'Подключение к серверу...'

  subscriptionSocket = new WebSocket(buildSocketUrl('connect', 'leaderboard'))

  subscriptionSocket.onopen = () => {
    connectionState.value = 'connected'
    statusMessage.value = 'Подписка на обновления активна'
    socketError.value = ''
  }

  subscriptionSocket.onmessage = handleSubscriptionMessage

  subscriptionSocket.onerror = () => {
    connectionState.value = 'error'
    socketError.value = 'Ошибка подключения к websocket'
    statusMessage.value = 'Соединение не удалось'
  }

  subscriptionSocket.onclose = () => {
    if (!reconnectEnabled) {
      return
    }

    connectionState.value = 'connecting'
    statusMessage.value = 'Соединение потеряно, переподключение...'
    scheduleReconnect()
  }
}

onMounted(() => {
  reconnectEnabled = true
  connectSubscription()
})

onBeforeUnmount(() => {
  reconnectEnabled = false

  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
  }

  if (subscriptionSocket) {
    try {
      subscriptionSocket.close()
    } catch {
      // Ignore shutdown errors.
    }
  }
})
</script>

<template>
  <div class="container">
    <section class="leaderboard-section">
      <div class="leaderboard-header">
        <h1 class="leaderboard-title">Таблица лидеров</h1>
        <p class="leaderboard-description">
          Рейтинг обновляется в реальном времени
        </p>
        <div class="connection-row">
          <span class="connection-status" :class="connectionBadgeClass">
            {{ connectionState }}
          </span>
          <span class="connection-message">{{ statusMessage }}</span>
        </div>
        <div class="header-actions">
          <button @click="openCreateUserModal" class="add-user-btn">＋ Добавить пользователя</button>
          <button @click="showSettings = !showSettings" class="settings-btn">
            ⚙️ {{ showSettings ? 'Скрыть настройки' : 'Настройки' }}
          </button>
        </div>
      </div>

      <div v-if="showEditModal" class="modal-backdrop" @click.self="closeEditModal">
        <div class="modal-card">
          <div class="modal-header">
            <h2 class="modal-title">Редактировать пользователя</h2>
            <button class="modal-close-btn" @click="closeEditModal">✕</button>
          </div>

          <div class="modal-body">
            <label class="modal-field">
              <span>Очки</span>
              <input v-model="editDraft.score" type="number" class="formula-input modal-input" placeholder="0" />
            </label>

            <div class="parameter-list">
              <label v-for="variable in variables" :key="variable.key" class="modal-field">
                <span>{{ variable.name }}</span>
                <input
                  v-model="tagDraftValues[variable.key]"
                  type="number"
                  class="formula-input modal-input"
                  :placeholder="`Значение для ${variable.name}`"
                />
              </label>
            </div>

            <p v-if="socketError" class="settings-error">{{ socketError }}</p>
          </div>

          <div class="modal-actions">
            <button @click="saveEntry" class="add-btn">Сохранить</button>
            <button @click="deleteEntry()" class="remove-btn wide-remove">Удалить</button>
            <button @click="resetEditDraft" class="neutral-btn">Сбросить</button>
          </div>
        </div>
      </div>

      <div v-if="showSettings" class="settings-backdrop" @click.self="showSettings = false">
        <div class="settings-modal">
          <div class="modal-header">
            <h2 class="modal-title">Настройки лидерборда</h2>
            <button class="modal-close-btn" @click="showSettings = false">✕</button>
          </div>

          <div class="settings-panel">
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
                  placeholder="Название"
                />
                <input
                  v-model="newVariable.key"
                  type="text"
                  class="variable-input"
                  placeholder="Ключ"
                />
                <button @click="addVariable" class="add-btn">+ Добавить</button>
              </div>
            </div>

          </div>
        </div>
      </div>

      <div class="leaderboard-container">
        <div class="leaderboard-table-shell">
          <div class="leaderboard-table">
            <div class="table-scroll-area">
              <div class="table-header" :style="{ gridTemplateColumns: gridColumns }">
                <div class="header-cell rank-cell">Место</div>
                <div class="header-cell user-cell">Пользователь</div>
                <div class="header-cell score-cell">Очки</div>
                <div
                  v-for="(variable, variableIndex) in variables"
                  :key="`${variable.key}-${variableIndex}`"
                  class="header-cell var-cell"
                >
                  {{ variable.name }}
                </div>
              </div>

              <div class="table-body">
                <div v-for="user in leaderboardRows" :key="user.userId" class="table-row" :class="{ 'top-three': user.rank <= 3 }" :style="{ gridTemplateColumns: gridColumns }">
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
                  <div
                    v-for="(variable, variableIndex) in variables"
                    :key="`${variable.key}-${variableIndex}`"
                    class="body-cell var-cell"
                  >
                    <span class="var-value">{{ user[variable.key] }}</span>
                  </div>
                </div>

                <div v-if="!leaderboardRows.length" class="empty-state">
                  Пока нет данных. Добавьте записи через backend и они появятся здесь.
                </div>
              </div>
            </div>
          </div>

          <div v-if="leaderboardRows.length" class="table-actions-column">
            <div class="table-actions-spacer"></div>
            <div v-for="user in leaderboardRows" :key="`${user.userId}-action`" class="table-action-cell">
              <button @click="selectEntry(user)" class="inline-action-btn" aria-label="Редактировать пользователя">✏️</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div v-if="showUserModal" class="modal-backdrop" @click.self="closeUserModal">
      <div class="modal-card">
        <div class="modal-header">
          <h2 class="modal-title">
            {{ draftMode === 'create' ? 'Добавить пользователя' : 'Редактировать пользователя' }}
          </h2>
          <button class="modal-close-btn" @click="closeUserModal">✕</button>
        </div>

        <div class="modal-body">
          <label class="modal-field">
            <span>Имя пользователя</span>
            <input
              v-model="editDraft.key"
              type="text"
              class="formula-input modal-input"
              placeholder="Например: player_1"
            />
          </label>

          <label class="modal-field">
            <span>Очки</span>
            <input v-model="editDraft.score" type="number" class="formula-input modal-input" placeholder="0" />
          </label>

          <div class="parameter-list">
            <label v-for="variable in variables" :key="variable.key" class="modal-field">
              <span>{{ variable.name }}</span>
              <input
                v-model="tagDraftValues[variable.key]"
                type="number"
                class="formula-input modal-input"
                :placeholder="`Значение для ${variable.name}`"
              />
            </label>
          </div>

          <p v-if="socketError" class="settings-error">{{ socketError }}</p>
        </div>

        <div class="modal-actions">
          <button @click="saveEntry" class="add-btn">{{ draftMode === 'create' ? 'Добавить' : 'Сохранить' }}</button>
          <button @click="closeUserModal" class="neutral-btn">Отмена</button>
        </div>
      </div>
    </div>
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
  margin-bottom: 30px;
  position: relative;
  z-index: 1;
}

.leaderboard-title {
  font-size: 3rem;
  margin-bottom: 10px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.leaderboard-description {
  font-size: 1.05rem;
  color: rgba(255, 255, 255, 0.75);
}

.connection-row {
  margin-top: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.connection-status {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.badge-connected {
  background: rgba(118, 212, 118, 0.18);
  color: #9ef0b0;
  border: 1px solid rgba(118, 212, 118, 0.35);
}

.badge-connecting {
  background: rgba(102, 126, 234, 0.18);
  color: #c8d2ff;
  border: 1px solid rgba(102, 126, 234, 0.35);
}

.badge-error {
  background: rgba(255, 107, 107, 0.18);
  color: #ffb0b0;
  border: 1px solid rgba(255, 107, 107, 0.35);
}

.connection-message {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.header-actions {
  margin-top: 16px;
  display: flex;
  gap: 14px;
  justify-content: center;
  flex-wrap: wrap;
}

.add-user-btn {
  border: 1px solid rgba(118, 212, 118, 0.45);
  background: rgba(118, 212, 118, 0.16);
  color: rgba(255, 255, 255, 0.98);
  padding: 10px 18px;
  min-height: 0;
  min-width: 0;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.2s ease, border-color 0.2s ease;
}

.add-user-btn:hover {
  background: rgba(118, 212, 118, 0.28);
  transform: translateY(-1px);
}

.settings-btn {
  border: 1px solid rgba(102, 126, 234, 0.5);
  background: rgba(102, 126, 234, 0.15);
  color: rgba(255, 255, 255, 0.95);
  padding: 10px 18px;
  min-height: 0;
  min-width: 0;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
}

.settings-btn:hover {
  background: rgba(102, 126, 234, 0.3);
  transform: translateY(-1px);
}

.settings-panel {
  margin: 0;
  padding: 0;
  background: transparent;
  border: none;
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

.editor-grid {
  display: grid;
  grid-template-columns: minmax(180px, 1fr) minmax(140px, 180px) minmax(240px, 1.4fr);
  gap: 10px;
}

.editor-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 12px;
}

.add-btn,
.remove-btn,
.neutral-btn {
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  color: white;
}

.add-btn {
  background: rgba(102, 126, 234, 0.8);
  padding: 0 14px;
  min-height: 38px;
  min-width: auto;
  border-radius: 8px;
  font-size: 0.92rem;
}

.remove-btn {
  background: rgba(255, 107, 107, 0.8);
  width: 38px;
  height: 38px;
  min-width: 38px;
}

.wide-remove {
  width: auto;
  padding: 0 14px;
}

.neutral-btn {
  background: rgba(255, 255, 255, 0.12);
  padding: 0 14px;
  min-height: 38px;
  min-width: auto;
  border-radius: 8px;
  font-size: 0.92rem;
}

.settings-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(4, 8, 20, 0.72);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  z-index: 1950;
}

.settings-modal {
  width: min(980px, 100%);
  background: linear-gradient(180deg, rgba(17, 24, 39, 0.98), rgba(15, 23, 42, 0.98));
  border: 1px solid rgba(102, 126, 234, 0.35);
  border-radius: 18px;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.45);
  overflow: hidden;
  color-scheme: dark;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(4, 8, 20, 0.72);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  z-index: 2000;
}

.modal-card {
  width: min(560px, 100%);
  max-height: calc(100vh - 48px);
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, rgba(17, 24, 39, 0.98), rgba(15, 23, 42, 0.98));
  border: 1px solid rgba(102, 126, 234, 0.35);
  border-radius: 18px;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.45);
  overflow: hidden;
  color-scheme: dark;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 20px 22px 14px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.18);
  color: #ffffff;
}

.modal-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: #ffffff;
}

.modal-close-btn {
  width: 38px;
  height: 38px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.06);
  color: white;
  cursor: pointer;
}

.modal-body {
  padding: 18px 22px;
  display: grid;
  gap: 14px;
  flex: 1 1 auto;
  overflow-y: auto;
}

.modal-field {
  display: grid;
  gap: 8px;
  color: rgba(255, 255, 255, 0.88);
  font-size: 0.92rem;
}

.modal-field span {
  color: #ffffff;
}

.modal-input {
  color: #ffffff !important;
  caret-color: #ffffff;
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(102, 126, 234, 0.42);
  font-family: inherit;
  appearance: none;
}

.modal-input::placeholder,
.modal-card .modal-input::-webkit-input-placeholder,
.modal-card .modal-input::-moz-placeholder,
.modal-card .modal-input:-ms-input-placeholder {
  color: rgba(255, 255, 255, 0.45) !important;
  opacity: 1 !important;
}

.modal-input:focus {
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff;
}

.modal-input:-webkit-autofill,
.modal-input:-webkit-autofill:hover,
.modal-input:-webkit-autofill:focus,
.modal-input:-webkit-autofill:active {
  -webkit-text-fill-color: #ffffff !important;
  caret-color: #ffffff;
  box-shadow: 0 0 0 1000px rgba(255, 255, 255, 0.06) inset;
  transition: background-color 9999s ease-out 0s;
}

.settings-modal .settings-panel {
  max-width: none;
  padding: 20px 22px 22px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 0 22px 22px;
  flex-wrap: wrap;
}

.leaderboard-container {
  max-width: 1000px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.leaderboard-table {
  --table-scrollbar-width: 8px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  max-height: 600px;
  overflow: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  flex: 1 1 auto;
  min-width: 0;
  background: transparent;
}

.table-scroll-area {
  min-width: 100%;
  width: max-content;
  background: rgba(0, 0, 0, 0.3);
}

.table-header {
  display: grid;
  gap: 20px;
  padding: 20px 30px;
  background: rgba(102, 126, 234, 0.1);
  border-bottom: 1px solid rgba(102, 126, 234, 0.2);
  position: sticky;
  top: 0;
  z-index: 2;
}

.header-cell {
  font-weight: 600;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.9);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.leaderboard-table-shell {
  display: flex;
  align-items: start;
  gap: 16px;
  width: 100%;
}

.table-actions-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 0 0 72px;
  background: transparent;
  border: none;
  overflow: visible;
  padding-top: 67px;
}

.table-row {
  display: grid;
  gap: 20px;
  padding: 20px 30px;
  transition: background 0.3s ease;
  min-width: 100%;
}

.table-header {
  min-width: 100%;
}

.table-actions-spacer {
  display: none;
  width: 100%;
}

.table-action-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 64px;
  padding: 20px 0;
  border-bottom: none;
  background: transparent;
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
  gap: 12px;
}

.user-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  font-weight: 700;
}

.username {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
}

.score {
  font-size: 1.05rem;
  font-weight: 700;
  color: #9ce7ff;
}

.var-value {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.8);
}

.inline-action-btn {
  border: none;
  border-radius: 10px;
  background: rgba(102, 126, 234, 0.26);
  border: 1px solid rgba(102, 126, 234, 0.55);
  color: #fff;
  width: 48px;
  height: 48px;
  font-size: 1.15rem;
  cursor: pointer;
}

.empty-state {
  padding: 24px 30px;
  color: rgba(255, 255, 255, 0.65);
}

.table-body::-webkit-scrollbar {
  width: var(--table-scrollbar-width);
}

.table-body::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.06);
}

.table-body::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.45);
  border-radius: 999px;
}

.table-body::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.65);
}

.table-scroll-area .table-header,
.table-scroll-area .table-row,
.table-scroll-area .empty-state {
  background-clip: padding-box;
}

.table-scroll-area .table-row.top-three {
  background: rgba(102, 126, 234, 0.08);
}

@media (max-width: 1100px) {
  .leaderboard-section {
    padding-left: 24px;
    padding-right: 24px;
  }

  .editor-grid,
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
  }

  .table-header {
    display: none;
  }

  .leaderboard-table-shell {
    display: block;
  }

  .table-actions-column {
    display: none;
  }

  .body-cell {
    justify-content: flex-start;
  }

  .variable-item,
  .add-variable {
    grid-template-columns: 1fr;
  }

  .add-user-btn,
  .settings-btn {
    width: 100%;
    min-width: 0;
  }

  .modal-actions {
    justify-content: stretch;
  }

  .modal-actions .add-btn,
  .modal-actions .neutral-btn {
    width: 100%;
    min-height: 42px;
  }

  .settings-modal {
    width: min(560px, 100%);
  }
}
</style>
