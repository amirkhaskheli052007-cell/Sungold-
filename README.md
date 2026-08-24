# Sungold Organic - Professional E-Commerce & Business Management System

## Quick Start (VS Code)
1. Folder ko VS Code mein open karo
2. Terminal mein:
   pip install -r requirements.txt
   streamlit run app.py

3. Admin Login:
   Password default: Dildar0912fdh (env se change kar sakte ho)
   
4. Customer: Register -> Login -> Shop automatically dikhega

## Data Safety
- sungold_orders.db ko delete nahi karta
- Saare migrations IF NOT EXISTS / ALTER TABLE se hain
- Purane orders text format bhi chalte hain

## Features Implemented
- Customer Register/Login with bcrypt hashing
- Categories clickable: Chicken, Eggs, Vegetables, Mutton
- Product search working
- Add to Cart with decimal qty (3.4, 8.03)
- Checkout with auto-fill, delivery, packing, discount
- Order history, reorder, invoice reprint, WhatsApp
- Admin: Dashboard with From-To filters, Customer/Order/Product/Payment/Ledger/Reports
- Dynamic Ledger: order debit, payment credit, adjustment - auto sync on edit/delete
- Payments: Add/Edit/Delete with confirmation
- Products: Add/Edit/Price/Available/Unavailable
- Reports: Product-wise, Category-wise, Customer-wise with CSV + PDF
- Printing: A4 Invoice (S/N Product Qty UnitPrice Total - headings bold), Customer Statement, Blank Payment Sheet 5/10/15
- Backup: CSV + DB download

## Live Deployment
Local par chalne ke baad:
- Streamlit Cloud: github par push -> streamlit cloud deploy
- Render.com / Railway: pip install + streamlit run app.py
SQLite hosting par persist nahi karta - production ke liye Postgres recommend hai.

Live link code se automatic nahi banta. Deploy karna parta hai.
