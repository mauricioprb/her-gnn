<script setup lang="ts">
defineProps<{
  icon?: string;
  title: string;
  subtitle?: string;
  stack?: boolean;
}>();
</script>

<template>
  <header
    class="rounded-2xl border border-surface-200 bg-surface-0 px-5 py-5 shadow-sm sm:px-6 sm:py-6 dark:border-surface-800 dark:bg-surface-950"
  >
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div :class="stack ? 'flex flex-col items-start gap-3' : 'flex items-start gap-3.5'">
        <span
          v-if="icon"
          class="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-primary-500/10 text-primary-600 ring-1 ring-primary-500/20 dark:text-primary-400"
          :class="stack ? '' : 'mt-0.5'"
        >
          <i :class="['pi', icon, 'text-lg']" />
        </span>
        <div class="min-w-0">
          <h1
            class="text-xl font-semibold leading-tight tracking-tight text-balance text-surface-900 sm:text-2xl dark:text-surface-0"
          >
            {{ title }}
          </h1>
          <p v-if="subtitle" class="mt-1.5 max-w-2xl text-sm leading-relaxed text-surface-500">
            {{ subtitle }}
          </p>
        </div>
      </div>
      <div v-if="$slots.actions" class="flex w-full flex-wrap items-center gap-2 sm:w-auto">
        <slot name="actions" />
      </div>
    </div>
    <div
      v-if="$slots.default"
      class="mt-5 flex flex-col gap-3 border-t border-surface-200 pt-5 sm:flex-row sm:flex-wrap sm:items-center sm:gap-x-6 sm:gap-y-3 dark:border-surface-800"
    >
      <slot />
    </div>
  </header>
</template>
