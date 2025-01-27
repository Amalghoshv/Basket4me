import frappe
import requests
import json
from datetime import datetime


@frappe.whitelist(allow_guest=True)
def sync_customers_from_external_api():
    external_api_url = "https://dev-api.basket4me.com:8443/api/businesserp/customers"
    external_api_headers = {
        "x-access-apikey": "X355D9FAC5E211EF80AB0A46B22E7688"
    }
    external_api_params = {
        "storeCode": "BRUAE101S00101",
        "accessDate": "2024-12-29",
        "page": 1
    }

    try:
        response = requests.get(external_api_url, headers=external_api_headers, params=external_api_params)
        response.raise_for_status()
        data = response.json()

        if not data or "data" not in data:
            frappe.log_error("No data received from external API", "Sync Customers")
            return

        for customer in data["data"]:
            store_name = customer.get("storeName")

            if not store_name:
                frappe.log_error("Missing 'storeName' in customer data", "Sync Customers")
                continue

            existing_customer = frappe.db.get_value(
                "Customer", {"customer_name": store_name}, ["name"], as_dict=True
            )

            customer_payload = {
                "customer_name": store_name,
                "custom_customer_code": customer.get("storeId"),
                "custom_store_mobile": customer.get("storeMobile"),
                "custom_district": customer.get("storeDistrictName"),
                "custom_custom_location": customer.get("storeLocationName"),
                "custom_state": customer.get("storeStateName"),
                "custom_pin_code": customer.get("storePinCode"),
                "custom_name_of_contact_person": customer.get("storeContactPerson")
            }

            if existing_customer:
                customer_doc = frappe.get_doc("Customer", existing_customer["name"])
                changes_made = False

                for key, value in customer_payload.items():
                    if customer_doc.get(key) != value:
                        customer_doc.set(key, value)
                        changes_made = True

                if changes_made:
                    customer_doc.save(ignore_permissions=True)
                    frappe.db.commit()
            else:
                customer_doc = frappe.get_doc({
                    "doctype": "Customer",
                    **customer_payload
                })
                customer_doc.insert(ignore_permissions=True)
                frappe.db.commit()

    except requests.exceptions.RequestException as e:
        frappe.log_error(f"Failed to fetch data: {e}", "Sync Customers")
    except Exception as e:
        frappe.log_error(f"Error syncing customers: {e}", "Sync Customers")




@frappe.whitelist(allow_guest=True)
def sync_items_from_external_api():
    external_api_url = "https://dev-api.basket4me.com:8443/api/businesserp/products"
    external_api_headers = {
        "accept": "application/json",
        "x-access-apikey": "X355D9FAC5E211EF80AB0A46B22E7688"
    }
    external_api_params = {
        "storeCode": "BRUAE101S00101",
        "accessDate": "2024-12-29",
        "page": 1 
    }
    
    items_per_page = 100  
    
    try:
        page = 1
        while True:
            external_api_params["page"] = page
            response = requests.get(external_api_url, headers=external_api_headers, params=external_api_params)
            response.raise_for_status()
            data = response.json()

            if not data or "data" not in data:
                frappe.log_error("No data received from external API", "Sync Items")
                return

            if not data["data"]:
                break

            for product in data["data"]:
                item_code = product.get("prodCode")  
                item_name = product.get("prodName")  
                description = product.get("prodDesc") or product.get("prodDetailDesc") 
                brand = product.get("brandName") 
                main_category = product.get("mainCategoryName")  
                category = product.get("categoryName") 

                units = frappe.parse_json(product.get("units", "[]"))
                base_unit = next((unit for unit in units if unit.get("baseUnit") == 1), {})
                stock_uom = base_unit.get("unitName") or "Nos"  

                item_payload = {
                    "item_code": item_code,
                    "item_name": item_name,
                    "description": description,
                    "brand": brand,
                    "item_group": main_category,
                    "stock_uom": stock_uom,
                    "custom_category": category,  
                }

                existing_item = frappe.db.get_value("Item", {"item_code": item_code}, ["name"], as_dict=True)

                if existing_item:
                    item_doc = frappe.get_doc("Item", existing_item["name"])
                    changes_made = False

                    for key, value in item_payload.items():
                        if item_doc.get(key) != value:
                            item_doc.set(key, value)
                            changes_made = True

                    if changes_made:
                        item_doc.save(ignore_permissions=True)
                        frappe.db.commit()
                else:
                    item_doc = frappe.get_doc({
                        "doctype": "Item",
                        **item_payload
                    })
                    item_doc.insert(ignore_permissions=True)
                    frappe.db.commit()

            page += 1

    except requests.exceptions.RequestException as e:
        frappe.log_error(f"Failed to fetch data: {e}", "Sync Items")
    except Exception as e:
        frappe.log_error(f"Error syncing items: {e}", "Sync Items")





