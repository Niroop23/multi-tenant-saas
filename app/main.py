from fastapi import FastAPI
from app.routes import authRoutes, org_routes,inviteRoutes

app=FastAPI()


app.include_router(authRoutes.router)
app.include_router(org_routes.router)
app.include_router(inviteRoutes.router)

@app.get("/")
def root():
    return {"message":"home page"}