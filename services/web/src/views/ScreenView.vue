<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useToast } from 'primevue/usetoast'
import Message from 'primevue/message'
import Skeleton from 'primevue/skeleton'

import PageHeader from '@/components/PageHeader.vue'
import StatPill from '@/components/StatPill.vue'
import SectionCard from '@/components/SectionCard.vue'
import ScreenForm from '@/components/ScreenForm.vue'
import ResultsTable from '@/components/ResultsTable.vue'
import ParityScatter from '@/components/ParityScatter.vue'
import ResidualHistogram from '@/components/ResidualHistogram.vue'
import EmptyState from '@/components/EmptyState.vue'
import { useScreen, useStats } from '@/composables'
import { useScreenStore } from '@/stores/screen'

const toast = useToast()
const store = useScreenStore()
const { lastResult, hasResult, form } = storeToRefs(store)

const screenMutation = useScreen()
const stats = useStats()

const submitting = computed(() => screenMutation.isPending.value)
const errorMsg = computed(() => screenMutation.error.value?.message)

function onSubmit() {
  screenMutation.mutate({ ...form.value }, {
    onSuccess: (data) => {
      toast.add({
        severity: 'success',
        summary: `${data.n_candidates} candidatos encontrados`,
        detail: data.n_candidates === 0
          ? 'Nenhum match com esses elementos'
          : `Mostrando top ${data.rows.length} ordenados por |ΔG_H|`,
        life: 3500,
      })
    },
    onError: (err) => {
      toast.add({
        severity: 'error',
        summary: 'Falha na triagem',
        detail: err.message,
        life: 6000,
      })
    },
  })
}

function onReset() {
  store.resetForm()
  toast.add({ severity: 'info', summary: 'Padrões restaurados', life: 2000 })
}
</script>

<template>
  <section class="mx-auto max-w-7xl space-y-6 px-6 py-8">
    <PageHeader
      icon="pi-search"
      title="Triagem de catalisadores"
      subtitle="Filtre por composição, ranqueie por |ΔG_H_pred|, exporte resultados."
    >
      <template v-if="stats.data.value">
        <StatPill icon="pi-database" :value="stats.data.value.n_structures.toLocaleString('pt-BR')" label="estruturas" />
        <StatPill icon="pi-check-square" :value="stats.data.value.n_test_canonical.toLocaleString('pt-BR')" label="teste" />
        <StatPill icon="pi-atom" :value="stats.data.value.available_elements.length" label="metais" />
        <StatPill icon="pi-microchip-ai" :value="stats.data.value.available_models.length" label="modelos" />
      </template>
      <Skeleton v-else width="20rem" height="2rem" />
    </PageHeader>

    <ScreenForm :submitting="submitting" @submit="onSubmit" @reset="onReset" />

    <Message v-if="errorMsg" severity="error" :closable="false">
      {{ errorMsg }}
    </Message>

    <section v-if="submitting">
      <div class="space-y-3 rounded-2xl border border-surface-200 bg-surface-0 p-5 dark:border-surface-800 dark:bg-surface-950">
        <Skeleton height="2.5rem" />
        <Skeleton v-for="i in 8" :key="i" height="2.25rem" />
      </div>
    </section>

    <template v-else-if="hasResult && lastResult">
      <ResultsTable :result="lastResult" />

      <section class="space-y-3">
        <div class="flex items-center gap-2">
          <span class="grid h-7 w-7 place-items-center rounded-md bg-primary-500/10 text-primary-600 dark:text-primary-400">
            <i class="pi pi-chart-scatter text-xs" />
          </span>
          <h2 class="text-sm font-semibold uppercase tracking-wider text-surface-700 dark:text-surface-200">
            Diagnósticos do conjunto retornado
          </h2>
        </div>
        <div class="grid gap-4 lg:grid-cols-[1.2fr_1fr]">
          <ParityScatter
            :y-true="lastResult.rows.map((r) => r.delta_G_H)"
            :y-pred="lastResult.rows.map((r) => r.dG_pred)"
            :title="`Parity — ${lastResult.rows.length} candidatos`"
            color="#10b981"
          />
          <ResidualHistogram
            :y-true="lastResult.rows.map((r) => r.delta_G_H)"
            :y-pred="lastResult.rows.map((r) => r.dG_pred)"
            color="#10b981"
          />
        </div>
      </section>
    </template>

    <SectionCard v-else :padded="false">
      <EmptyState
        icon="pi-sparkles"
        title="Nenhuma triagem realizada ainda"
        description="Selecione os metais alvo, ajuste a quantidade e clique em Triar candidatos para receber os top-N ranqueados."
      />
    </SectionCard>
  </section>
</template>
