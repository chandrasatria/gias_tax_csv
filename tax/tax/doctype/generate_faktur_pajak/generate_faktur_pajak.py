# -*- coding: utf-8 -*-
# Copyright (c) 2015, Bobby and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class GenerateFakturPajak(Document):
	
	@frappe.whitelist()
	def generate_no_faktur(self):
		if not self.prefix_1 :
			frappe.throw("Kode Transaksi & Status belum terisi ")


		if not self.tahun_penggunaan:
			frappe.throw("Tahun Penggunaan belum terisi ")

		

		if not self.prefix_3 :
			frappe.throw("Kode Tahun belum terisi ")

		if not self.start_number and not self.end_number :
			frappe.throw("Start / End Number belum terisi ")

		count = 0
		if len(self.prefix_1) == 3 and self.prefix_1.isdigit():
			count = 0
		else :
			frappe.throw("Format Kode Transaksi & Status salah, harus 3 digit angka")


		count = 0
		if len(self.prefix_3) == 2 and self.prefix_3.isdigit():
			count = 0
		else :
			frappe.throw("Format Kode Tahun salah, harus 2 digit angka")

		temp = ""
		for x in range(int(self.start_number), int(int(self.end_number)+1)):
			if x > 0 and x <= 10 :
				temp = "0000000"+str(x)
				if x >= 10 :
					temp = "000000"+str(x)
			elif x > 10 and x <= 100 :
				temp = "000000"+str(x)
				if x >= 100 :
					temp = "00000"+str(x)
			elif x > 100 and x <= 1000 :
				temp = "00000"+str(x)
				if x == 1000 :
					temp = "0000"+str(x)
			elif x > 1000 and x <= 10000 :
				temp = "0000"+str(x)
				if x >= 10000 :
					temp = "000"+str(x)
			elif x > 10000 and x <= 1000000 :
				temp = "000"+str(x)
				if x >= 1000000 :
					temp = "00"+str(x)
			elif x > 100000 and x <= 1000000 :	
				temp = "00"+str(x)
				if x >= 1000000 :
					temp = "0"+str(x)
			elif x > 1000000 and x <= 10000000 :	
				temp = "0"+str(x)
				if x >= 10000000 :
					temp = str(x)
			else :
				temp = str(x)

			final_temp = str(self.prefix_1) + "-" + str(self.prefix_3) + "." + str(temp)

			patokan_fp = frappe.db.sql(""" 
				SELECT fp.`name`, fp.`is_used` FROM `tabFaktur Pajak` fp WHERE fp.`name`="{}" 

				""".format(final_temp),as_list=1)
			
			if patokan_fp :
				frappe.msgprint("Faktur Pajak "+final_temp+" sudah dibuat sebelumnya !")
			else :
				pr_doc = frappe.new_doc("Faktur Pajak")
				pr_doc.update({
					"no_faktur": final_temp,
					"is_used": 0,
					"tahun_penggunaan": self.tahun_penggunaan
				})

				pr_doc.flags.ignore_permissions = 1
				pr_doc.insert()

				frappe.msgprint("Faktur Pajak "+final_temp+" created !")

