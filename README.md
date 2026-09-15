# ControlBox DB / INS — datos crudos y graficos

Analisis de las campanias de prueba del INS montado en el vehiculo. Cada salida a campo
deja datos crudos (backup de la base `ControlBox.db`, log de `candump` del bus CAN,
capturas de CoolTerm, fotos de las balizas) que se pasan a CSV y se grafican aca:
trayectoria, velocidad/marcha, orientacion y comparacion contra el GNSS/UTM.P

Este repo es **datos + notebooks**. Los readers que convierten el bus CAN a CSV viven en
el repo `hwt_candump_reader`.

## Flujo de trabajo

Hay dos caminos, segun como se capturo la prueba.

**A — ControlBox** (el que se usa desde 2026-09-02):

```
data/raw/<fecha>/<variante>/ControlBox_<ddmm>-<hhmm>.db
   |  export de la tabla INSDataLog, un CSV por .db  (paso manual, ver abajo)
   v
data/processed/<fecha>/<variante>/<nombre_de_prueba>.csv
   |  notebooks/prueba.ipynb : decodifica hex -> escala /100 -> grafica
   v
outputs/  (png, trayectoria*.html, verificacion_ins.csv)
```

**B — bus CAN** (hasta 2026-08-18):

```
data/raw/<fecha>/<test>/candump-*.log
   |  hwt_candump_reader:  python3 scripts/InsReaders2.py     (los nombres de archivo
   |                                                           se editan en el __main__)
   v
data/processed/<fecha>/<test>/ins_data_*.csv  +  speed_gear_*.csv
   |  hwt_candump_reader:  python3 scripts/InsReconstruct.py <in>.csv -o <out>_abs.csv
   v
data/processed/<fecha>/*_abs.csv
   |  notebooks/plot_ins_data.ipynb / plot_ins_speed_gear.ipynb / plot_ins_abs.ipynb
   v
outputs/
```

## Correr

Los notebooks se abren en VS Code eligiendo `.venv/Scripts/python.exe` como kernel
(Python 3.14, Windows). El venv trae `ipykernel`, no el servidor de Jupyter.

```bash
.venv/Scripts/python.exe scripts/plot_test.py     # los scripts corren desde cualquier cwd
```

`requirements.txt` es un `pip freeze` **desactualizado**: le faltan `plotly`, `nbformat` y
`utm`, que si estan instalados en el venv y los usan las celdas de mapas y del slider.

## Notebooks

| notebook | entrada | que hace |
|---|---|---|
| `prueba.ipynb` | CSV del ControlBox | **el principal.** Decodifica, escala, grafica trayectoria local, la rota/traslada contra UTM, la dibuja sobre OpenStreetMap (folium) y sobre un slider temporal (plotly). Al final trae funciones reutilizables por prueba: `cargar_prueba`, `giro_idx`, `plot_trayectoria_tiempo`, `plot_legs`, `plot_vs_utm`, `plot_integracion_velocidad` |
| `estimacion_plot_espejo.ipynb` | CSV del ControlBox | version previa del anterior (campania 2026-07-27): rotacion por yaw relativo, sin mapas |
| `plot_ins_data.ipynb` | `ins_data_*.csv` | trayectoria `pos_x`/`pos_y`, series de cada componente y detalle de `pos_z` |
| `plot_ins_speed_gear.ipynb` | `ins_data_*.csv` + `speed_gear_*.csv` | velocidad y marcha en el tiempo, velocidad coloreada por marcha, e integracion de la velocidad con signo segun la marcha para comparar ida vs vuelta |
| `plot_ins_abs.ipynb` | `*_abs.csv` | posicion relativa (por segmento) vs absoluta reconstruida |
| `plot_cuat_euler.ipynb` | `cuat.csv` (MIP Monitor) | cuaternion -> angulos de Euler (ZYX) vs tiempo |
| `plot_inc_data.ipynb` | `inc_data.csv` | serie y distribucion de yaw/pitch/roll del inclinometro |

## Formato de los datos

**CSV del ControlBox** (`curva_L.csv`, `linea_recta.csv`, `prueba_*.csv`): es un volcado de
la tabla `INSDataLog` del `.db`. `time` es epoch en ms (decimal); el resto son **hex
little-endian con signo**, y `raw` es la concatenacion de todos. El blob `data` mide
48 bytes y se corta asi:

| campo | bytes | unidad real |
|---|---|---|
| `ts` | 8 | ms (reloj del equipo) |
| `utm_x`, `utm_y`, `z` | 4 c/u | centesimas de metro -> `/100` |
| `utm_zone_n` | 4 | zona UTM (18) |
| `utm_zone_l` | 4 | banda UTM, como codigo ASCII (76 -> `chr` -> `L`) |
| `heading` | 4 | centesimas de grado -> `/100` |
| `inx_x`, `inx_y`, `inx_z` | 4 c/u | offset del INS respecto de la baliza, cm -> `/100` |
| `inx_yaw` | 4 | centesimas de grado -> `/100` |

