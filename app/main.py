from fastapi import FastAPI
from app.routes import authRoutes, org_routes

app=FastAPI()


app.include_router(authRoutes.router)
app.include_router(org_routes.router)

@app.get("/")
def root():
    return {"message":"home page"}