<script setup lang="ts">
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import FloatingNavbar from '@/components/FloatingNavbar.vue'
import ShortcutsDialog from '@/components/ShortcutsDialog.vue'
import { useGlobalShortcuts } from '@/composables'

useGlobalShortcuts()
</script>

<template>
  <div class="flex h-full flex-col">
    <FloatingNavbar />

    <!-- pt-20 dá espaço para o navbar flutuante (fixed) -->
    <main class="flex-1 overflow-auto bg-surface-50 pt-20 dark:bg-surface-900">
      <RouterView />
    </main>

    <Toast position="bottom-right" />
    <ConfirmDialog />
    <ShortcutsDialog />
  </div>
</template>
