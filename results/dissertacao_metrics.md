# Métricas

Dataset: 5.860 estruturas HER do Catalysis Hub
Split: 4.220 treino / 468 validação / 1.172 teste (canônico por id, seed=42)
Target: ΔG_H\* (eV) ∈ [-2, 2]
GPU: NVIDIA GeForce RTX 5060 Ti 16 GB
Referência: Wang et al. (2025), npj Computational Materials 11:111 - R²=0.922 (ETR, 10 features)

---

## Legenda: tipos de modelo

| Termo                    | Significado                                                                                                                                                                                                     |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ETR**                  | Extremely Randomized Trees (scikit-learn). Modelo de árvore, não é rede neural.                                                                                                                                 |
| **MACE**                 | Message-passing Atomic Cluster Expansion. GNN equivariante 3D para sistemas atômicos.                                                                                                                           |
| **MACE-MP-0**            | MACE pré-treinado no Materials Project / Open Catalyst Project (milhões de estruturas).                                                                                                                         |
| **SchNet**               | GNN para materiais treinada do zero (sem pré-treino) nos 5.860 exemplos do Catalysis Hub.                                                                                                                       |
| **Backbone**             | Corpo principal da rede neural (MACE: message passing + interações equivariantes, 4.7M parâmetros).                                                                                                             |
| **Cabeça (MLP head)**    | Camadas finais que mapeiam os embeddings de nó → predição de ΔG_H\*.                                                                                                                                            |
| **Congelado (frozen)**   | Os pesos do backbone **não são atualizados** durante o treino. Só a cabeça aprende. O backbone só faz inferência (forward pass), usando conhecimento pré-treinado. Ideal para poucos dados - evita overfitting. |
| **Completo (full)**      | O backbone **inteiro é treinado** junto com a cabeça (fine-tune end-to-end). Requer mais VRAM e mais dados; risco de overfitting com datasets pequenos.                                                         |
| **Híbrido**              | Combinação de GNN como extrator de features + modelo clássico (ETR) como preditor. A GNN **não é treinada** na tarefa-alvo - só extrai representações.                                                          |
| **GNN pura**             | A rede neural **é o modelo preditivo**: recebe a estrutura 3D e produz ΔG_H\* diretamente. É a abordagem proposta pela dissertação.                                                                             |
| **Features handcrafted** | Descritores eletrônicos/estruturais calculados manualmente (10 features de Wang et al.), sem uso de aprendizado profundo.                                                                                       |
| **Embeddings**           | Vetores latentes extraídos das camadas internas do MACE-MP-0 (640 dimensões por átomo). Capturam o ambiente químico local.                                                                                      |
| **SHAP**                 | SHapley Additive exPlanations - método para medir importância de cada feature na predição.                                                                                                                      |
| **PCA**                  | Principal Component Analysis - redução de dimensionalidade linear.                                                                                                                                              |

---

## Resultados principais

| Modelo                                            |  R² test  |  MAE  | RMSE  | # Params |    Tipo    |
| ------------------------------------------------- | :-------: | :---: | :---: | :------: | :--------: |
| **ETR + MACE embeddings (512-dim, frozen)**       | **0.961** | 0.071 | 0.123 |    -     |  Híbrido   |
| ETR + MACE PCA 99% (77 comp)                      |   0.960   | 0.077 | 0.125 |    -     |  Híbrido   |
| ETR + MACE top-50 SHAP                            |   0.958   | 0.077 | 0.129 |    -     |  Híbrido   |
| ETR + MACE PCA 90% (26 comp)                      |   0.956   | 0.080 | 0.131 |    -     |  Híbrido   |
| ETR + MACE top-20 SHAP                            |   0.952   | 0.085 | 0.138 |    -     |  Híbrido   |
| **MACE fine-tune Stage A (frozen + MLP 2-layer)** | **0.947** | 0.083 | 0.144 |   328K   |    GNN     |
| MACE fine-tune Stage A+ (frozen + MLP 3-layer)    |   0.945   | 0.072 | 0.148 |   919K   |    GNN     |
| MACE fine-tune Stage C (full fine-tune)           |   0.940   | 0.084 | 0.153 |   5.0M   |    GNN     |
| ETR + MACE top-10 SHAP                            |   0.940   | 0.096 | 0.154 |    -     |  Híbrido   |
| ETR + 10 features handcrafted (Wang et al.)       |   0.934   | 0.096 | 0.161 |    -     |  Baseline  |
| Paper Wang et al. (2025)                          |   0.922   |   -   | 0.186 |    -     | Referência |
| SchNet (GNN treinada do zero)                     |   0.908   | 0.060 | 0.190 |   456K   |    GNN     |
| ETR + MACE escalares (7 feat)                     |   0.864   | 0.158 | 0.231 |    -     |  Baseline  |

---

