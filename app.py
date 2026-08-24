
import csv, io, json, os, re, sqlite3, urllib.parse, hashlib
from datetime import datetime, timedelta, date
from io import BytesIO
import streamlit as st
import pandas as pd
try:
    import bcrypt
    HAS_BCRYPT=True
except:
    HAS_BCRYPT=False
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Sungold Organic", page_icon="🌱", layout="wide", initial_sidebar_state="expanded")
FARM_NAME="Sungold Organic"
FARM_PHONE="0345-2005309"
WHATSAPP_NUMBER=os.getenv("SUNGOLD_WHATSAPP_NUMBER","923452005309")
FARM_EMAIL="Sungoldorganic@gmail.com"
FARM_ADDRESS="Deh Kakar, Malir District, Karachi, Sindh, Pakistan | Sungold Organic, Lahore, Punjab, Pakistan"
ADMIN_PASSWORD=os.getenv("SUNGOLD_ADMIN_PASSWORD","Dildar0912fdh")
DB_NAME=os.getenv("SUNGOLD_DB","sungold_orders.db")
DEFAULT_DELIVERY_CHARGE=0
TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN","")
TELEGRAM_CHAT_ID=os.getenv("TELEGRAM_CHAT_ID","")
MONTH_NAMES=["January","February","March","April","May","June","July","August","September","October","November","December"]

PRODUCT_CATALOG_ORIGINAL={
    "Organic Chicken": {
        "Organic Chicken Whole W/o + Organs, kg":1620,
        "Organic Chicken Whole W/o 16 Piece, kg":1620,
        "Organic Chicken Whole W/o 12 Piece, kg":1620,
        "Organic Chicken Whole W/o 14 Piece, kg":1620,
        "Organic Chicken Whole W/o 10 Piece, kg":1620,
        "Organic Chicken Whole W/o 8 Piece, kg":1620,
        "Organic Chicken Whole W/o 4 Piece, kg":1620,
        "Organic Chicken Whole W/o 2 Piece, kg":1620,
        "Organic Chicken Whole Boneless, kg":1690,
        "Organic Chicken Whole Mince, kg":1700,
        "Organic Chicken Whole Customs, kg":1680,
        "Organic Chicken Whole With Skin, kg":1720,
        "Organic Chicken 4piece With Skin, kg":1720,
        "Organic Chicken Boneless Mixed Cubes, 500g":1350,
        "Organic Chicken Mixed Mince, 500g":1350,
        "Organic Chicken Breast Filet, 500g":1375,
        "Organic Chicken White Meat Mince, 500g":1370,
        "Organic Chicken White Boneless Cubes, kg":1375,
        "Organic Chicken Julienne Strips 500g":1390,
        "Organic Chicken Tender Pops 500g":1390,
        "Organic Chicken Thigh Filet 500g":1375,
        "Organic Chicken Dark Boneless 500g":1375,
        "Organic Chicken Dark Mince 500g":1370,
        "Organic Chicken Thigh Without Skin 500g":990,
        "Organic Chicken Drumsticks 500g":990,
        "Organic Chicken Wings 500g":590,
        "Organic Chicken Leg Tikka 500g":1180,
        "Organic Chicken Breast Tikka 500g":1300,
        "Organic Chicken Liver 250g":300,
        "Organic giblets 250g":250,
        "Organic Soup Bones 500g":300,
        "Organic Feet 250g":200,
        "Organic Dog + Cat":380,
        "Organic Neck 500g":380,
        "Organic Burger":300,
        "Organic Charbi":350,
    },
    "Organic Eggs": {
        "Organic eggs Lohman Brown large per egg":70,
        "Organic eggs Lohman Brown extra large per egg":75,
        "Organic eggs Lohman Brown jumbo per egg":90,
        "organic Home Churned Butter 200g":800,
        "Organic Mustard Oil Coldpress Extra Virgin 1000ml":1560,
        "Organic Desi Ghee (Home Free Mlik ) 330g":2125,
        "organic Cheese, Zeera/Red Chillies":875,
        "Cottage Cheese, Plain":875,
        "Organic Deosi Sidr Berri Honey 450g":1250,
        "Organic Custard Apple (Shareefa)":100,
        "Organically Raised Whole Wheat Flour (Atta) 5kg":1200,
        "Bees Bounty organic Robinia Honey 80z":1200,
        "Mix vegetable Achaar in oil ":960,
        "Moringa Leaves 100g":100,
    },
    "Organic Vegetables": {
        "Organic Tomatoes":80,
        "Organic Potato":80,
        "Organic Fresh Onions 500g":60,
        "Organic Karipatta 50g":50,
        "Organic Celery":100,
        "Organic Green Chilies":50,
        "Organic Salad Tomatoes":80,
        "Organic Baby Spinach":75,
        "Organic Spinach":70,
        "Organic Methi / Fenugreek":70,
        "Organic Kasuri Methi":60,
        "Organic Rocket Salad":50,
        "Organic Tulsi,Basil, 50g":50,
        "Organic Endive Salad":50,
        "Organic Black Magic Kale":60,
        "Organic Blue Kale":60,
        "Organic Red Russian Kale":60,
        "Organic Scottish Kale":60,
        "Organic Dill / Soah":50,
        "Organic Coriander / Dhania":50,
        "Organic Podina, Mint 50g":50,
        "Organic White Radish Leaves":70,
        "Organic White Radish Without Leaves":85,
        "Organic Eggplant Long":70,
        "Organic Eggplant Round":70,
        "Organic Danver Orange Carrots":80,
        "Organic Red Carrots":80,
        "Organic Finger Carrots":100,
        "Organic Potatoes":50,
        "Organic Baby Potatoes":50,
        "Organic Cabbage":110,
        "Organic Baby Onions 250g":50,
        "Organic Onions":60,
        "Organic Okra (Bhindi) 500g":90,
        "Organic Round Gourd (Kuddu) 500g":80,
        "Organic Long Loki, bottle gourd 500g":80,
        "organic Guar phalli, cluster beans 500g":80,
        "Organic Pumpkin(Paytha Kuddu) kg ":150,
        "Organic Toari, Soft Gourd, 500g":90,
        "organic Kakri Kheera, cucumber 500g":80,
    },
    "Organic Mutton": {
        "Organically Raised Mutton brain":400,
        "Organically Raised Mutton Chops 500g":1750,
        "Organically Raised Mutton breast 500g":1200,
        "Organically Raised Mutton Kidney (gurdas) pair":424,
        "Organically Raised Mutton Mince 500g ":1980,
        "Organically Raised prime mix boti 500g":1705,
        "Mutton Liver (kaleaji)":477,
        "Mutton Heart (dil)":300,
        "Organically Raised Prime Mutton Mince 500g":1980,
        "Organically Raised Mutton Raan (back leg) 500g":1810,
        "Organically Raised Mutton breast and Ribs 500g":1200,
    },
}

def get_conn():
    conn=sqlite3.connect(DB_NAME, check_same_thread=False, timeout=10)
    conn.row_factory=sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
    except:
        pass
    return conn

def create_database():
    conn=get_conn()
    cur=conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT, phone TEXT, address TEXT, delivery_area TEXT, created_at TEXT, updated_at TEXT, UNIQUE(name COLLATE NOCASE))")
    cur.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT UNIQUE, customer_name TEXT, email TEXT, phone TEXT, address TEXT, delivery_area TEXT, order_items TEXT, order_items_json TEXT, subtotal REAL, delivery_charge REAL DEFAULT 0, packing_material REAL DEFAULT 0, discount REAL DEFAULT 0, total_amount REAL, order_date TEXT, status TEXT DEFAULT 'Pending', payment_status TEXT DEFAULT 'Unpaid', month_key TEXT, created_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS cart_state (key TEXT PRIMARY KEY, data TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS customer_auth (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT NOT NULL, email TEXT UNIQUE, phone TEXT, password_hash TEXT NOT NULL, created_at TEXT, UNIQUE(customer_name COLLATE NOCASE))")
    cur.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, name TEXT UNIQUE, price REAL, is_available INTEGER DEFAULT 1, created_at TEXT, updated_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, payment_id TEXT UNIQUE, customer_name TEXT, order_id TEXT, amount REAL, payment_date TEXT, payment_method TEXT, reference_no TEXT, notes TEXT, created_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS adjustments (id INTEGER PRIMARY KEY AUTOINCREMENT, adjustment_id TEXT UNIQUE, customer_name TEXT, amount REAL, adjustment_type TEXT, reason TEXT, adjustment_date TEXT, created_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS ledger_transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, transaction_type TEXT, reference_id TEXT, description TEXT, debit REAL DEFAULT 0, credit REAL DEFAULT 0, transaction_date TEXT, order_id TEXT, payment_id TEXT, adjustment_id TEXT, created_at TEXT)")
    existing={r[1] for r in cur.execute("PRAGMA table_info(orders)").fetchall()}
    for col, sql in [("order_items_json","ALTER TABLE orders ADD COLUMN order_items_json TEXT"),("subtotal","ALTER TABLE orders ADD COLUMN subtotal REAL DEFAULT 0"),("delivery_charge","ALTER TABLE orders ADD COLUMN delivery_charge REAL DEFAULT 0"),("packing_material","ALTER TABLE orders ADD COLUMN packing_material REAL DEFAULT 0"),("discount","ALTER TABLE orders ADD COLUMN discount REAL DEFAULT 0"),("payment_status","ALTER TABLE orders ADD COLUMN payment_status TEXT DEFAULT 'Unpaid'"),("month_key","ALTER TABLE orders ADD COLUMN month_key TEXT"),("created_at","ALTER TABLE orders ADD COLUMN created_at TEXT")]:
        if col not in existing:
            try: cur.execute(sql)
            except: pass
    conn.commit()
    conn.close()
    seed_products_if_empty()
    backfill_month_keys()

def seed_products_if_empty():
    conn=get_conn()
    count=conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    if count==0:
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for cat, items in PRODUCT_CATALOG_ORIGINAL.items():
            for name, price in items.items():
                try:
                    conn.execute("INSERT OR IGNORE INTO products(category,name,price,is_available,created_at,updated_at) VALUES (?,?,?,?,?,?)",(cat, name.strip(), float(price), 1, now, now))
                except: pass
        conn.commit()
    conn.close()

def parse_order_datetime(value):
    if not value: return None
    text=str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S","%d-%b-%Y %I:%M %p","%d-%b-%Y %H:%M","%Y-%m-%dT%H:%M:%S","%d-%b-%Y","%Y-%m-%d"):
        try: return datetime.strptime(text,fmt)
        except: continue
    return None

def month_key_of(dt): return dt.strftime("%Y-%m") if dt else "unknown"
def month_label(key):
    try:
        y,m=key.split("-")
        return f"{MONTH_NAMES[int(m)-1]} {y}"
    except: return key or "Unknown"

def backfill_month_keys():
    conn=get_conn()
    rows=conn.execute("SELECT id, order_date, created_at FROM orders WHERE month_key IS NULL OR month_key=''").fetchall()
    for row in rows:
        dt=parse_order_datetime(row["created_at"]) or parse_order_datetime(row["order_date"])
        key=month_key_of(dt) if dt else "unknown"
        conn.execute("UPDATE orders SET month_key=? WHERE id=?",(key,row["id"]))
    if rows: conn.commit()
    conn.close()

create_database()

def hash_password(pw):
    if HAS_BCRYPT:
        return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
    else:
        return hashlib.sha256(pw.encode()).hexdigest()

def check_password(pw, hashed):
    if HAS_BCRYPT:
        try: return bcrypt.checkpw(pw.encode(), hashed.encode())
        except: return False
    else:
        return hashlib.sha256(pw.encode()).hexdigest()==hashed

def generate_order_id(): return "SG-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]
def generate_payment_id(): return "PAY-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]
def generate_adjustment_id(): return "ADJ-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]

def clean_phone(phone):
    phone=re.sub(r"[\s\-()+]","",str(phone).strip())
    if phone.startswith("0"): phone="92"+phone[1:]
    return phone

def valid_email(email): return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or "") is not None
def parse_quantity(value):
    try: return max(float(str(value).strip()),0.0)
    except: return 0.0
