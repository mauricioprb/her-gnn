<script setup lang="ts">
import PageHeader from '@/components/PageHeader.vue'
import SectionCard from '@/components/SectionCard.vue'

const tech = [
  { label: 'Backend', value: 'FastAPI · Python 3.14' },
  { label: 'Modelos', value: 'MACE-MP-0 · ETR · SchNet' },
  { label: 'Frontend', value: 'Vue 3 · Vite 7 · TypeScript' },
  { label: 'UI', value: 'PrimeVue 4 · Tailwind 4' },
  { label: 'Charts', value: 'ECharts 6' },
  { label: 'Deploy', value: 'Docker Compose' },
]

const pipeline = [
  { step: 1, title: 'Curadoria', desc: 'Filtros sobre 60k reações Catalysis Hub → 5860 estruturas HER limpas' },
  { step: 2, title: 'Embeddings MACE-MP-0', desc: 'Extração de embeddings invariantes 512-dim por estrutura' },
  { step: 3, title: 'Treino multi-seed', desc: 'SchNet + MACE Stage A (5 seeds), ETR baseline determinístico' },
  { step: 4, title: 'Triagem', desc: 'Filtro composicional + predição + ranqueamento por |ΔG_H|' },
]
</script>

<template>
  <section class="mx-auto max-w-5xl space-y-6 px-6 py-8">
    <PageHeader
      icon="pi-info-circle"
      title="Sobre AETHER"
      subtitle="AI-Equivariant Tool for Hydrogen Evolution Research"
    />

    <SectionCard title="O que é" icon="pi-bookmark">
      <p class="text-sm leading-relaxed text-surface-700 dark:text-surface-300">
        AETHER prediz a energia de adsorção de hidrogênio (ΔG_H) para catalisadores
        candidatos à reação de evolução de hidrogênio (HER), usando representações
        invariantes pré-treinadas do MACE-MP-0 combinadas com Extra Trees Regressor.
        O princípio de Sabatier indica que catalisadores ótimos para HER têm
        ΔG_H ≈ 0 eV.
      </p>
    </SectionCard>

    <div class="grid gap-4 md:grid-cols-2">
      <SectionCard title="Stack" icon="pi-code">
        <dl class="space-y-2.5 text-sm">
          <div v-for="t in tech" :key="t.label" class="flex items-baseline justify-between gap-3">
            <dt class="text-xs font-medium uppercase tracking-wide text-surface-500">{{ t.label }}</dt>
            <dd class="font-mono text-xs text-surface-700 dark:text-surface-200">{{ t.value }}</dd>
          </div>
        </dl>
      </SectionCard>

      <SectionCard title="Dataset" icon="pi-database">
        <dl class="space-y-2.5 text-sm">
          <div class="flex items-baseline justify-between">
            <dt class="text-xs font-medium uppercase tracking-wide text-surface-500">Fonte</dt>
            <dd class="font-mono text-xs">Catalysis Hub</dd>
          </div>
          <div class="flex items-baseline justify-between">
            <dt class="text-xs font-medium uppercase tracking-wide text-surface-500">Estruturas</dt>
            <dd class="font-mono text-xs">5.860</dd>
          </div>
          <div class="flex items-baseline justify-between">
            <dt class="text-xs font-medium uppercase tracking-wide text-surface-500">Split canônico</dt>
            <dd class="font-mono text-xs">4.220 / 468 / 1.172</dd>
          </div>
          <div class="flex items-baseline justify-between">
            <dt class="text-xs font-medium uppercase tracking-wide text-surface-500">Filtros</dt>
            <dd class="font-mono text-xs">ΔG ∈ [-2, 2] · cov ≤ 25%</dd>
          </div>
          <div class="flex items-baseline justify-between">
            <dt class="text-xs font-medium uppercase tracking-wide text-surface-500">Reação</dt>
            <dd class="font-mono text-xs">0.5 H₂(g) + * → H*</dd>
          </div>
        </dl>
      </SectionCard>
    </div>

    <SectionCard title="Pipeline" icon="pi-sitemap" :padded="false">
      <ol class="grid gap-3 p-5 md:grid-cols-2 lg:grid-cols-4">
        <li
          v-for="p in pipeline"
          :key="p.step"
          class="relative rounded-xl border border-surface-200 bg-surface-50 p-4 dark:border-surface-800 dark:bg-surface-900/60"
        >
          <span class="absolute -top-2.5 left-3 rounded-md bg-primary-500 px-2 py-0.5 text-[10px] font-bold text-white">
            {{ p.step }}
          </span>
          <h4 class="mt-1 text-sm font-semibold text-surface-900 dark:text-surface-0">{{ p.title }}</h4>
          <p class="mt-1 text-xs text-surface-500">{{ p.desc }}</p>
        </li>
      </ol>
    </SectionCard>
  </section>
</template>
