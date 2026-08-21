# -*- coding: utf-8 -*-
# @Author: jorgemiranda
# @Date:   2020-11-06 15:25:58
# @Last Modified by:   Jorge Miranda
# @Last Modified time: 2023-10-31 15:05:37
import datetime
import csv
import modules.Candump as Candump
import modules.J1939 as J1939
from modules.Utils import NumberFromBuffer


# PGNs de interes
PGN_INS = 0xF019     # posicion INS
PGN_SPEED = 0xFEF1   # velocidad (CCVS)
PGN_GEAR = 0xF005    # marcha (ETC1)

# En CAN0 la velocidad y la marcha llegan con direccion de origen (SA) 0xF8
# (los IDs terminan en F8: 18FEF1F8 / 18F005F8). El README inyecta con SA 0x11/0x03,
# pero aqui filtramos por PGN, asi que sirve para ambos casos.
SA_SPEED_GEAR = 0xF8


class InsReader(Candump.CanReader):
    def __init__(self, csv_path="ins_data.csv", speed_gear_csv_path="speed_gear_data.csv"):
        self.csv_file = open(csv_path, mode="w", newline="", encoding="utf-8")
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(["date", "ref_id", "pos_x", "pos_y", "pos_z", "yaw"])

        # CSV de velocidad y marcha (ambas senales + ultimo valor conocido de la otra)
        self.sg_file = open(speed_gear_csv_path, mode="w", newline="", encoding="utf-8")
        self.sg_writer = csv.writer(self.sg_file)
        self.sg_writer.writerow(["date", "speed_kmh", "gear"])
        self.last_speed = None
        self.last_gear = None

    def OnMessage(self, canmsg):
        j1939msg = J1939.Decode(canmsg)
        if j1939msg != None:
            # print("Timestamp", j1939msg.timestamp, "PGN: ", hex(j1939msg.pgn) + "\tSIZE: ", j1939msg.size, "\tDATA: ",  j1939msg.data, "\n")
            self.ProcessMessage(j1939msg)

    def ProcessMessage(self, msg):
        date = datetime.datetime.fromtimestamp(msg.timestamp).strftime("%Y-%m-%d %H:%M:%S")
        if msg.pgn == PGN_INS:
            n = msg.size // 16
            for i in range(n):
                offset = i * 16
                ref_id = NumberFromBuffer(msg.data, 0 + offset, 2, "big", False)
                pos_x = NumberFromBuffer(msg.data, 2 + offset, 4, "big", True)
                pos_y = NumberFromBuffer(msg.data, 6 + offset, 4, "big", True)
                pos_z = NumberFromBuffer(msg.data, 10 + offset, 4, "big", True)
                yaw = NumberFromBuffer(msg.data, 14 + offset, 2, "big", True)

                print(
                    date,
                    "ref id: ",
                    ref_id,
                    "\tpos_x:",
                    pos_x,
                    "\tpos_y: ",
                    pos_y,
                    "\tpos_z: ",
                    pos_z,
                    "\tyaw: ",
                    yaw,
                )

                self.csv_writer.writerow([date, ref_id, pos_x, pos_y, pos_z, yaw])
            self.csv_file.flush()

        elif msg.pgn == PGN_SPEED:
            # Velocidad (CCVS): byte0=FF, velocidad x256 little-endian en bytes 1-2.
            # En CAN0 los bytes de cola son FF; 0xFFFF = senal no disponible (SNA).
            raw = NumberFromBuffer(msg.data, 1, 2, "little", False)
            speed = None if raw == 0xFFFF else raw / 256.0
            self.last_speed = speed
            print(date, "\tspeed:", speed, "km/h")
            self.WriteSpeedGear(date)

        elif msg.pgn == PGN_GEAR:
            # Marcha (ETC1): byte0 = marcha + 125  ->  gear = byte0 - 125
            #   0x7C=-1 (R), 0x7D=0 (N/P), 0x7E=+1 (D). 0xFF = no disponible.
            g = NumberFromBuffer(msg.data, 0, 1, "big", False)
            gear = None if g == 0xFF else g - 125
            self.last_gear = gear
            print(date, "\tgear:", gear)
            self.WriteSpeedGear(date)

    def WriteSpeedGear(self, date):
        self.sg_writer.writerow([date, self.last_speed, self.last_gear])
        self.sg_file.flush()

    def close(self):
        self.csv_file.close()
        self.sg_file.close()


if __name__ == "__main__":
    ins_reader = InsReader("ins_data_prueba_20.csv", "speed_gear_prueba_20.csv")
    try:
        # ins_reader.RemoteReader("can0", "192.168.3.72", "root", "mssadminkey2018", "system_key")
        ins_reader.LogReader("04_08/candump-2026-08-04_212438.log")
        # ins_reader.RemoteReader("can0", "192.168.2.10", "root", "root")
    finally:
        ins_reader.close()
