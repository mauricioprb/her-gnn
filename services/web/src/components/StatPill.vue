<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  icon?: string
  hint?: string
}>()
</script>

<template>
  <div class="flex items-center gap-2.5">
    <span
      v-if="icon"
      class="grid h-8 w-8 place-items-center rounded-lg bg-surface-100 text-surface-600 dark:bg-surface-800 dark:text-surface-300"
    >
      <i :class="['pi', icon, 'text-xs']" />
    </span>
    <div class="leading-tight">
      <div class="flex items-baseline gap-1.5">
        <span class="font-mono text-sm font-semibold tabular-nums text-surface-900 dark:text-surface-0">
          {{ value }}
        </span>
        <span class="text-[11px] text-surface-500">{{ label }}</span>
      </div>
      <p v-if="hint" class="text-[10px] text-surface-400">{{ hint }}</p>
    </div>
  </div>
</template>
