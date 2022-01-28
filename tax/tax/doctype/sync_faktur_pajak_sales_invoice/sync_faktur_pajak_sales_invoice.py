# -*- coding: utf-8 -*-
# Copyright (c) 2018, Myme and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SyncFakturPajakSalesInvoice(Document):
	

	def sync_faktur_pajak_sales_invoice(self):
		# frappe.throw("Test")

		get_sales_invoice = frappe.db.sql(""" 
			SELECT 
			sinv.`name`,
			sinv.`posting_date`, 
			sinv.`faktur_pajak` 
			FROM `tabSales Invoice` sinv
			WHERE sinv.`docstatus` = 1
			AND sinv.`is_return` = 0
			AND (sinv.`faktur_pajak` = "" or sinv.`faktur_pajak` IS NULL)

			order by sinv.`posting_date`, sinv.`name` asc
		""", as_list=1)

		if get_sales_invoice :

			panjang_array_sinv = len(get_sales_invoice)

			get_nomor = frappe.db.sql(""" 
				SELECT fp.`creation`, fp.`name`, fp.`is_used` FROM `tabFaktur Pajak` fp
				WHERE fp.`is_used` = 0
				ORDER BY fp.`creation`, fp.`name` ASC

				LIMIT {0}

			""".format(panjang_array_sinv), as_list=1)

			panjang_array_nomor = len(get_nomor)

			if panjang_array_nomor < panjang_array_sinv :
				frappe.throw("Jumlah Nomor Pajak lebih sedikit daripada Jumlah Sales Invoice, Jumlah Faktur Pajak = "+str(panjang_array_nomor)+", Jumlah Sales Invoice = "+str(panjang_array_sinv))

			string_update_sinv = ""
			string_update_faktur_pajak = ""
			
			# for idx, val in enumerate(ints):
    		# print(idx, val)

    
			for idx, i in enumerate(get_sales_invoice) :
				kode_sinv = i[0]
				nomor_faktur = get_nomor[idx][1]


				if idx == len(get_sales_invoice) - 1 :
					string_update_sinv += "(" + "'"+str(kode_sinv)+"'" + "," + "'"+str(nomor_faktur)+"'" + ")"
					string_update_faktur_pajak += "(" + "'"+str(nomor_faktur)+"'" + "," + "'"+str("1")+"'" + ")"
				else :
					string_update_sinv += "(" + "'"+str(kode_sinv)+"'" + "," + "'"+str(nomor_faktur)+"'" + "),"
					string_update_faktur_pajak += "(" + "'"+str(nomor_faktur)+"'" + "," + "'"+str("1")+"'" + "),"


			# frappe.msgprint(string_update_sinv)

			frappe.db.sql(""" 
				
				INSERT INTO `tabSales Invoice`
				(`name`, `faktur_pajak`) 
				VALUES 
				{0}
				ON DUPLICATE KEY 
				UPDATE 
				faktur_pajak = VALUES(faktur_pajak)

			""".format(string_update_sinv))

			frappe.db.sql(""" 
				
				INSERT INTO `tabFaktur Pajak`
				(`name`, `is_used`) 
				VALUES 
				{0}
				ON DUPLICATE KEY 
				UPDATE 
				is_used = VALUES(is_used)

			""".format(string_update_faktur_pajak))


			# frappe.throw(string_update_sinv)
			frappe.db.commit()

			frappe.msgprint("Done")

