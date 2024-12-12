// Copyright (c) 2024, siva and contributors
// For license information, please see license.txt

frappe.ui.form.on('Service Request', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__("Create Sales Invoice"), () => {
                frappe.new_doc("Sales Invoice", {}, invoice => {
                    invoice.items = [];

                    invoice.customer = frm.doc.customer;
                    invoice.company = frm.doc.company;
                    invoice.posting_date = frappe.datetime.now_date();

                    frm.doc.parts_replaced.forEach(part => {
                        if (part.part_name && part.quantity_qty > 0) { 
                            let invoice_item = frappe.model.add_child(invoice, 'items');
                            invoice_item.item_code = part.part_name; 
                            invoice_item.qty = part.quantity_qty;
                            invoice_item.uom = "Nos"; 
                        }
                    });

                    frappe.set_route("Form", "Sales Invoice", invoice.name);
                });
            }, __("Create"));
        }
    }
});
