import frappe
from frappe.core.doctype.communication.email import make
from frappe.utils.pdf import get_pdf
from jinja2 import Template

@frappe.whitelist()
def send_email_with_invoices(item_code):
    invoices = frappe.db.sql("""
        select
            DISTINCT si.name, si.posting_date
        from
            `tabSales Invoice Item` as si_item
            JOIN `tabSales Invoice` as si on si.name = si_item.parent
        where
            si.docstatus = 1 and si_item.item_code = '{}'
        order by
            timestamp(si.posting_date, si.posting_time) desc
        limit 5
    """.format(item_code), as_dict= True)

    if not invoices:
        return 'No invoices found for this item'

    attachments = []
    for invoice in invoices:
        html_content = frappe.get_print('Sales Invoice', invoice.name, print_format='Standard')
        pdf_data = get_pdf(html_content)
        
        attachments.append({
            'fname': f"{invoice.name}.pdf",
            'fcontent': pdf_data,
            'content_type': 'application/pdf'  
        })
   
    template_str = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Invoice Summary</title>
    </head>
    <body>
        <p>Dear Customer,</p>

        <p>Please find a summary of your recent invoices:</p>

        <table border="1" cellspacing="0" cellpadding="5">
            <thead>
                <tr>
                    <th>Invoice Name</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                {% for invoice in invoices %}
                <tr>
                    <td>{{ invoice.name }}</td>
                    <td>{{ invoice.posting_date }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

    </body>
    </html>
    """

    template = Template(template_str)
    message = template.render({'invoices': invoices})

    recipient = 'romitpatel414@gmail.com'
    subject = f'Latest 5 Sales Invoices for Item {item_code}'

    email = make(subject=subject, content=message, recipients=[recipient],
                 attachments=attachments, send_email=True)

    return 'Email sent successfully'
