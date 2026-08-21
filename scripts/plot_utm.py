from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.paths import PROC, OUT

import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
df = pd.read_csv(PROC / "prueba1.csv", dtype=str)
f = lambda x: int.from_bytes(bytes.fromhex(x), byteorder="little", signed=True)
for c in [c for c in df.columns if c not in ("time","raw")]:
    df[c] = df[c].apply(f)
df["utm_x"] = df["utm_x"]/100.0; df["utm_y"] = df["utm_y"]/100.0
df_log = df
fig, ax = plt.subplots(figsize=(8,8))
ax.plot(df_log["utm_x"], df_log["utm_y"], lw=1, color="steelblue", zorder=1)
x0,y0 = df_log["utm_x"].iloc[0], df_log["utm_y"].iloc[0]
xf,yf = df_log["utm_x"].iloc[-1], df_log["utm_y"].iloc[-1]
ax.scatter(x0,y0,color="green",s=120,marker="o",zorder=3,label="Inicio")
ax.scatter(xf,yf,color="red",s=140,marker="*",zorder=3,label="Fin")
ax.annotate(f"Inicio\n({x0:.1f}, {y0:.1f})",(x0,y0),textcoords="offset points",xytext=(10,10),color="green",fontsize=9)
ax.annotate(f"Fin\n({xf:.1f}, {yf:.1f})",(xf,yf),textcoords="offset points",xytext=(10,10),color="red",fontsize=9)
ax.set_xlabel("utm_x [m] (Este)"); ax.set_ylabel("utm_y [m] (Norte)")
ax.set_title("Trayectoria UTM (utm_x vs utm_y)")
ax.set_aspect("equal", adjustable="datalim"); ax.grid(True, alpha=0.3); ax.legend()
plt.tight_layout(); plt.savefig(OUT / "p_utm.png", dpi=90)
print("ok")
