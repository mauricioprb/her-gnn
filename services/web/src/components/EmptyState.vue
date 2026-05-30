<script setup lang="ts">
defineProps<{
  icon?: string;
  title: string;
  description?: string;
}>();
</script>

<template>
  <div
    class="relative flex flex-col items-center justify-center overflow-hidden rounded-2xl border border-dashed border-surface-300 bg-surface-0 px-6 py-16 text-center dark:border-surface-700 dark:bg-surface-950"
  >
    <div
      class="pointer-events-none absolute inset-0 bg-linear-to-b from-primary-50/30 to-transparent dark:from-primary-950/30"
    ></div>
    <div
      v-if="icon"
      class="relative mb-4 grid h-16 w-16 place-items-center rounded-2xl bg-primary-500/10 text-primary-600 ring-1 ring-primary-500/20 dark:text-primary-400"
    >
      <i :class="['pi', icon, 'text-2xl']" />
    </div>
    <h3 class="relative text-base font-semibold text-surface-800 dark:text-surface-100">
      {{ title }}
    </h3>
    <p v-if="description" class="relative mt-1 max-w-md text-sm text-surface-500">
      {{ description }}
    </p>
    <div class="relative mt-4">
      <slot />
    </div>
  </div>
</template>
