from fastapi import FastAPI,Query
from typing import Optional,List
from pydantic import BaseModel, Field
 
app = FastAPI()
 # ── Pydantic model 
class OrderRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2, max_length=100)
    product_id:       int = Field(..., gt=0)
    quantity:         int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)

class CustomerFeedback(BaseModel):
    customer_name: str=Field(...,min_length=2)
    product_id:    int=Field(...,gt=0)
    rating:        int=Field(...,gt=0,lt=6)
    comment:       Optional[str]=Field(default=None,max_length=300)

class OrderItem(BaseModel):
    product_id:  int=Field(...,gt=0)
    quantity: int=Field(...,gt=0,le=50)

class BulkOrder(BaseModel):
    company_name: str=Field(...,min_length=2)
    contact_email: str=Field(...,min_length=5)
    items: List[OrderItem]=Field(...,min_items=1)

# ── Temporary data — acting as our database for now ──────────
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499,  'category': 'Electronics', 'in_stock': True },
    {'id': 2, 'name': 'Notebook',       'price':  99,  'category': 'Stationery',  'in_stock': True },
    {'id': 3, 'name': 'USB Hub',         'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set',          'price':  49, 'category': 'Stationery',  'in_stock': True },
    {'id':5, 'name': 'Laptop Stand',     'price': 500,'category':'Electronics',  'in_stock': True},
    {'id':6, 'name': 'Mechanical Keyboard', 'price': 1000,  'category':'Electronics',  'in_stock': True},
    {'id':7, 'name': 'Webcam',             'price': 700,   'category':'Electronics',  'in_stock': True}
]
orders        = []
order_counter = 1
feedbacks=[]

# ══ HELPER FUNCTIONS ══════════════════════════════════════════════
 
def find_product(product_id: int):
    """Search products list by ID. Returns product dict or None."""
    for p in products:
        if p['id'] == product_id:
            return p
    return None
 
def calculate_total(product: dict, quantity: int) -> int:
    """Multiply price by quantity and return total."""
    return product['price'] * quantity
 
def filter_products_logic(category=None, min_price=None,
                          max_price=None, in_stock=None):
    """Apply filters and return matching products."""
    result = products
    if category  is not None:
        result = [p for p in result if p['category'] == category]
    if min_price is not None:
        result = [p for p in result if p['price'] >= min_price]
    if max_price is not None:
        result = [p for p in result if p['price'] <= max_price]
    if in_stock  is not None:
        result = [p for p in result if p['in_stock'] == in_stock]
    return result
 
# ── Endpoint 0 — Home ────────────────────────────────────────
@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}
 
# ── Endpoint 1 — Return all products ──────────────────────────
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}

@app.get('/products/filter')
def filter_products(
    category:  str  = Query(None, description='Electronics or Stationery'),
    max_price: int  = Query(None, description='Maximum price'),
    in_stock:  bool = Query(None, description='True = in stock only'),
    min_price: int =  Query(None, description='Minimum price')
):
    result = filter_products_logic(category, min_price, max_price, in_stock)
    return {'filtered_products': result, 'count': len(result)}

# ── Day 3: Compare (fixed route — must stay BEFORE /{product_id}) ─
 
@app.get('/products/compare')
def compare_products(
    product_id_1: int = Query(..., description='First product ID'),
    product_id_2: int = Query(..., description='Second product ID'),
):
    p1 = find_product(product_id_1)
    p2 = find_product(product_id_2)
    if not p1:
        return {'error': f'Product {product_id_1} not found'}
    if not p2:
        return {'error': f'Product {product_id_2} not found'}
    cheaper = p1 if p1['price'] < p2['price'] else p2
    return {
        'product_1':    p1,
        'product_2':    p2,
        'better_value': cheaper['name'],
        'price_diff':   abs(p1['price'] - p2['price']),
    }

# End Point- get Products based on availability
@app.get('/products/in_stock')
def get_by_stock(): 
    result=[p for p in products if p['in_stock']==True]
    return {"in_stock_products":result,"count":len(result)}


#End Point -get best and premium deals
@app.get('/products/deals')
def get_deals():
    best_deal=min(products,key=lambda x:x['price'])
    pre_deal=max(products,key=lambda x:x['price'])
    return {"best_deal":best_deal,"premium_pick":pre_deal}

