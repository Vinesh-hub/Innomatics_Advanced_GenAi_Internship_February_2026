from fastapi import FastAPI,Query
 
app = FastAPI()
 
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
    in_stock:  bool = Query(None, description='True = in stock only')
):
    result = products          # start with all products
 
    if category:
        result = [p for p in result if p['category'] == category]
 
    if max_price:
        result = [p for p in result if p['price'] <= max_price]
 
    if in_stock is not None:
        result = [p for p in result if p['in_stock'] == in_stock]
 
    return {'filtered_products': result, 'count': len(result)}
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
# ── Endpoint 2 — Return one product by its ID ──────────────────
@app.get('/products/{product_id}')
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {'product': product}
    return {'error': 'Product not found'}
#-- Endpoint - Return products by category
@app.get('/products/category/{category_name}')
def get_category(category_name: str):
    result=[p for p in products if p['category']==category_name]
    return (({"products":result},{"total":len(result)}) if result else {"erorr": "No products found in these category"})
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
