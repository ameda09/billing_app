# app.py - Flask Backend
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import io
import base64
from PIL import Image as PILImage

app = Flask(__name__)
CORS(app)

# File paths
INVENTORY_CSV = 'inventory.csv'
BILLS_CSV = 'bills.csv'
SIGNATURES_DIR = 'signatures'

# Ensure directories exist
os.makedirs(SIGNATURES_DIR, exist_ok=True)

# Initialize CSV files if they don't exist
def initialize_files():
    if not os.path.exists(INVENTORY_CSV):
        df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Laptop', 'Wireless Mouse', 'Office Chair', 'Desk Lamp', 'Notebook Set'],
            'price': [899.99, 29.99, 249.99, 45.99, 12.99]
        })
        df.to_csv(INVENTORY_CSV, index=False)
    else:
        # Clean existing file - remove category column if it exists
        df = pd.read_csv(INVENTORY_CSV)
        if 'category' in df.columns:
            df = df.drop('category', axis=1)
            df.to_csv(INVENTORY_CSV, index=False)
            print("Removed category column from existing inventory.csv")
    
    if not os.path.exists(BILLS_CSV):
        df = pd.DataFrame(columns=['bill_id', 'date', 'customer_name', 'customer_phone', 
                                   'customer_email', 'items', 'total', 'payment_status', 'notes'])
        df.to_csv(BILLS_CSV, index=False)

initialize_files()

# Fixed shop details
SHOP_DETAILS = {
    'name': 'Prime Retail Store',
    'owner': 'John Doe',
    'address': '123 Business Street, Commerce City',
    'phone': '+1 (555) 123-4567',
    'email': 'contact@primeretail.com',
    'gst': 'GST123456789'
}

# Root route
@app.route('/')
def home():
    return jsonify({
        'message': 'Flask Billing API is running!',
        'shop': SHOP_DETAILS,
        'version': '1.0',
        'endpoints': {
            'shop': '/api/shop',
            'inventory': '/api/inventory',
            'bills': '/api/bills',
            'delete_bill': '/api/bills/<bill_id>',
            'generate_bill': '/api/generate-bill',
            'signature': '/api/signature'
        },
        'frontend': 'Access the Streamlit app at http://localhost:8501'
    })

# Get all inventory items
@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    try:
        df = pd.read_csv(INVENTORY_CSV)
        # Convert pandas data types to Python native types for JSON serialization
        records = df.to_dict('records')
        for record in records:
            record['id'] = int(record['id'])
            record['price'] = float(record['price'])
        return jsonify(records)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Add new item to inventory
@app.route('/api/inventory', methods=['POST'])
def add_inventory_item():
    try:
        data = request.json
        df = pd.read_csv(INVENTORY_CSV)
        
        new_id = int(df['id'].max() + 1) if len(df) > 0 else 1
        new_item = {
            'id': new_id,
            'name': data['name'],
            'price': float(data['price'])
    
        }
        
        df = pd.concat([df, pd.DataFrame([new_item])], ignore_index=True)
        df.to_csv(INVENTORY_CSV, index=False)
        
        return jsonify(new_item), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update inventory item
