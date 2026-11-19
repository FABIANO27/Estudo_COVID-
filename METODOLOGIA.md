# Metodologia

## 1. Definições (SIVEP-Gripe)

| Indicador | Definição | Campo |
|---|---|---|
| **Casos** | Registros de SRAG hospitalizada com classificação final "SRAG por covid-19", semanas epidemiológicas 1 a 47 nos dois anos | `CLASSI_FIN = 5`, `SEM_NOT <= 47` |
| **Internados** | Casos com internação registrada | `HOSPITAL = 1` |
| **Em UTI** | Internados que passaram por UTI | `UTI = 1` |
| **Óbitos** | Evolução "óbito" (não inclui "óbito por outras causas") | `EVOLUCAO = 2` |
| **Ventilação invasiva** | Uso de suporte ventilatório invasivo | `SUPORT_VEN = 1` |
| **Letalidade** | Óbitos ÷ casos × 100. Casos sem desfecho entram no denominador; o valor pode estar subestimado | |

- O ano de cada registro é o ano do arquivo (`INFLUD25` = 2025).
- A semana 47 de 2026 está incompleta (2 casos na base de 16/11/2026); os totais de 2026 estão subestimados e podem mudar.
- Casos leves não aparecem aqui: o SIVEP-Gripe cobre SRAG hospitalizada. Os 118.851 casos de síndrome gripal divulgados pelo Ministério da Saúde são de outro sistema.

### Resultados (base de 16/11/2026, semanas 1 a 47)

| | 2025 | 2026 |
|---|---|---|
| Casos | 16.701 | 5.888 |
| Internados | 16.038 | 5.582 |
| Em UTI | 5.266 | 1.758 |
| Óbitos | 2.616 | 753 |
| Letalidade | 15,7% | 12,8% |

## 2. Dias médios de internação (SIVEP-Gripe)
Script: `src/calcular_dias_medios_sivep.py`. Internados com datas válidas (0 a 120 dias):
- **Dias totais** = `DT_EVOLUCA` − `DT_INTERNA`.
- **Dias de UTI** = `DT_SAIDUTI` − `DT_ENTUTI`, só para `UTI = 1`.
- **Dias de enfermaria** = dias totais − dias de UTI (calculado para todos os internados).

| Média de dias | 2025 | 2026 | Usado no simulador |
|---|---|---|---|
| Enfermaria | 8,0 | 8,1 | 8,0 |
| UTI | 9,1 | 8,1 | 8,9 (média ponderada pelo nº de pacientes com datas) |

Cobertura: 14.389 de 16.038 internados (2025) e 4.620 de 5.582 (2026) têm as datas de internação e desfecho; só 3.179 (2025) e 944 (2026) dos pacientes de UTI têm as duas datas de UTI. As **medianas são menores** (4 dias em enfermaria e 5 em UTI): poucos casos longos puxam a média. Casos ainda internados ficam de fora, então as médias de 2026 podem estar subestimadas.

## 3. Diária de UTI: custo FHEMIG (R$ 3.445)
Fonte: Alemão et al., 2022 (ver `FONTES.md`). Custo por paciente/dia na UTI covid em 2020, ponderado pelos pacientes/dia de cada hospital:

| Hospital | Custo por paciente/dia | Pacientes/dia | Tabela do artigo |
|---|---|---|---|
| HJK | R$ 2.995,93 | 4.546 | 2 |
| HRJP | R$ 3.629,53 | 4.975 | 6 |
| HEM | R$ 3.607,99 | 6.888 | 8 |

Média ponderada = (2.995,93 × 4.546 + 3.629,53 × 4.975 + 3.607,99 × 6.888) ÷ 16.409 ≈ **R$ 3.445**.
Ficaram de fora o HRBJA (R$ 15.029,79, apenas 14 pacientes e leitos ociosos) e o HRAD (R$ 2.910,50, sem o dado de pacientes/dia para ponderar). Os próprios autores resumem o resultado como cerca de R$ 3.600 (HEM e HRJP) e cerca de R$ 3.000 (HJK e HRAD).

