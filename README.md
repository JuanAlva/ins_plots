# Kvaser J1939 Injector

Inyecta tramas J1939 (CAN 29-bit, 250kbps) via Kvaser U100 usando la librería oficial
`canlib` (no `python-can`).

**Solo funciona con un JAC JS2** — las tramas 11-bit (`28D`=marcha, `271`=velocidad) que
lee `replay`/`bridge` vienen de ese vehículo específico; otro modelo puede usar IDs/formato
distintos.

## Archivos

- `can_kvaser.py` — inyección directa, replay de log, y bridge desde ELM327
- `can_log_grande.txt` — log de ejemplo del JAC JS2 para probar `replay`

## Requisitos

- Driver propietario de Kvaser (`mhydra`/`kvcommon` vía dkms, de
  [astuff/kvaser-linuxcan](https://github.com/astuff/kvaser-linuxcan)) — no `kvaser_usb`/SocketCAN.
- `pip install -r requirements.txt` (`canlib` no está en PyPI, ver ese archivo).
- U100 por USB, canal 0.

## Uso

```bash
python3 can_kvaser.py speed 100 --repeat --interval 0.5
python3 can_kvaser.py gear 2 --repeat --interval 0.5      # -1=R, 0=N, 1,2,3...=marchas

python3 can_kvaser.py replay can_log_grande.txt --realtime   # log del JAC -> J1939
python3 can_kvaser.py bridge                                  # ELM327 en vivo -> J1939
```

## Codificación J1939

ID: `(6 << 26) | (pgn << 8) | source_address`

- **Velocidad** — PGN `0xFEF1` (CCVS), SA `0x11`: `FF <lo> <hi> CC FF FF 1F FF`, velocidad×256 little-endian en bytes 1-2.
- **Marcha** — PGN `0xF005` (ETC1), SA `0x03`: `<g> 00 00 <g> 20 4E 4E 32`, `<g>` = marcha + 125.

El JAC (automático) solo reporta `P/R/N/D`, se mapea `P/N→0, R→-1, D→1` (`GEAR_TO_J1939`).

## Fuente: tramas del JAC JS2 (ELM327, `ATMA`)

`CAN_ID B0 B1 B2 B3 B4 B5 B6 B7`:
- `28D` → marcha, byte `B2` (`01`=P, `02`=R, `03`=N, `04`=D)
- `271` → velocidad, `((B2 << 8) | B3) / 256.0` km/h

`bridge` configura el ELM327 (`/dev/ttyUSB0`, 115200): `ATZ`, `ATE0`, `ATL0`, `ATH1`, `ATSP6`, `0100`, `ATMA`.