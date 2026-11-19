"""
Extrai as AIH de covid-19 (proxy) dos arquivos RD do SIH/SUS (.dbc, em .zip).

Uso:
  gcc -O2 -o dbc2dbf src/sih/dbc2dbf.c
  python src/sih/extrair_covid_sih.py <pasta_com_zips> <pasta_saida>

Cada zip deve conter arquivos RD<UF><AA><MM>.dbc (ex.: RDMG2501.dbc).
Saída: um .pkl por mês em <pasta_saida>, só com as AIH de covid.

Definição de covid usada (ver docs/METODOLOGIA.md):
  DIAG_PRINC == 'B342' ou começando com 'U07'.
"""
import glob, os, subprocess, sys, tempfile, zipfile
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from dbf import open_dbf, col_str, col_num

NUM = ['DIAS_PERM', 'VAL_SH', 'VAL_SP', 'VAL_TOT', 'VAL_UTI', 'UTI_MES_TO', 'UTI_INT_TO', 'MORTE']
pasta_zips, saida = sys.argv[1], sys.argv[2]
exe = os.path.join(os.path.dirname(__file__), '..', '..', 'dbc2dbf')
os.makedirs(saida, exist_ok=True)

with tempfile.TemporaryDirectory() as tmp:
    for z in sorted(glob.glob(os.path.join(pasta_zips, '*.zip'))):
        zf = zipfile.ZipFile(z)
        for nome in sorted(n for n in zf.namelist() if n.lower().endswith('.dbc')):
            destino = os.path.join(saida, nome + '.pkl')
            if os.path.exists(destino):
                continue
            zf.extract(nome, tmp)
            dbc, dbf_ = os.path.join(tmp, nome), os.path.join(tmp, 'cur.dbf')
            subprocess.run([exe, dbc, dbf_], check=True, capture_output=True)
            arr, F = open_dbf(dbf_)
            dp = col_str(arr, F, 'DIAG_PRINC')
            m = (dp == b'B342') | np.char.startswith(dp, b'U07')
            sub = arr[m]
            d = pd.DataFrame({c: col_num(sub, F, c) for c in NUM})
            d['IDENT'] = col_str(sub, F, 'IDENT').astype(str)
            d['PROC'] = col_str(sub, F, 'PROC_REA').astype(str)
            d['UF'], d['ANO'], d['MES'] = nome[2:4], 2000 + int(nome[4:6]), int(nome[6:8])
            d.to_pickle(destino)
            os.remove(dbc); os.remove(dbf_)
            print(nome, len(arr), int(m.sum()), flush=True)
