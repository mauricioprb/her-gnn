<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import MultiSelect from 'primevue/multiselect'
import SelectButton from 'primevue/selectbutton'
import Slider from 'primevue/slider'
import InputNumber from 'primevue/inputnumber'
import ToggleSwitch from 'primevue/toggleswitch'
import Button from 'primevue/button'
import Skeleton from 'primevue/skeleton'

import { useScreenStore } from '@/stores/screen'
import { useElements } from '@/composables'
import type { ModelName } from '@/api'

const emit = defineEmits<{ submit: []; reset: [] }>()
defineProps<{ submitting?: boolean }>()

const store = useScreenStore()
const { form } = storeToRefs(store)

const { data: elements, isLoading: loadingElements } = useElements()

const modelOptions: { label: string; value: ModelName; r2: string; hint: string }[] = [
  { label: 'ETR + emb',    value: 'etr_emb',  r2: 'R² 0.961', hint: 'rápido · CPU' },
  { label: 'MACE Stage A', value: 'stagea',   r2: 'R² 0.956 ± 0.002', hint: 'GNN · GPU recomendada' },
  { label: 'Ensemble',     value: 'ensemble', r2: 'média', hint: 'consenso dos dois' },
]

const canSubmit = computed(() => form.value.elements.length > 0 && form.value.top > 0)
const currentModelHint = computed(() => modelOptions.find((m) => m.value === form.value.model))

function onSubmit() {
  if (!canSubmit.value) return
  emit('submit')
}

function onKeydown(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') onSubmit()
}
</script>

<template>
  <form
    class="rounded-2xl border border-surface-200 bg-surface-0 shadow-sm dark:border-surface-800 dark:bg-surface-950"
    @submit.prevent="onSubmit"
    @keydown="onKeydown"
  >
    <div class="grid gap-0 lg:grid-cols-[1.4fr_1fr]">
      <div class="border-b border-surface-200 p-5 dark:border-surface-800 lg:border-b-0 lg:border-r">
        <div class="mb-3 flex items-center gap-2">
          <span class="grid h-6 w-6 place-items-center rounded-md bg-primary-500/10 text-primary-600 dark:text-primary-400">
            <i class="pi pi-tag text-[10px]" />
          </span>
          <h3 class="text-xs font-semibold uppercase tracking-wider text-surface-700 dark:text-surface-200">
            Composição
          </h3>
        </div>
        <Skeleton v-if="loadingElements" height="2.5rem" class="w-full!" />
        <MultiSelect
          v-else
          v-model="form.elements"
          :options="elements ?? []"
          display="chip"
          filter
          :placeholder="form.elements.length ? '' : 'Selecione os metais obrigatórios'"
          class="w-full"
          :max-selected-labels="10"
          @change="store.setForm({ elements: form.elements })"
        />
        <p class="mt-2 text-xs text-surface-500">
          Catalisadores devem conter <em>todos</em> os metais selecionados. H ignorado.
        </p>
      </div>

      <div class="p-5">
        <div class="mb-3 flex items-center gap-2">
          <span class="grid h-6 w-6 place-items-center rounded-md bg-primary-500/10 text-primary-600 dark:text-primary-400">
            <i class="pi pi-microchip-ai text-[10px]" />
          </span>
          <h3 class="text-xs font-semibold uppercase tracking-wider text-surface-700 dark:text-surface-200">
            Modelo
          </h3>
        </div>
        <SelectButton
          v-model="form.model"
          :options="modelOptions"
          option-label="label"
          option-value="value"
          :allow-empty="false"
          class="w-full"
          @change="store.setForm({ model: form.model })"
        />
        <div class="mt-2 flex items-baseline justify-between gap-2 text-xs text-surface-500">
          <span>{{ currentModelHint?.hint }}</span>
          <span class="font-mono font-semibold text-primary-700 dark:text-primary-400">
            {{ currentModelHint?.r2 }}
          </span>
        </div>
      </div>
    </div>

    <div class="grid gap-0 border-t border-surface-200 dark:border-surface-800 md:grid-cols-[1fr_auto]">
      <div class="border-b border-surface-200 p-5 dark:border-surface-800 md:border-b-0 md:border-r">
        <div class="mb-3 flex items-center justify-between gap-3">
          <div class="flex items-center gap-2">
            <span class="grid h-6 w-6 place-items-center rounded-md bg-primary-500/10 text-primary-600 dark:text-primary-400">
              <i class="pi pi-sort-amount-up text-[10px]" />
            </span>
            <h3 class="text-xs font-semibold uppercase tracking-wider text-surface-700 dark:text-surface-200">
              Quantidade de candidatos
            </h3>
          </div>
          <InputNumber
            v-model="form.top"
            :min="1"
            :max="500"
            show-buttons
            button-layout="horizontal"
            :step="1"
            :input-style="{ width: '3.5rem', textAlign: 'center' }"
            @update:model-value="store.setForm({ top: form.top })"
          />
        </div>
        <Slider
          v-model="form.top"
          :min="5"
          :max="100"
          :step="1"
          @change="store.setForm({ top: form.top })"
        />
        <div class="mt-1 flex justify-between text-[10px] tabular-nums text-surface-400">
          <span>5</span><span>25</span><span>50</span><span>75</span><span>100</span>
        </div>
      </div>

      <div class="flex flex-col gap-2 p-5">
        <div class="mb-1 flex items-center gap-2">
          <span class="grid h-6 w-6 place-items-center rounded-md bg-primary-500/10 text-primary-600 dark:text-primary-400">
            <i class="pi pi-filter text-[10px]" />
          </span>
          <h3 class="text-xs font-semibold uppercase tracking-wider text-surface-700 dark:text-surface-200">
            Filtros
          </h3>
        </div>
        <label class="flex items-start gap-3">
          <ToggleSwitch
            v-model="form.exclude_train"
            @change="store.setForm({ exclude_train: form.exclude_train })"
          />
          <span class="text-xs leading-snug">
            <span class="block font-medium text-surface-700 dark:text-surface-200">Excluir conjunto de treino</span>
            <span class="block text-[11px] text-surface-500">
              Restringe ao test canônico (1172 IDs). Evita predições memorizadas.
            </span>
          </span>
        </label>
      </div>
    </div>

    <footer
      class="flex flex-wrap items-center justify-between gap-3 rounded-b-2xl border-t border-surface-200 bg-surface-50 px-5 py-3 dark:border-surface-800 dark:bg-surface-900/60"
    >
      <div class="flex items-center gap-3 text-[11px] text-surface-500">
        <span>
          Atalho:
          <kbd class="rounded border border-surface-300 bg-surface-0 px-1.5 py-0.5 text-[10px] font-mono dark:border-surface-700 dark:bg-surface-950">Ctrl</kbd>
          +
          <kbd class="rounded border border-surface-300 bg-surface-0 px-1.5 py-0.5 text-[10px] font-mono dark:border-surface-700 dark:bg-surface-950">Enter</kbd>
        </span>
      </div>
      <div class="flex items-center gap-2">
        <Button
          type="button"
          label="Restaurar"
          icon="pi pi-refresh"
          severity="secondary"
          text
          size="small"
          @click="emit('reset')"
        />
        <Button
          type="submit"
          :label="submitting ? 'Processando…' : 'Triar candidatos'"
          icon="pi pi-search"
          icon-pos="right"
          :loading="submitting"
          :disabled="!canSubmit || submitting"
        />
      </div>
    </footer>
  </form>
</template>