## 4. Diária de enfermaria: valor pago pelo SUS (R$ 89)
O artigo da FHEMIG não traz custo de enfermaria (ver lacuna em `FONTES.md`). Usou-se o valor **pago** pelo SUS no SIH.

**Extração** (`src/sih/`):
1. `dbc2dbf.c` descompacta os arquivos `.dbc` (cabeçalho DBF + dados comprimidos em formato PKWare DCL). Validação: no arquivo de ES de jan/2025 o tamanho do `.dbf` gerado é igual a cabeçalho + registros × tamanho do registro; os demais 83 arquivos foram descompactados sem erro (não verificados um a um).
2. `extrair_covid_sih.py` filtra as AIH de covid.
3. `calcular_diarias.py` calcula as diárias.

**Definição de covid no SIH:** diagnóstico principal `B34.2` (ou `U07*`). Nos arquivos amostrados para essa verificação (MG 03/2026 e SP 03/2025) **não havia registros com `U07`** nem com o procedimento específico de covid (0303010223); a checagem não foi repetida nos 84 arquivos. O recorte é, portanto, pequeno e pode deixar casos de fora. Resultado: 1.654 AIH (todas com `IDENT = 1`) em ES, MG, RJ e SP, de jan/2025 a set/2026.

**Fórmulas:**
- Diária UTI paga = Σ `VAL_UTI` ÷ Σ `UTI_MES_TO`, nas AIH com `UTI_MES_TO > 0` (250 AIH, 1.790 dias).
- Diária de enfermaria paga = (Σ `VAL_TOT` − Σ `VAL_UTI`) ÷ (Σ `DIAS_PERM` − Σ dias de UTI), nas AIH com `DIAS_PERM >= dias de UTI` (8.178 dias fora da UTI).

| Sudeste, jan/2025 a set/2026 | Valor |
|---|---|
| Diária de UTI paga | R$ 690,49 (R$ 600 a R$ 757 por UF e ano) |
| Diária de enfermaria paga | **R$ 89,05** (R$ 54 a R$ 102 por UF e ano) |
| Valor médio por AIH | R$ 1.210,32 |
| Permanência média | 6,0 dias |

Detalhe por UF e ano em `data/sih_resumo_diarias_sudeste.csv`. A diária de enfermaria é baixa porque o SUS paga a covid por **valor fechado por internação**; dividir esse valor pelos dias não representa custo hospitalar.

## 5. Simulador (`web/index.html`)

```
Custo da enfermaria = internados × dias médios em enfermaria × diária de enfermaria
Custo da UTI        = pacientes em UTI × dias médios em UTI × diária de UTI
Custo total         = custo da enfermaria + custo da UTI
```

Valores iniciais: dias (8,0 e 8,9, SIVEP-Gripe), diária de enfermaria (R$ 89, SIH/SUS, valor pago) e diária de UTI (R$ 3.445, custo FHEMIG). Exemplo com esses valores:

| | Enfermaria | UTI | Total |
|---|---|---|---|
| 2025 | 16.038 × 8 × 89 = R$ 11,4 mi | 5.266 × 8,9 × 3.445 = R$ 161,5 mi | R$ 172,9 mi |
| 2026 | 5.582 × 8 × 89 = R$ 4,0 mi | 1.758 × 8,9 × 3.445 = R$ 53,9 mi | R$ 57,9 mi |

## 6. Limitações
1. **Bases diferentes na mesma conta:** UTI em custo real (FHEMIG), enfermaria em valor pago (SIH). O total subestima o custo real da enfermaria.
2. **Custo de UTI de 2020, de hospitais estaduais de Minas.** Pacientes de 2020 eram mais graves; não está atualizado para 2026 nem representa toda a rede.
3. **Dias de internação do SIVEP-Gripe** (média 8) diferem da permanência média do SIH (6,0): populações diferentes.
4. **Recorte do SIH** (B34.2) é pequeno e pode não representar toda a covid hospitalizada.
5. **Dados preliminares** do SIVEP-Gripe (16/11/2026) e do SIH, sujeitos a revisão; 2026 está incompleto.
6. **Descrições de procedimentos do SIH:** 26 dos 31 códigos não foram confirmados (ver `FONTES.md`).