@frappe.whitelist(allow_guest=True)
def sync_sales_orders_from_external_api():
    external_api_url = "https://dev-api.basket4me.com:8443/api/businesserp/salesOrders"
    external_api_headers = {
        "x-access-apikey": "X355D9FAC5E211EF80AB0A46B22E7688"
    }
    external_api_params = {
        "storeCode": "BRUAE101S00101",
        "accessDate": "2024-12-04",
        "page": 1
    }

    try:
        response = requests.get(external_api_url, headers=external_api_headers, params=external_api_params)
        response.raise_for_status()  
        data = response.json()

        if not data or "data" not in data:
            frappe.log_error("No data received from external API", "Sync Sales Orders")
            return

        for order in data["data"]:
            tran_ref_no = order.get("tranRefNo")

            if not tran_ref_no:
                frappe.log_error("Missing 'tranRefNo' in sales order data", "Sync Sales Orders")
                continue

            bStoreId = order.get("bStoreId")

            if not bStoreId:
                frappe.log_error(f"Missing 'bStoreId' in sales order {tran_ref_no}", "Sync Sales Orders")
                continue

            customer = frappe.db.get_value(
                "Customer", {"custom_customer_code": bStoreId}, ["name"], as_dict=True
            )

            if not customer:
                frappe.log_error(f"Customer with custom_customer_code {bStoreId} not found", "Sync Sales Orders")
                continue

            today_date = datetime.today().strftime("%Y-%m-%d")  
            sales_order_payload = {
                "customer": customer["name"],  
                "posting_date": today_date, 
                "delivery_date": today_date, 
                "total": sum([product['amount'] for product in json.loads(order['products'])]),
                "discount_amount": 0, 
                "net_total": sum([product['amount'] for product in json.loads(order['products'])]),
                "total_taxes_and_charges": 0, 
                "grand_total": sum([product['amount'] for product in json.loads(order['products'])]),
                "items": [],
                "po_no": tran_ref_no  
            }

            for product in json.loads(order['products']):
                item = {
                    "item_code": product['prodName'], 
                    "qty": product['quantity'],
                    "rate": product['tranSPPrice'],
                    "amount": product['amount']
                }
                sales_order_payload["items"].append(item)

            existing_order = frappe.db.get_value(
                "Sales Order", {"po_no": tran_ref_no}, ["name"], as_dict=True
            )

            if existing_order:
                sales_order_doc = frappe.get_doc("Sales Order", existing_order["name"])
                changes_made = False

                for key, value in sales_order_payload.items():
                    if sales_order_doc.get(key) != value:
                        sales_order_doc.set(key, value)
                        changes_made = True

                if changes_made:
                    sales_order_doc.save(ignore_permissions=True)
                    frappe.db.commit()
            else:
                sales_order_doc = frappe.get_doc({
                    "doctype": "Sales Order",
                    **sales_order_payload
                })
                sales_order_doc.insert(ignore_permissions=True)
                frappe.db.commit()

    except requests.exceptions.RequestException as e:
        frappe.log_error(f"Failed to fetch data: {e}", "Sync Sales Orders")
    except Exception as e:
        frappe.log_error(f"Error syncing sales orders: {e}", "Sync Sales Orders")