#End point to get store summery
@app.get('/products/summery')
def get_producct_summery():
    prod_count=len(products)
    no_instock=len([p for p in products if p['in_stock']==True])
    no_outofstock=prod_count-no_instock
    category_list=set(p['category'] for p in products)
    most_expensive=max(products,key=lambda x:x['price'])
    cheapest=min(products,key=lambda x:x['price'])
    return {"total_products":prod_count , "in_stock_count": no_instock, "out_of_stock_count": no_outofstock,"most_expensive":{"name":most_expensive['name'],"price":most_expensive['price']},"cheapest":{"name":cheapest['name'],"price":cheapest['price']},"categories": category_list }


# ── Endpoint 2 — Return one product by its ID ──────────────────
@app.get('/products/{product_id}')
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {'product': product}
    return {'error': 'Product not found'}

#Endpoint to get name,price of product
@app.get('/products/{product_id}/price')
def get_price(product_id:int):
    for product in products:
        if product['id']==product_id:
            return {"Name":product['name'],"Price":product['price']}
    return {"error":"Product not found"}
    


#-- Endpoint - Return products by category
@app.get('/products/category/{category_name}')
def get_category(category_name: str):
    result=[p for p in products if p['category']==category_name]
    return (({"products":result},{"total":len(result)}) if result else {"erorr": "No products found in these category"})


#endpoint to get order summery
@app.get('/store/summery')
def get_store_summery():
    prod_count=len(products)
    no_instock=len([p for p in products if p['in_stock']==True])
    no_outofstock=prod_count-no_instock
    category_list=set(p['category'] for p in products)
    return {"store_name": "My E-commerce Store","total_products":prod_count , "in_stock": no_instock, "out_of_stock": no_outofstock, "categories": category_list }


#End point to get products by name
@app.get('/products/search/{keyword}')
def get_prod_byname(keyword: str):
    product=[p for p in products if keyword.lower() in p['name'].lower()]
    return ({"products":product,"count":len(product)} if product else {"error":"No product matched your search"})

@app.post('/orders')
def place_order(order_data: OrderRequest):
    global order_counter
 
    product = find_product(order_data.product_id)
    if not product:
        return {'error': 'Product not found'}
 
    if not product['in_stock']:
        return {'error': f"{product['name']} is out of stock"}
 
    total = calculate_total(product, order_data.quantity)
 
    order = {
        'order_id':         order_counter,
        'customer_name':    order_data.customer_name,
        'product':          product['name'],
        'quantity':         order_data.quantity,
        'delivery_address': order_data.delivery_address,
        'total_price':      total,
        'status':           'pending',
    }
    orders.append(order)
    order_counter = order_counter + 1
    return {'message': 'Order placed successfully', 'order': order}
 
@app.get('/orders')
def get_all_orders():
    return {'orders': orders, 'total_orders': len(orders)}

#Endpoint for feedback posting
@app.post('/feedback')
def feedback_post(feedback_info: CustomerFeedback):
    feedback={
        "customer_name":feedback_info.customer_name,
        "product_id":feedback_info.product_id,
        "rating":feedback_info.rating,
        "comment":feedback_info.comment
    }
    feedbacks.append(feedback)
    return {"messege":"Feedback submited successfully","feedback":feedback}


#endpoint for bulk order palcement
@app.post('/orders/bulk')
def place_bulk_order(order:BulkOrder):
    confirmed,failed,grand_total=[],[],0
    for item in order.items:
        product=next((p for p in products if p['id']==item.product_id),None)
        if not product:
            failed.append({"product_id":item.product_id,"reason":"Product not found"})
        elif not product["in_stock"]:
            failed.append({"propduct_id":item.product_id,"reason":f"{product['name']} is out of stock"})
        else:
            subtotal=product['price']*item.quantity
            grand_total+=subtotal
            confirmed.append({"product_id":item.product_id,"quantity":item.quantity,"subtotal":subtotal})
    return {"company": order.company_name, "confirmed": confirmed,
            "failed": failed, "grand_total": grand_total}

#Endpoint for getting order with order id
@app.get('/orders/{order_id}')
def get_orders(order_id: int):
    for order in orders:
        if order['order_id']==order_id:
            return {"oeder":order}
    return {"error":"order not found"}

@app.patch('/orders/{order_id}/confirm')
def confirm_order(order_id:int):
    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "confirmed"
            return {"message": "Order confirmed", "order": order}
    return {"error": "Order not found"}

