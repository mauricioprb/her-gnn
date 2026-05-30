<script setup lang="ts">
defineProps<{
  icon?: string
  title: string
  subtitle?: string
}>()
</script>

<template>
  <header
    class="rounded-2xl border border-surface-200 bg-surface-0 px-6 py-6 shadow-sm dark:border-surface-800 dark:bg-surface-950"
  >
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div class="flex items-center gap-3">
        <span
          v-if="icon"
          class="grid h-11 w-11 place-items-center rounded-xl bg-primary-500/10 text-primary-600 ring-1 ring-primary-500/20 dark:text-primary-400"
        >
          <i :class="['pi', icon, 'text-lg']" />
        </span>
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-surface-900 dark:text-surface-0">
            {{ title }}
          </h1>
          <p v-if="subtitle" class="mt-0.5 text-sm text-surface-500">{{ subtitle }}</p>
        </div>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <slot name="actions" />
      </div>
    </div>
    <div v-if="$slots.default" class="mt-5 flex flex-wrap items-center gap-x-6 gap-y-2">
      <slot />
    </div>
  </header>
</template>
