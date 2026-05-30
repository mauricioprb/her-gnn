<script setup lang="ts">
import { computed } from 'vue'
import Skeleton from 'primevue/skeleton'
import Message from 'primevue/message'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import Button from 'primevue/button'

import PageHeader from '@/components/PageHeader.vue'
import StatPill from '@/components/StatPill.vue'
import SectionCard from '@/components/SectionCard.vue'
import ModelCard from '@/components/ModelCard.vue'
import MaeBarChart from '@/components/MaeBarChart.vue'
import CumulativeErrorChart from '@/components/CumulativeErrorChart.vue'
import ParityScatter from '@/components/ParityScatter.vue'
import { useComparison, useComparisonPredictions } from '@/composables'

const { data, isLoading, error, refetch } = useComparison()
const { data: preds, isLoading: loadingPreds } = useComparisonPredictions()

const sortedByR2 = computed(() =>
  [...(data.value?.models ?? [])].sort((a, b) => b.r2_test - a.r2_test),
)

const bestR2 = computed(() => Math.max(...(data.value?.models ?? []).map((m) => m.r2_test), -Infinity))
const bestMaeMeV = computed(() => Math.min(...(data.value?.models ?? []).map((m) => m.mae_meV_test), Infinity))
const bestFracChem = computed(() =>
  Math.max(...(data.value?.models ?? []).map((m) => m.frac_chem_acc_test ?? -Infinity)),
)
const bestRmse = computed(() => Math.min(...(data.value?.models ?? []).map((m) => m.rmse_test), Infinity))

function fmtR2(m: { r2_test: number; r2_test_std: number | null }) {
  return m.r2_test_std != null
    ? `${m.r2_test.toFixed(4)} ± ${m.r2_test_std.toFixed(4)}`
    : m.r2_test.toFixed(4)
}

function fmtMae(m: { mae_test: number; mae_test_std: number | null }) {
  return m.mae_test_std != null
    ? `${m.mae_test.toFixed(4)} ± ${m.mae_test_std.toFixed(4)}`
    : m.mae_test.toFixed(4)
}

function kindLabel(k: string) {
  return k === 'baseline' ? 'Baseline' : k === 'gnn' ? 'GNN' : 'Híbrido'
}

function kindSeverity(k: string): 'secondary' | 'info' | 'success' {
  return k === 'baseline' ? 'secondary' : k === 'gnn' ? 'info' : 'success'
}
</script>

