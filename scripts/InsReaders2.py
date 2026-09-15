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

class InsReader(Candump.CanReader):
	def __init__(self, csv_path="ins_data.csv"):
		self.csv_file = open(csv_path, mode="w", newline="", encoding="utf-8")
		self.csv_writer = csv.writer(self.csv_file)
		self.csv_writer.writerow(["date", "ref_id", "pos_x", "pos_y", "pos_z", "yaw"])

	def OnMessage(self, canmsg):
		j1939msg = J1939.Decode(canmsg)
		if j1939msg != None:
			#print("Timestamp", j1939msg.timestamp, "PGN: ", hex(j1939msg.pgn) + "\tSIZE: ", j1939msg.size, "\tDATA: ",  j1939msg.data, "\n")
			self.ProcessMessage(j1939msg)

	def ProcessMessage(self, msg):
		date = datetime.datetime.fromtimestamp(msg.timestamp).strftime('%Y-%m-%d %H:%M:%S')
		if msg.pgn == 0xF019:
			n = msg.size//16
			for i in range(n):
				offset = i*16
				ref_id = NumberFromBuffer(msg.data, 0 + offset, 2, 'big', False)
				pos_x = NumberFromBuffer(msg.data, 2 + offset, 4, 'big', True)
				pos_y = NumberFromBuffer(msg.data, 6 + offset, 4, 'big', True)
				pos_z = NumberFromBuffer(msg.data, 10 + offset, 4, 'big', True)
				yaw = NumberFromBuffer(msg.data, 14 + offset, 2, 'big', True)

				print(date, "ref id: ", ref_id, "\tpos_x:", pos_x, "\tpos_y: ", pos_y, "\tpos_z: ", pos_z, "\tyaw: ", yaw)

				self.csv_writer.writerow([date, ref_id, pos_x, pos_y, pos_z, yaw])
			self.csv_file.flush()

	def close(self):
		self.csv_file.close()

if __name__ == '__main__':
    ins_reader = InsReader("ins_data_prueba_20.csv")
    try:
        #ins_reader.RemoteReader("can0", "192.168.3.72", "root", "mssadminkey2018", "system_key")
        ins_reader.LogReader("candump-2026-08-03_220734.log")
        #ins_reader.RemoteReader("can0", "192.168.2.10", "root", "root")
    finally:
        ins_reader.close()