from fastapi import Depends,FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import Product
from database import session,engine
import database_models
from sqlalchemy.orm import Session

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"]
)

database_models.Base.metadata.create_all(bind=engine)

@app.get("/")
def greet():
    return "Welcome"

products=[
    Product(id=1,name="Laptop",description="Gaming Laptop",price=999,quantity=5),
    Product(id=2,name="Mac",description="Mac Laptop",price=1999,quantity=6)
]
def getDb():
    db=session()
    try:
        yield db
    finally:
        db.close()


def initDb():
    db=session()
    count=db.query(database_models.Product).count
    if count == 0:
        for product in products:
            db.add(database_models.Product(**product.model_dump()))
        db.commit()

initDb()

@app.get("/products")
def getAllProducts(db:Session=Depends(getDb)):
    db_products=db.query(database_models.Product).all()
    return db_products

@app.get("/products/{id}")
def getProductByID(id:int,db:Session=Depends(getDb)):
    db_product=db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        return db_product
    return "Product not found"

@app.post("/products")
def addProduct(product: Product,db:Session=Depends(getDb)):
    db.add(database_models.Product(**product.model_dump()))
    db.commit()
    return product



@app.put("/products/{id}")
def updateProduct(id:int, product:Product,db:Session=Depends(getDb)):
    db_product=db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db_product.name=product.name
        db_product.description=product.description
        db_product.price=product.price
        db_product.quantity=product.quantity
        db.commit()
        return "Product Updated"
    else:    
        return "No product Found"


@app.delete("/products/{id}")
def deleteProduct(id:int,db:Session=Depends(getDb)):
    db_product=db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return "Product Deleted"
    else:
        return "Product not found"