def fmt_qty(q):
    q=float(q)
    return str(int(q)) if q==int(q) else f"{q:g}"

def load_cart_from_db():
    conn=get_conn()
    row=conn.execute("SELECT data FROM cart_state WHERE key='cart'").fetchone()
    conn.close()
    if not row or not row["data"]: return []
    try: return json.loads(row["data"])
    except: return []

def save_cart_to_db(cart):
    conn=get_conn()
    conn.execute("INSERT OR REPLACE INTO cart_state(key,data) VALUES('cart',?)",(json.dumps(cart),))
    conn.commit()
    conn.close()

if "cart" not in st.session_state:
    st.session_state.cart=load_cart_from_db()

for k,d in {"last_order_id":None,"last_pdf":None,"last_order":None,"confirm_delete_order":None,"confirm_delete_customer":None,"user":None,"user_role":None,"selected_category":"All"}.items():
    if k not in st.session_state: st.session_state[k]=d

def add_to_cart(category, product_name, price, quantity):
    qty=parse_quantity(quantity)
    if qty<=0: return False
    st.session_state.cart.append({"category":category,"product":product_name,"price":float(price),"quantity":qty,"total":round(float(price)*qty,2)})
    save_cart_to_db(st.session_state.cart)
    return True

def remove_from_cart(index):
    if 0<=index<len(st.session_state.cart):
        st.session_state.cart.pop(index)
        save_cart_to_db(st.session_state.cart)

def update_cart_quantity(index, quantity):
    qty=parse_quantity(quantity)
    item=st.session_state.cart[index]
    item["quantity"]=qty
    item["total"]=round(item["price"]*qty,2)
    save_cart_to_db(st.session_state.cart)

def clear_cart():
    st.session_state.cart=[]
    save_cart_to_db([])

def cart_subtotal(): return sum(float(i["total"]) for i in st.session_state.cart)

def save_customer(name,email,phone,address,area):
    now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn=get_conn()
    conn.execute("INSERT INTO customers (name,email,phone,address,delivery_area,created_at,updated_at) VALUES (?,?,?,?,?,?,?) ON CONFLICT(name) DO UPDATE SET email=excluded.email,phone=excluded.phone,address=excluded.address,delivery_area=excluded.delivery_area,updated_at=excluded.updated_at",(name.strip(),email.strip(),clean_phone(phone),address.strip(),area.strip(),now,now))
    conn.commit()
    conn.close()

def find_customer(name):
    conn=get_conn()
    row=conn.execute("SELECT * FROM customers WHERE name=? COLLATE NOCASE LIMIT 1",(name,)).fetchone()
    conn.close()
    return row

def customer_names():
    conn=get_conn()
    rows=conn.execute("SELECT name FROM customers ORDER BY name COLLATE NOCASE").fetchall()
    conn.close()
    return [r["name"] for r in rows]

def get_all_products(only_available_for_customer=False, search="", category_filter="All"):
    conn=get_conn()
    q="SELECT * FROM products"
    clauses=[]
    params=[]
    if only_available_for_customer: clauses.append("is_available=1")
    if category_filter!="All":
        clauses.append("category=?")
        params.append(category_filter)
    if search:
        clauses.append("name LIKE ? COLLATE NOCASE")
        params.append(f"%{search}%")
    if clauses: q+=" WHERE "+" AND ".join(clauses)
    q+=" ORDER BY category, name COLLATE NOCASE"
    rows=conn.execute(q,params).fetchall()
    conn.close()
    return rows

def get_categories():
    conn=get_conn()
    rows=conn.execute("SELECT DISTINCT category FROM products ORDER BY category").fetchall()
    conn.close()
    return [r["category"] for r in rows]

def build_order_items(cart):
    return "\n".join(f"{i}. {item['product']} | Qty: {fmt_qty(item['quantity'])} | Rs {item['price']:,.0f} | Total: Rs {item['total']:,.0f}" for i,item in enumerate(cart,1))

def build_order_items_json(cart): return json.dumps(cart)

def parse_order_items(text):
    cart_items=[]
    for line in (text or "").split("\n"):
        parts=[p.strip() for p in line.split("|")]
        if len(parts)<4: continue
        name=parts[0].split(". ",1)[-1]
        qty=parse_quantity(parts[1].replace("Qty:",""))
        price=parse_quantity(parts[2].replace("Rs","").replace(",",""))
        total=parse_quantity(parts[3].replace("Total:","").replace("Rs","").replace(",",""))
        cart_items.append({"product":name,"quantity":qty,"price":price,"total":total})
    return cart_items

def order_row_to_dict(order):
    try:
        cart_json=json.loads(order["order_items_json"]) if order["order_items_json"] else []
        cart=cart_json if cart_json else parse_order_items(order["order_items"])
    except:
        cart=parse_order_items(order["order_items"])
    return {"order_id":order["order_id"],"customer_name":order["customer_name"],"email":order["email"] or "","phone":order["phone"] or "","address":order["address"] or "","delivery_area":order["delivery_area"] or "","cart":cart,"subtotal":float(order["subtotal"] or 0),"delivery_charge":float(order["delivery_charge"] or 0),"packing_material":float(order["packing_material"] or 0),"discount":float(order["discount"] or 0),"total_amount":float(order["total_amount"] or 0),"order_date":order["order_date"],"status":order["status"],"payment_status":order["payment_status"] if "payment_status" in order.keys() else "Unpaid"}