#invoice
@frappe.whitelist(allow_guest=True)
def sync_sales_invoices_from_external_api():
    external_api_url = "https://dev-api.basket4me.com:8443/api/businesserp/salesInvoices"
    external_api_headers = {
        "x-access-apikey": "X355D9FAC5E211EF80AB0A46B22E7688"
    }
    external_api_params = {
        "storeCode": "BRUAE101S00101",
        "accessDate": "2024-12-04",
        "page": 1
    }

    try:
        response = requests.get(external_api_url, headers=external_api_headers, params=external_api_params)
        response.raise_for_status()
        data = response.json()

        if not data or "data" not in data:
            frappe.log_error("No data received from external API", "Sync Sales Invoices")
            return

        for invoice in data["data"]:
            tran_ref_no = invoice.get("tranRefNo")

            if not tran_ref_no:
                frappe.log_error("Missing 'tranRefNo' in sales invoice data", "Sync Sales Invoices")
                continue

            bStoreId = invoice.get("bStoreId")

            if not bStoreId:
                frappe.log_error(f"Missing 'bStoreId' in sales invoice {tran_ref_no}", "Sync Sales Invoices")
                continue

            customer = frappe.db.get_value(
                "Customer", {"custom_customer_code": bStoreId}, ["name"], as_dict=True
            )

            if not customer:
                frappe.log_error(f"Customer with custom_customer_code {bStoreId} not found", "Sync Sales Invoices")
                continue

            try:
                posting_date = invoice.get("tranDate", "").split("T")[0]
                sales_invoice_payload = {
                    "customer": customer["name"],
                    "posting_date": posting_date,
                    "due_date": posting_date,
                    "total": sum([product['amount'] for product in json.loads(invoice['products'])]),
                    "net_total": sum([product['amount'] for product in json.loads(invoice['products'])]),
                    "total_taxes_and_charges": 0,
                    "grand_total": sum([product['amount'] for product in json.loads(invoice['products'])]),
                    "items": [],
                    "remarks": tran_ref_no
                }

                for product in json.loads(invoice['products']):
                    item_code = product['prodName']
                    if not frappe.db.exists("Item", item_code):
                        frappe.log_error(f"Item {item_code} not found. Skipping invoice {tran_ref_no}", "Sync Sales Invoices")
                        break

                    item = {
                        "item_code": item_code,
                        "qty": product['quantity'],
                        "rate": product['tranSPPrice'],
                        "amount": product['amount']
                    }
                    sales_invoice_payload["items"].append(item)
                else:
                    existing_invoice = frappe.db.get_value(
                        "Sales Invoice", {"remarks": tran_ref_no}, ["name"], as_dict=True
                    )

                    if existing_invoice:
                        sales_invoice_doc = frappe.get_doc("Sales Invoice", existing_invoice["name"])
                        changes_made = False

                        for key, value in sales_invoice_payload.items():
                            if sales_invoice_doc.get(key) != value:
                                sales_invoice_doc.set(key, value)
                                changes_made = True

                        if changes_made:
                            sales_invoice_doc.save(ignore_permissions=True)
                            frappe.db.commit()
                    else:
                        sales_invoice_doc = frappe.get_doc({
                            "doctype": "Sales Invoice",
                            **sales_invoice_payload
                        })
                        sales_invoice_doc.insert(ignore_permissions=True)
                        frappe.db.commit()

            except Exception as inner_e:
                frappe.log_error(f"Error processing invoice {tran_ref_no}: {inner_e}", "Sync Sales Invoices")

    except requests.exceptions.RequestException as e:
        frappe.log_error(f"Failed to fetch data: {e}", "Sync Sales Invoices")
    except Exception as e:
        frappe.log_error(f"Error syncing sales invoices: {e}", "Sync Sales Invoices")

