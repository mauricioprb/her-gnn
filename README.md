# her-gnn

Dissertacao: predicao de catalisadores de HER (Hydrogen Evolution Reaction).
Etapa 1 = baseline Extra Trees sobre 10 features (replica Wang et al., npj Comput.
Mater. (2025) 11:111, [DOI 10.1038/s41524-025-01607-4](https://doi.org/10.1038/s41524-025-01607-4)).
Etapa 2 = SchNet (GNN) sobre os mesmos dados, com comparacao honesta (mesmo split).

## Reproducao (5 comandos)

Gerenciado por [uv](https://docs.astral.sh/uv/) (Python 3.14):

```bash
uv sync                                          # 1. ambiente
uv run python scripts/01_download.py             # 2. dump bruto do Catalysis Hub
uv run python scripts/02_build_dataset.py        # 3. .traj + LMDB + SQLite (filtros + features)
uv run python scripts/03_train_baseline.py       # 4. treina ETR, metricas, figuras
uv run jupyter lab                               # 5. notebooks exploratorios
```

`01_download.py` usa duas passadas: metadata de ~60k reacoes `products="H"`,
depois estruturas so das ~9k reacoes HER limpas (`0.5H2(g) + * -> H*`) que
passam os filtros de metadata (~15min). Saidas: `data/raw/`,
`data/processed/her_dataset.traj`, `data/lmdb/her_dataset.lmdb`,
`data/metadata.sqlite`, `data/figures/`.

## Resultados

5860 estruturas curadas, mesmo split de teste (1172) para ambos os modelos.
Fonte auditavel: `results/summary.json` (gerado pelos scripts, sem retreinar).

| Modelo | R² test | MAE test | RMSE test | # params |
|--------|---------|----------|-----------|----------|
| ETR (10 features) | 0.934 | 0.096 | 0.161 | — |
| SchNet (do zero)  | 0.908 | 0.060 | 0.190 | 455.809 |

SchNet (sem pretraining) iguala o ETR: R² um pouco menor (0.908 vs 0.934) mas
MAE menor (0.060 vs 0.096). Responde a pergunta de banca: a arquitetura sozinha
ja chega ao baseline de features; o ganho esperado do pretraining fica para a
Etapa 3. VRAM pico no treino: 0.39 GB (batch 32).

Nota: o R² do ETR re-ancorou de 0.910 (Etapa 1, ordem de linha pre-dedupe) para
0.934 ao fixar o split canonico por id (`data/splits.json`), agora reproduzivel e
compartilhado com o SchNet. O `train_test_split` original dependia da ordem das
linhas do SQLite, que mudou no rebuild com deduplicacao.

## Como reproduzir metricas

```bash
uv sync
# Etapa 1
uv run python scripts/01_download.py
uv run python scripts/02_build_dataset.py
uv run python scripts/03_train_baseline.py     # ETR -> results/runs/{ts}_etr_baseline
# Etapa 2 (GPU obrigatoria)
uv run python scripts/04_build_graphs.py        # grafos PyG + data/splits.json
uv run python scripts/05_train_schnet.py --smoke           # checagem rapida (<2min)
uv run python scripts/05_train_schnet.py --run-name schnet_baseline
uv run python scripts/06_compare.py             # tabela + figuras (sem GPU, <30s)
```

Toda metrica fica em `results/runs/{timestamp}_{name}/` (config.yaml, metrics.json,
predictions.parquet, figures/, env.txt) e e agregada em `results/summary.json`.

## Pipeline

- `ingest.py` - query GraphQL (metadata + busca por id em lote) + reconstrucao
  de `ase.Atoms` (sistema `Hstar`)
- `filters.py` - equacao HER limpa (`0.5H2(g) + * -> H*`, exclui co-adsorcao
  H2S/NH3/...), `delta_G in [-2,2]`, cobertura <= 25%, ligacao H-superficie
  em [1,3] A; sitio (top/bridge/hollow) por coordenacao do H em 2.4 A
- `features.py` - as 10 features (medias geometricas via `mendeleev`)
- `geometry.py` - atomos centrais (2.4 A do H) e vizinhos (1a camada, raios
  covalentes)
- `storage.py` - `.traj`, LMDB (estilo fairchem) e SQLite, com IDs alinhados
- `baseline.py` - ExtraTrees, split 80/20, GridSearchCV 10-fold, R2/MAE/MSE/RMSE
- `plots.py` - Fig. 3b (histograma), 4f (parity), 6d (SHAP)

Etapa 2 (GNN), so arquivos novos, Etapa 1 intacta:

- `data/graph_builder.py` - `ase.Atoms` -> `Data` PyG; arestas PBC-aware via
  `neighbor_list("ijdS")` com `pbc=[True,True,False]` (sem cruzar vacuo em z)
- `data/dataset.py` - `HERDataset(InMemoryDataset)`, cacheia `her_pyg.pt` (idempotente)
- `data/splits.py` - split canonico por id (mesmo do ETR), `data/splits.json`
- `models/schnet.py` - `LitSchNet`; forward usa arestas precomputadas (PBC, dispensa
  `torch-cluster`), alvo normalizado, metricas via `torchmetrics`
- `training/run_logger.py` - `RunLogger`: cria `results/runs/{...}` e popula
- `training/train.py`, `training/evaluate.py` - loop Lightning + metricas/parity

Notebooks (`01` explora, `02` filtros/features, `03` baseline, `04` grafos)
importam de `src/her_gnn`, sem duplicar logica.

### Desvios documentados do paper

- Vizinhos e CN usam lista de vizinhanca por raios covalentes (o cutoff de
  2.4 A do paper define so os atomos centrais; e curto demais para a 1a camada
  metal-metal).
- `Out_e` = `nvalence` do mendeleev (consistente por grupo); `Nd`/`Np` =
  contagem total de eletrons d/p.
- Contagem final (5860) fica abaixo dos 10.855 do paper: a API do Catalysis Hub
  limita paginas a 200 itens e o cursor padrao repete/pula registros; o snapshot
  de 2025 do paper nao e reproduzivel hoje. A paginacao de metadata usa
  `order:"id"` e deduplica por id. O alvo principal (R2 >= 0.90) foi atingido.

### GPU

Etapa 2 exige CUDA (treino na RTX 5060 Ti 16GB). `scripts/05_train_schnet.py`
falha ruidosamente se CUDA ausente, usa `precision="16-mixed"` e reporta VRAM
pico. SchNet com batch=32 fica < 1 GB de VRAM neste dataset.

## Estrutura

```
src/her_gnn/   ingest, filters, features, geometry, storage, baseline, plots, dataset
               data/ (graph_builder, dataset, splits), models/ (schnet),
               training/ (run_logger, train, evaluate)
notebooks/     01 explora, 02 filtros/features, 03 baseline, 04 grafos
scripts/       01_download, 02_build_dataset, 03_train_baseline,
               04_build_graphs, 05_train_schnet, 06_compare
data/          raw, processed (.traj + her_pyg.pt), lmdb, figures, metadata.sqlite
results/       runs/{ts}_{name}/ + summary.json (metricas auditaveis)
```
