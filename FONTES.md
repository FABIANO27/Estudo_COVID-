# Fontes

Todas as fontes usadas neste projeto, com o que foi retirado de cada uma.
Data de consulta: 18/11/2026. Os dados do SIVEP-Gripe e do SIH/SUS são preliminares e mudam com revisões.

## 1. Fontes usadas nos cálculos

### 1.1 SIVEP-Gripe (SRAG 2019 a 2026) — número de casos, internações, UTI, óbitos, dias de internação
- **Origem:** Portal de Dados Abertos do SUS, conjunto "SRAG 2019 a 2026".
  https://dadosabertos.saude.gov.br/dataset/srag-2019-a-2026
- **Arquivos:** `INFLUD25-16-11-2026.parquet` (336.435 registros) e `INFLUD26-16-11-2026.parquet` (248.899 registros), versão de 16/11/2026.
- **Dicionário de dados:** `dicionario-de-dados-2019-a-2025.pdf` (SIVEP-Gripe, Ministério da Saúde, 25/05/2023), disponível no mesmo conjunto de dados.
- **Usado para:** tabela Resumo (casos, internados, UTI, óbitos, ventilação invasiva, letalidade), curvas semanais, faixa etária, UF e médias de dias de internação.
- **Campos principais:** `CLASSI_FIN`, `SEM_NOT`, `HOSPITAL`, `UTI`, `EVOLUCAO`, `SUPORT_VEN`, `NU_IDADE_N`, `TP_IDADE`, `SG_UF`, `DT_INTERNA`, `DT_EVOLUCA`, `DT_ENTUTI`, `DT_SAIDUTI`.
- **Dados brutos não estão neste repositório** (são grandes). Baixe no link acima.

### 1.2 SIH/SUS — valores pagos pelo SUS (diária de enfermaria)
- **Origem:** Sistema de Informações Hospitalares do SUS (DATASUS), arquivos RD (AIH reduzida), formato `.dbc`.
- **Arquivos:** ES, MG, RJ e SP; 2025 (jan a dez) e 2026 (jan a set), por exemplo `RDMG2501.dbc`. Fornecidos pelo autor do projeto.
- **Usado para:** diária de enfermaria paga pelo SUS (R$ 89) e, como referência alternativa não usada no simulador final, diária de UTI paga (R$ 690).
- **Campos principais:** `DIAG_PRINC`, `PROC_REA`, `IDENT`, `DIAS_PERM`, `UTI_MES_TO`, `VAL_SH`, `VAL_SP`, `VAL_UTI`, `VAL_TOT`, `MORTE`.
- **Dados brutos não estão neste repositório.**

### 1.3 Artigo da FHEMIG — custo real da diária de UTI covid (R$ 3.445)
- **Referência:** ALEMÃO, M. M.; BARBOSA, D. M.; COUTO, W. A. D.; SOUSA, A. A.; RIBEIRO, B. F.; MELO, V. S. A. *O custo do leito UTI do paciente COVID-19 em unidades hospitalares de Minas Gerais: referências para avaliação do modelo de financiamento durante a Pandemia.* **Brazilian Journal of Health Review**, v. 5, n. 2, p. 5661-5686, 2022. DOI: 10.34119/bjhrv5n2-145
- **Link:** https://ojs.brazilianjournals.com.br/ojs/index.php/BJHR/article/view/45925
- **Base do artigo:** SIGH-Custos (sistema de custos da FHEMIG, custeio por absorção), 2019 a 2020; faturamento do TabWin/DATASUS.
- **Usado para:** custo por paciente/dia de UTI covid em 2020 nos hospitais HJK (R$ 2.995,93, Tabela 2), HRJP (R$ 3.629,53, Tabela 6) e HEM (R$ 3.607,99, Tabela 8). O valor de R$ 3.445 é uma **média ponderada calculada neste projeto**, não consta no artigo (ver `METODOLOGIA.md`).
- **Também citado do artigo:** diária média de UTI faturada pelo SUS na rede FHEMIG (R$ 733 em 2020 e R$ 525 em 2019, Tabela 9) e déficit superior a 60% entre faturado e custo real.

## 2. Fontes usadas para identificar a covid e descrever procedimentos do SIH

| Informação | Fonte |
|---|---|
| Procedimento específico de covid (0303010223) e exclusão do CID B34.2 do procedimento 0303010193 | Portaria SAES nº 245, de 24/03/2020. https://www.planalto.gov.br/CCIVIL_03/Portaria/PRT/Portaria%20245-MS.htm e https://www.conass.org.br/?p=20899 |
| 0303140151 = tratamento de pneumonias ou influenza (gripe) | Parecer 1501/2024, Comitê Estadual de Saúde (TRF2). https://static.trf2.jus.br/nas-internet/documento/comite-estadual-saude/pareceres/2024/parecer-1501-2024.pdf |
| 0301060088 = diagnóstico e/ou atendimento de urgência em clínica médica | Parecer 3322/2024, TJRJ. https://www.tjrj.jus.br/documents/d/guest/parecer-3322-2024 |
| 0301060010 = clínica pediátrica; 0301060070 = clínica cirúrgica | Protocolo de regulação de acesso à internação, Hospital Estadual Ernestina Lopes Jaime (Goiás). https://goias.gov.br/saude/wp-content/uploads/sites/34/regulacao_estadual/protocolos-regulacao-acesso-internacao-urgencia-emergencia/Hospital%20Estadual%20Ernestina%20Lopes%20Jaime%20-%20HEELJ.pdf |

