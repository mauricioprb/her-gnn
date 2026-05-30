<script setup lang="ts">
import { RouterLink } from 'vue-router'
import Button from 'primevue/button'
import Skeleton from 'primevue/skeleton'

import PageHeader from '@/components/PageHeader.vue'
import StatPill from '@/components/StatPill.vue'
import { useStats } from '@/composables'

const stats = useStats()

const features = [
  {
    icon: 'pi-search',
    title: 'Triagem por composição',
    text: 'Defina os metais alvo. Receba os top-N catalisadores ordenados por |ΔG_H|.',
    to: '/screen',
    cta: 'Iniciar triagem',
  },
  {
    icon: 'pi-chart-bar',
    title: 'Comparação entre modelos',
    text: 'ETR + MACE embeddings, MACE Stage A, SchNet e baseline handcrafted lado-a-lado.',
    to: '/compare',
    cta: 'Comparar agora',
  },
  {
    icon: 'pi-info-circle',
    title: 'Sobre o dataset',
    text: '5.860 estruturas Catalysis Hub. Split canônico 4.220 / 468 / 1.172.',
    to: '/about',
    cta: 'Ver detalhes',
  },
]
</script>

<template>
  <section class="mx-auto max-w-7xl space-y-6 px-6 py-8">
    <PageHeader
      icon="pi-bolt"
      title="AETHER — triagem de catalisadores HER"
      subtitle="Predição de ΔG_H com representações pré-treinadas MACE-MP-0 + ETR. Princípio de Sabatier: ΔG_H ≈ 0 é ótimo."
    >
      <template #actions>
        <RouterLink to="/screen">
          <Button label="Começar triagem" icon="pi pi-arrow-right" icon-pos="right" />
        </RouterLink>
        <a href="/api/docs" target="_blank" rel="noopener">
          <Button label="API docs" icon="pi pi-external-link" severity="secondary" outlined />
        </a>
      </template>
      <template v-if="stats.data.value">
        <StatPill icon="pi-database" :value="stats.data.value.n_structures.toLocaleString('pt-BR')" label="estruturas" />
        <StatPill icon="pi-check-square" :value="stats.data.value.n_test_canonical.toLocaleString('pt-BR')" label="teste canônico" />
        <StatPill icon="pi-atom" :value="stats.data.value.available_elements.length" label="metais" />
        <StatPill icon="pi-microchip-ai" :value="stats.data.value.available_models.length" label="modelos" />
      </template>
      <Skeleton v-else width="24rem" height="2rem" />
    </PageHeader>

    <div class="grid gap-4 md:grid-cols-3">
      <RouterLink
        v-for="f in features"
        :key="f.to"
        :to="f.to"
        class="group relative flex h-full flex-col overflow-hidden rounded-2xl border border-surface-200 bg-surface-0 p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md dark:border-surface-800 dark:bg-surface-950"
      >
        <span
          class="relative mb-4 grid h-11 w-11 place-items-center rounded-xl bg-primary-500/10 text-primary-600 ring-1 ring-primary-500/20 dark:text-primary-400"
        >
          <i :class="['pi', f.icon, 'text-lg']" />
        </span>
        <h3 class="relative text-base font-semibold text-surface-900 dark:text-surface-0">
          {{ f.title }}
        </h3>
        <p class="relative mt-2 flex-1 text-sm leading-relaxed text-surface-600 dark:text-surface-300">
          {{ f.text }}
        </p>
        <div class="relative mt-4 flex items-center gap-1.5 text-sm font-medium text-primary-600 dark:text-primary-400">
          {{ f.cta }}
          <i class="pi pi-arrow-right text-xs transition-transform group-hover:translate-x-1" />
        </div>
      </RouterLink>
    </div>

    <section class="rounded-2xl border border-surface-200 bg-surface-0 p-6 shadow-sm dark:border-surface-800 dark:bg-surface-950">
      <div class="mb-4 flex items-center gap-2">
        <span class="grid h-7 w-7 place-items-center rounded-md bg-primary-500/10 text-primary-600 dark:text-primary-400">
          <i class="pi pi-flag text-xs" />
        </span>
        <h2 class="text-sm font-semibold uppercase tracking-wider text-surface-700 dark:text-surface-200">
          Principais resultados
        </h2>
      </div>
      <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <div class="rounded-xl border border-surface-200 bg-surface-50 p-4 dark:border-surface-800 dark:bg-surface-900/60">
          <div class="text-[10px] font-medium uppercase tracking-wide text-surface-500">ETR + MACE emb</div>
          <div class="mt-1 font-mono text-xl font-semibold text-primary-600 dark:text-primary-400 tabular-nums">0.961</div>
          <div class="text-[11px] text-surface-500">R² test · MAE 71 meV</div>
        </div>
        <div class="rounded-xl border border-surface-200 bg-surface-50 p-4 dark:border-surface-800 dark:bg-surface-900/60">
          <div class="text-[10px] font-medium uppercase tracking-wide text-surface-500">MACE Stage A</div>
          <div class="mt-1 font-mono text-xl font-semibold tabular-nums">0.956 ± 0.002</div>
          <div class="text-[11px] text-surface-500">R² test n=5 · MAE 71 meV</div>
        </div>
        <div class="rounded-xl border border-surface-200 bg-surface-50 p-4 dark:border-surface-800 dark:bg-surface-900/60">
          <div class="text-[10px] font-medium uppercase tracking-wide text-surface-500">ETR + 10 handcrafted</div>
          <div class="mt-1 font-mono text-xl font-semibold tabular-nums">0.934</div>
          <div class="text-[11px] text-surface-500">R² test · MAE 96 meV</div>
        </div>
        <div class="rounded-xl border border-surface-200 bg-surface-50 p-4 dark:border-surface-800 dark:bg-surface-900/60">
          <div class="text-[10px] font-medium uppercase tracking-wide text-surface-500">SchNet (do zero)</div>
          <div class="mt-1 font-mono text-xl font-semibold tabular-nums">0.911 ± 0.051</div>
          <div class="text-[11px] text-surface-500">R² test n=5 · MAE 73 meV</div>
        </div>
      </div>
    </section>
  </section>
</template>
