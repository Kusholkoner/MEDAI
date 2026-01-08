from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any
import os
import json
from dotenv import load_dotenv

# Attempt to import Supabase client
try:
    from supabase import create_client
except Exception:
    create_client = None

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL') or os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_KEY', '')

SUPABASE_AVAILABLE = False
supabase = None
if create_client and SUPABASE_URL and SUPABASE_KEY and SUPABASE_URL != 'YOUR_SUPABASE_URL':
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        SUPABASE_AVAILABLE = True
    except Exception:
        SUPABASE_AVAILABLE = False

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

# Simple Pydantic models
class Product(BaseModel):
    id: Optional[str]
    name: str
    category: Optional[str] = None
    brand: Optional[str] = None
    price: float
    discount_percent: Optional[float] = 0.0
    stock: Optional[int] = 0
    requires_prescription: Optional[bool] = False
    description: Optional[str] = None
    image_url: Optional[str] = None
    expiry_date: Optional[str] = None

class CartItem(BaseModel):
    id: Optional[str]
    user_email: str
    product_id: str
    quantity: int

class Order(BaseModel):
    id: Optional[str]
    user_email: str
    total_amount: float
    order_status: Optional[str] = 'placed'
    payment_status: Optional[str] = 'pending'

class EPrescription(BaseModel):
    id: Optional[str]
    patient_email: str
    doctor_name: str
    medicines: List[Any]
    dosage: Optional[Any] = None
    instructions: Optional[str] = None
    issued_date: Optional[str] = None
    valid_until: Optional[str] = None

class Reminder(BaseModel):
    id: Optional[str]
    user_email: str
    medicine_name: str
    time: str
    start_date: str
    end_date: Optional[str] = None
    linked_prescription_id: Optional[str] = None

app = FastAPI(title='medAI2 API', version='0.1')

# Helper functions for storage fallback
def _read_local(table: str):
    path = os.path.join(DATA_DIR, f"{table}.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def _write_local(table: str, data):
    path = os.path.join(DATA_DIR, f"{table}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

# Generic getter
def fetch_table(table: str):
    if SUPABASE_AVAILABLE and supabase:
        try:
            resp = supabase.table(table).select('*').execute()
            return resp.data or []
        except Exception:
            pass
    return _read_local(table)

# Generic inserter
def insert_table_local(table: str, item: dict):
    items = _read_local(table)
    items.append(item)
    _write_local(table, items)
    return item

# Endpoints
@app.get('/health')
def health_check():
    return {'status': 'ok', 'supabase': SUPABASE_AVAILABLE}

@app.get('/products', response_model=List[Product])
def list_products():
    return fetch_table('pharmacy_products')

@app.post('/products', response_model=Product)
def create_product(p: Product):
    # For simplicity this endpoint writes locally if Supabase not available
    item = p.dict()
    if SUPABASE_AVAILABLE and supabase:
        try:
            supabase.table('pharmacy_products').insert(item).execute()
            return item
        except Exception:
            pass
    # fallback
    insert_table_local('pharmacy_products', item)
    return item

@app.get('/cart/{user_email}', response_model=List[CartItem])
def get_cart(user_email: str):
    items = fetch_table('pharmacy_cart')
    return [i for i in items if i.get('user_email') == user_email]

@app.post('/cart', response_model=CartItem)
def add_to_cart(item: CartItem):
    obj = item.dict()
    if SUPABASE_AVAILABLE and supabase:
        try:
            supabase.table('pharmacy_cart').insert(obj).execute()
            return obj
        except Exception:
            pass
    insert_table_local('pharmacy_cart', obj)
    return obj

@app.post('/orders', response_model=Order)
def create_order(order: Order):
    obj = order.dict()
    if SUPABASE_AVAILABLE and supabase:
        try:
            supabase.table('pharmacy_orders').insert(obj).execute()
            return obj
        except Exception:
            pass
    insert_table_local('pharmacy_orders', obj)
    return obj

@app.post('/e_prescriptions', response_model=EPrescription)
def create_prescription(ep: EPrescription):
    obj = ep.dict()
    if SUPABASE_AVAILABLE and supabase:
        try:
            supabase.table('e_prescriptions').insert(obj).execute()
            return obj
        except Exception:
            pass
    insert_table_local('e_prescriptions', obj)
    return obj

@app.get('/e_prescriptions/{user_email}', response_model=List[EPrescription])
def get_prescriptions(user_email: str):
    items = fetch_table('e_prescriptions')
    return [i for i in items if i.get('patient_email') == user_email]

@app.post('/medicine_reminders', response_model=Reminder)
def add_reminder(rem: Reminder):
    obj = rem.dict()
    if SUPABASE_AVAILABLE and supabase:
        try:
            supabase.table('medicine_reminders').insert(obj).execute()
            return obj
        except Exception:
            pass
    insert_table_local('medicine_reminders', obj)
    return obj

@app.get('/medicine_reminders/{user_email}', response_model=List[Reminder])
def get_reminders_api(user_email: str):
    items = fetch_table('medicine_reminders')
    return [i for i in items if i.get('user_email') == user_email]

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