**Ressalvas:** (a) o código 0301060010 aparece com outra descrição ("atendimento de urgência com observação até 24 horas") em listas de produção de um hospital de Guaíra (SP); adotou-se a descrição pediátrica por coerência com os demais códigos de urgência. (b) Os outros 26 códigos do arquivo `sih_covid_amostra_sudeste.csv` (92 linhas) ficaram como "Descrição não confirmada". Confirmar na tabela SIGTAP: http://sigtap.datasus.gov.br

## 3. Fontes de contexto (não entram nos cálculos do simulador)
Usadas para situar os números de SRAG deste projeto em relação aos divulgados pelo Ministério da Saúde:
- Ministério da Saúde, *Informe Vigilância das Síndromes Gripais, SE 44 de 2026*: https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/c/covid-19/publicacoes-tecnicas/informes/informe-sindromes-gripais-se-44-de-2026-ampliado.pdf
- Exame, "Covid volta a crescer no Brasil há seis semanas, afirma Ministério da Saúde" (07/11/2026): https://exame.com/brasil/covid-volta-a-crescer-no-brasil-ha-seis-semanas-afirma-ministerio-da-saude/
- Exame, "Covid-19: casos graves voltam a subir no Brasil; veja onde estão em alta": https://exame.com/ciencia/covid-19-casos-graves-voltam-a-subir-no-brasil-veja-onde-estao-em-alta/
- Forbes Saúde, "Ministério da Saúde alerta para alta de Covid-19 em 18 estados" (11/2026): https://forbes.com.br/forbes-saude/2026/11/ministerio-da-saude-alerta-para-alta-de-covid-19-em-18-estados/

Figuras divulgadas: 118.851 casos de **síndrome gripal** por Covid-19 em 2026 (até 04/11), cerca de 68% abaixo de 2025; e cerca de 3,4 mil casos **graves** em 2026 contra 9,2 mil em 2025 no mesmo intervalo (queda de 63%, segundo o Ministério). Essas figuras vêm de outros sistemas/recortes, não são comparáveis diretamente com os casos deste projeto, mas apontam na mesma direção: neste projeto, SRAG por covid-19 hospitalizada caiu cerca de 65% (16.701 em 2025 para 5.888 em 2026, semanas 1 a 47).

Portais de acesso: Ministério da Saúde (https://www.gov.br/saude/pt-br/assuntos/covid-19), InfoGripe/Fiocruz (https://info.gripe.fiocruz.br), OpenDataSUS (https://opendatasus.saude.gov.br).

## 4. Fontes consultadas e descartadas

| Fonte | Motivo do descarte |
|---|---|
| ApuraSUS (sistema de custos do DATASUS; Manual de Gestão de Custos, SES-MG: https://www.saude.mg.gov.br/wp-content/uploads/2021/08/Manual-de-Gestao-de-Custos-Projeto-OtimizaSUS-7ef.pdf) | Dados por hospital não são públicos; não foi possível consultar valores para Minas Gerais. |
| Deliberação da Secretaria de Saúde do DF (diária de UTI adulto SIGTAP: R$ 819,08) | Valor do DF, de 2025; não é a competência vigente nem Minas. |
| Tabela de valores da SESAP de Praia Grande (UTI R$ 2.145,69; enfermaria R$ 958,74) | Tabela municipal com valores próprios, não representa o SUS. |
| Página do código 0802010083 (UTI II adulto) em site de consulta ao SIGTAP | Os valores mostrados (R$ 51.000 e R$ 9.000) não são valores por dia. |
| Notícias da FHEMIG sobre abertura de leitos covid (fhemig.mg.gov.br) | Informam quantidade de leitos e contratações, sem custo de enfermaria. |
| TabNet/DATASUS | Não traz valor de diária de UTI ou enfermaria, só valor por internação; interface não consultável por link. |

## 5. Lacuna conhecida
**Não foi encontrada fonte pública para o custo real da enfermaria covid na rede FHEMIG.** A base de custos (SIGH-Custos) existe, mas não é pública. Caminho sugerido: pedido pela Lei de Acesso à Informação à FHEMIG, solicitando o custo médio por paciente/dia dos centros de custo de enfermaria/clínica médica (HEM, HJK, HRJP, HRAD), 2019, 2020 e, se houver, 2025.
