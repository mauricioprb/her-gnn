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

| Modelo | R² test | MAE test | RMSE test | # feat/params |
|--------|---------|----------|-----------|---------------|
| **ETR + MACE embeddings** | **0.961** | 0.072 | — | 512 |
| ETR + MACE emb (top-20)   | 0.952 | 0.085 | — | 20 |
| ETR (10 features handcrafted) | 0.934 | 0.096 | 0.161 | 10 |
| SchNet (do zero)          | 0.908 | 0.060 | 0.190 | 455.809 |
| ETR + MACE escalares      | 0.864 | 0.158 | — | 7 |

Ordenacao final: **embeddings MACE > handcrafted > SchNet > escalares MACE**.
Os embeddings de no do MACE-MP-0 (potencial de fundacao) sao a melhor
representacao para HER neste dataset; ate top-10 dims ja supera as 10 features
handcrafted. SchNet do zero (sem pretraining) fica abaixo, confirmando que o
ganho vem da representacao pre-treinada, nao so da arquitetura GNN.

Nota: o R² do ETR re-ancorou de 0.910 (Etapa 1, ordem de linha pre-dedupe) para
0.934 ao fixar o split canonico por id (`data/splits.json`), agora reproduzivel e
compartilhado com todos os modelos. O `train_test_split` original dependia da
ordem das linhas do SQLite, que mudou no rebuild com deduplicacao.

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
# Etapa 3 - Tarefa 2 / Fase A.5 / Fase B
uv run python scripts/07_extract_mace_features.py            # escalares MACE (GPU)
uv run python scripts/08b_feature_reduction_sweep.py         # sweep escalares (Fase A.5)
uv run python scripts/09_extract_mace_embeddings.py          # embeddings 512-dim (GPU)
uv run python scripts/08b_feature_reduction_sweep.py --feature-set emb   # sweep embeddings (Fase B)
```

Toda metrica fica em `results/runs/{timestamp}_{name}/` (config.yaml, metrics.json,
predictions.parquet, figures/, env.txt) e e agregada em `results/summary.json`.

## Etapa 3 - Tarefa 2: extracao de features MACE-MP-0

Extrai descritores do potencial de fundacao MACE-MP-0 (medium) para cada
estrutura, em `data/mace_features/{train,val,test}.npz`, alinhados ao split
canonico (`splits.json`; val recortado do train como no SchNet).

```bash
uv run python scripts/07_extract_mace_features.py   # ~10 min na RTX 5060 Ti
```

7 features escalares por estrutura (energias per-atom do MACE):
`mace_E_total`, `mace_E_per_atom`, `mace_E_H`, `mace_E_neighbors_mean`,
`mace_E_neighbors_min`, `mace_E_surface_mean`, `mace_n_neighbors`. Embeddings de
no ficam adiados (a API expoe energias per-atom facilmente; embeddings exigem
forward manual) — escalares ja bastam para a EDA da Fase A.5. Idempotente
(`--force` para reextrair). Stats em `results/runs/{ts}_mace_extraction/feature_stats.json`.
Validacao + smoke: `notebooks/07_mace_smoke.ipynb`.

## Etapa 3 - Fase A.5: EDA e reducao de features MACE

EDA, importancia (SHAP/permutation/RFE) e sweep de reducao sobre as 7 features
escalares. `notebooks/08_mace_features_eda.ipynb` +
`scripts/08b_feature_reduction_sweep.py` (gera 8 runs + grafico R² vs #features).

```bash
uv run python scripts/08b_feature_reduction_sweep.py   # ~6 min, sem GPU
```

Sweep (ETR, split canonico, vs baselines ETR-handcrafted=0.934 e SchNet=0.908):

| Estrategia | # feat | R² test |
|------------|--------|---------|
| all / RFE  | 7 | 0.864 |
| top-5 SHAP | 5 | 0.863 |
| top-3 SHAP | 3 | 0.807 |
| PCA 99% var| 5 | 0.846 |
| PCA 95% var| 4 | 0.837 |
| PCA 90% var| 3 | 0.816 |
| composicao | 16 | 0.863 |

SHAP: `mace_E_H` (0.23) >> `E_neighbors_mean` (0.15) ~ `E_neighbors_min` (0.14)
>> `n_neighbors` (0.06) >> energias globais (`E_total`/`E_per_atom`/`E_surface_mean`,
~0.02 cada). A energia de ligacao do H e suas vizinhancas carregam quase toda a
informacao.

### Achado e decisao (Fase B)

- **Numero final de features: 5** (`E_H`, `E_neighbors_mean`, `E_neighbors_min`,
  `n_neighbors` + 1). Estrategia vencedora: **top-5 por SHAP** (R²=0.863, contra
  0.864 com todas — perda desprezivel cortando as 3 energias globais redundantes).
  PCA nunca supera top-K; composicao (analogia ao phi) nao gerou nada melhor.
- **Porem o teto das 7 escalares (0.864) fica abaixo dos baselines** (ETR-handcrafted
  0.934, SchNet 0.908). Energias per-atom do MACE-MP-0, sozinhas, sao menos
  preditivas que os descritores eletronicos handcrafted para HER.
- **Decisao: vale ir para a Fase B.** Como ate o conjunto completo de escalares
  nao alcanca os baselines (features complementares, nao redundantes — heuristica
  do prompt), o ganho deve vir dos **embeddings de no do MACE** (adiados na
  Tarefa 2) e/ou fine-tune. Proximo passo concreto: extrair os embeddings
  invariantes do MACE e repetir esta EDA no espaco ~300-dim antes de decidir
  fine-tune.
- **Validacao cross-model (MLP)**: top-5 (0.817) >= all (0.812) > top-3 (0.783),
  mesma ordem do ETR — o achado "5 features bastam, 3 globais sao redundantes"
  nao e especifico ao tipo de modelo.

## Etapa 3 - Fase B: embeddings de no do MACE

A Fase A.5 mostrou que os escalares nao bastam, entao extraimos os **embeddings
de no invariantes (L=0) do MACE-MP-0** e repetimos a EDA/sweep no espaco 512-dim.

```bash
uv run python scripts/09_extract_mace_embeddings.py          # ~6 min GPU -> *_emb.npz
uv run python scripts/08b_feature_reduction_sweep.py --feature-set emb
```

Pooling: `[emb(H), mean(emb(vizinhos<2.4A))]` dos descritores invariantes ->
512 features. Agora samples/features ~9, entao a reducao importa de fato.

| Estrategia | # feat | R² test |
|------------|--------|---------|
| all        | 512 | 0.961 |
| top-100 SHAP | 100 | 0.961 |
| top-50 SHAP  | 50 | 0.958 |
| top-20 SHAP  | 20 | 0.952 |
| top-10 SHAP  | 10 | 0.940 |
| PCA 99% var  | 77 | 0.960 |
| PCA 95% var  | 38 | 0.957 |
| PCA 90% var  | 26 | 0.956 |

SHAP: as dimensoes do embedding do **H adsorvido** (`embH_*`) dominam — coerente
com `mace_E_H` ser a escalar mais importante.

### Achado e decisao

- **Os embeddings MACE batem todos os baselines** (0.961 vs handcrafted 0.934,
  SchNet 0.908, escalares 0.864). Mesmo **top-10 dims (0.940) > 10 handcrafted**.
- **Numero recomendado: top-20 (0.952)** — sweet spot interpretabilidade/acuracia;
  top-50 (0.958) se quiser quase o teto. PCA 90% (26 comp, 0.956) tambem otimo.
- **Decisao: representacao MACE pre-treinada e o caminho.** A cabeca leve (ETR)
  sobre embeddings frozen ja e o melhor modelo do projeto, sem fine-tune. Proximo
  passo opcional: fine-tune end-to-end do MACE pode dar ganho marginal, mas o
  embedding frozen ja supera tudo — o custo/beneficio do fine-tune e questionavel
  e pode ser discutido como secao da dissertacao.

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
