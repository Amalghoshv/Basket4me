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





import frappe
import requests
import json
from datetime import datetime

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
