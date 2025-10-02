# streamlit_app.py - Streamlit Frontend
import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime

# Configuration - Use environment variable for backend URL
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5001")
API_BASE_URL = f"{BACKEND_URL}/api"

# Page config
st.set_page_config(
    page_title="Ganpati Electronics and E Services - Dynamic Billing System",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
    font-size: 2.8rem;
    color: #4a4e58;
    text-align: center;
    margin-bottom: 4rem;
}
    .section-header {
        font-size: 1.2rem;
        color: #3b82f6;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
    }
    .info-box {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #c9ccd0;
    border-left
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'inventory' not in st.session_state:
    st.session_state.inventory = []

# Helper functions
def fetch_inventory():
    try:
        response = requests.get(f"{API_BASE_URL}/inventory", timeout=10)
        if response.status_code == 200:
            inventory = response.json()
            st.session_state.inventory = inventory
            return inventory
        else:
            st.error(f"Failed to fetch inventory: {response.text}")
            return []
    except requests.exceptions.ConnectionError:
        st.info("💡 **Solution**: Run `python app.py` in your terminal to start the Flask backend.")
        return []
    except requests.exceptions.Timeout:
        st.error("⏰ **Timeout Error**: The server is taking too long to respond.")
        return []
    except Exception as e:
        st.error(f"❌ **Error fetching inventory**: {str(e)}")
        return []

def add_item_to_inventory(name, price):
    try:
        response = requests.post(
            f"{API_BASE_URL}/inventory",
            json={'name': name, 'price': price},
            timeout=10
        )
        if response.status_code == 201:
            # Automatically refresh inventory after adding
            new_item = response.json()
            st.success(f"✅ Added '{new_item['name']}' with ID {new_item['id']}")
            fetch_inventory()
            return True
        else:
            error_msg = response.json().get('error', 'Unknown error') if response.headers.get('content-type', '').startswith('application/json') else response.text
            st.error(f"❌ Failed to add item: {error_msg}")
            return False
    except requests.exceptions.ConnectionError:
        st.error("🔴 **Connection Error**: Cannot connect to the Flask server.")
        return False
    except Exception as e:
        st.error(f"❌ Error adding item: {str(e)}")
        return False

def update_inventory_item(item_id, name, price):
    try:
        response = requests.put(
            f"{API_BASE_URL}/inventory/{item_id}",
            json={'name': name, 'price': price},
            timeout=10
        )
        if response.status_code == 200:
            fetch_inventory()
            return True
        else:
            st.error(f"❌ Failed to update item: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        st.error("🔴 **Connection Error**: Cannot connect to the Flask server.")
        return False
    except Exception as e:
        st.error(f"❌ Error updating item: {str(e)}")
        return False

def delete_inventory_item(item_id):
    try:
        response = requests.delete(f"{API_BASE_URL}/inventory/{item_id}", timeout=10)
        if response.status_code == 200:
            fetch_inventory()
            return True
        else:
            st.error(f"❌ Failed to delete item: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        st.error("🔴 **Connection Error**: Cannot connect to the Flask server.")
        return False
    except Exception as e:
        st.error(f"❌ Error deleting item: {str(e)}")
        return False

def delete_bill(bill_id):
    try:
        response = requests.delete(f"{API_BASE_URL}/bills/{bill_id}", timeout=10)
        if response.status_code == 200:
            st.success(f"✅ Bill {bill_id} deleted successfully!")
            return True
        elif response.status_code == 404:
            st.error(f"❌ Bill {bill_id} not found")
            return False
        else:
            error_msg = response.json().get('error', 'Unknown error') if response.headers.get('content-type', '').startswith('application/json') else response.text
            st.error(f"❌ Failed to delete bill: {error_msg}")
            return False
    except requests.exceptions.ConnectionError:
        st.error("🔴 **Connection Error**: Cannot connect to the Flask server.")
        return False
    except Exception as e:
        st.error(f"❌ Error deleting bill: {str(e)}")
        return False

def add_to_cart(item):
    for cart_item in st.session_state.cart:
        if cart_item['id'] == item['id']:
            cart_item['quantity'] += 1
            return
    st.session_state.cart.append({**item, 'quantity': 1})

def remove_from_cart(item_id):
    st.session_state.cart = [item for item in st.session_state.cart if item['id'] != item_id]

def update_cart_quantity(item_id, quantity):
    for item in st.session_state.cart:
        if item['id'] == item_id:
            item['quantity'] = max(1, quantity)

def calculate_total():
    subtotal = sum(item['price'] * item['quantity'] for item in st.session_state.cart)
    return subtotal

# Sidebar - Shop Information
# with st.sidebar:
#     st.markdown("### 🏪 Shop Information")
#     st.markdown("""
#     <div style="background-color: #f0f9ff; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #3b82f6;">
#         <h4 style="color: #1e40af; margin-top: 0;">Ganpati Electronics and E Services</h4>
#         <p style="margin: 0.2rem 0; color: #4b5563;"><strong>Owner:</strong> Joga Ram Sai, Devendra Choudhary</p>
#         <p style="margin: 0.2rem 0; color: #4b5563;"><strong>📍 Address:</strong> Batadoo, Barmer (Raj)</p>
#         <p style="margin: 0.2rem 0; color: #4b5563;"><strong>📞 Phone:</strong> 9928754381, 7726969098</p>
#         <p style="margin: 0.2rem 0; color: #4b5563;"><strong>📧 Email:</strong> ganpatiemitrabatadu@gmail.com</p>
        
#     </div>
#     """, unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🧾 Ganpati Electronics and E Services - Dynamic Billing System</h1>', unsafe_allow_html=True)

# Connection status check
def check_backend_connection():
    try:
        response = requests.get(f"{API_BASE_URL}/../", timeout=5)  # Check root endpoint
        return response.status_code == 200
    except:
        return False

# Display connection status




# Main tabs
tab1, tab2, tab3 = st.tabs(["🛒 Billing", "📦 Inventory Management", "📋 Bill History"])

# TAB 1: BILLING
with tab1:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<div class="section-header">Product Catalog</div>', unsafe_allow_html=True)
        
        # Fetch inventory automatically if empty
        if not st.session_state.inventory:
            with st.spinner("Loading inventory..."):
                st.session_state.inventory = fetch_inventory()
        
        # Auto-refresh inventory button
        col_refresh, col_search, col_empty = st.columns([1, 2, 2])
        with col_refresh:
            if st.button("🔄 Refresh", key="refresh_billing"):
                with st.spinner("Refreshing inventory..."):
                    fetch_inventory()
                    st.experimental_rerun()
        
        with col_search:
            # Search - now half the length
            search_term = st.text_input("🔍 Search products", placeholder="Search by name", label_visibility="collapsed")
        
        with col_empty:
            st.empty()  # Empty space

        # Filter inventory
        filtered_inventory = st.session_state.inventory
        if search_term:
            filtered_inventory = [
                item for item in st.session_state.inventory
                if search_term.lower() in item['name'].lower()
            ]
        
        # Display products in smaller, more compact boxes
        if filtered_inventory:
            for i in range(0, len(filtered_inventory), 4):  # 4 items per row instead of 3
                cols = st.columns(4)
                for j, col in enumerate(cols):
                    if i + j < len(filtered_inventory):
                        item = filtered_inventory[i + j]
                        with col:
                            # Smaller, more compact product cards
                            st.markdown(f"""
                            <div style="
                                background-color: #f8f9fa; 
                                padding: 0.5rem; 
                                border-radius: 0.3rem; 
                                border-left: 2px solid #3b82f6;
                                margin-bottom: 0.3rem;
                                height: 90px;
                                display: flex;
                                flex-direction: column;
                                justify-content: space-between;
                            ">
                                <h6 style="margin: 0; font-size: 0.8rem; color: #1f2937; line-height: 1.2;">{item['name']}</h6>
                                <p style="margin: 0.2rem 0; font-size: 0.75rem; color: #059669; font-weight: bold;">₹{item['price']:.2f}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            if st.button(f"➕", key=f"add_{item['id']}", help=f"Add {item['name']} to cart"):
                                add_to_cart(item)
                                st.success(f"Added {item['name']} to cart!")
                                st.experimental_rerun()
        else:
            st.info("No products found. Add items to inventory first.")
    
    with col2:
        # Shopping cart header with clear button on the right
        col_header, col_clear = st.columns([2, 1])
        with col_header:
            st.markdown('<div class="section-header">Shopping Cart</div>', unsafe_allow_html=True)
        with col_clear:
            if st.session_state.cart:
                if st.button("🗑️ Clear Cart", type="secondary", use_container_width=True):
                    st.session_state.cart = []
                    st.success("🧹 Cart cleared!")
                    st.experimental_rerun()
        
        if st.session_state.cart:
            for item in st.session_state.cart:
                with st.container():
                    st.markdown(f"**{item['name']}**")
                    col_qty, col_price, col_remove = st.columns([2, 2, 1])
                    
                    with col_qty:
                        new_qty = st.number_input(
                            "Qty",
                            min_value=1,
                            value=item['quantity'],
                            key=f"qty_{item['id']}",
                            label_visibility="collapsed"
                        )
                        if new_qty != item['quantity']:
                            update_cart_quantity(item['id'], new_qty)
                            st.experimental_rerun()
                    
                    with col_price:
                        st.text(f"₹{item['price'] * item['quantity']:.2f}")
                    
                    with col_remove:
                        if st.button("🗑️", key=f"remove_{item['id']}"):
                            remove_from_cart(item['id'])
                            st.experimental_rerun()
                    
                    st.markdown("---")
            
            # Totals
            subtotal = calculate_total()
            total = subtotal
            
            st.markdown(f"""
            **Subtotal:** ₹{subtotal:.2f}  
            **Total:** ₹{total:.2f}
            """)
            
            st.markdown('<div class="section-header">Customer Details</div>', unsafe_allow_html=True)
            customer_name = st.text_input("Customer Name*", key="cust_name")
            customer_phone = st.text_input("Mobile Number*", key="cust_phone")
            payment_status = st.selectbox("Payment Status", ["Paid", "Unpaid"])
            notes = st.text_area("Remarks (Optional)", key="cust_notes", height=60)
            
            if st.button("🧾 Generate Bill", type="primary", use_container_width=True):
                if not customer_name or not customer_phone:
                    st.error("Customer name and mobile number are required!")
                else:
                    # Prepare bill data
                    bill_data = {
                        'shop': {
                            'name': 'Ganpati Electronics and E Services',
                            'owner': 'Jogaram Sai',
                            'address': 'Batadoo, Barmer (Raj)',
                            'phone': '9928754381, 7726969098',
                            'email': 'ganpatiemitrabatadu@gmail.com'
                        },
                        'customer': {
                            'name': customer_name,
                            'phone': customer_phone
                        },
                        'items': [
                            {
                                'name': item['name'],
                                'quantity': item['quantity'],
                                'price': item['price'],
                                'total': item['price'] * item['quantity']
                            }
                            for item in st.session_state.cart
                        ],
                        'subtotal': subtotal,
                        'total': total,
                        'payment_status': payment_status,
                        'notes': notes
                    }
                    
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/generate-bill",
                            json=bill_data,
                            timeout=30  # Longer timeout for PDF generation
                        )
                        
                        if response.status_code == 200:
                            st.success("✅ Bill generated successfully!")
                            
                            # Download button
                            st.download_button(
                                label="📥 Download PDF",
                                data=response.content,
                                file_name=f"Bill_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf"
                            )
                            
                            st.info("💡 Cart will be cleared automatically after successful bill generation.")
                            # Auto-clear cart after successful bill generation
                            st.session_state.cart = []
                        else:
                            st.error(f"❌ Error generating bill: {response.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("🔴 **Connection Error**: Cannot connect to the Flask server.")
                    except requests.exceptions.Timeout:
                        st.error("⏰ **Timeout Error**: Bill generation is taking too long.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            st.info("Cart is empty. Add items to start billing.")

# TAB 2: INVENTORY MANAGEMENT
with tab2:
    st.markdown('<div class="section-header">Inventory Management</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Add New Item")
        with st.form("add_item_form"):
            new_name = st.text_input("Item Name*")
            new_price = st.number_input("Price*", min_value=0, step=10)
         
            
            submit = st.form_submit_button("➕ Add Item", use_container_width=True)
            if submit:
                if new_name and new_price :
                    if add_item_to_inventory(new_name, new_price):
                        # Success message is handled in the function
                        st.experimental_rerun()
                    else:
                        # Error message is handled in the function
                        pass
                else:
                    st.error("❌ All fields are required!")
        
        st.markdown("---")
        st.markdown("#### Import from CSV")
        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
        if uploaded_file:
            st.info("CSV should have columns: name, price")
            if st.button("📤 Import"):
                try:
                    files = {'file': uploaded_file}
                    response = requests.post(f"{API_BASE_URL}/inventory/import", files=files, timeout=15)
                    if response.status_code == 200:
                        st.success(f"✅ {response.json()['message']}")
                        fetch_inventory()
                        st.experimental_rerun()
                    else:
                        st.error(f"❌ {response.json().get('error', 'Import failed')}")
                except requests.exceptions.ConnectionError:
                    st.error("🔴 **Connection Error**: Cannot connect to the Flask server.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        st.markdown("#### Current Inventory")
        if st.button("🔄 Refresh", key="refresh_inventory"):
            with st.spinner("Refreshing inventory..."):
                fetch_inventory()
                st.experimental_rerun()
        
        if st.session_state.inventory:
            df = pd.DataFrame(st.session_state.inventory)
            
            # Display as editable table
            st.dataframe(
                df,
                column_config={
                    "id": "ID",
                    "name": st.column_config.TextColumn("Name", width="medium"),
                    "price": st.column_config.NumberColumn("Price", format="₹%.2f")
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Delete item
            st.markdown("#### Delete Item")
            item_to_delete = st.selectbox(
                "Select item to delete",
                options=st.session_state.inventory,
                format_func=lambda x: f"{x['name']} - ₹{x['price']:.2f}"
            )
            if st.button("🗑️ Delete Selected Item", type="secondary"):
                if delete_inventory_item(item_to_delete['id']):
                    st.success(f"✅ Deleted {item_to_delete['name']}")
                    st.experimental_rerun()
                else:
                    st.error("❌ Failed to delete item")
        else:
            st.info("No items in inventory")

# TAB 3: BILL HISTORY
with tab3:
    st.markdown('<div class="section-header">Bill History</div>', unsafe_allow_html=True)
    
    try:
        response = requests.get(f"{API_BASE_URL}/bills", timeout=10)
        if response.status_code == 200:
            bills = response.json()
            if bills:
                df = pd.DataFrame(bills)
                
                # Display bills with action buttons
                st.subheader("📋 All Bills")
                
                for index, bill in df.iterrows():
                    with st.expander(f"Bill {bill['bill_id']} - {bill['customer_name']} - {bill['total']:.2f} ({bill['payment_status']})"):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.write(f"**Date:** {bill['date']}")
                            st.write(f"**Customer:** {bill['customer_name']}")
                            st.write(f"**Phone:** {bill.get('customer_phone', 'N/A')}")
                            st.write(f"**Email:** {bill.get('customer_email', 'N/A')}")
                            st.write(f"**Total:** {bill['total']:.2f}Rs")
                            st.write(f"**Payment Status:** {bill['payment_status']}")
                            if bill.get('notes'):
                                st.write(f"**Notes:** {bill['notes']}")
                        
                        with col2:
                            # View Items button with better formatting - add date to make key unique
                            bill_date_key = bill['date'].replace(' ', '_').replace(':', '_').replace('-', '_')
                            if st.button(f"👁️ View Items", key=f"view_{bill['bill_id']}_{bill_date_key}"):
                                try:
                                    import ast
                                    items = ast.literal_eval(bill['items']) if bill['items'] else []
                                    st.markdown("**Items in this bill:**")
                                    for idx, item in enumerate(items, 1):
                                        st.markdown(f"**{idx}.** {item['name']} - Qty: {item['quantity']} - Price: ₹{item['price']:.2f} - **Total: ₹{item['total']:.2f}**")
                                except:
                                    st.error("Items data not available")
                        
                        with col3:
                            # Delete button - add date to make key unique
                            if st.button(f"🗑️ Delete", key=f"delete_{bill['bill_id']}_{bill_date_key}", type="secondary"):
                                if st.session_state.get(f"confirm_delete_{bill['bill_id']}", False):
                                    if delete_bill(bill['bill_id']):
                                        st.experimental_rerun()
                                else:
                                    st.session_state[f"confirm_delete_{bill['bill_id']}"] = True
                                    st.warning("⚠️ Click Delete again to confirm")
                
                # Summary statistics
                st.subheader("📊 Statistics")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Bills", len(df))
                with col2:
                    st.metric("Total Revenue", f"{df['total'].sum():.2f}Rs")
                with col3:
                    paid_count = len(df[df['payment_status'] == 'Paid'])
                    st.metric("Paid Bills", paid_count)
                with col4:
                    unpaid_count = len(df[df['payment_status'] == 'Unpaid'])
                    st.metric("Unpaid Bills", unpaid_count)
                
                # Data table view
                st.subheader("📋 Table View")
                st.dataframe(
                    df[['bill_id', 'date', 'customer_name', 'total', 'payment_status']],
                    column_config={
                        "bill_id": "Bill ID",
                        "date": "Date",
                        "customer_name": "Customer",
                        "total": st.column_config.NumberColumn("Total", format="₹%.2f"),
                        "payment_status": "Status"
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No bills generated yet")
        else:
            st.error(f"❌ Failed to fetch bills: {response.text}")
    except requests.exceptions.ConnectionError:
        st.error("🔴 **Connection Error**: Cannot connect to the Flask server.")
        st.info("💡 **Solution**: Ensure the Flask backend is running on port 5001.")
    except Exception as e:
        st.error(f"❌ Error fetching bills: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; padding: 2rem;">
    <p>Ganpati Electronics and E Services - Dynamic Billing System v1.0 | Built with Streamlit & Flask</p>
    <p>© 2025 Ganpati Electronics and E Services. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)