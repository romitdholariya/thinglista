frappe.ui.form.on('Item', {
    refresh: function(frm) {
        frm.add_custom_button(__('Send Email'), function() {
            send_email_with_invoices(frm);
        }, __('Actions'));
    }
});

function send_email_with_invoices(frm) {
    frappe.call({
        method: "thingslista.doc_events.item.send_email_with_invoices",
        args: {
            item_code: frm.doc.item_code
        },
        callback: function(r) {
            if(r.message) {
                frappe.msgprint(__(r.message));
            }
        }
    });
}
