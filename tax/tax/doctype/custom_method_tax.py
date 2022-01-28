from __future__ import unicode_literals
import frappe
from frappe.desk.reportview import get_match_cond
from frappe.model.db_query import DatabaseQuery
from frappe.utils import nowdate
import json
import socket
from frappe.model.document import Document


class custom_method(Document):
	pass
	# tambahan rico

@frappe.whitelist()
def isikan_nomor_faktur_pajak(doc, method):

	# query ambil nomor faktur pajak
	today_date = frappe.utils.today()
	posting_date = str(doc.posting_date)
	tahun = posting_date[0:4]


	result = frappe.db.sql(""" 
		SELECT fp.`creation`, fp.`name`, fp.`is_used` FROM `tabFaktur Pajak` fp
		where fp.`is_used` = 0 and
		fp.`tahun_penggunaan` = "{}"
		ORDER BY fp.`creation`, fp.`name` ASC
		LIMIT 1
	""".format(tahun), as_list=1)



	# function mengisikan faktur pajak
	if result :
		if doc.is_return == 0 :
			nomor_faktur_pajak = result[0][1]
			doc.faktur_pajak = nomor_faktur_pajak

	
@frappe.whitelist()
def faktur_pajak_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	conditions = []
	args = {

		'txt': "%{0}%".format(txt),
		"start": start,
		"page_len": page_len
	}

	return frappe.db.sql("""SELECT
		fp.`no_faktur`,
		sinv.`name`
		FROM `tabFaktur Pajak` fp

		LEFT JOIN `tabSales Invoice` sinv
		ON sinv.`faktur_pajak` = fp.`no_faktur`

		WHERE fp.`is_used` = 0
		AND fp.`disabled` = 0
		AND (sinv.`name` IS NULL OR sinv.`docstatus` = 2)

		AND fp.`no_faktur` LIKE %(txt)s

		ORDER BY fp.`creation` ASC
		LIMIT 20 """, args, as_dict=as_dict)


@frappe.whitelist()
def create_faktur_pajak_purchase_invoice_on_submit(doc,method):
	if doc.faktur_pajak :
		patokan_fp = frappe.db.sql(""" 
				SELECT fp.`name`, fp.`is_used` FROM `tabFaktur Pajak` fp WHERE fp.`name`="{}" 

				""".format(doc.faktur_pajak),as_list=1)
			
		if patokan_fp :
			frappe.msgprint("Faktur Pajak "+str(doc.faktur_pajak)+" sudah dibuat sebelumnya !")
		else :

			pr_doc = frappe.new_doc("Faktur Pajak")
			pr_doc.update({
				"no_faktur": str(doc.faktur_pajak),
				"is_used": 1
			})

			pr_doc.flags.ignore_permissions = 1
			pr_doc.save()

			frappe.msgprint("Faktur Pajak "+str(doc.faktur_pajak)+" created !")


@frappe.whitelist()
def update_faktur_pajak_sales_invoice_on_submit(doc,method):
	if doc.faktur_pajak :
		frappe.db.sql ("""
			update 
			`tabFaktur Pajak` 
			set 
			is_used= 1
			where 
			name="{0}"
		""".format(str(doc.faktur_pajak)))


@frappe.whitelist()
def update_faktur_pajak_sales_invoice_on_cancel(doc,method):
	if doc.faktur_pajak :
		frappe.db.sql ("""
			update 
			`tabFaktur Pajak` 
			set 
			is_used= 0
			where 
			name="{0}"
		""".format(str(doc.faktur_pajak)))

		frappe.db.sql ("""
			update 
			`tabSales Invoice` 
			set 
			faktur_pajak = ""
			where 
			name="{0}"
		""".format(str(doc.name)))

		frappe.db.commit()



@frappe.whitelist()
def cek_status(doc, method):
	if doc.faktur_pajak :
		faktur_pajak = frappe.db.sql(""" select a.`name`, a.`faktur_pajak` from `tabSales Invoice` a where a.`faktur_pajak` = "{0}" and  a.name not like "{1}" limit 1   """.format(str(doc.faktur_pajak),str(doc.name)))
		cek_used =  frappe.db.sql(""" SELECT a.name, a.is_used  FROM `tabFaktur Pajak` a WHERE a.name = "{0}" and a.is_used = 1;  """.format(str(doc.faktur_pajak)))
		if faktur_pajak:
			frappe.throw("Faktur Pajak {1} sudah digunakan di Invoice {0} ".format(faktur_pajak[0][0], faktur_pajak[0][1]))
			# 	frappe.throw("Faktur Pajak {0} sudah digunakan di invoice {1} ".format(faktur_pajak[0][1],faktur_pajak[0][0] ))
				# frappe.throw("Faktur Pajak {0} sudah digunakan ".format(doc.faktur_pajak))
		else :
			if cek_used:
				cek_used_dua =  frappe.db.sql(""" SELECT a.name, a.is_used  , b.name FROM `tabFaktur Pajak` a , `tabSales Invoice` b WHERE a.name = b.faktur_pajak AND a.`name` = "{0}" AND a.is_used = 1;  """.format(str(doc.faktur_pajak)))
				if cek_used_dua:
					if cek_used_dua[0][2] == doc.name :
						pass
				else:
					frappe.throw("Faktur Pajak {0} sudah digunakan ".format(doc.faktur_pajak))
				
				# if cek_used[0][0] == doc.faktur_pajak :
				# 	pass
				# elif cek_used[0][0] != doc.faktur_pajak :
					
			else:
				frappe.db.sql ("""
					update 
					`tabFaktur Pajak` 
					set 
					is_used= 1
					where 
					name="{0}"
				""".format(str(doc.faktur_pajak)))