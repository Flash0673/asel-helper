<script setup lang="ts">
const storageKey = 'svoe-vino:age-confirmed-until'
const confirmationDuration = 30 * 24 * 60 * 60 * 1000
const dialog = ref<HTMLDialogElement | null>(null)
const heading = ref<HTMLHeadingElement | null>(null)
const ready = ref(false)
const confirmed = ref(false)
const declined = ref(false)
let previousOverflow = ''

onMounted(async () => {
  try {
    const expiresAt = Number(localStorage.getItem(storageKey))
    confirmed.value = Number.isFinite(expiresAt) && expiresAt > Date.now() && expiresAt <= Date.now() + confirmationDuration
  } catch {
    // Storage can be unavailable; confirmation still works for the current visit.
  }
  ready.value = true
  if (!confirmed.value) {
    previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    await nextTick()
    dialog.value?.showModal()
    heading.value?.focus()
  }
})

function confirmAge() {
  try {
    localStorage.setItem(storageKey, String(Date.now() + confirmationDuration))
  } catch {
    // Keep the site usable when the browser does not allow local storage.
  }
  confirmed.value = true
  dialog.value?.close()
  document.body.style.overflow = previousOverflow
}

async function changeDecision(value: boolean) {
  declined.value = value
  await nextTick()
  heading.value?.focus()
}

function keepGateOpen() {
  if (!confirmed.value && dialog.value?.isConnected && !dialog.value.open) dialog.value.showModal()
}

onBeforeUnmount(() => {
  if (ready.value && !confirmed.value) document.body.style.overflow = previousOverflow
})
</script>

<template>
  <div v-show="ready" :inert="!confirmed" :aria-hidden="!confirmed ? 'true' : undefined">
    <slot />
  </div>
  <dialog ref="dialog" class="age-gate" closedby="none" aria-labelledby="age-gate-title" aria-describedby="age-gate-description" @cancel.prevent @keydown.esc.prevent.stop @close="keepGateOpen">
    <div class="age-gate-card">
      <img class="age-gate-logo" src="/svg/logo/svoe-vino-logo.svg" alt="Своё Вино" width="128" height="48" />
      <span class="age-gate-badge" aria-label="18 плюс">18<span>+</span></span>
      <h2 id="age-gate-title" ref="heading" tabindex="-1">{{ declined ? 'Этот сайт — для совершеннолетних' : 'Вам уже исполнилось 18 лет?' }}</h2>
      <p id="age-gate-description">{{ declined ? 'Информация об алкогольной продукции доступна только посетителям, достигшим 18 лет.' : 'Сайт содержит информацию об алкогольной продукции. Пожалуйста, подтвердите ваш возраст.' }}</p>
      <div v-if="!declined" class="age-gate-actions">
        <button type="button" class="btn-wine" @click="confirmAge">Да, мне есть 18 лет</button>
        <button type="button" class="btn-wine-outline" @click="changeDecision(true)">Нет, мне ещё нет 18</button>
      </div>
      <button v-else type="button" class="age-gate-back" @click="changeDecision(false)">Вернуться к подтверждению</button>
      <p v-if="!declined" class="age-gate-hint">Запомним подтверждение на этом устройстве на 30 дней.</p>
    </div>
  </dialog>
</template>

<style scoped>
.age-gate { width:min(520px,calc(100% - 32px)); max-width:none; max-height:calc(100dvh - 32px); margin:auto; padding:0; border:1px solid #e4d7c8; border-radius:28px; background:#faf7f2; color:#3d352f; box-shadow:0 24px 100px #2b171642; overflow:auto; }
.age-gate::backdrop { background:#30211dcc; backdrop-filter:blur(7px); }
.age-gate-card { padding:36px 42px 30px; display:flex; flex-direction:column; align-items:center; text-align:center; }
.age-gate-logo { width:128px; height:48px; object-fit:contain; }
.age-gate-badge { display:flex; align-items:baseline; justify-content:center; width:108px; height:108px; margin:26px 0 24px; padding-top:22px; border:1px solid #d9bcae; border-radius:50%; color:#8f3d42; font-family:Prata,Georgia,serif; font-size:44px; line-height:1.5; }
.age-gate-badge span { font-size:30px; }
.age-gate h2 { max-width:390px; font-size:30px; line-height:1.35; font-weight:400; outline:none; }
.age-gate p { margin-top:16px; color:#75675e; font-size:16px; line-height:1.65; }
.age-gate-actions { display:grid; width:100%; gap:12px; margin-top:28px; }
.age-gate-actions button { min-height:50px; font-size:15px; }
.age-gate button:focus-visible { outline:2px solid #8f3d42; outline-offset:4px; }
.age-gate .age-gate-hint { max-width:320px; margin-top:20px; color:#89796c; font-size:13px; line-height:1.5; }
.age-gate-back { min-height:44px; margin-top:22px; color:#8f3d42; font-size:14px; text-decoration:underline; text-underline-offset:4px; }
@media(max-width:480px) {
  .age-gate { border-radius:22px; }
  .age-gate-card { padding:26px 24px 24px; }
  .age-gate-badge { width:92px; height:92px; padding-top:16px; margin:22px 0; font-size:40px; }
  .age-gate h2 { font-size:27px; }
  .age-gate-actions { margin-top:24px; }
}
@media(max-height:650px) {
  .age-gate-card { padding-top:22px; padding-bottom:22px; }
  .age-gate-badge { width:auto; height:auto; padding:0; margin:14px 0; border:0; font-size:34px; }
}
</style>