Todo viene en centesimas. La escala esta cruzada contra la propia base, tabla contra log:
en la campania 2026-07-21, `z=11622` -> 116.22 m = `IBeacon.altitude` y `heading=29549` ->
295.49 = `HeadingBeacon.heading`; en la de 2026-09-02, 407.46 m y 245.24 grados, que son
los valores de las balizas de ese sitio.

**CSV de los readers**: `ins_data_*` = `date, ref_id, pos_x, pos_y, pos_z, yaw` (posicion
en mm y yaw en centesimas de grado, relativos a la ultima referencia leida: cuando cambia
`ref_id` la posicion vuelve a cero). `speed_gear_*` = `date, speed_kmh, gear`
(`-1`=R, `0`=N, `1`=D). `*_abs` agrega `segment, abs_*, abs_*_m, yaw_deg, step_mm`.

## Agregar una campania nueva

1. `data/raw/<fecha ISO>/<variante o test>/` con los `.db` / `.log` / capturas / fotos.
   La fecha es la del dia de la prueba, no la del dia en que se proceso.
2. Exportar un CSV por `.db` a `data/processed/<fecha>/<misma subcarpeta>/`, con un nombre
   que diga que se hizo (`curva_L`, `linea_recta`).
3. Abrir `notebooks/prueba.ipynb` y cambiar **solo** la primera celda de datos:
   `log_path = PROC / "<fecha>/<variante>/<archivo>.csv"`.
4. Para el bloque de comparacion contra UTM, ajustar `psi` (rumbo de la linea de balizas
   respecto del Norte). **Sale del `.db` de esa campania**, no es un valor fijo:

   ```sql
   select * from HeadingBeacon;   -- 2026-07-21: 295.5   |   2026-09-02: 245.24
   select * from IBeacon;         -- lat/lon/altitud de cada baliza
   ```

   El `295.5` que quedo por omision en `plot_vs_utm` es el de 2026-07-21 y **no sirve para
   2026-09-02**. La columna `heading` del propio log trae ese mismo rumbo (245.23), asi que
   lo mas robusto es tomarlo de ahi en vez de escribirlo a mano.
5. Lo que se regenera va a `outputs/`; los `.png`/`.html` con nombre fijo se pisan, asi
   que si el grafico importa, guardarlo en `outputs/<fecha>/`.

Como saber de que `.db` salio un CSV: coinciden la cantidad de filas y el primer `time`
con `select count(*), min(time) from INSDataLog`.

El paso 2 hoy se hace **fuera de este repo** (no hay script aca). Con el layout de arriba
es reproducible directo desde el `.db`: `select time, hex(data) from INSDataLog order by id`
y cortar el hex en los campos de la tabla.

## Estructura

```
data/
  raw/<fecha>/[<test>/]     datos crudos: ControlBox*.db, candump-*.log,
                            capturas CoolTerm, fotos de campo
  processed/<fecha>/        CSV listos para graficar, con la misma subcarpeta que el crudo
  processed/                CSV sueltos cuya campania no esta determinada
outputs/[<fecha>/]          graficos (png), mapas (html) y CSV derivados de los notebooks
notebooks/                  los analisis
scripts/                    scripts sueltos de ploteo
modules/paths.py            RAW / PROC / OUT — las rutas, resueltas desde la raiz del repo
```

Regla para ubicar un archivo nuevo: `.db` / `.log` / captura / foto -> `data/raw/<fecha>/`;
CSV de un reader o de un export -> `data/processed/<fecha>/`; cualquier cosa que un
notebook pueda volver a generar -> `outputs/`.

## Rutas en el codigo

Nada usa rutas relativas al directorio de trabajo. Los notebooks arrancan con:

```python
import sys
from pathlib import Path
ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT))
from modules.paths import RAW, PROC, OUT

df = pd.read_csv(PROC / "2026-09-02/v200/linea_recta.csv")
```

y los scripts con `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))`.

Dentro de `PROC / "..."` conviene usar `/` y no `\`: con backslash el notebook solo corre
en Windows.

## Notas

- `abs_z` / `pos_z` del INS acumula deriva vertical (baja en los dos sentidos de marcha);
  para planta usar `abs_x` / `abs_y`. Detalle en el repo `hwt_candump_reader`.
- `scripts/InsReaders2.py` es una copia divergente del reader de `hwt_candump_reader` y no
  corre aca tal cual: le faltan `modules/Candump.py`, `modules/J1939.py` y `modules/Utils.py`.
- Cuando se analiza mas de una prueba a la vez se viene duplicando `prueba.ipynb`
  (`prueba_copy_tmp.ipynb`). Las funciones del final del notebook estan pensadas para
  evitarlo: un solo notebook, un `for` sobre los CSV de la campania.
