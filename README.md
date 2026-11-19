# Dados

## Incluídos (agregados, sem dados pessoais)
- `resumo.json`: totais por ano, casos por semana epidemiológica, faixa etária e UF (SIVEP-Gripe, covid-19, semanas 1 a 47).
- `sih_resumo_diarias_sudeste.csv`: diária de UTI e de enfermaria **pagas pelo SUS**, por UF e ano (SIH/SUS).
- `sih_covid_amostra_sudeste.csv`: 1.654 internações (AIH) de covid-19 do Sudeste, sem identificação de pacientes. Coluna `DESCRICAO_PROCEDIMENTO` ao lado do código; 26 códigos estão como "Descrição não confirmada". Separador `;` e decimal `,`.

## Não incluídos (baixar na origem)
- **SIVEP-Gripe:** `INFLUD25-16-11-2026.parquet` e `INFLUD26-16-11-2026.parquet`, em https://dadosabertos.saude.gov.br/dataset/srag-2019-a-2026
- **SIH/SUS (RD):** arquivos `RD<UF><AA><MM>.dbc` de ES, MG, RJ e SP, 2025 (jan a dez) e 2026 (jan a set), do DATASUS.