## Ablação - Redução de dimensionalidade nos embeddings MACE

| Estratégia          | # Features | R² test |  MAE  | RMSE  |
| ------------------- | :--------: | :-----: | :---: | :---: |
| Todos os embeddings |    512     |  0.961  | 0.071 | 0.123 |
| Top-100 SHAP        |    100     |  0.961  | 0.073 | 0.124 |
| Top-50 SHAP         |     50     |  0.958  | 0.077 | 0.129 |
| PCA 99% var         |     77     |  0.960  | 0.077 | 0.125 |
| PCA 95% var         |     38     |  0.957  | 0.079 | 0.130 |
| PCA 90% var         |     26     |  0.956  | 0.080 | 0.131 |
| Top-20 SHAP         |     20     |  0.952  | 0.085 | 0.138 |
| Top-10 SHAP         |     10     |  0.940  | 0.096 | 0.154 |

---

## Ablação - Redução de features escalares MACE (7 feat)

| Estratégia             | # Features | R² test |  MAE  | RMSE  |
| ---------------------- | :--------: | :-----: | :---: | :---: |
| Todas 7 (RFE)          |     7      |  0.864  | 0.158 | 0.231 |
| Top-5 SHAP             |     5      |  0.863  | 0.160 | 0.232 |
| PCA 99% var            |     5      |  0.846  | 0.172 | 0.246 |
| PCA 95% var            |     4      |  0.837  | 0.185 | 0.253 |
| PCA 90% var            |     3      |  0.816  | 0.202 | 0.269 |
| Top-3 SHAP             |     3      |  0.807  | 0.210 | 0.275 |
| Composição (análogo φ) |     16     |  0.863  | 0.162 | 0.232 |

---

## Fine-tune MACE (GNN end-to-end)

| Estágio  | Backbone  |                   Cabeça                   | R² test |  MAE  | RMSE  | Params | Tempo  |
| -------- | :-------: | :----------------------------------------: | :-----: | :---: | :---: | :----: | :----: |
| Stage A  | Congelado |          MLP 2-layer (1280→256→1)          |  0.947  | 0.083 | 0.144 |  328K  | 12 min |
| Stage A+ | Congelado | MLP 3-layer (1280→512→256→1) + dropout 0.1 |  0.945  | 0.072 | 0.148 |  919K  | 33 min |
| Stage C  | Completo  |                MLP 2-layer                 |  0.940  | 0.084 | 0.153 |  5.0M  | 48 min |

---

## Extração de features MACE-MP-0

| Tipo                          |   Features    | Dim |  Tempo  |  VRAM   |
| ----------------------------- | :-----------: | :-: | :-----: | :-----: |
| Escalares (per-atom energies) |       7       |  -  | 3.7 min | 0.64 GB |
| Embeddings invariantes de nó  | 256 × 2 = 512 |  -  | 6.3 min | 0.64 GB |

---

## Visualização hierárquica dos resultados

```
                    ETR + MACE embeddings (Congelado)
                              0.961  ← teto de informação
                              │
    ┌─────────────────────────┤
    │                         │
MACE Stage A (GNN pura)    ETR + PCA 90%
    0.947                     0.956
    │                         │
    ├─────────────────────┐   │
    │                     │   │
MACE Stage C (full)   ETR handcrafted  ETR + top-20
    0.940                 0.934          0.952
    │
SchNet (GNN do zero)
    0.908
```

---

## Hipótese

Uma GNN equivariante pré-treinada (MACE-MP-0) com fine-tune supera
modelos baseados em features manuais na predição de ΔG_H\* para
catalisadores HER.

## Evidência

1. O baseline ETR + 10 features handcrafted atinge R²=0.934,
   superando o paper de referência (0.922).
2. Uma GNN treinada do zero (SchNet) fica abaixo (0.908) -
   o pré-treino é essencial.
3. Embeddings invariantes congelados do MACE + ETR atingem R²=0.961,
   estabelecendo o teto de informação acessível nos dados.
4. O fine-tune do MACE com cabeça MLP (Stage A) atinge R²=0.947,
   confirmando a hipótese: a GNN pré-treinada supera o baseline
   handcrafted (0.934) e o paper (0.922) sem usar features manuais.
5. A redução de dimensionalidade mostra que 10-20 dimensões dos
   embeddings já superam as 10 features handcrafted, demonstrando
   a superioridade da representação aprendida.

## Limitações

- Dataset de 5.860 estruturas (vs 10.855 do paper) devido a
  limitações da API do Catalysis Hub.
- O ETR sobre embeddings congelados (0.961) supera a MLP (0.947),
  sugerindo que modelos baseados em árvore extraem mais informação
  de representações de alta dimensionalidade com poucos exemplos.
- Full fine-tune (Stage C) sofre de overfitting com 5M parâmetros.