def create_order_transaction(order):
    conn=get_conn()
    try:
        conn.execute("DELETE FROM ledger_transactions WHERE order_id=? AND transaction_type='order'",(order["order_id"],))
        if order["status"]!="Cancelled":
            conn.execute("INSERT INTO ledger_transactions (customer_name,transaction_type,reference_id,description,debit,credit,transaction_date,order_id,created_at) VALUES (?,?,?,?,?,?,?,?,?)",(order["customer_name"],"order",order["order_id"],f"Order {order['order_id']}",float(order["total_amount"]),0,order["created_at"],order["order_id"],datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    finally: conn.close()

def update_order_transaction(order_id, new_amount, status, customer_name):
    conn=get_conn()
    conn.execute("DELETE FROM ledger_transactions WHERE order_id=? AND transaction_type='order'",(order_id,))
    if status!="Cancelled":
        conn.execute("INSERT INTO ledger_transactions (customer_name,transaction_type,reference_id,description,debit,credit,transaction_date,order_id,created_at) VALUES (?,?,?,?,?,?,?,?,?)",(customer_name,"order",order_id,f"Order {order_id} (Updated)",float(new_amount),0,datetime.now().strftime("%Y-%m-%d %H:%M:%S"),order_id,datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def delete_order_transaction(order_id):
    conn=get_conn()
    conn.execute("DELETE FROM ledger_transactions WHERE order_id=? AND transaction_type='order'",(order_id,))
    conn.commit()
    conn.close()

def create_payment_transaction(payment):
    conn=get_conn()
    conn.execute("DELETE FROM ledger_transactions WHERE payment_id=? AND transaction_type='payment'",(payment["payment_id"],))
    conn.execute("INSERT INTO ledger_transactions (customer_name,transaction_type,reference_id,description,debit,credit,transaction_date,payment_id,created_at) VALUES (?,?,?,?,?,?,?,?,?)",(payment["customer_name"],"payment",payment["payment_id"],f"Payment {payment['payment_id']} - {payment['payment_method']}",0,float(payment["amount"]),payment["payment_date"],payment["payment_id"],datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def update_payment_transaction(payment):
    conn=get_conn()
    conn.execute("DELETE FROM ledger_transactions WHERE payment_id=? AND transaction_type='payment'",(payment["payment_id"],))
    conn.execute("INSERT INTO ledger_transactions (customer_name,transaction_type,reference_id,description,debit,credit,transaction_date,payment_id,created_at) VALUES (?,?,?,?,?,?,?,?,?)",(payment["customer_name"],"payment",payment["payment_id"],f"Payment {payment['payment_id']} - {payment['payment_method']} (Updated)",0,float(payment["amount"]),payment["payment_date"],payment["payment_id"],datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def delete_payment_transaction(payment_id):
    conn=get_conn()
    conn.execute("DELETE FROM ledger_transactions WHERE payment_id=? AND transaction_type='payment'",(payment_id,))
    conn.commit()
    conn.close()

def create_adjustment_transaction(adj):
    conn=get_conn()
    conn.execute("DELETE FROM ledger_transactions WHERE adjustment_id=? AND transaction_type='adjustment'",(adj["adjustment_id"],))
    debit=float(adj["amount"]) if adj["adjustment_type"]=="Debit" else 0
    credit=float(adj["amount"]) if adj["adjustment_type"]=="Credit" else 0
    conn.execute("INSERT INTO ledger_transactions (customer_name,transaction_type,reference_id,description,debit,credit,transaction_date,adjustment_id,created_at) VALUES (?,?,?,?,?,?,?,?,?)",(adj["customer_name"],"adjustment",adj["adjustment_id"],f"Adjustment {adj['adjustment_id']} - {adj['reason']}",debit,credit,adj["adjustment_date"],adj["adjustment_id"],datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def delete_adjustment_transaction(adj_id):
    conn=get_conn()
    conn.execute("DELETE FROM ledger_transactions WHERE adjustment_id=? AND transaction_type='adjustment'",(adj_id,))
    conn.commit()
    conn.close()

def get_customer_ledger(customer_name):
    conn=get_conn()
    rows=conn.execute("SELECT * FROM ledger_transactions WHERE customer_name=? COLLATE NOCASE ORDER BY transaction_date ASC, id ASC",(customer_name,)).fetchall()
    conn.close()
    ledger=[]
    bal=0
    for r in rows:
        bal+=float(r["debit"] or 0)-float(r["credit"] or 0)
        ledger.append({**dict(r),"running_balance":bal})
    return ledger

def get_customer_balance(customer_name):
    ledger=get_customer_ledger(customer_name)
    return ledger[-1]["running_balance"] if ledger else 0

def save_order(order):
    conn=get_conn()
    conn.execute("INSERT INTO orders (order_id,customer_name,email,phone,address,delivery_area,order_items,order_items_json,subtotal,delivery_charge,packing_material,discount,total_amount,order_date,status,payment_status,month_key,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(order["order_id"],order["customer_name"],order["email"],order["phone"],order["address"],order["delivery_area"],order["order_items"],order["order_items_json"],order["subtotal"],order["delivery_charge"],order["packing_material"],order["discount"],order["total_amount"],order["order_date"],order["status"],order["payment_status"],order["month_key"],order["created_at"]))
    conn.commit()
    conn.close()
    create_order_transaction(order)

def delete_order(db_id, order_id_str):
    conn=get_conn()
    conn.execute("DELETE FROM orders WHERE id=?",(db_id,))
    conn.commit()
    conn.close()
    delete_order_transaction(order_id_str)

def delete_customer(name, with_orders=False):
    conn=get_conn()
    removed=0
    if with_orders:
        orders=conn.execute("SELECT id, order_id FROM orders WHERE customer_name=? COLLATE NOCASE",(name,)).fetchall()
        cur=conn.execute("DELETE FROM orders WHERE customer_name=? COLLATE NOCASE",(name,))
        removed=cur.rowcount or 0
        conn.execute("DELETE FROM payments WHERE customer_name=? COLLATE NOCASE",(name,))
        conn.execute("DELETE FROM adjustments WHERE customer_name=? COLLATE NOCASE",(name,))
        conn.execute("DELETE FROM ledger_transactions WHERE customer_name=? COLLATE NOCASE",(name,))
        conn.execute("DELETE FROM customer_auth WHERE customer_name=? COLLATE NOCASE",(name,))
        conn.commit()
        conn.close()
        return removed
    conn.execute("DELETE FROM customers WHERE name=? COLLATE NOCASE",(name,))
    conn.commit()
    conn.close()
    return removed

def get_setting(key, default):
    conn=get_conn()
    row=conn.execute("SELECT value FROM settings WHERE key=?",(key,)).fetchone()
    conn.close()
    if not row: return default
    try: return float(row["value"])
    except: return default

def set_setting(key,value):
    conn=get_conn()
    conn.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",(key,str(float(value))))
    conn.commit()
    conn.close()

def get_delivery_charge(): return get_setting("delivery_charge", DEFAULT_DELIVERY_CHARGE)
def set_delivery_charge(v): set_setting("delivery_charge", v)

def whatsapp_link(order):
    lines=[f"*{FARM_NAME}*",f"Invoice: {order['order_id']}",f"Customer: {order['customer_name']}",""]
    for i,item in enumerate(order["cart"],1):
        lines.append(f"{i}. {item['product']} x {fmt_qty(item['quantity'])} = Rs {item['total']:,.0f}")
    lines+=["",f"Subtotal: Rs {order['subtotal']:,.0f}",f"Delivery: Rs {order['delivery_charge']:,.0f}"]
    if order.get("packing_material",0)>0: lines.append(f"Packing Material: Rs {order['packing_material']:,.0f}")
    if order.get("discount",0)>0: lines.append(f"Discount: -Rs {order['discount']:,.0f}")
    lines.append(f"GRAND TOTAL: Rs {order['total_amount']:,.0f}")
    return "https://wa.me/"+order["phone"]+"?text="+urllib.parse.quote("\n".join(lines))

def whatsapp_admin_link(order):
    msg=f"New Order\nOrder: {order['order_id']}\nCustomer: {order['customer_name']}\nPhone: {order['phone']}\nArea: {order['delivery_area']}\nTotal: Rs {order['total_amount']:,.0f}\nTime: {order['order_date']}\n\n{order['order_items']}"
    return f"https://wa.me/{WHATSAPP_NUMBER}?text="+urllib.parse.quote(msg)

def telegram_notify(order):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID: return False
    try:
        import requests
        text=f"SUNGOLD NEW ORDER\nOrder: {order['order_id']}\nCustomer: {order['customer_name']}\nPhone: {order['phone']}\nArea: {order['delivery_area']}\nTotal: Rs {order['total_amount']:,.0f}\nTime: {order['order_date']}\n\n{order['order_items']}"
        url=f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        return requests.post(url,json={"chat_id":TELEGRAM_CHAT_ID,"text":text},timeout=10).ok
    except: return False

def orders_to_csv(rows):
    out=io.StringIO()
    writer=csv.writer(out)
    writer.writerow(["Order ID","Month","Date","Customer","Phone","Area","Address","Subtotal","Delivery","Packing","Discount","Grand Total","Status","Payment"])
    for r in rows:
        writer.writerow([r["order_id"],month_label(r["month_key"]),r["order_date"],r["customer_name"],r["phone"],r["delivery_area"],r["address"],float(r["subtotal"] or 0),float(r["delivery_charge"] or 0),float(r["packing_material"] or 0),float(r["discount"] or 0),float(r["total_amount"] or 0),r["status"],r["payment_status"]])
    return out.getvalue().encode("utf-8")

LINE_COLOR=colors.black
LINE_WIDTH=0.9

def make_invoice_pdf(order):
    buffer=BytesIO()
    doc=SimpleDocTemplate(buffer,pagesize=A4,rightMargin=12*mm,leftMargin=12*mm,topMargin=10*mm,bottomMargin=10*mm,title=f"Sungold Invoice {order['order_id']}",author=FARM_NAME)
    styles=getSampleStyleSheet()
    title=ParagraphStyle("BillTitle",parent=styles["Title"],fontName="Helvetica-Bold",fontSize=21,leading=24,alignment=TA_CENTER,textColor=colors.black)
    center=ParagraphStyle("Center",parent=styles["Normal"],fontName="Helvetica-Bold",fontSize=9.5,leading=13,alignment=TA_CENTER,textColor=colors.black)
    bold=ParagraphStyle("Bold",parent=styles["Normal"],fontName="Helvetica-Bold",fontSize=10,leading=13,textColor=colors.black)
    bold_right=ParagraphStyle("BoldRight",parent=bold,alignment=TA_RIGHT)
    label=ParagraphStyle("Label",parent=bold,fontSize=9.5,textColor=colors.black)
    section=ParagraphStyle("Section",parent=styles["Heading3"],fontName="Helvetica-Bold",fontSize=11,leading=13,spaceBefore=4,spaceAfter=5,textColor=colors.black)
    story=[Paragraph(FARM_NAME.upper(),title),Paragraph("FRESH FARM PRODUCTS - ORDER / SALES INVOICE",center),Paragraph(f"{FARM_ADDRESS}<br/>Phone: {FARM_PHONE} | Email: {FARM_EMAIL}",center),Spacer(1,7)]
    info=[[Paragraph("Invoice / Order ID",label),Paragraph(order["order_id"],bold),Paragraph("Date & Time",label),Paragraph(order["order_date"],bold)],[Paragraph("Customer",label),Paragraph(order["customer_name"],bold),Paragraph("Phone",label),Paragraph(order["phone"],bold)],[Paragraph("Email",label),Paragraph(order["email"] or "-",bold),Paragraph("Delivery Area",label),Paragraph(order["delivery_area"],bold)],[Paragraph("Delivery Address",label),Paragraph(order["address"],bold),Paragraph("Status",label),Paragraph(order.get("status","Pending"),bold)]]
    info_table=Table(info,colWidths=[30*mm,63*mm,30*mm,63*mm])
    info_table.setStyle(TableStyle([("GRID",(0,0),(-1,-1),LINE_WIDTH,LINE_COLOR),("BOX",(0,0),(-1,-1),1.4,LINE_COLOR),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    story+=[info_table,Spacer(1,8),Paragraph("ORDER DETAILS",section)]
    rows=[[Paragraph("S/N",bold),Paragraph("Product",bold),Paragraph("Quantity",bold_right),Paragraph("Unit Price Rs.",bold_right),Paragraph("Total Rs.",bold_right)]]
    for i,item in enumerate(order["cart"],1):
        rows.append([Paragraph(str(i),bold),Paragraph(item["product"],bold),Paragraph(fmt_qty(item["quantity"]),bold_right),Paragraph(f"Rs {item['price']:,.0f}",bold_right),Paragraph(f"Rs {item['total']:,.0f}",bold_right)])
    item_table=Table(rows,colWidths=[10*mm,94*mm,20*mm,30*mm,32*mm],repeatRows=1)
    item_table.setStyle(TableStyle([("GRID",(0,0),(-1,-1),LINE_WIDTH,LINE_COLOR),("BOX",(0,0),(-1,-1),1.4,LINE_COLOR),("LINEBELOW",(0,0),(-1,0),1.4,LINE_COLOR),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    story+=[item_table,Spacer(1,8)]
    summary=[["Subtotal",f"Rs {order['subtotal']:,.0f}"]]
    if float(order.get("delivery_charge",0))>0: summary.append(["Delivery Charges",f"Rs {order['delivery_charge']:,.0f}"])
    if float(order.get("packing_material",0))>0: summary.append(["Packing Material",f"Rs {order['packing_material']:,.0f}"])
    if float(order.get("discount",0))>0: summary.append(["Discount",f"- Rs {order['discount']:,.0f}"])
    summary.append(["GRAND TOTAL",f"Rs {order['total_amount']:,.0f}"])
    summary_table=Table(summary,colWidths=[55*mm,45*mm],hAlign="RIGHT")
    summary_table.setStyle(TableStyle([("GRID",(0,0),(-1,-1),LINE_WIDTH,LINE_COLOR),("BOX",(0,0),(-1,-1),1.4,LINE_COLOR),("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),("TEXTCOLOR",(0,0),(-1,-1),colors.black),("FONTSIZE",(0,0),(-1,-1),10),("FONTSIZE",(0,-1),(-1,-1),12),("ALIGN",(1,0),(1,-1),"RIGHT"),("LINEABOVE",(0,-1),(-1,-1),1.4,LINE_COLOR),("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    footer=Table([[Paragraph("Thank you for choosing Sungold Organic.<br/>Fresh & Organic Products Delivered",center)]],colWidths=[186*mm])
    footer.setStyle(TableStyle([("BOX",(0,0),(-1,-1),1.4,LINE_COLOR),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
    story+=[summary_table,Spacer(1,10),footer]
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def make_customer_statement_pdf(customer_name, rows, ledger):
    buffer=BytesIO()
    doc=SimpleDocTemplate(buffer,pagesize=A4,rightMargin=12*mm,leftMargin=12*mm,topMargin=10*mm,bottomMargin=10*mm,title=f"Sungold Statement {customer_name}",author=FARM_NAME)
    styles=getSampleStyleSheet()
    title=ParagraphStyle("StTitle",parent=styles["Title"],fontName="Helvetica-Bold",fontSize=20,leading=23,alignment=TA_CENTER,textColor=colors.black)
    center=ParagraphStyle("StCenter",parent=styles["Normal"],fontName="Helvetica-Bold",fontSize=9.5,leading=13,alignment=TA_CENTER,textColor=colors.black)
    bold=ParagraphStyle("StBold",parent=styles["Normal"],fontName="Helvetica-Bold",fontSize=9.5,leading=12,textColor=colors.black)
    bold_right=ParagraphStyle("StBoldRight",parent=bold,alignment=TA_RIGHT)
    first=rows[0] if rows else None
    story=[Paragraph(FARM_NAME.upper(),title),Paragraph("CUSTOMER BILL HISTORY / STATEMENT",center),Paragraph(f"{FARM_ADDRESS}<br/>Phone: {FARM_PHONE} | Email: {FARM_EMAIL}",center),Spacer(1,8)]
    head=[[Paragraph("Customer",bold),Paragraph(customer_name,bold),Paragraph("Printed On",bold),Paragraph(datetime.now().strftime("%d-%b-%Y %I:%M %p"),bold)],[Paragraph("Phone",bold),Paragraph((first["phone"] if first else "") or "-",bold),Paragraph("Total Bills",bold),Paragraph(str(len(rows)),bold)],[Paragraph("Address",bold),Paragraph((first["address"] if first else "") or "-",bold),Paragraph("Area",bold),Paragraph((first["delivery_area"] if first else "") or "-",bold)]]
    head_table=Table(head,colWidths=[26*mm,67*mm,26*mm,67*mm])
    head_table.setStyle(TableStyle([("GRID",(0,0),(-1,-1),LINE_WIDTH,LINE_COLOR),("BOX",(0,0),(-1,-1),1.4,LINE_COLOR),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    story+=[head_table,Spacer(1,8)]
    data=[[Paragraph("Date",bold),Paragraph("Type",bold),Paragraph("Reference",bold),Paragraph("Description",bold),Paragraph("Debit",bold_right),Paragraph("Credit",bold_right),Paragraph("Balance",bold_right)]]
    for r in ledger:
        data.append([Paragraph(str(r["transaction_date"])[:16],bold),Paragraph(r["transaction_type"],bold),Paragraph(r["reference_id"],bold),Paragraph(r["description"][:30],bold),Paragraph(f"Rs {float(r['debit'] or 0):,.0f}" if r["debit"] else "-",bold_right),Paragraph(f"Rs {float(r['credit'] or 0):,.0f}" if r["credit"] else "-",bold_right),Paragraph(f"Rs {float(r['running_balance']):,.0f}",bold_right)])
    table=Table(data,colWidths=[28*mm,18*mm,24*mm,38*mm,22*mm,22*mm,24*mm],repeatRows=1)
    table.setStyle(TableStyle([("GRID",(0,0),(-1,-1),LINE_WIDTH,LINE_COLOR),("BOX",(0,0),(-1,-1),1.4,LINE_COLOR),("LINEBELOW",(0,0),(-1,0),1.4,LINE_COLOR),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
    story+=[table,Spacer(1,8)]
    grand=sum(float(o["total_amount"] or 0) for o in rows if o["status"]!="Cancelled")
    bal=ledger[-1]["running_balance"] if ledger else 0
    totals=Table([["TOTAL BUSINESS",f"Rs {grand:,.0f}"],["OUTSTANDING BALANCE",f"Rs {bal:,.0f}"]],colWidths=[55*mm,45*mm],hAlign="RIGHT")
    totals.setStyle(TableStyle([("GRID",(0,0),(-1,-1),LINE_WIDTH,LINE_COLOR),("BOX",(0,0),(-1,-1),1.4,LINE_COLOR),("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),11),("ALIGN",(1,0),(1,-1),"RIGHT"),("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    story+=[totals]
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def make_blank_payment_sheet_pdf(num_rows=15):
    buffer=BytesIO()
    doc=SimpleDocTemplate(buffer,pagesize=A4,rightMargin=10*mm,leftMargin=10*mm,topMargin=10*mm,bottomMargin=10*mm,title=f"Payment Sheet {num_rows}",author=FARM_NAME)
    styles=getSampleStyleSheet()
    title=ParagraphStyle("Title2",parent=styles["Title"],fontName="Helvetica-Bold",fontSize=18,leading=20,alignment=TA_CENTER,textColor=colors.black)
    center=ParagraphStyle("Center2",parent=styles["Normal"],fontName="Helvetica-Bold",fontSize=9,leading=12,alignment=TA_CENTER,textColor=colors.black)
    bold=ParagraphStyle("Bold2",parent=styles["Normal"],fontName="Helvetica-Bold",fontSize=9,leading=11,textColor=colors.black)
    bold_c=ParagraphStyle("BoldC",parent=bold,alignment=TA_CENTER)
    story=[Paragraph(FARM_NAME.upper(),title),Paragraph(f"BLANK CUSTOMER PAYMENT SHEET - {num_rows} Customers",center),Paragraph(f"{FARM_ADDRESS} | {FARM_PHONE}",center),Spacer(1,6)]
    header=[Paragraph("S/N",bold_c),Paragraph("Customer Name",bold_c),Paragraph("Order Amount (Rs.)",bold_c),Paragraph("Payment Received (Rs.)",bold_c),Paragraph("Payment Date",bold_c),Paragraph("Balance / Notes",bold_c)]
    data=[header]
    for i in range(1,num_rows+1):
        data.append([Paragraph(str(i),bold_c),Paragraph("",bold),Paragraph("",bold),Paragraph("",bold),Paragraph("",bold),Paragraph("",bold)])
    row_heights=[8*mm]+[12*mm]*num_rows
    table=Table(data,colWidths=[10*mm,50*mm,30*mm,35*mm,25*mm,40*mm],rowHeights=row_heights,repeatRows=1)
    table.setStyle(TableStyle([("GRID",(0,0),(-1,-1),LINE_WIDTH,LINE_COLOR),("BOX",(0,0),(-1,-1),1.4,LINE_COLOR),("LINEBELOW",(0,0),(-1,0),1.4,LINE_COLOR),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def make_report_pdf(title_text, from_date, to_date, columns, rows_data):
    buffer=BytesIO()
    doc=SimpleDocTemplate(buffer,pagesize=A4,rightMargin=10*mm,leftMargin=10*mm,topMargin=10*mm,bottomMargin=10*mm,title=title_text,author=FARM_NAME)
    styles=getSampleStyleSheet()
    tstyle=ParagraphStyle("RTitle",parent=styles["Title"],fontName="Helvetica-Bold",fontSize=16,leading=18,alignment=TA_CENTER,textColor=colors.black)
    cstyle=ParagraphStyle("RCenter",parent=styles["Normal"],fontName="Helvetica-Bold",fontSize=9,leading=12,alignment=TA_CENTER,textColor=colors.black)
    bstyle=ParagraphStyle("RBold",parent=styles["Normal"],fontName="Helvetica-Bold",fontSize=8,leading=10,textColor=colors.black)
    story=[Paragraph(FARM_NAME.upper(),tstyle),Paragraph(title_text.upper(),cstyle),Paragraph(f"From: {from_date} To: {to_date} | Printed: {datetime.now().strftime('%d-%b-%Y %I:%M %p')}",cstyle),Spacer(1,8)]
    header=[Paragraph(col,bstyle) for col in columns]
    data=[header]
    for rd in rows_data:
        data.append([Paragraph(str(x),bstyle) for x in rd])
    col_widths=[(170/len(columns))*mm]*len(columns)
    table=Table(data,colWidths=col_widths,repeatRows=1)
    table.setStyle(TableStyle([("GRID",(0,0),(-1,-1),LINE_WIDTH,LINE_COLOR),("BOX",(0,0),(-1,-1),1.4,LINE_COLOR),("LINEBELOW",(0,0),(-1,0),1.4,LINE_COLOR),("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]))
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def search_orders(query="", customer=None, limit=300, from_date=None, to_date=None):
    conn=get_conn()
    rows=conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    conn.close()
    q=(query or "").strip().lower()
    result=[]
    for r in rows:
        if customer and (r["customer_name"] or "").lower()!=customer.lower(): continue
        if q and not any(q in (r[field] or "").lower() for field in ("customer_name","phone","order_id","order_date","delivery_area","address","order_items","order_items_json") if r[field]): continue
        if from_date or to_date:
            dt=parse_order_datetime(r["created_at"]) or parse_order_datetime(r["order_date"])
            if not dt: continue
            if from_date and dt.date()<from_date: continue
            if to_date and dt.date()>to_date: continue
        result.append(r)
        if len(result)>=limit: break
    return result

st.markdown("""
<style>
.main {background:#fafaf7;}
h1,h2,h3 {font-family: 'Segoe UI', sans-serif; font-weight:800 !important;}
.stButton>button {border-radius:10px; font-weight:700; border:1px solid #111;}
div[data-testid="stMetric"] {background:white; border:1px solid #e5e5e5; padding:15px; border-radius:12px;}
</style>
""", unsafe_allow_html=True)

col_logo, col_title, col_auth = st.columns([1,4,2])
with col_logo: st.markdown("## 🌱")
with col_title:
    st.markdown(f"# {FARM_NAME}")
    st.caption("Fresh Organic Farm Products - Professional Online Store - Karachi & Lahore")
with col_auth:
    if st.session_state.user:
        st.success(f"Logged: {st.session_state.user} ({st.session_state.user_role})")
        if st.button("Logout"):
            st.session_state.user=None
            st.session_state.user_role=None
            st.rerun()
    else:
        st.info("Guest - Login for full shop")

with st.sidebar:
    st.header("🌱 Sungold")
    st.write(f"📞 {FARM_PHONE}")
    st.write(f"📧 {FARM_EMAIL}")
    st.divider()
    if st.session_state.user_role=="admin":
        menu=st.radio("Navigation", ["Dashboard","Shop (Customer View)","Cart & Checkout","Orders Management","Customers","Products Management","Payments & Ledger","Reports","Printing","Backup & Settings"], index=0)
    elif st.session_state.user_role=="customer":
        menu=st.radio("Navigation", ["Shop","Cart & Checkout","My Orders","My Profile","WhatsApp Contact"], index=0)
    else:
        menu=st.radio("Navigation", ["Shop","Cart & Checkout","Customer Login/Register","Admin Login","WhatsApp Contact"], index=0)
    st.divider()
    st.metric("Items in cart", len(st.session_state.cart))
    st.metric("Cart value", f"Rs {cart_subtotal():,.0f}")

def customer_register(name,email,phone,password,address,area):
    if not name or not email or not password: return False, "Name, Email, Password required"
    if not valid_email(email): return False, "Invalid email"
    if len(password)<6: return False, "Password min 6 chars"
    conn=get_conn()
    exists=conn.execute("SELECT * FROM customer_auth WHERE email=? COLLATE NOCASE OR customer_name=? COLLATE NOCASE",(email,name)).fetchone()
    if exists:
        conn.close()
        return False, "Email or Name already registered"
    now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ph=hash_password(password)
    try:
        conn.execute("INSERT INTO customer_auth(customer_name,email,phone,password_hash,created_at) VALUES (?,?,?,?,?)",(name.strip(),email.strip().lower(),clean_phone(phone),ph,now))
        conn.execute("INSERT INTO customers (name,email,phone,address,delivery_area,created_at,updated_at) VALUES (?,?,?,?,?,?,?) ON CONFLICT(name) DO UPDATE SET email=excluded.email, phone=excluded.phone, address=excluded.address, delivery_area=excluded.delivery_area, updated_at=excluded.updated_at",(name.strip(),email.strip(),clean_phone(phone),address.strip(),area.strip(),now,now))
        conn.commit()
        conn.close()
        return True, "Registered successfully"
    except Exception as e:
        conn.close()
        return False, str(e)

def customer_login(email,password):
    conn=get_conn()
    row=conn.execute("SELECT * FROM customer_auth WHERE email=? COLLATE NOCASE",(email,)).fetchone()
    conn.close()
    if not row: return False, "Email not found"
    if check_password(password,row["password_hash"]):
        return True, dict(row)
    else:
        return False, "Wrong password"

if menu in ["Shop","Shop (Customer View)"]:
    st.subheader("🛍 Professional Organic Shop")
    cats=get_categories()
    all_cats=["All"]+cats
    cols=st.columns(5)
    for i, cat in enumerate(all_cats):
        with cols[i%5]:
            if st.button(cat, key=f"cat_{cat}", use_container_width=True, type="primary" if st.session_state.selected_category==cat else "secondary"):
                st.session_state.selected_category=cat
                st.rerun()
    st.divider()
    search_term=st.text_input("🔍 Search product (e.g. Breast, Chicken, Egg, Tomato)", key="shop_search_main").strip()
    selected_cat_display=st.session_state.selected_category
    st.write(f"**Selected Category:** {selected_cat_display}")
    only_avail=(st.session_state.user_role!="admin")
    products_rows=get_all_products(only_available_for_customer=only_avail, search=search_term, category_filter=selected_cat_display)
    if not products_rows:
        st.warning("No products found for this filter. Try All or different search.")
    else:
        for row in products_rows:
            with st.container(border=True):
                c1,c2,c3,c4=st.columns([4,2,2,2])
                with c1:
                    st.markdown(f"**{row['name']}**")
                    st.caption(f"Category: {row['category']} | {'✅ Available' if row['is_available'] else '❌ Unavailable'}")
                with c2:
                    st.metric("Price", f"Rs {float(row['price']):,.0f}")
                with c3:
                    qty=st.number_input("Qty", min_value=0.0, max_value=10000.0, value=1.0, step=0.1, format="%.2f", key=f"qty_{row['id']}")
                with c4:
                    if st.button("➕ Add to Cart", key=f"add_{row['id']}", use_container_width=True):
                        if add_to_cart(row["category"], row["name"], row["price"], qty):
                            st.success(f"Added {row['name']}")
                        else:
                            st.error("Qty must be >0")
    st.divider()
    st.info(f"🛒 Cart has {len(st.session_state.cart)} items. Go to Cart & Checkout to place order.")

elif menu=="Cart & Checkout":
    st.subheader("🛒 Cart & Checkout")
    if not st.session_state.cart:
        st.info("Cart empty. Add products from Shop.")
    else:
        for i, item in enumerate(list(st.session_state.cart)):
            with st.container(border=True):
                c1,c2,c3,c4,c5=st.columns([4,1.4,1.5,1.5,0.8])
                with c1: st.write(f"**{item['product']}** ({item['category']})")
                with c2:
                    new_qty=st.number_input("Qty", min_value=0.0, value=float(item["quantity"]), step=0.1, format="%.2f", key=f"cqty_{i}", label_visibility="collapsed")
                    if abs(new_qty-float(item["quantity"]))>1e-9:
                        update_cart_quantity(i,new_qty)
                        st.rerun()
                with c3: st.write(f"Rs {item['price']:,.0f}")
                with c4: st.write(f"Rs {item['total']:,.0f}")
                with c5:
                    if st.button("✕", key=f"cremove_{i}"):
                        remove_from_cart(i)
                        st.rerun()
        if st.button("🗑 Clear Cart"):
            clear_cart()
            st.rerun()
        subtotal=cart_subtotal()
        st.divider()
        st.subheader("💰 Charges")
        cc1,cc2,cc3=st.columns(3)
        with cc1: delivery=st.number_input("Delivery Charges (Rs)", min_value=0.0, value=float(get_delivery_charge()), step=50.0, key="chk_delivery_main")
        with cc2:
            charge_packing=st.checkbox("Charge packing material?", key="chk_pack_on_main")
            packing=st.number_input("Packing Material (Rs)", min_value=0.0, value=0.0, step=50.0, key="chk_pack_amt_main", disabled=not charge_packing)
            if not charge_packing: packing=0.0
        with cc3:
            give_discount=st.checkbox("Give discount?", key="chk_disc_on_main")
            discount=st.number_input("Discount (Rs)", min_value=0.0, value=0.0, step=50.0, key="chk_disc_amt_main", disabled=not give_discount)
            if not give_discount: discount=0.0
        discount=min(discount, subtotal+delivery+packing)
        grand_total=subtotal+delivery+packing-discount
        st.write(f"**Subtotal:** Rs {subtotal:,.0f}")
        st.write(f"**Delivery:** Rs {delivery:,.0f}")
        st.write(f"**Packing:** Rs {packing:,.0f}" if packing>0 else "**Packing:** Not charged")
        if discount>0: st.write(f"**Discount:** - Rs {discount:,.0f}")
        st.subheader(f"Grand Total: Rs {grand_total:,.0f}")
        st.divider()
        st.subheader("👤 Customer Information")
        logged_customer=None
        if st.session_state.user_role=="customer":
            logged_customer=find_customer(st.session_state.user)
            if not logged_customer:
                conn=get_conn()
                auth=conn.execute("SELECT * FROM customer_auth WHERE email=? COLLATE NOCASE",(st.session_state.user,)).fetchone()
                if not auth:
                    auth=conn.execute("SELECT * FROM customer_auth WHERE customer_name=? COLLATE NOCASE",(st.session_state.user,)).fetchone()
                conn.close()
                if auth:
                    logged_customer=find_customer(auth["customer_name"])
        if st.session_state.user_role=="admin":
            names=customer_names()
            selected_customer=st.selectbox("Returning Customer? Select", ["➕ New Customer"]+names, key="admin_customer_select")
            selected=None if selected_customer=="➕ New Customer" else find_customer(selected_customer)
        else:
            selected=logged_customer
            selected_customer=selected["name"] if selected else "➕ New Customer"
        c1,c2=st.columns(2)
        with c1:
            customer_name=st.text_input("Customer Name *", value=selected["name"] if selected else (st.session_state.user if st.session_state.user_role=="customer" else ""), key=f"cn_main_{selected_customer}")
            customer_email=st.text_input("Email (optional)", value=selected["email"] if selected else (st.session_state.user if "@" in str(st.session_state.user or "") else ""), key=f"ce_main_{selected_customer}")
        with c2:
            customer_phone=st.text_input("Mobile / WhatsApp *", value=selected["phone"] if selected else "", key=f"cp_main_{selected_customer}")
            delivery_area=st.text_input("Delivery Area *", value=selected["delivery_area"] if selected else "", key=f"ca_main_{selected_customer}")
        customer_address=st.text_area("Complete Delivery Address *", value=selected["address"] if selected else "", height=100, key=f"cad_main_{selected_customer}")
        if st.button("✅ PLACE ORDER & CREATE BILL", type="primary", use_container_width=True):
            if not st.session_state.user and st.session_state.user_role!="admin":
                st.error("Please login as customer first to place order. Go to Customer Login/Register.")
            elif not customer_name.strip(): st.error("Please enter customer name.")
            elif customer_email.strip() and not valid_email(customer_email.strip()): st.error("Email format not valid.")
            elif not customer_phone.strip(): st.error("Please enter mobile.")
            elif not delivery_area.strip(): st.error("Please enter delivery area.")
            elif not customer_address.strip(): st.error("Please enter address.")
            else:
                stamp=datetime.now()
                order={"order_id":generate_order_id(),"customer_name":customer_name.strip(),"email":customer_email.strip(),"phone":clean_phone(customer_phone),"address":customer_address.strip(),"delivery_area":delivery_area.strip(),"cart":list(st.session_state.cart),"order_items":build_order_items(st.session_state.cart),"order_items_json":build_order_items_json(st.session_state.cart),"subtotal":subtotal,"delivery_charge":float(delivery),"packing_material":float(packing),"discount":float(discount),"total_amount":float(grand_total),"order_date":stamp.strftime("%d-%b-%Y %I:%M %p"),"status":"Pending","payment_status":"Unpaid","month_key":month_key_of(stamp),"created_at":stamp.strftime("%Y-%m-%d %H:%M:%S")}
                save_customer(order["customer_name"],order["email"],order["phone"],order["address"],order["delivery_area"])
                save_order(order)
                st.session_state.last_pdf=make_invoice_pdf(order)
                st.session_state.last_order=order
                st.session_state.last_order_id=order["order_id"]
                telegram_ok=telegram_notify(order)
                clear_cart()
                st.success(f"🎉 Order created: {order['order_id']} saved in {month_label(order['month_key'])}")
                if telegram_ok: st.success("📱 Telegram notification sent.")
        if st.session_state.last_pdf and st.session_state.last_order:
            last=st.session_state.last_order
            st.divider()
            st.subheader(f"🖨 Print Bill — {last['order_id']}")
            d1,d2=st.columns(2)
            with d1:
                st.download_button("⬇ Download / Print A4 Bill (PDF)", data=st.session_state.last_pdf, file_name=f"{last['order_id']}.pdf", mime="application/pdf", use_container_width=True)
            with d2:
                st.link_button("💬 Send summary on WhatsApp", whatsapp_link(last), use_container_width=True)
                st.link_button("📲 Send to Admin WhatsApp", whatsapp_admin_link(last), use_container_width=True)

elif menu=="Customer Login/Register":
    st.subheader("👤 Customer Authentication")
    tab_login, tab_register = st.tabs(["Login","Register"])
    with tab_login:
        email=st.text_input("Email", key="login_email")
        password=st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", type="primary"):
            ok, res=customer_login(email,password)
            if ok:
                st.session_state.user=res["email"]
                st.session_state.user_role="customer"
                st.success(f"Welcome {res['customer_name']}")
                st.rerun()
            else:
                st.error(res)
    with tab_register:
        name=st.text_input("Full Name *", key="reg_name")
        email=st.text_input("Email *", key="reg_email")
        phone=st.text_input("Phone *", key="reg_phone")
        address=st.text_area("Address *", key="reg_address")
        area=st.text_input("Delivery Area *", key="reg_area")
        password=st.text_input("Password * (min 6)", type="password", key="reg_pass")
        password2=st.text_input("Confirm Password *", type="password", key="reg_pass2")
        if st.button("Register", type="primary"):
            if password!=password2: st.error("Passwords do not match")
            else:
                ok,msg=customer_register(name,email,phone,password,address,area)
                if ok: st.success(msg+" Now login.")
                else: st.error(msg)

elif menu=="Admin Login":
    st.subheader("🔐 Admin Login")
    pwd=st.text_input("Admin Password", type="password")
    if st.button("Login as Admin", type="primary"):
        if pwd==ADMIN_PASSWORD:
            st.session_state.user="Admin"
            st.session_state.user_role="admin"
            st.success("Admin logged in")
            st.rerun()
        else:
            st.error("Incorrect password")

elif menu=="My Orders":
    if st.session_state.user_role!="customer":
        st.error("Please login as customer")
    else:
        st.subheader("📦 My Orders - Order History")
        conn=get_conn()
        auth=conn.execute("SELECT * FROM customer_auth WHERE email=? COLLATE NOCASE",(st.session_state.user,)).fetchone()
        if not auth:
            auth=conn.execute("SELECT * FROM customer_auth WHERE customer_name=? COLLATE NOCASE",(st.session_state.user,)).fetchone()
        conn.close()
        cust_name=auth["customer_name"] if auth else st.session_state.user
        orders=search_orders(customer=cust_name, limit=100)
        if not orders:
            st.info("No orders yet. Shop now!")
        else:
            for o in orders:
                rebuilt=order_row_to_dict(o)
                with st.expander(f"{o['order_id']} | Rs {float(o['total_amount'] or 0):,.0f} | {o['status']} | {o['order_date']}"):
                    st.write(f"**Status:** {o['status']} | **Payment:** {o['payment_status']} | **Total:** Rs {float(o['total_amount'] or 0):,.0f}")
                    st.text(o["order_items"])
                    c1,c2,c3=st.columns(3)
                    with c1:
                        st.download_button("🖨 Invoice PDF", data=make_invoice_pdf(rebuilt), file_name=f"{o['order_id']}.pdf", mime="application/pdf", key=f"myinv_{o['id']}")
                    with c2:
                        if st.button("🔁 Reorder", key=f"reorder_{o['id']}"):
                            for item in rebuilt["cart"]:
                                conn=get_conn()
                                prow=conn.execute("SELECT * FROM products WHERE name=? COLLATE NOCASE",(item["product"],)).fetchone()
                                conn.close()
                                cat=prow["category"] if prow else "Organic Chicken"
                                add_to_cart(cat, item["product"], item["price"], item["quantity"])
                            st.success("Added to cart - go to Cart & Checkout")
                    with c3:
                        st.link_button("💬 WhatsApp", whatsapp_link(rebuilt))

elif menu=="My Profile":
    if st.session_state.user_role!="customer":
        st.error("Login required")
    else:
        conn=get_conn()
        auth=conn.execute("SELECT * FROM customer_auth WHERE email=? COLLATE NOCASE",(st.session_state.user,)).fetchone()
        if not auth:
            auth=conn.execute("SELECT * FROM customer_auth WHERE customer_name=? COLLATE NOCASE",(st.session_state.user,)).fetchone()
        conn.close()
        cust=find_customer(auth["customer_name"] if auth else st.session_state.user)
        st.subheader(f"👤 Profile - {auth['customer_name'] if auth else st.session_state.user}")
        if cust:
            st.write(f"**Email:** {cust['email']} | **Phone:** {cust['phone']}")
            st.write(f"**Area:** {cust['delivery_area']}")
            st.write(f"**Address:** {cust['address']}")
        ledger=get_customer_ledger(auth["customer_name"] if auth else st.session_state.user)
        bal=ledger[-1]["running_balance"] if ledger else 0
        st.metric("Outstanding Balance", f"Rs {bal:,.0f}")
        with st.expander("Edit Profile"):
            new_phone=st.text_input("Phone", value=cust["phone"] if cust else "")
            new_area=st.text_input("Delivery Area", value=cust["delivery_area"] if cust else "")
            new_address=st.text_area("Address", value=cust["address"] if cust else "")
            new_email=st.text_input("Email", value=cust["email"] if cust else "")
            if st.button("Save Profile"):
                save_customer(auth["customer_name"] if auth else st.session_state.user, new_email, new_phone, new_address, new_area)
                st.success("Profile updated")

elif menu=="Dashboard":
    st.subheader("📊 Admin Dashboard - Business Overview")
    conn=get_conn()
    all_orders=conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    conn.close()
    f1,f2,f3,f4=st.columns(4)
    with f1: from_date=st.date_input("From Date", value=date.today()-timedelta(days=30), key="dash_from")
    with f2: to_date=st.date_input("To Date", value=date.today(), key="dash_to")
    with f3: status_filter=st.selectbox("Order Status", ["All","Pending","Confirmed","Processing","Out for Delivery","Delivered","Cancelled"], key="dash_status")
    with f4: pay_filter=st.selectbox("Payment Status", ["All","Unpaid","Partially Paid","Paid"], key="dash_pay")
    filtered=[]
    for o in all_orders:
        dt=parse_order_datetime(o["created_at"]) or parse_order_datetime(o["order_date"])
        if not dt: continue
        if dt.date()<from_date or dt.date()>to_date: continue
        if status_filter!="All" and o["status"]!=status_filter: continue
        if pay_filter!="All" and o["payment_status"]!=pay_filter: continue
        filtered.append(o)
    total_orders=len(filtered)
    sales=sum(float(o["total_amount"] or 0) for o in filtered if o["status"]!="Cancelled")
    pending=sum(1 for o in filtered if o["status"]=="Pending")
    delivered=sum(1 for o in filtered if o["status"]=="Delivered")
    conn=get_conn()
    ledger_all=conn.execute("SELECT customer_name, SUM(debit-credit) as bal FROM ledger_transactions GROUP BY customer_name").fetchall()
    conn.close()
    outstanding=sum(float(r["bal"] or 0) for r in ledger_all if float(r["bal"] or 0)>0)
    m1,m2,m3,m4,m5=st.columns(5)
    m1.metric("Total Orders", total_orders)
    m2.metric("Total Sales", f"Rs {sales:,.0f}")
    m3.metric("Pending", pending)
    m4.metric("Delivered", delivered)
    m5.metric("Outstanding", f"Rs {outstanding:,.0f}")
    st.divider()
    st.subheader("Customer Outstanding")
    if ledger_all:
        df=pd.DataFrame([{"Customer":r["customer_name"],"Balance":float(r["bal"] or 0)} for r in ledger_all])
        df=df[df["Balance"]!=0].sort_values("Balance",ascending=False)
        st.dataframe(df,use_container_width=True)

elif menu=="Orders Management":
    st.subheader("📋 Orders Management")
    conn=get_conn()
    all_orders=conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    conn.close()
    month_keys=sorted({(o["month_key"] or "unknown") for o in all_orders}, reverse=True)
    current_key=month_key_of(datetime.now())
    options=["All Months"]+month_keys
    default_index=options.index(current_key) if current_key in options else 0
    f1,f2,f3=st.columns([2,2,2])
    with f1: chosen_month=st.selectbox("Select Month", options, index=default_index, format_func=lambda k: "All Months" if k=="All Months" else month_label(k), key="ord_month")
    with f2: search_text=st.text_input("🔍 Search (customer/order/phone)", key="ord_search").strip().lower()
    with f3: status_filter=st.selectbox("Status filter", ["All","Pending","Confirmed","Processing","Out for Delivery","Delivered","Cancelled"], key="ord_status")
    orders=[o for o in all_orders if (chosen_month=="All Months" or (o["month_key"] or "unknown")==chosen_month) and (status_filter=="All" or o["status"]==status_filter) and (not search_text or search_text in (o["customer_name"] or "").lower() or search_text in (o["order_id"] or "").lower() or search_text in (o["phone"] or "").lower())]
    st.write(f"**{len(orders)} bills found**")
    if orders: st.download_button("⬇ Export CSV", data=orders_to_csv(orders), file_name=f"sungold_orders_{chosen_month}.csv", mime="text/csv")
    for order in orders[:200]:
        with st.expander(f"{order['order_id']} | {order['customer_name']} | Rs {float(order['total_amount'] or 0):,.0f} | {order['status']} | {month_label(order['month_key'])}"):
            c1,c2=st.columns(2)
            with c1:
                st.write(f"**Date:** {order['order_date']} | **Month:** {month_label(order['month_key'])}")
                st.write(f"**Customer:** {order['customer_name']} | **Phone:** {order['phone']}")
                st.write(f"**Payment:** {order['payment_status']}")
            with c2:
                st.write(f"**Area:** {order['delivery_area']}")
                st.write(f"**Address:** {order['address']}")
                st.write(f"**Total:** Rs {float(order['total_amount'] or 0):,.0f}")
            st.text(order["order_items"])
            status_options=["Pending","Confirmed","Processing","Out for Delivery","Delivered","Cancelled"]
            payment_options=["Unpaid","Paid","Partially Paid"]
            ns=st.selectbox("Order Status", status_options, index=status_options.index(order["status"]) if order["status"] in status_options else 0, key=f"status_{order['id']}")
            np_=st.selectbox("Payment Status", payment_options, index=payment_options.index(order["payment_status"]) if order["payment_status"] in payment_options else 0, key=f"payment_{order['id']}")
            rebuilt=order_row_to_dict(order)
            b1,b2,b3,b4=st.columns(4)
            with b1:
                if st.button("💾 Update", key=f"update_{order['id']}"):
                    conn=get_conn()
                    conn.execute("UPDATE orders SET status=?, payment_status=? WHERE id=?",(ns,np_,order["id"]))
                    conn.commit()
                    conn.close()
                    update_order_transaction(order["order_id"], float(order["total_amount"] or 0), ns, order["customer_name"])
                    st.success("Order updated & ledger synced")
                    st.rerun()
            with b2: st.download_button("⬇ PDF", data=make_invoice_pdf(rebuilt), file_name=f"{order['order_id']}.pdf", mime="application/pdf", key=f"dl_{order['id']}")
            with b3: st.link_button("💬 WhatsApp", whatsapp_link(rebuilt), use_container_width=True)
            with b4:
                if st.button("🗑 Delete Bill", key=f"del_{order['id']}"):
                    st.session_state.confirm_delete_order=order["id"]
                    st.rerun()
            if st.session_state.confirm_delete_order==order["id"]:
                st.warning(f"Are you sure you want to permanently delete bill {order['order_id']}? This will also remove ledger entry.")
                y1,y2=st.columns(2)
                with y1:
                    if st.button("✅ Yes, delete it", key=f"delyes_{order['id']}"):
                        delete_order(order["id"], order["order_id"])
                        st.session_state.confirm_delete_order=None
                        st.success("Bill deleted & ledger synced")
                        st.rerun()
                with y2:
                    if st.button("❌ Cancel", key=f"delno_{order['id']}"):
                        st.session_state.confirm_delete_order=None
                        st.rerun()

elif menu=="Customers":
    st.subheader("👥 Customer Management")
    conn=get_conn()
    rows=conn.execute("SELECT name,email,phone,delivery_area,address,updated_at FROM customers ORDER BY name COLLATE NOCASE").fetchall()
    order_counts={r["customer_name"]:r["c"] for r in conn.execute("SELECT customer_name, COUNT(*) AS c FROM orders GROUP BY customer_name").fetchall()}
    ledger_bals={r["customer_name"]:float(r["bal"] or 0) for r in conn.execute("SELECT customer_name, SUM(debit-credit) as bal FROM ledger_transactions GROUP BY customer_name").fetchall()}
    conn.close()
    search=st.text_input("🔍 Search customer", key="cust_search").strip().lower()
    filtered=[r for r in rows if not search or search in r["name"].lower() or search in (r["phone"] or "").lower() or search in (r["email"] or "").lower()]
    if filtered:
        st.dataframe([{"Customer":r["name"],"Email":r["email"],"Phone":r["phone"],"Area":r["delivery_area"],"Orders":order_counts.get(r["name"],0),"Balance":f"Rs {ledger_bals.get(r['name'],0):,.0f}"} for r in filtered], use_container_width=True, hide_index=True)
    st.divider()
    names_list=[r["name"] for r in rows]
    if names_list:
        selected_cust=st.selectbox("Select customer for ledger/statement", names_list, key="cust_detail_pick")
        if selected_cust:
            conn=get_conn()
            cust_orders=conn.execute("SELECT * FROM orders WHERE customer_name=? COLLATE NOCASE ORDER BY id DESC",(selected_cust,)).fetchall()
            conn.close()
            ledger=get_customer_ledger(selected_cust)
            bal=ledger[-1]["running_balance"] if ledger else 0
            st.metric("Outstanding Balance", f"Rs {bal:,.0f}")
            if ledger:
                st.dataframe([{"Date":l["transaction_date"],"Type":l["transaction_type"],"Ref":l["reference_id"],"Desc":l["description"],"Debit":float(l["debit"] or 0),"Credit":float(l["credit"] or 0),"Balance":float(l["running_balance"])} for l in ledger], use_container_width=True)
            if cust_orders:
                st.download_button(f"⬇ Statement PDF for {selected_cust}", data=make_customer_statement_pdf(selected_cust, cust_orders, ledger), file_name=f"statement_{selected_cust.replace(' ','_')}.pdf", mime="application/pdf")

elif menu=="Products Management":
    st.subheader("📦 Product Management")
    tab_view, tab_add = st.tabs(["View & Edit Products","Add New Product"])
    with tab_view:
        search=st.text_input("🔍 Search product", key="prod_search_admin").strip()
        cat_filter=st.selectbox("Category filter", ["All"]+get_categories(), key="prod_cat_filter_admin")
        rows=get_all_products(only_available_for_customer=False, search=search, category_filter=cat_filter)
        st.write(f"{len(rows)} products")
        for r in rows:
            with st.expander(f"{r['name']} | {r['category']} | Rs {float(r['price']):,.0f} | {'✅' if r['is_available'] else '❌'}"):
                c1,c2,c3=st.columns(3)
                with c1: new_name=st.text_input("Name", value=r["name"], key=f"pname_{r['id']}")
                with c2: new_price=st.number_input("Price", value=float(r["price"]), key=f"pprice_{r['id']}")
                with c3: new_cat=st.text_input("Category", value=r["category"], key=f"pcat_{r['id']}")
                new_avail=st.checkbox("Available", value=bool(r["is_available"]), key=f"pavail_{r['id']}")
                if st.button("💾 Update Product", key=f"pupd_{r['id']}"):
                    conn=get_conn()
                    conn.execute("UPDATE products SET name=?, price=?, category=?, is_available=?, updated_at=? WHERE id=?",(new_name.strip(), float(new_price), new_cat.strip(), 1 if new_avail else 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), r["id"]))
                    conn.commit()
                    conn.close()
                    st.success("Product updated")
                    st.rerun()
    with tab_add:
        new_name=st.text_input("Product Name *", key="new_prod_name")
        new_cat=st.text_input("Category *", key="new_prod_cat")
        new_price=st.number_input("Price *", min_value=0.0, value=0.0, key="new_prod_price")
        new_avail=st.checkbox("Available", value=True, key="new_prod_avail")
        if st.button("➕ Add Product", type="primary"):
            if not new_name or not new_cat:
                st.error("Name and Category required")
            else:
                conn=get_conn()
                try:
                    conn.execute("INSERT INTO products(category,name,price,is_available,created_at,updated_at) VALUES (?,?,?,?,?,?)",(new_cat.strip(), new_name.strip(), float(new_price), 1 if new_avail else 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    st.success("Product added")
                except Exception as e:
                    st.error(f"Error: {e}")
                conn.close()

elif menu=="Payments & Ledger":
    st.subheader("💳 Payments, Adjustments & Dynamic Ledger")
    tab_pay, tab_adj, tab_ledger = st.tabs(["Payments","Adjustments","Customer Ledger"])
    with tab_pay:
        st.write("### Add Payment")
        c1,c2,c3=st.columns(3)
        with c1: pay_customer=st.selectbox("Customer", customer_names(), key="pay_customer")
        with c2: pay_amount=st.number_input("Amount", min_value=0.0, value=0.0, key="pay_amount")
        with c3: pay_method=st.selectbox("Method", ["Cash","Bank Transfer","Online Transfer","Easypaisa","JazzCash","Other"], key="pay_method")
        c4,c5=st.columns(2)
        with c4: pay_date=st.date_input("Payment Date", value=date.today(), key="pay_date")
        with c5: pay_ref=st.text_input("Reference No", key="pay_ref")
        pay_order=st.text_input("Related Order ID (optional)", key="pay_order")
        pay_notes=st.text_area("Notes", key="pay_notes")
        if st.button("➕ Add Payment", type="primary"):
            if not pay_customer or pay_amount<=0:
                st.error("Customer and amount required")
            else:
                pid=generate_payment_id()
                now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn=get_conn()
                conn.execute("INSERT INTO payments(payment_id,customer_name,order_id,amount,payment_date,payment_method,reference_no,notes,created_at) VALUES (?,?,?,?,?,?,?,?,?)",(pid,pay_customer,pay_order,float(pay_amount),pay_date.strftime("%Y-%m-%d %H:%M:%S"),pay_method,pay_ref,pay_notes,now))
                conn.commit()
                conn.close()
                create_payment_transaction({"payment_id":pid,"customer_name":pay_customer,"amount":float(pay_amount),"payment_date":pay_date.strftime("%Y-%m-%d %H:%M:%S"),"payment_method":pay_method})
                st.success(f"Payment {pid} added & ledger synced")
        st.divider()
        conn=get_conn()
        pays=conn.execute("SELECT * FROM payments ORDER BY id DESC LIMIT 100").fetchall()
        conn.close()
        for p in pays:
            with st.expander(f"{p['payment_id']} | {p['customer_name']} | Rs {float(p['amount']):,.0f} | {p['payment_method']}"):
                new_amount=st.number_input("Amount", value=float(p["amount"]), key=f"pay_edit_amount_{p['id']}")
                if st.button("💾 Update Payment", key=f"pay_upd_{p['id']}"):
                    conn=get_conn()
                    conn.execute("UPDATE payments SET amount=? WHERE id=?",(float(new_amount),p["id"]))
                    conn.commit()
                    conn.close()
                    update_payment_transaction({"payment_id":p["payment_id"],"customer_name":p["customer_name"],"amount":float(new_amount),"payment_date":p["payment_date"],"payment_method":p["payment_method"]})
                    st.success("Payment updated & ledger synced")
                    st.rerun()
                if st.button("🗑 Delete Payment", key=f"pay_del_{p['id']}"):
                    conn=get_conn()
                    conn.execute("DELETE FROM payments WHERE id=?",(p["id"],))
                    conn.commit()
                    conn.close()
                    delete_payment_transaction(p["payment_id"])
                    st.success("Payment deleted & ledger synced")
                    st.rerun()
    with tab_adj:
        st.write("### Add Balance Adjustment")
        adj_customer=st.selectbox("Customer", customer_names(), key="adj_customer")
        adj_type=st.selectbox("Type", ["Credit (reduces balance)","Debit (increases balance)"], key="adj_type")
        adj_amount=st.number_input("Amount", min_value=0.0, value=0.0, key="adj_amount")
        adj_reason=st.text_input("Reason", key="adj_reason")
        adj_date=st.date_input("Date", value=date.today(), key="adj_date")
        if st.button("➕ Add Adjustment"):
            if not adj_customer or adj_amount<=0:
                st.error("Customer and amount required")
            else:
                aid=generate_adjustment_id()
                typ="Credit" if "Credit" in adj_type else "Debit"
                now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn=get_conn()
                conn.execute("INSERT INTO adjustments(adjustment_id,customer_name,amount,adjustment_type,reason,adjustment_date,created_at) VALUES (?,?,?,?,?,?,?)",(aid,adj_customer,float(adj_amount),typ,adj_reason,adj_date.strftime("%Y-%m-%d %H:%M:%S"),now))
                conn.commit()
                conn.close()
                create_adjustment_transaction({"adjustment_id":aid,"customer_name":adj_customer,"amount":float(adj_amount),"adjustment_type":typ,"reason":adj_reason,"adjustment_date":adj_date.strftime("%Y-%m-%d %H:%M:%S")})
                st.success("Adjustment added & ledger synced")
    with tab_ledger:
        sel=st.selectbox("Select Customer", customer_names(), key="ledger_customer")
        if sel:
            ledger=get_customer_ledger(sel)
            st.metric("Outstanding Balance", f"Rs {get_customer_balance(sel):,.0f}")
            if ledger:
                st.dataframe([{"Date":l["transaction_date"],"Type":l["transaction_type"],"Ref":l["reference_id"],"Desc":l["description"],"Debit":float(l["debit"] or 0),"Credit":float(l["credit"] or 0),"Balance":float(l["running_balance"])} for l in ledger], use_container_width=True)

elif menu=="Reports":
    st.subheader("📊 Reports - From Date to To Date")
    from_date=st.date_input("From Date", value=date.today()-timedelta(days=30), key="rep_from")
    to_date=st.date_input("To Date", value=date.today(), key="rep_to")
    report_type=st.selectbox("Report Type", ["Product-wise Sales","Category-wise Sales","Customer-wise Sales","Chicken Sales","Mutton Sales","Vegetables Sales","Eggs Sales"], key="rep_type")
    search_term=st.text_input("🔍 Search", key="rep_search").strip().lower()
    conn=get_conn()
    all_orders=conn.execute("SELECT * FROM orders").fetchall()
    conn.close()
    filtered_orders=[]
    for o in all_orders:
        dt=parse_order_datetime(o["created_at"]) or parse_order_datetime(o["order_date"])
        if not dt: continue
        if not (from_date<=dt.date()<=to_date): continue
        if o["status"]=="Cancelled": continue
        filtered_orders.append(o)
    product_sales={}
    category_sales={}
    customer_sales={}
    for o in filtered_orders:
        try:
            items=json.loads(o["order_items_json"]) if o["order_items_json"] else parse_order_items(o["order_items"])
        except:
            items=parse_order_items(o["order_items"])
        for item in items:
            conn=get_conn()
            prow=conn.execute("SELECT category FROM products WHERE name=? COLLATE NOCASE",(item["product"],)).fetchone()
            conn.close()
            cat=prow["category"] if prow else "Unknown"
            pname=item["product"]
            qty=float(item["quantity"] or 0)
            total=float(item["total"] or 0)
            if pname not in product_sales:
                product_sales[pname]={"category":cat,"qty":0,"sales":0,"orders_set":set()}
            product_sales[pname]["qty"]+=qty
            product_sales[pname]["sales"]+=total
            product_sales[pname]["orders_set"].add(o["order_id"])
            if cat not in category_sales:
                category_sales[cat]={"qty":0,"sales":0,"orders_set":set()}
            category_sales[cat]["qty"]+=qty
            category_sales[cat]["sales"]+=total
            category_sales[cat]["orders_set"].add(o["order_id"])
        cname=o["customer_name"]
        if cname not in customer_sales:
            customer_sales[cname]={"orders":0,"purchased":0}
        customer_sales[cname]["orders"]+=1
        customer_sales[cname]["purchased"]+=float(o["total_amount"] or 0)
    if report_type=="Product-wise Sales":
        rows_data=[]
        for pname, data in product_sales.items():
            if search_term and search_term not in pname.lower(): continue
            rows_data.append([pname, data["category"], f"{data['qty']:.2f}", f"Rs {data['sales']:,.0f}", len(data["orders_set"])])
        st.dataframe(pd.DataFrame(rows_data, columns=["Product","Category","Qty Sold","Total Sales","Num Orders"]), use_container_width=True)
        if rows_data:
            st.download_button("⬇ Export CSV", data=pd.DataFrame(rows_data, columns=["Product","Category","Qty Sold","Total Sales","Num Orders"]).to_csv(index=False).encode("utf-8"), file_name="product_sales.csv", mime="text/csv")
            pdf=make_report_pdf("Product-wise Sales Report", from_date, to_date, ["Product","Category","Qty","Sales","Orders"], rows_data)
            st.download_button("⬇ PDF Report (A4)", data=pdf, file_name="product_sales_report.pdf", mime="application/pdf")
    elif report_type=="Category-wise Sales":
        rows_data=[]
        for cat, data in category_sales.items():
            rows_data.append([cat, f"{data['qty']:.2f}", f"Rs {data['sales']:,.0f}", len(data["orders_set"])])
        st.dataframe(pd.DataFrame(rows_data, columns=["Category","Total Qty","Total Sales","Num Orders"]), use_container_width=True)
        if rows_data:
            pdf=make_report_pdf("Category-wise Sales Report", from_date, to_date, ["Category","Qty","Sales","Orders"], rows_data)
            st.download_button("⬇ PDF Report (A4)", data=pdf, file_name="category_sales_report.pdf", mime="application/pdf")

elif menu=="Printing":
    st.subheader("🖨 Professional Printing")
    tab_inv, tab_blank = st.tabs(["Reprint Invoice & Statement","Blank Payment Sheets"])
    with tab_inv:
        q=st.text_input("🔍 Search Order ID / Customer / Phone", key="print_search")
        results=search_orders(q, limit=100) if q else []
        for r in results:
            rebuilt=order_row_to_dict(r)
            with st.expander(f"{r['order_id']} | {r['customer_name']} | Rs {float(r['total_amount'] or 0):,.0f}"):
                st.download_button("🖨 Invoice PDF (A4 Bold Headings)", data=make_invoice_pdf(rebuilt), file_name=f"{r['order_id']}.pdf", mime="application/pdf", key=f"print_inv_{r['id']}")
    with tab_blank:
        num=st.selectbox("Customers per page", [5,10,15], index=2)
        st.download_button(f"⬇ Download Blank {num} Customers Sheet (A4)", data=make_blank_payment_sheet_pdf(num), file_name=f"blank_payment_sheet_{num}.pdf", mime="application/pdf", key=f"blank_{num}")

elif menu=="Backup & Settings":
    st.subheader("💾 Backup & Settings")
    conn=get_conn()
    customers=conn.execute("SELECT * FROM customers").fetchall()
    orders=conn.execute("SELECT * FROM orders").fetchall()
    payments=conn.execute("SELECT * FROM payments").fetchall()
    ledger=conn.execute("SELECT * FROM ledger_transactions").fetchall()
    conn.close()
    st.write(f"Customers: {len(customers)} | Orders: {len(orders)} | Payments: {len(payments)} | Ledger: {len(ledger)}")
    c1,c2,c3,c4=st.columns(4)
    with c1:
        csv_data=io.StringIO()
        writer=csv.writer(csv_data)
        writer.writerow(["name","email","phone","address","delivery_area"])
        for r in customers: writer.writerow([r["name"],r["email"],r["phone"],r["address"],r["delivery_area"]])
        st.download_button("⬇ Customers CSV", data=csv_data.getvalue().encode("utf-8"), file_name="customers_backup.csv", mime="text/csv")
    with c2: st.download_button("⬇ Orders CSV", data=orders_to_csv(orders), file_name="orders_backup.csv", mime="text/csv")
    with c3:
        csv_data=io.StringIO()
        writer=csv.writer(csv_data)
        writer.writerow(["payment_id","customer","order_id","amount","method","date"])
        for r in payments: writer.writerow([r["payment_id"],r["customer_name"],r["order_id"],r["amount"],r["payment_method"],r["payment_date"]])
        st.download_button("⬇ Payments CSV", data=csv_data.getvalue().encode("utf-8"), file_name="payments_backup.csv", mime="text/csv")
    with c4:
        if os.path.exists(DB_NAME):
            with open(DB_NAME,"rb") as f:
                st.download_button("⬇ Complete DB Backup (SQLite)", data=f.read(), file_name="sungold_orders_backup.db", mime="application/octet-stream")
    st.divider()
    new_delivery=st.number_input("Default Delivery Charge (Rs)", min_value=0.0, value=float(get_delivery_charge()), step=50.0)
    if st.button("Save Delivery Charge"):
        set_delivery_charge(new_delivery)
        st.success("Delivery charge updated")

elif menu=="WhatsApp Contact":
    st.subheader("💬 Contact Sungold Organic on WhatsApp")
    st.write(f"**Phone:** {FARM_PHONE} | **Email:** {FARM_EMAIL}")
    st.write(f"**Address:** {FARM_ADDRESS}")
    msg=st.text_area("Your Message", value="Assalam-o-Alaikum, I want to order organic products from Sungold Organic.")
    wa_link=f"https://wa.me/{WHATSAPP_NUMBER}?text="+urllib.parse.quote(msg)
    st.link_button("📲 Open WhatsApp", wa_link, use_container_width=True)

st.divider()
st.caption(f"© {datetime.now().year} {FARM_NAME} - Professional Orders & A4 Billing System - Data Safe Version")
