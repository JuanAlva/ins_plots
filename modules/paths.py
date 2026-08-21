"""Rutas del proyecto, resueltas desde la raiz del repo.

Uso (desde un notebook en notebooks/ o un script en scripts/):

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path.cwd().parent))      # notebooks
    from modules.paths import RAW, PROC, OUT

    df = pd.read_csv(PROC / "2026-08-18/test3/ins_data_prueba_50.csv")
    fig.savefig(OUT / "trayectoria.png")

Convencion de carpetas:
  RAW  = data/raw/<fecha>/[<test>/]  datos crudos: candump, .db de ControlBox,
                                     capturas CoolTerm, fotos de campo
  PROC = data/processed/<fecha>/     csv que salen de los readers; los sueltos
                                     (campania no determinada) van en la raiz de PROC
  OUT  = outputs/[<fecha>/]          graficos, mapas html y csv derivados
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
PROC = DATA / "processed"
OUT = ROOT / "outputs"

__all__ = ["ROOT", "DATA", "RAW", "PROC", "OUT"]
