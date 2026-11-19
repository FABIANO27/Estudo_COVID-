"""
Calcula a diária de UTI e a diária de enfermaria efetivamente PAGAS pelo SUS
(média do Sudeste) a partir da saída de extrair_covid_sih.py.

Uso: python src/sih/calcular_diarias.py <pasta_com_pkl>

  diária UTI        = soma(VAL_UTI) / soma(UTI_MES_TO), nas AIH com UTI_MES_TO > 0
  diária enfermaria = (soma(VAL_TOT) - soma(VAL_UTI)) / (soma(DIAS_PERM) - soma(dias UTI)),
                      nas AIH com DIAS_PERM >= dias UTI e DIAS_PERM > 0
"""
import glob, os, sys
import numpy as np, pandas as pd

d = pd.concat([pd.read_pickle(f) for f in glob.glob(os.path.join(sys.argv[1], '*.pkl'))], ignore_index=True)
d = d[d.IDENT == '1'].copy()
d['uti_d'] = d.UTI_MES_TO.fillna(0)


def calc(g):
    u = g[g.uti_d > 0]
    diaria_uti = u.VAL_UTI.sum() / u.uti_d.sum() if u.uti_d.sum() > 0 else np.nan
    ok = g[(g.DIAS_PERM >= g.uti_d) & (g.DIAS_PERM > 0)]
    dias_enf = (ok.DIAS_PERM - ok.uti_d).sum()
    diaria_enf = (ok.VAL_TOT.sum() - ok.VAL_UTI.sum()) / dias_enf if dias_enf > 0 else np.nan
    return pd.Series(dict(aih=len(g), aih_com_uti=len(u), dias_uti=u.uti_d.sum(),
                          diaria_uti=diaria_uti, dias_fora_uti=dias_enf, diaria_enfermaria=diaria_enf,
                          valor_medio_aih=g.VAL_TOT.mean(), permanencia_media=g.DIAS_PERM.mean()))


por_ano_uf = d.groupby(['ANO', 'UF']).apply(calc).reset_index()
total = calc(d).to_frame().T.assign(ANO='2025-2026', UF='SUDESTE')
out = pd.concat([por_ano_uf, total], ignore_index=True)
pd.set_option('display.width', 200)
print(out.round(2).to_string(index=False))
out.round(2).to_csv('sih_resumo_diarias_sudeste.csv', sep=';', decimal=',', index=False)