#payment entry

@frappe.whitelist(allow_guest=True)
def sync_payment_entries_from_external_api():
    external_api_url = "https://dev-api.basket4me.com:8443/api/businesserp/receipts"
    external_api_headers = {
        "x-access-apikey": "X355D9FAC5E211EF80AB0A46B22E7688"
    }
    external_api_params = {
        "storeCode": "BRUAE101S00101",
        "accessDate": "2024-12-04",
        "page": 1
    }

    try:
        response = requests.get(external_api_url, headers=external_api_headers, params=external_api_params)
        response.raise_for_status()
        data = response.json()

        if not data or "data" not in data:
            frappe.log_error("No data received from external API for payment entries", "Sync Payment Entries")
            return

        for receipt in data["data"]:
            tran_ref_no = receipt.get("tranRefNo")

            if not tran_ref_no:
                frappe.log_error("Missing 'tranRefNo' in payment receipt data", "Sync Payment Entries")
                continue

            customer = frappe.db.get_value(
                "Customer", {"custom_customer_code": receipt.get("bStoreId")}, ["name"], as_dict=True
            )

            if not customer:
                frappe.log_error(f"Customer with custom_customer_code {receipt.get('bStoreId')} not found", "Sync Payment Entries")
                continue

            transaction_currency = receipt.get("currencyCD", "").strip()
            default_currency = frappe.defaults.get_global_default("currency")

            exchange_rate = 1.0
            if transaction_currency and transaction_currency != default_currency:
                exchange_rate = frappe.db.get_value(
                    "Currency Exchange",
                    {"from_currency": transaction_currency, "to_currency": default_currency},
                    "exchange_rate"
                )
                if not exchange_rate:
                    frappe.log_error(
                        f"Exchange rate not found for {transaction_currency} to {default_currency}",
                        "Sync Payment Entries"
                    )
                    continue

            try:
                payment_entry_payload = {
                    "posting_date": receipt.get("tranDate", "").split("T")[0],
                    "party_type": "Customer",
                    "party": customer["name"],
                    "payment_type": "Receive",
                    "paid_amount": receipt.get("amountPaid"),
                    "received_amount": receipt.get("amountPaid") * exchange_rate,
                    "source_exchange_rate": 1.0,
                    "target_exchange_rate": exchange_rate,
                    "reference_no": tran_ref_no,
                    "reference_date": receipt.get("tranDate", "").split("T")[0],
                    "remarks": receipt.get("remarks"),
                    "mode_of_payment": receipt.get("paymentType").capitalize(),
                    "currency": transaction_currency or default_currency,
                    "paid_to": "Cash - E"  
                }

                existing_payment_entry = frappe.db.get_value(
                    "Payment Entry", {"reference_no": tran_ref_no}, ["name"], as_dict=True
                )

                if existing_payment_entry:
                    payment_entry_doc = frappe.get_doc("Payment Entry", existing_payment_entry["name"])
                    changes_made = False

                    for key, value in payment_entry_payload.items():
                        if payment_entry_doc.get(key) != value:
                            payment_entry_doc.set(key, value)
                            changes_made = True

                    if changes_made:
                        payment_entry_doc.save(ignore_permissions=True)
                        frappe.db.commit()
                else:
                    payment_entry_doc = frappe.get_doc({
                        "doctype": "Payment Entry",
                        **payment_entry_payload
                    })
                    payment_entry_doc.insert(ignore_permissions=True)
                    frappe.db.commit()

            except Exception as inner_e:
                frappe.log_error(f"Error processing payment receipt {tran_ref_no}: {inner_e}", "Sync Payment Entries")

    except requests.exceptions.RequestException as e:
        frappe.log_error(f"Failed to fetch data: {e}", "Sync Payment Entries")
    except Exception as e:
        frappe.log_error(f"Error syncing payment entries: {e}", "Sync Payment Entries")
