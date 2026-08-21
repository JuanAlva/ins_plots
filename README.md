# ControlBox DB / INS — datos crudos y graficos

Analisis de las campanias de prueba del INS montado en el vehiculo: se juntan los
datos crudos de cada salida a campo (log de `candump` del bus CAN, backup de la base
`ControlBox.db`, capturas de CoolTerm) con los CSV que salen de los readers, y se
grafican trayectoria, velocidad/marcha y orientacion.

Los readers que producen los CSV **no viven aqui**, viven en el repo
`hwt_candump_reader` (`scripts/InsReader.py`, `scripts/InsReaders2.py`,
`scripts/InsReconstruct.py`). Este repo es solo datos + notebooks.

## Estructura

```
data/
  raw/<fecha>/[<test>/]     datos crudos: candump-*.log, ControlBox*.db,
                            capturas CoolTerm, fotos de campo
  processed/<fecha>/        CSV que salen de los readers (ins_data_*, speed_gear_*,
                            prueba_*), con la misma subcarpeta de test que el crudo
  processed/                CSV sueltos cuya campania no esta determinada
outputs/[<fecha>/]          graficos (png), mapas (html) y CSV derivados de los notebooks
notebooks/                  los analisis
scripts/                    scripts sueltos de ploteo
modules/paths.py            RAW / PROC / OUT — las rutas, resueltas desde la raiz del repo
docs/                       notas
```

Las fechas son ISO (`2026-08-18`) y corresponden al dia de la prueba, no al dia en
que se proceso el archivo.

Regla para ubicar un archivo nuevo: `.log` / `.db` / captura / foto -> `data/raw/<fecha>/`;
CSV de un reader -> `data/processed/<fecha>/`; cualquier cosa que un notebook pueda
volver a generar -> `outputs/`.

## Rutas en el codigo

Nada usa rutas relativas al directorio de trabajo. Los notebooks arrancan con:

```python
import sys
from pathlib import Path
ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT))
from modules.paths import RAW, PROC, OUT

df = pd.read_csv(PROC / "2026-08-18/test3/ins_data_prueba_50.csv")
```

y los scripts con `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))`, asi
que corren desde cualquier directorio:

```bash
.venv/Scripts/python.exe scripts/plot_test.py
```

## Notas

- `abs_z` / `pos_z` del INS acumula deriva vertical (baja en los dos sentidos de
  marcha); para planta usar `abs_x` / `abs_y`. Detalle en el repo `hwt_candump_reader`.
- `scripts/InsReaders2.py` es una copia divergente del reader del otro repo y no corre
  aqui tal cual: le faltan `modules/Candump.py`, `modules/J1939.py` y `modules/Utils.py`.
- `requirements.txt` es el volcado del `.venv` de Windows (`.venv/Scripts/python.exe`).
