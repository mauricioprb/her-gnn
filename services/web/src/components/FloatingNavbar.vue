<script setup lang="ts">
import { ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useDark, useToggle } from '@vueuse/core'
import { showShortcutsHelp } from '@/composables'

const route = useRoute()
const mobileOpen = ref(false)

const isDark = useDark({
  selector: 'html',
  attribute: 'class',
  valueDark: 'dark',
  valueLight: '',
})
const toggleDark = useToggle(isDark)

watch(() => route.path, () => {
  mobileOpen.value = false
})

const navItems = [
  { to: '/screen', label: 'Triagem', icon: 'pi-search' },
  { to: '/compare', label: 'Comparar', icon: 'pi-chart-bar' },
  { to: '/about', label: 'Sobre', icon: 'pi-info-circle' },
]

function isActive(to: string): boolean {
  if (to === '/') return route.path === '/'
  return route.path.startsWith(to)
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="mobileOpen"
      class="fixed inset-0 z-40 bg-black/30 backdrop-blur-sm lg:hidden"
      @click="mobileOpen = false"
    />
  </Teleport>

  <nav
    class="fixed top-0 left-0 right-0 z-50 mx-auto w-full max-w-6xl px-4 pt-4 sm:px-6"
  >
    <div
      class="flex items-center justify-between rounded-2xl border border-surface-200/60 bg-surface-0/80 px-4 py-3 shadow-lg shadow-surface-300/10 backdrop-blur-xl dark:border-surface-700/60 dark:bg-surface-950/80 dark:shadow-black/20 sm:px-6"
    >
      <RouterLink to="/" class="flex shrink-0 items-center gap-3" @click="mobileOpen = false">
        <span class="grid h-9 w-9 place-items-center rounded-lg bg-primary-500 text-white font-bold text-sm">
          A
        </span>
        <div class="hidden leading-tight sm:block">
          <div class="text-sm font-semibold tracking-wide">AETHER</div>
          <div class="text-xs text-surface-500">HER catalyst screening</div>
        </div>
      </RouterLink>

      <div class="hidden items-center gap-1 lg:flex">
        <RouterLink
          v-for="r in navItems"
          :key="r.to"
          :to="r.to"
          class="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors"
          :class="isActive(r.to)
            ? 'bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300'
            : 'text-surface-600 hover:bg-surface-100 hover:text-surface-900 dark:text-surface-400 dark:hover:bg-surface-800 dark:hover:text-surface-0'"
        >
          <i :class="['pi', r.icon, 'text-xs']" />
          {{ r.label }}
        </RouterLink>
      </div>

      <div class="hidden items-center gap-1 lg:flex">
        <button
          type="button"
          class="grid h-9 w-9 place-items-center rounded-lg text-surface-500 transition-colors hover:bg-surface-100 hover:text-surface-700 dark:text-surface-400 dark:hover:bg-surface-800 dark:hover:text-surface-0"
          title="Atalhos (?)"
          @click="showShortcutsHelp = true"
        >
          <i class="pi pi-question-circle text-sm" />
        </button>
        <button
          type="button"
          class="grid h-9 w-9 place-items-center rounded-lg text-surface-500 transition-colors hover:bg-surface-100 hover:text-surface-700 dark:text-surface-400 dark:hover:bg-surface-800 dark:hover:text-surface-0"
          :title="isDark ? 'Tema claro' : 'Tema escuro'"
          @click="toggleDark()"
        >
          <i :class="['pi text-sm', isDark ? 'pi-sun' : 'pi-moon']" />
        </button>
      </div>

      <button
        type="button"
        class="grid h-9 w-9 place-items-center rounded-lg text-surface-600 transition-colors hover:bg-surface-100 dark:text-surface-300 dark:hover:bg-surface-800 lg:hidden"
        :aria-label="mobileOpen ? 'Fechar menu' : 'Abrir menu'"
        @click="mobileOpen = !mobileOpen"
      >
        <i :class="['pi text-sm', mobileOpen ? 'pi-times' : 'pi-bars']" />
      </button>
    </div>

    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      leave-active-class="transition-all duration-200 ease-in"
      enter-from-class="opacity-0 -translate-y-2 scale-y-95"
      leave-to-class="opacity-0 -translate-y-2 scale-y-95"
    >
      <div
        v-if="mobileOpen"
        class="mt-2 overflow-hidden rounded-2xl border border-surface-200/60 bg-surface-0/90 shadow-xl shadow-surface-300/10 backdrop-blur-xl dark:border-surface-700/60 dark:bg-surface-950/90 dark:shadow-black/30 lg:hidden"
      >
        <div class="flex flex-col gap-1 px-3 py-3">
          <RouterLink
            v-for="r in navItems"
            :key="r.to"
            :to="r.to"
            class="flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-colors"
            :class="isActive(r.to)
              ? 'bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300'
              : 'text-surface-600 hover:bg-surface-100 hover:text-surface-900 dark:text-surface-400 dark:hover:bg-surface-800 dark:hover:text-surface-0'"
            @click="mobileOpen = false"
          >
            <i :class="['pi', r.icon, 'text-base']" />
            {{ r.label }}
          </RouterLink>

          <hr class="my-2 border-surface-200 dark:border-surface-700" />

          <div class="flex items-center justify-between px-4 py-2">
            <span class="text-sm text-surface-500">Ações</span>
            <div class="flex items-center gap-1">
              <button
                type="button"
                class="grid h-10 w-10 place-items-center rounded-lg text-surface-500 transition-colors hover:bg-surface-100 hover:text-surface-700 dark:text-surface-400 dark:hover:bg-surface-800 dark:hover:text-surface-0"
                title="Atalhos (?)"
                @click="showShortcutsHelp = true; mobileOpen = false"
              >
                <i class="pi pi-question-circle" />
              </button>
              <button
                type="button"
                class="grid h-10 w-10 place-items-center rounded-lg text-surface-500 transition-colors hover:bg-surface-100 hover:text-surface-700 dark:text-surface-400 dark:hover:bg-surface-800 dark:hover:text-surface-0"
                :title="isDark ? 'Tema claro' : 'Tema escuro'"
                @click="toggleDark()"
              >
                <i :class="['pi', isDark ? 'pi-sun' : 'pi-moon']" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </nav>
</template>
