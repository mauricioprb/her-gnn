<script setup lang="ts">
import { computed } from "vue";
import Tag from "primevue/tag";
import type { ModelComparisonRow } from "@/api";

const props = defineProps<{
  model: ModelComparisonRow;
  bestR2: number;
  bestMaeMeV: number;
  bestFracChem: number;
  bestRmse: number;
}>();

const isBestR2 = computed(() => Math.abs(props.model.r2_test - props.bestR2) < 1e-9);
const isBestMae = computed(() => Math.abs(props.model.mae_meV_test - props.bestMaeMeV) < 1e-6);
const isBestFrac = computed(
  () =>
    props.model.frac_chem_acc_test != null &&
    Math.abs(props.model.frac_chem_acc_test - props.bestFracChem) < 1e-9,
);
const isBestRmse = computed(() => Math.abs(props.model.rmse_test - props.bestRmse) < 1e-9);

const kindStyle = computed(() => {
  switch (props.model.kind) {
    case "baseline":
      return { label: "Simples", severity: "secondary" as const };
    case "gnn":
      return { label: "Rede neural", severity: "info" as const };
    case "hybrid":
      return { label: "Combinado", severity: "success" as const };
    default:
      return { label: props.model.kind, severity: "secondary" as const };
  }
});

function fmt(n: number | null, digits = 3) {
  return n == null ? "n/d" : n.toFixed(digits);
}

function fmtInt(n: number | null) {
  return n == null ? "n/d" : n.toLocaleString("pt-BR");
}

const accentStyle = computed(() => ({
  borderTopColor: props.model.color,
}));
</script>

<template>
  <article
    class="relative flex flex-col rounded-xl border border-surface-200 bg-surface-0 p-5 shadow-sm transition hover:shadow-md dark:border-surface-800 dark:bg-surface-950 border-t-4"
    :style="accentStyle"
  >
    <header class="mb-4 flex items-start justify-between gap-2">
      <div>
        <h3 class="text-sm font-semibold leading-tight">{{ model.display }}</h3>
        <p class="mt-0.5 text-xs text-surface-500">
          {{ model.is_multiseed ? `média de ${model.n_seeds} testes` : "teste único" }}
        </p>
      </div>
      <Tag
        :severity="kindStyle.severity"
        :value="kindStyle.label"
        rounded
        class="shrink-0 whitespace-nowrap"
      />
    </header>

    <div class="mb-4 rounded-lg bg-surface-50 px-3 py-2.5 dark:bg-surface-900/50">
      <div class="text-2xs font-medium uppercase tracking-wide text-surface-500">Precisão</div>
      <div class="mt-0.5 flex items-baseline gap-1.5 font-mono tabular-nums">
        <span
          class="text-2xl font-semibold"
          :class="
            isBestR2
              ? 'text-primary-600 dark:text-primary-400'
              : 'text-surface-900 dark:text-surface-0'
          "
        >
          {{ fmt(model.r2_test, 4) }}
        </span>
        <span v-if="model.r2_test_std != null" class="text-2xs text-surface-500"
          >± {{ model.r2_test_std.toFixed(4) }}</span
        >
        <i v-if="isBestR2" class="pi pi-star-fill text-xs text-amber-500" title="melhor" />
      </div>
    </div>

    <dl class="divide-y divide-surface-100 text-sm dark:divide-surface-800/70">
      <div class="flex items-center justify-between py-2">
        <dt class="text-xs text-surface-500">Erro médio</dt>
        <dd class="flex items-baseline gap-1 font-mono tabular-nums">
          <span :class="isBestMae ? 'font-semibold text-primary-600 dark:text-primary-400' : ''"
            >{{ model.mae_meV_test.toFixed(0) }} meV</span
          >
          <span v-if="model.mae_test_std != null" class="text-2xs text-surface-400"
            >± {{ (model.mae_test_std * 1000).toFixed(0) }}</span
          >
          <i v-if="isBestMae" class="pi pi-star-fill text-2xs text-amber-500" />
        </dd>
      </div>

      <div class="flex items-center justify-between py-2">
        <dt class="text-xs text-surface-500">Erro típico</dt>
        <dd class="flex items-baseline gap-1 font-mono tabular-nums">
          <span :class="isBestRmse ? 'font-semibold text-primary-600 dark:text-primary-400' : ''"
            >{{ fmt(model.rmse_test, 4) }} eV</span
          >
          <i v-if="isBestRmse" class="pi pi-star-fill text-2xs text-amber-500" />
        </dd>
      </div>

      <div class="flex items-center justify-between py-2">
        <dt class="text-xs text-surface-500">% quase exatos</dt>
        <dd class="flex items-baseline gap-1 font-mono tabular-nums">
          <span :class="isBestFrac ? 'font-semibold text-primary-600 dark:text-primary-400' : ''">{{
            model.frac_chem_acc_test != null
              ? (model.frac_chem_acc_test * 100).toFixed(1) + "%"
              : "n/d"
          }}</span>
          <i v-if="isBestFrac" class="pi pi-star-fill text-2xs text-amber-500" />
        </dd>
      </div>

      <div class="flex items-center justify-between py-2">
        <dt class="text-xs text-surface-500">Acerto na ordem</dt>
        <dd class="font-mono tabular-nums">{{ fmt(model.spearman_rho_test, 4) }}</dd>
      </div>

      <div class="flex items-center justify-between py-2">
        <dt class="text-xs text-surface-500">Complexidade</dt>
        <dd class="font-mono tabular-nums">{{ fmtInt(model.n_params) }}</dd>
      </div>
    </dl>
  </article>
</template>
