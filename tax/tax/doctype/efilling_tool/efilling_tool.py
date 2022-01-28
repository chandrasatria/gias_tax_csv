# -*- coding: utf-8 -*-
# Copyright (c) 2015, Bobby and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import re
from frappe.model.document import Document
from frappe.utils import cstr, flt, getdate, comma_and, cint, in_words
from datetime import datetime


class EFillingTool(Document):

	@frappe.whitelist()
	def print_to_excel(self):
		return self.get_csv()

	@frappe.whitelist()
	def get_csv(self):
		if self.kategori == "Faktur Pajak Masukan" :
			
			item_list=[" "]
			item_list.append(['FM', 'KD_JENIS_TRANSAKSI', 'FG_PENGGANTI', 'NOMOR_FAKTUR', 'MASA_PAJAK','TAHUN_PAJAK', 'TANGGAL_FAKTUR', 'NPWP','NAMA','ALAMAT_LENGKAP','JUMLAH_DPP','JUMLAH_PPN','JUMLAH_PPNBM','IS_CREDITABLE','REFERENSI'])
			
			check = 0 
			for i in self.get_data_pajak_masukan :
				if(i.check==1) :
					check=1

			if(check==1) : 
				for a in self.get_data_pajak_masukan :
					if(a.check==1) :
							item_list.append([str(a.fm),str(a.kd_jenis_transaksi),str(a.fg_pengganti),str(a.nomor_faktur),str(a.masa_pajak),str(a.tahun_pajak),str(a.tanggal_faktur),str(a.npwp),str(a.nama),a.alamat_lengkap,str(a.jumlah_dpp),str(a.jumlah_ppn),str(a.jumlah_ppnbm),str(a.is_creditable),str(a.referensi)])
				
			return item_list

		elif self.kategori == "PENJUALAN" or self.kategori == "PENJUALAN KTP":
			item_list2=[]
			item_list2.append(['FK', 'KD_JENIS_TRANSAKSI', 'FG_PENGGANTI', 'NOMOR_FAKTUR', 'MASA_PAJAK','TAHUN_PAJAK', 'TANGGAL_FAKTUR', 'NPWP','NAMA','ALAMAT_LENGKAP','JUMLAH_DPP','JUMLAH_PPN','JUMLAH_PPNBM','ID_KETERANGAN_TAMBAHAN','FG_UANG_MUKA','UANG_MUKA_DPP','UANG_MUKA_PPN','UANG_MUKA_PPNBM','REFERENSI','KODE_DOKUMEN_PENDUKUNG'])
			item_list2.append(['LT', 'NPWP','NAMA','JALAN','BLOK','NOMOR','RT','RW','KECAMATAN','KELURAHAN','KABUPATEN','PROPINSI','KODE_POS','NOMOR_TELEPON', "", "", "", "", "",""])
			item_list2.append(['OF','KODE_OBJEK', 'NAMA', 'HARGA_SATUAN', 'JUMLAH_BARANG', 'HARGA_TOTAL','DISKON', 'DPP', 'PPN','TARIF_PPNBM','PPNBM','','','','','','','','',''])

			
			_company = frappe.db.get_single_value("Global Defaults","default_company")
			company = frappe.get_doc("Company",_company)

			check = 0 
			for i in self.get_data_pajak_keluaran :
				if(i.check==1) :
					check=1

			if(check==1) : 
				for a in self.get_data_pajak_keluaran :
					if(a.check==1) :

						# cek included in basic rate or not
						cek_included = frappe.db.sql(""" 

							SELECT * FROM `tabSales Taxes and Charges` stt
							WHERE stt.`parent` = "{}"
							AND stt.`included_in_print_rate` = 1

						""".format(a.referensi),as_list=1)
						npwp = "000000000000000"
						if a.npwp:
							npwp = a.npwp

						# bagian FK
						item_list2.append([
							str(a.fk),
							str(a.kd_jenis_transaksi),
							str(a.fg_pengganti),
							str(a.nomor_faktur),
							str(a.masa_pajak),
							str(a.tahun_pajak),
							str(a.tanggal_faktur),
							str(npwp),
							str(a.nama),
							a.alamat_lengkap,
							str(a.jumlah_dpp),
							str(a.jumlah_ppn),
							str(a.jumlah_ppnbm),
							str(a.id_keterangan_tambahan),
							str(a.fg_uang_muka),
							str(a.uang_muka_dpp),
							str(a.uang_muka_ppn),
							str(a.uang_muka_ppnbm),
							str(a.referensi),
							str("")
						])

						# bagian LT
						item_list2.append([
								str("FAPR"),
								str("PT. GLOBAL INDONESIA ASIA SEJAHTERA"),
								str("SPRINGHILL OFFICE TOWER LT 5 UNIT A H JL BENYAMIN SUEB RUAS D7 BLOK D6 KEC. PADEMANGAN"),
								"","","","","","","","","","","","","","","","",""])

						anak = []

						ppn_pct = 1

						if cek_included :
							ppn_pct = 1.1
							anak = frappe.db.sql("""
								SELECT
								sinvi.`item_code`,
								sinvi.`item_name`,
								ifnull(sinvi.`price_list_rate`,0) as price_list_rate,
								ifnull(sinvi.`rate`, 0) as rate,
								((sinvi.`price_list_rate` - sinvi.`rate`) * sinvi.`qty`) as discount,
								sinvi.`qty`,
								sinvi.`amount` as amount,
								sinvi.discount_amount,
								sinvi.prorate_discount

								FROM `tabSales Invoice Item` sinvi
								WHERE sinvi.`parent` = "{}" 
							""".format(a.referensi),as_list=1)
						else:
							anak = frappe.db.sql("""
								SELECT
								sinvi.`item_code`,
								sinvi.`item_name`,
								ifnull(sinvi.`price_list_rate`,0) as price_list_rate,
								ifnull(sinvi.`rate`, 0) as rate,
								((sinvi.`price_list_rate` - sinvi.`rate`) * sinvi.`qty`) as discount,
								sinvi.`qty`,
								sinvi.`amount` as amount,
								sinvi.discount_amount,
								sinvi.prorate_discount

								FROM `tabSales Invoice Item` sinvi
								WHERE sinvi.`parent` = "{}" 
							""".format(a.referensi),as_list=1)

						if anak:
							for i in anak:
								kode_object = str(i[0])
								nama_item = str(i[1])

								harga_satuan, harga_total, diskon, tarif_ppnbm, ppnbm = 0, 0, 0, 0, 0
								# if rate > price list rate
								
								if i[3] > i[2] :

									harga_satuan = "{0:.5f}".format((i[3]/ppn_pct))
									harga_total = "{0:.5f}".format(((i[3]*i[5])/ppn_pct))
									diskon = 0
								else :
									harga_satuan = "{0:.5f}".format((i[2]/ppn_pct))
									harga_total = "{0:.5f}".format(((i[2]*i[5])/ppn_pct))
									diskon = "{0:.5f}".format((i[7] + i[8]/ppn_pct))

								jumlah_barang = str(i[5])

								dpp = "{0:.4f}".format((i[6]/ppn_pct))
								ppn = "{0:.3f}".format(((i[6]/ppn_pct)*10/100))

								# bagian OF
								item_list2.append([
										'OF',
										kode_object,
										nama_item,
										harga_satuan,  
										jumlah_barang,  
										harga_total,  
										diskon, 
										dpp, 
										ppn, 
										tarif_ppnbm,
										ppnbm,
										"","","","","","","","",""])

			return item_list2

		elif self.kategori == "Faktur Pajak Retur Masukan" :
			item_list3=[" "]
			item_list3.append(['RM','NPWP','NAMA', 'KD_JENIS_TRANSAKSI', 'FG_PENGGANTI', 'NOMOR_FAKTUR', 'TANGGAL_FAKTUR', 'IS_CREDITABLE','NO_DOKUMEN_RETUR', 'TANGGAL_RETUR','MASA_PAJAK_RETUR','TAHUN_PAJAK_RETUR',  'NILAI_RETUR_DPP','NILAI_RETUR_PPN','NILAI_RETUR_PPNBM'])
			
			check = 0 
			for i in self.get_data_retur_masukan :
				if(i.check==1) :
					check=1

			if(check==1) : 
				for a in self.get_data_retur_masukan :
					if(a.check==1) :
						item_list3.append([str(a.rm),str(a.npwp),str(a.nama),str(a.kd_jenis_transaksi),str(a.fg_pengganti),str(a.nomor_faktur),str(a.tanggal_faktur),str(a.is_creditable),str(a.no_dokumen_retur),str(a.tanggal_retur),str(a.masa_pajak_retur),str(a.tahun_pajak_retur),str(a.nilai_retur_dpp),str(a.nilai_retur_ppn),str(a.nilai_retur_ppnbm)])

			return item_list3

		elif self.kategori == "Faktur Pajak Retur Keluaran" :
			item_list4=[" "]
			item_list4.append(['RK','NPWP','NAMA', 'KD_JENIS_TRANSAKSI', 'FG_PENGGANTI', 'NOMOR_FAKTUR', 'TANGGAL_FAKTUR','NO_DOKUMEN_RETUR', 'TANGGAL_RETUR','MASA_PAJAK_RETUR','TAHUN_PAJAK_RETUR',  'NILAI_RETUR_DPP','NILAI_RETUR_PPN','NILAI_RETUR_PPNBM'])
			
			check = 0 
			for i in self.get_data_retur_keluaran :
				if(i.check==1) :
					check=1
			if(check==1) : 
				for a in self.get_data_retur_keluaran :
					if(a.check==1) :
						item_list4.append([str(a.rk),str(a.npwp),str(a.nama),str(a.kd_jenis_transaksi),str(a.fg_pengganti),str(a.nomor_faktur),str(a.tanggal_faktur),str(a.no_dokumen_retur),str(a.tanggal_retur),str(a.masa_pajak_retur),str(a.tahun_pajak_retur),str(a.nilai_retur_dpp),str(a.nilai_retur_ppn),str(a.nilai_retur_ppnbm)])

			return item_list4


	@frappe.whitelist()
	def get_data(self):
		
		if self.date_from and self.date_to :
			if self.kategori == "Faktur Pajak Masukan" :

				self.set('get_data_pajak_masukan', [])
				data_pajak_masukan = frappe.db.sql("""  
					select 
					MONTH(pm.`tax_date`),
					YEAR(pm.`tax_date`),
					DATE_FORMAT(pm.`tax_date`,'%d/%m/%Y'),
					pm.`net_total`,
					pm.`total_taxes_and_charges`,
					pm.`name`,
					REPLACE(REPLACE(su.alamat_pajak, '<br', ' '),'-',' '),
					REPLACE(REPLACE(su.nama_pajak, '<br', ' '),'-',' ')
					from `tabPurchase Invoice` pm 
					JOIN `tabSupplier` su ON su.supplier_name=pm.supplier
					where pm.`docstatus` = 1 and pm.is_return != 1 AND pm.`posting_date`  between "{0}" and "{1}"  """.format(self.date_from,self.date_to),as_list=1)


				if data_pajak_masukan :

					for d in data_pajak_masukan :
						pi = self.append('get_data_pajak_masukan', {})
						pi.masa_pajak				= d[0]
						pi.tahun_pajak				= d[1]
						pi.tanggal_faktur			= d[2]
						pi.jumlah_dpp				= d[3]
						pi.jumlah_ppn				= d[4]
						pi.referensi				= d[5]
						pi.alamat_lengkap			= d[6]
						pi.nama					= d[7]
						pi.fm = "FM"
						pi.fg_pengganti = '0'
						pi.jumlah_ppnbm = '0'
						pi.is_creditable = '1'
						hoho = frappe.get_doc("Purchase Invoice",pi.referensi)
						hasil = frappe.get_doc("Supplier",hoho.supplier).no_npwp
						pi.npwp = re.sub('[^0-9]','', hasil)
						kdjenistransaksi = frappe.get_doc("Supplier",hoho.supplier).nomor_awalan_pajak
						pi.kd_jenis_transaksi = kdjenistransaksi
						pi.nomor_faktur =  re.sub('[^0-9]','', str(hoho.faktur_pajak))
						pi.faktur_export = pi.nomor_faktur
						nofak = pi.nomor_faktur
						


				else :
					frappe.throw("Data tidak ditemukan")


			elif self.kategori == "PENJUALAN" or self.kategori == "PENJUALAN KTP":
				
				self.set('get_data_pajak_keluaran', [])
				data_pajak_keluaran = frappe.db.sql(""" 
					select
					MONTH(pm.`tax_date`),
					YEAR(pm.`tax_date`),
					DATE_FORMAT(pm.`tax_date`,'%d/%m/%Y'),
					pm.`net_total`,
					pm.`total_taxes_and_charges`,
					pm.`name` as sinv_name,
					REPLACE(REPLACE(cus.alamat_pajak, '<br>', ' '),'-',' '),
					REPLACE(REPLACE(cus.nama_pajak, '<br>', ' '),'-',' '),
					REPLACE(REPLACE(REPLACE(cus.tax_id, '.', ''),'-',' '),' ',''),
					cus.`nomor_awalan_pajak`,
					cus.no_ktp,
					cus.tax_id,
					pm.dp_or_not,
					pm.nilai_invoice_dp
					from `tabSales Invoice` pm
					left JOIN `tabCustomer` cus ON cus.name=pm.customer
					where pm.`docstatus` = 1 and pm.is_return != 1 AND pm.`posting_date`  between "{0}" and "{1}"

					

					 """.format(self.date_from,self.date_to),as_list=1)

				if data_pajak_keluaran :

					for a in data_pajak_keluaran :

						# mengambil perhitungan dpp dan ppn item
						total_dpp = 0
						total_ppn = 0

						# cek included in basic rate or not
						cek_included = frappe.db.sql(""" 

							SELECT * FROM `tabSales Taxes and Charges` stt
							WHERE stt.`parent` = "{}"
							AND stt.`included_in_print_rate` = 1

						""".format(a[5]),as_list=1)


						if cek_included :
							
							anak = frappe.db.sql("""
								SELECT
								sinvi.`item_code`,
								sinvi.`item_name`,
								ifnull(sinvi.`price_list_rate`,0) as price_list_rate,
								ifnull(sinvi.`rate`, 0) as rate,
								((sinvi.`price_list_rate` - sinvi.`rate`) * sinvi.`qty`) as discount,
								sinvi.`qty`,
								sinvi.`amount` as amount

								FROM `tabSales Invoice Item` sinvi
								WHERE sinvi.`parent` = "{}" 
							""".format(a[5]),as_list=1)

							if anak :
								for i in anak :
									total_dpp += float("{0:.4f}".format((i[6]*10/11)))
									total_ppn += float("{0:.3f}".format(((i[6]*10/11)*10/100)))

						else :

							anak = frappe.db.sql("""
								SELECT
								sinvi.`item_code`,
								sinvi.`item_name`,
								ifnull(sinvi.`price_list_rate`,0) as price_list_rate,
								ifnull(sinvi.`rate`, 0) as rate,
								((sinvi.`price_list_rate` - sinvi.`rate`) * sinvi.`qty`) as discount,
								sinvi.`qty`,
								sinvi.`amount` as amount

								FROM `tabSales Invoice Item` sinvi
								WHERE sinvi.`parent` = "{}" 
							""".format(a[5]),as_list=1)

							if anak :
								for i in anak :
									total_dpp += float("{0:.4f}".format((i[6])))
									total_ppn += float("{0:.3f}".format(((i[6]*10/100))))


						awalan = ""
						if a[11]:
							awalan = a[11]
						elif a[10]:
							awalan = a[10]

						nama = ""
						if awalan:
							nama = "{}#NIK#NAMA#{}".format(awalan, a[7])

						pk = self.append('get_data_pajak_keluaran', {})
						pk.masa_pajak				= a[0]
						pk.tahun_pajak				= a[1]
						pk.tanggal_faktur			= a[2]
						pk.jumlah_dpp				= str(total_dpp)
						pk.jumlah_ppn				= str(total_ppn)
						pk.referensi				= a[5]
						pk.alamat_lengkap			= a[6]
						pk.nama					= a[7]
						pk.npwp					= a[8]
						pk.kd_jenis_transaksi		= a[9]
						pk.fk = "FK"
						pk.fg_pengganti = '0'
						pk.jumlah_ppnbm = '0'
						pk.id_keterangan_tambahan = '0'
						if str(a[12]) == "DP":
							pk.fg_uang_muka = '2'
						else:
							pk.fg_uang_muka = '0'

						pk.uang_muka_dpp = flt(a[3]) - flt(a[13])
						pk.uang_muka_ppn = pk.uang_muka_dpp * 10 / 100
						pk.uang_muka_ppnbm = '0'
						hoho = frappe.get_doc("Sales Invoice",pk.referensi)
						pk.nomor_faktur =  re.sub('[^0-9]','', str(hoho.faktur_pajak))
						pk.faktur_export = pk.nomor_faktur
						nofak = pk.nomor_faktur
				else :
					frappe.throw("Data tidak ditemukan")	

			elif self.kategori == "Faktur Pajak Retur Masukan" :
				self.set('get_data_retur_masukan', [])
				data_retur_masukan = frappe.db.sql("""  
					select 
					DATE_FORMAT(pm.`tax_date`,'%d/%m/%Y'),
					pm.`name`,
					DATE_FORMAT(pm.`posting_date`,'%d/%m/%Y'),
					MONTH(pm.`tax_date`),
					YEAR(pm.`tax_date`),
					pm.`net_total`,
					pm.`total_taxes_and_charges`,
					pm.`name`,
					REPLACE(REPLACE(su.alamat_pajak, '<br', ' '),'-',' '),
					REPLACE(REPLACE(su.nama_pajak, '<br', ' '),'-',' ')
					from `tabPurchase Invoice` pm
					JOIN `tabSupplier` su ON su.supplier_name=pm.supplier
					where pm.`docstatus` = 1 and pm.is_return = 1 AND pm.`posting_date`   between "{0}" and "{1}" """.format(self.date_from,self.date_to),as_list=1)

				if data_retur_masukan :
					for d in data_retur_masukan :
						pi = self.append('get_data_retur_masukan', {})
						pi.tanggal_faktur			= d[0]
						pi.no_dokumen_retur			= d[1]			
						pi.tanggal_retur			= d[2]
						pi.masa_pajak_retur			= d[3]
						pi.tahun_pajak_retur		= d[4]
						pi.nilai_retur_dpp			= d[5]
						pi.nilai_retur_ppn			= d[6]
						pi.referensi				= d[7]
						pi.alamat_lengkap			= d[8]
						pi.nama					= d[9]
						pi.rm = "RM"
						pi.fg_pengganti = '0'
						pi.nilai_retur_ppnbm = '0'
						pi.is_creditable = '1'
						hoho = frappe.get_doc("Purchase Invoice",pi.referensi)
						hasil = frappe.get_doc("Supplier",hoho.supplier).no_npwp
						pi.npwp = re.sub('[^0-9]','', hasil)
						kdjenistransaksi = frappe.get_doc("Supplier",hoho.supplier).nomor_awalan_pajak
						pi.kd_jenis_transaksi = kdjenistransaksi
						pi.nomor_faktur =  re.sub('[^0-9]','', str(hoho.faktur_pajak))
						pi.faktur_export = pi.nomor_faktur
						nofak = pi.nomor_faktur
				else :
					frappe.throw("Data tidak ditemukan")
					
			elif self.kategori == "Faktur Pajak Retur Keluaran" :
				self.set('get_data_retur_keluaran', [])
				data_retur_keluaran = frappe.db.sql(""" 
					select
					DATE_FORMAT(pm.`tax_date`,'%d/%m/%Y'),
					pm.`name`,
					DATE_FORMAT(pm.`posting_date`,'%d/%m/%Y'),
					MONTH(pm.`tax_date`),
					YEAR(pm.`tax_date`),
					pm.`net_total`,
					pm.`total_taxes_and_charges`,
					pm.`name`,

					REPLACE(REPLACE(cus.alamat_pajak, '<br>', ' '),'-',' '),
					REPLACE(REPLACE(cus.nama_pajak, '<br>', ' '),'-',' ')

					from `tabSales Invoice` pm
					left JOIN `tabCustomer` cus ON cus.name=pm.customer
					where pm.`docstatus` = 1 and pm.is_return = 1 AND pm.`posting_date`  between "{0}" and "{1}" """.format(self.date_from,self.date_to),as_list=1)

				if data_retur_keluaran :
				
					for d in data_retur_keluaran :
						pk = self.append('get_data_retur_keluaran', {})
						pk.tanggal_faktur			= d[0]
						pk.no_dokumen_retur			= d[1]			
						pk.tanggal_retur			= d[2]
						pk.masa_pajak_retur			= d[3]
						pk.tahun_pajak_retur		= d[4]
						pk.nilai_retur_dpp			= d[5]
						pk.nilai_retur_ppn			= d[6]
						pk.referensi				= d[7]
						pk.alamat_lengkap			= d[8]
						pk.nama					= d[9]
						pk.rk = "RK"
						pk.fg_pengganti = '0'
						pk.nilai_retur_ppnbm = '0'
						hoho = frappe.get_doc("Sales Invoice",pk.referensi)
						hasil = frappe.get_doc("Customer",hoho.customer).tax_id
						pk.npwp = re.sub('[^0-9]','', hasil)
						kdjenistransaksi = frappe.get_doc("Customer",hoho.customer).nomor_awalan_pajak
						pk.kd_jenis_transaksi = kdjenistransaksi
						pk.nomor_faktur =  re.sub('[^0-9]','', str(hoho.faktur_pajak))
						pk.faktur_export = pk.nomor_faktur
						nofak = pk.nomor_faktur
						
				else :
					frappe.throw("Data tidak ditemukan")

			else :
				frappe.throw("Type Packing List harus di isi!")

		else :
			frappe.throw("From dan To harus di isi !")


	@frappe.whitelist()
	def checkall(self) :
		if self.kategori == "Faktur Pajak Masukan" :
		
			for d in self.get_data_pajak_masukan :	
					d.check=1
					
		elif self.kategori == "PENJUALAN" :
		
			for d in self.get_data_pajak_keluaran :
					d.check=1


		elif self.kategori == "Faktur Pajak Retur Masukan" :
		
			for d in self.get_data_retur_masukan :
					d.check=1


		elif self.kategori == "Faktur Pajak Retur Keluaran" :
	
			for d in self.get_data_retur_keluaran :
					d.check=1

	@frappe.whitelist()
	def uncheckall(self) :
		if self.kategori == "Faktur Pajak Masukan" :
		
			for d in self.get_data_pajak_masukan :	
					d.check=0
					
		elif self.kategori == "PENJUALAN" :
		
			for d in self.get_data_pajak_keluaran :
					d.check=0


		elif self.kategori == "Faktur Pajak Retur Masukan" :
		
			for d in self.get_data_retur_masukan :
					d.check=0


		elif self.kategori == "Faktur Pajak Retur Keluaran" :
	
			for d in self.get_data_retur_keluaran :
					d.check=0


	def validate(self):
		if self.kategori == "Faktur Pajak Masukan" or self.kategori == "Faktur Pajak Retur Masukan" :
			self.check_nomorfaktur()
	

	def check_nomorfaktur(self) :
		
		if self.kategori == "Faktur Pajak Masukan" :

			exc_list = []
			text = ""
			i = 0
			check = 0 
			
			for d in self.get_data_pajak_masukan :

				i = i+1
				a =  d.nomor_faktur

				if  a in exc_list :

					text = text + (("\n" +"Sama pada {} di Row {} pada nomor invoice {}   ").format(d.nomor_faktur, i , d.referensi) ) + "<br>"

					check = 1

				else :
					if (str(a)!="") :
						exc_list.append(a)

			if (check==1) :
				frappe.msgprint(("{0}").format(text))


		elif self.kategori == "Faktur Pajak Retur Masukan" :

			exc_list = []
			text = ""
			i = 0
			check = 0 
			
			for d in self.get_data_retur_masukan :

				i = i+1
				a =  d.nomor_faktur

				if  a in exc_list :

					text = text + (("\n" +"Sama pada {} di Row {} pada nomor invoice {}   ").format(d.nomor_faktur, i , d.referensi) ) + "<br>"

					check = 1

				else :
					if (str(a)!="") :
						exc_list.append(a)

			if (check==1) :
				frappe.msgprint(("{0}").format(text))