@app.route('/api/inventory/<int:item_id>', methods=['PUT'])
def update_inventory_item(item_id):
    try:
        data = request.json
        df = pd.read_csv(INVENTORY_CSV)
        
        df.loc[df['id'] == item_id, 'name'] = data['name']
        df.loc[df['id'] == item_id, 'price'] = float(data['price'])
    
        
        df.to_csv(INVENTORY_CSV, index=False)
        return jsonify({'message': 'Item updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delete inventory item
@app.route('/api/inventory/<int:item_id>', methods=['DELETE'])
def delete_inventory_item(item_id):
    try:
        df = pd.read_csv(INVENTORY_CSV)
        df = df[df['id'] != item_id]
        df.to_csv(INVENTORY_CSV, index=False)
        return jsonify({'message': 'Item deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Import CSV
@app.route('/api/inventory/import', methods=['POST'])
def import_inventory():
    try:
        file = request.files['file']
        df = pd.read_csv(file)
        
        # Validate columns
        required_columns = ['name', 'price']
        if not all(col in df.columns for col in required_columns):
            return jsonify({'error': 'CSV must contain name and price columns'}), 400

        existing_df = pd.read_csv(INVENTORY_CSV)
        max_id = int(existing_df['id'].max()) if len(existing_df) > 0 else 0
        
        df['id'] = range(max_id + 1, max_id + 1 + len(df))
        df = pd.concat([existing_df, df], ignore_index=True)
        df.to_csv(INVENTORY_CSV, index=False)
        
        return jsonify({'message': f'{len(df) - len(existing_df)} items imported successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Save signature
@app.route('/api/signature', methods=['POST'])
def save_signature():
    try:
        data = request.json
        signature_data = data['signature']
        
        # Remove header from base64 string
        if ',' in signature_data:
            signature_data = signature_data.split(',')[1]
        
        # Save signature
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'signature_{timestamp}.png'
        filepath = os.path.join(SIGNATURES_DIR, filename)
        
        with open(filepath, 'wb') as f:
            f.write(base64.b64decode(signature_data))
        
        return jsonify({'filename': filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Generate PDF Bill
@app.route('/api/generate-bill', methods=['POST'])
def generate_bill():
    try:
        data = request.json
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=0.175*inch,  # Reduced from 0.7 to 0.175 (25% of original)
            leftMargin=0.175*inch,   # Reduced from 0.7 to 0.175 (25% of original)
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles - Better fonts and styling
        shop_name_style = ParagraphStyle(
            'ShopName',
            parent=styles['Heading1'],
            fontSize=20,  # Reduced from 24 to fit in one line
            textColor=colors.HexColor('#000000'),
            spaceAfter=4,  # Reduced spacing
            alignment=TA_CENTER,
            fontName='Times-Bold'  # Changed to Times-Bold for better appearance
        )
        
        shop_address_style = ParagraphStyle(
            'ShopAddress',
            parent=styles['Normal'],
            fontSize=11,  # Slightly reduced
            textColor=colors.HexColor('#000000'),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Times-Roman'  # Changed to Times-Roman
        )
        
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#000000'),
            fontName='Times-Roman'  # Changed to Times-Roman
        )
        
        bold_style = ParagraphStyle(
            'Bold',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#000000'),
            fontName='Times-Bold'  # Changed to Times-Bold
        )
        
        # === SHOP HEADER ===
        # Large shop name at top (one line)
        elements.append(Paragraph(data['shop']['name'].upper(), shop_name_style))
        elements.append(Spacer(1, 0.05*inch))  # Reduced spacing
        
        # Address, Phone and Email in one complete horizontal line
        contact_line = f"{data['shop']['address']} | Phone: {data['shop']['phone']} | Email: {data['shop']['email']}"
        elements.append(Paragraph(contact_line, shop_address_style))
        elements.append(Spacer(1, 0.08*inch))  # Minimized space between address and date
        
        # Date left, Owner Name right (below address line)
        date_owner_data = [
            [f"Date: {datetime.now().strftime('%d-%m-%Y')}", f"Owner: {data['shop'].get('owner', 'N/A')}"]
        ]
        
        date_owner_table = Table(date_owner_data, colWidths=[3.5*inch, 3.5*inch])  # Adjusted for reduced margins
        date_owner_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),  # Changed to Times-Roman
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),    # Date left
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),   # Owner right
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(date_owner_table)
        elements.append(Spacer(1, 0.1*inch))  # Reduced spacing
        
        # === SEPARATION LINE BETWEEN SHOP AND OTHER DETAILS ===
        from reportlab.platypus import HRFlowable
        elements.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.black))
        elements.append(Spacer(1, 0.15*inch))
        
        # === CUSTOMER DETAILS (simplified - only name and mobile) ===
        elements.append(Paragraph("CUSTOMER DETAILS:", bold_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Customer Name (full line)
        elements.append(Paragraph(f"Name: {data['customer']['name']}", normal_style))
        elements.append(Spacer(1, 0.05*inch))
        
        # Mobile No (full line)  
        elements.append(Paragraph(f"Mobile No: {data['customer'].get('phone', 'N/A')}", normal_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # === ITEMS TABLE (using complete page width) ===
        table_data = [['Sr No', 'Item', 'Price', 'Quantity', 'Amount']]
        
        # Add items with INR currency
        total_amount = 0
        for idx, item in enumerate(data['items'], 1):
            total_amount += item['total']
            table_data.append([
                str(idx),
                item['name'],
                f"₹{item['price']:.2f}",
                str(item['quantity']),
                f"₹{item['total']:.2f}"
            ])
        
        # Empty rows for more space
        for _ in range(3):
            table_data.append(['', '', '', '', ''])
        
        # Use complete page width: adjusted for reduced margins - fixed overflow
        items_table = Table(table_data, colWidths=[0.6*inch, 3.5*inch, 1.1*inch, 0.9*inch, 1.3*inch])  # Reduced widths to fit page
        items_table.setStyle(TableStyle([
            # Header
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),     # Changed to Times-Bold for header
            ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),   # Times-Roman for data rows
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),   # Sr No center
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),     # Item left
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),    # Price right
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),   # Quantity center
            ('ALIGN', (4, 0), (4, -1), 'RIGHT'),    # Amount right
            
            # Grid lines
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#000000')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Increased Padding for better appearance
            ('TOPPADDING', (0, 0), (-1, -1), 12),     # Increased from 8 to 12
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),  # Increased from 8 to 12
            ('LEFTPADDING', (0, 0), (-1, -1), 10),    # Increased from 6 to 10
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),   # Increased from 6 to 10
        ]))
        
        elements.append(items_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # === TOTAL AMOUNT (below table, right aligned) ===
        total_para = Paragraph(f"<b>Total Amount: ₹{data['total']:.2f} (In Rupees INR)</b>", 
                              ParagraphStyle('Total', 
                                           parent=normal_style, 
                                           fontSize=14, 
                                           alignment=TA_RIGHT,
                                           fontName='Helvetica-Bold'))
        elements.append(total_para)
        elements.append(Spacer(1, 0.1*inch))
        
        # === PAYMENT STATUS (below total, right aligned) ===
        status_color = colors.HexColor('#059669') if data['payment_status'] == 'Paid' else colors.HexColor('#dc2626')
        payment_para = Paragraph(f"Payment Status: <b>{data['payment_status'].upper()}</b>", 
                                ParagraphStyle('PaymentStatus', 
                                             parent=normal_style, 
                                             fontSize=11, 
                                             textColor=status_color,
                                             alignment=TA_RIGHT))
        elements.append(payment_para)
        elements.append(Spacer(1, 0.15*inch))  # Line break before footer
        
        # === SEPARATION LINE BEFORE REMARKS ===
        elements.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.black))
        elements.append(Spacer(1, 0.1*inch))
        
        # === COMPACT FOOTER ===
        # Remarks left, signature right - minimal space
        remarks_text = data.get('notes', '')
        if not remarks_text:
            remarks_text = ''
        
        footer_data = [
            ['Remarks:', 'Sign & Date:'],
            [remarks_text, '']
        ]
        
        footer_table = Table(footer_data, colWidths=[3.8*inch, 3.8*inch])  # Adjusted for reduced margins
        footer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),    # Changed to Times-Bold
            ('FONTNAME', (0, 1), (-1, 1), 'Times-Roman'),   # Changed to Times-Roman
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (1, 1), 15),  # Minimal space for signature
        ]))
        
        elements.append(footer_table)
        
        # === SIMPLE FOOTER ===
        elements.append(Spacer(1, 0.05*inch))
        elements.append(Paragraph(
            f"Generated on {datetime.now().strftime('%d-%m-%Y')} | Thank you!",
            ParagraphStyle(
                'Footer',
                parent=normal_style,
                fontSize=9,
                textColor=colors.HexColor('#666666'),
                alignment=TA_CENTER
            )
        ))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        # Save bill record without bill number reference
        bills_df = pd.read_csv(BILLS_CSV)
        # Generate a simple sequential ID for internal tracking
        next_id = len(bills_df) + 1
        
        new_bill = {
            'bill_id': next_id,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'customer_name': data['customer']['name'],
            'customer_phone': data['customer'].get('phone', ''),
            'customer_email': data['customer'].get('email', ''),
            'items': str(data['items']),
            'total': data['total'],
            'payment_status': data['payment_status'],
            'notes': data.get('notes', '')
        }
        bills_df = pd.concat([bills_df, pd.DataFrame([new_bill])], ignore_index=True)
        bills_df.to_csv(BILLS_CSV, index=False)
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Bill-{next_id}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get all bills
@app.route('/api/bills', methods=['GET'])
def get_bills():
    try:
        df = pd.read_csv(BILLS_CSV)
        # Convert pandas data types to Python native types for JSON serialization
        records = df.to_dict('records')
        for record in records:
            if 'total' in record:
                record['total'] = float(record['total'])
        return jsonify(records)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get shop details
@app.route('/api/shop', methods=['GET'])
def get_shop_details():
    return jsonify(SHOP_DETAILS)

# Delete bill
@app.route('/api/bills/<bill_id>', methods=['DELETE'])
def delete_bill(bill_id):
    try:
        df = pd.read_csv(BILLS_CSV)
        
        # Check if bill exists
        if bill_id not in df['bill_id'].astype(str).values:
            return jsonify({'error': f'Bill with ID {bill_id} not found'}), 404
        
        # Remove the bill
        df = df[df['bill_id'].astype(str) != str(bill_id)]
        df.to_csv(BILLS_CSV, index=False)
        
        return jsonify({'message': f'Bill {bill_id} deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)