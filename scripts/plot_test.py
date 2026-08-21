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
for c in ["inx_x","inx_y","inx_z","inx_yaw"]:
    df[c] = df[c]/100.0
t_rel = (df["ts"] - df["ts"].iloc[0]) / 1000.0
fig, ax = plt.subplots(figsize=(10,4))
ax.plot(t_rel, df["inx_x"], lw=1)
ax.set_xlabel("ts relativo [s]"); ax.set_ylabel("inx_x [m]")
ax.set_title("inx_x vs ts (relativo)"); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig(OUT / "p1.png", dpi=90)
fig, ax = plt.subplots(figsize=(6,6))
sc = ax.scatter(df["inx_x"], df["inx_y"], c=t_rel, cmap="viridis", s=8)
ax.plot(df["inx_x"], df["inx_y"], lw=0.5, color="gray", alpha=0.5)
ax.set_xlabel("inx_x [m]"); ax.set_ylabel("inx_y [m]")
ax.set_title("inx_x vs inx_y"); ax.set_aspect("equal", adjustable="datalim")
ax.grid(True, alpha=0.3); fig.colorbar(sc, ax=ax, label="ts relativo [s]")
plt.tight_layout(); plt.savefig(OUT / "p2.png", dpi=90)
print("ok  inx_x:[%.2f,%.2f]  inx_y:[%.2f,%.2f]" % (df["inx_x"].min(),df["inx_x"].max(),df["inx_y"].min(),df["inx_y"].max()))
