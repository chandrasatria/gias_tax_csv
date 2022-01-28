// Copyright (c) 2016, Bobby and contributors
// For license information, please see license.txt

frappe.ui.form.on('EFilling Tool', {
	refresh: function(frm) {
	}
});

cur_frm.cscript.print_to_excel= function(doc) {
	let get_template_url = frappe.request.url;

	var args = {}
	
	// catatan buat rico >> kuncinya disini..buat manggil runserverobj custom kita
	// jadi efilling_open_url_post itu cmn manggil API untuk manggil method python
	args.cmd = 'tax.tax.doctype.efilling_tool.custom_export.runserverobj';
	args.as_csv = 1;
	args.method = "print_to_excel";
	args.arg = "";

	if(doc.substr){
		args.doctype = doc.doctype;
	} else{
		args.docs = doc;
	}

	efilling_open_url_post(get_template_url, args);
}

frappe.query_reports["EFilling Tool"] = {
	"filters": [
		{
			"fieldname": "tanggal_faktur",
			"label": __("Tanggal"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.get_today()
		},

		]
}

function efilling_open_url_post(URL, PARAMS, new_window) {
	if (window.cordova) {
		let url = URL + 'api/method/' + PARAMS.cmd + frappe.utils.make_query_string(PARAMS, false);
		window.location.href = url;
	} else {
		// call a url as POST
		var temp=document.createElement("form");
		temp.action=URL;
		temp.method="POST";
		temp.style.display="none";
		if(new_window){
			temp.target = '_blank';
		}
		PARAMS["csrf_token"] = frappe.csrf_token;
		for(var x in PARAMS) {
			var opt=document.createElement("textarea");
			opt.name=x;
			var val = PARAMS[x];
			if(typeof val!='string')
				val = JSON.stringify(val);
			opt.value=val;
			temp.appendChild(opt);
		}
		document.body.appendChild(temp);
		temp.submit();
		return temp;
	}
};