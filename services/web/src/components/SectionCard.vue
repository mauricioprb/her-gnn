<script setup lang="ts">
defineProps<{
  title?: string
  subtitle?: string
  icon?: string
  padded?: boolean
}>()
</script>

<template>
  <section
    class="rounded-2xl border border-surface-200 bg-surface-0 shadow-sm dark:border-surface-800 dark:bg-surface-950"
  >
    <header
      v-if="title || $slots.actions"
      class="flex flex-wrap items-center justify-between gap-3 border-b border-surface-200 px-5 py-3.5 dark:border-surface-800"
    >
      <div class="flex items-center gap-2.5">
        <span
          v-if="icon"
          class="grid h-7 w-7 place-items-center rounded-md bg-primary-500/10 text-primary-600 dark:text-primary-400"
        >
          <i :class="['pi', icon, 'text-xs']" />
        </span>
        <div>
          <h2 class="text-sm font-semibold text-surface-900 dark:text-surface-0">{{ title }}</h2>
          <p v-if="subtitle" class="mt-0.5 text-xs text-surface-500">{{ subtitle }}</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <slot name="actions" />
      </div>
    </header>
    <div :class="padded === false ? '' : 'p-5'">
      <slot />
    </div>
  </section>
</template>