<template>
  <section class="mx-auto max-w-7xl space-y-6 px-6 py-8">
    <PageHeader
      icon="pi-chart-bar"
      title="Comparação de modelos"
      subtitle="4 modelos finais avaliados no mesmo test set canônico (1.172 estruturas). Multi-seed reportado como mean ± std."
    >
      <template v-if="data">
        <StatPill icon="pi-chart-line" :value="data.models.length" label="modelos" />
        <StatPill icon="pi-asterisk" value="1.172" label="test canônico" />
        <StatPill icon="pi-bullseye" :value="`${(data.chemical_accuracy_eV * 1000).toFixed(0)} meV`" label="chemical accuracy" />
      </template>
    </PageHeader>

    <div v-if="isLoading" class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <Skeleton v-for="i in 4" :key="i" height="14rem" />
    </div>

    <Message v-else-if="error" severity="error" :closable="false">
      <div class="flex items-center justify-between gap-3">
        <span>Falha ao carregar comparação: {{ error.message }}</span>
        <Button label="Tentar novamente" icon="pi pi-refresh" size="small" @click="refetch()" />
      </div>
    </Message>

    <template v-else-if="data">
      <section class="space-y-3">
        <div class="flex items-center gap-2">
          <span class="grid h-7 w-7 place-items-center rounded-md bg-primary-500/10 text-primary-600 dark:text-primary-400">
            <i class="pi pi-th-large text-xs" />
          </span>
          <h2 class="text-sm font-semibold uppercase tracking-wider text-surface-700 dark:text-surface-200">
            Resumo por modelo
          </h2>
        </div>
        <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <ModelCard
            v-for="m in sortedByR2"
            :key="m.display"
            :model="m"
            :best-r2="bestR2"
            :best-mae-me-v="bestMaeMeV"
            :best-frac-chem="bestFracChem"
            :best-rmse="bestRmse"
          />
        </div>
      </section>

      <section class="space-y-3">
        <div class="flex items-center gap-2">
          <span class="grid h-7 w-7 place-items-center rounded-md bg-primary-500/10 text-primary-600 dark:text-primary-400">
            <i class="pi pi-chart-line text-xs" />
          </span>
          <h2 class="text-sm font-semibold uppercase tracking-wider text-surface-700 dark:text-surface-200">
            Diagnósticos cross-modelo
          </h2>
        </div>
        <div class="grid gap-4 lg:grid-cols-[1fr_1.2fr]">
          <MaeBarChart :models="data.models" :chemical-accuracy-ev="data.chemical_accuracy_eV" />
          <CumulativeErrorChart
            v-if="preds"
            :models="preds.models"
            :chemical-accuracy-ev="preds.chemical_accuracy_eV"
          />
          <div
            v-else-if="loadingPreds"
            class="grid h-full place-items-center rounded-2xl border border-surface-200 bg-surface-0 p-6 shadow-sm dark:border-surface-800 dark:bg-surface-950"
          >
            <span class="text-xs text-surface-500">Carregando curvas…</span>
          </div>
        </div>

        <div v-if="preds" class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <ParityScatter
            v-for="m in preds.models"
            :key="m.display"
            :y-true="m.y_true"
            :y-pred="m.y_pred"
            :title="m.display"
            :color="m.color"
            height="240px"
          />
        </div>
      </section>

      <SectionCard
        title="Tabela completa"
        subtitle="Ordenada por R² test. Multi-seed reportado como mean ± std (n=5)."
        icon="pi-table"
        :padded="false"
      >
        <DataTable :value="sortedByR2" striped-rows class="text-sm!">
          <Column field="display" header="Modelo">
            <template #body="{ data: row }">
              <div class="flex items-center gap-2">
                <span class="inline-block h-2.5 w-2.5 rounded-full" :style="{ backgroundColor: row.color }"></span>
                <span class="font-medium">{{ row.display }}</span>
              </div>
            </template>
          </Column>
          <Column field="kind" header="Tipo">
            <template #body="{ data: row }">
              <Tag :severity="kindSeverity(row.kind)" :value="kindLabel(row.kind)" rounded />
            </template>
          </Column>
          <Column field="r2_test" header="R² test" sortable>
            <template #body="{ data: row }">
              <span class="font-mono tabular-nums">{{ fmtR2(row) }}</span>
            </template>
          </Column>
          <Column field="mae_test" header="MAE (eV)" sortable>
            <template #body="{ data: row }">
              <span class="font-mono tabular-nums">{{ fmtMae(row) }}</span>
            </template>
          </Column>
          <Column field="rmse_test" header="RMSE (eV)" sortable>
            <template #body="{ data: row }">
              <span class="font-mono tabular-nums">{{ row.rmse_test.toFixed(4) }}</span>
            </template>
          </Column>
          <Column field="spearman_rho_test" header="Spearman ρ" sortable>
            <template #body="{ data: row }">
              <span class="font-mono tabular-nums">{{ row.spearman_rho_test?.toFixed(4) ?? '—' }}</span>
            </template>
          </Column>
          <Column field="frac_chem_acc_test" header="% < 43 meV" sortable>
            <template #body="{ data: row }">
              <span class="font-mono tabular-nums">
                {{ row.frac_chem_acc_test != null ? (row.frac_chem_acc_test * 100).toFixed(1) + '%' : '—' }}
              </span>
            </template>
          </Column>
          <Column field="n_params" header="Parâmetros" sortable>
            <template #body="{ data: row }">
              <span class="font-mono tabular-nums">
                {{ row.n_params != null ? row.n_params.toLocaleString('pt-BR') : '—' }}
              </span>
            </template>
          </Column>
          <Column field="n_seeds" header="Seeds">
            <template #body="{ data: row }">
              <span class="text-xs text-surface-500">
                {{ row.is_multiseed ? `n=${row.n_seeds}` : 'determinístico' }}
              </span>
            </template>
          </Column>
        </DataTable>
      </SectionCard>
    </template>
  </section>
</template>
