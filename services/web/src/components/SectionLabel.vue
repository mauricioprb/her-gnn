<script setup lang="ts">
defineProps<{
  icon?: string;
  title: string;
  hint?: string;
}>();
</script>

<template>
  <div class="flex flex-wrap items-center justify-between gap-3">
    <div class="flex items-center gap-2.5">
      <span
        v-if="icon"
        class="grid h-7 w-7 place-items-center rounded-md bg-primary-500/10 text-primary-600 dark:text-primary-400"
      >
        <i :class="['pi', icon, 'text-xs']" />
      </span>
      <h2
        class="text-sm font-semibold uppercase tracking-wider text-surface-700 dark:text-surface-200"
      >
        {{ title }}
      </h2>
      <span v-if="hint" class="text-xs text-surface-400">({{ hint }})</span>
    </div>
    <div v-if="$slots.actions" class="flex items-center gap-2">
      <slot name="actions" />
    </div>
  </div>
</template>
