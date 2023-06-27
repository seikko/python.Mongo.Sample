from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from pymongo import MongoClient
from typing import List
from fastapi.responses import JSONResponse

from user import User
from settings import get_connection_string

app = FastAPI()
client = MongoClient(get_connection_string())
db = client['mydatabase']
collection = db['users']

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="User API",
        version="1.0",
        routes=app.routes,
    )
    app.openapi = custom_openapi
    app.openapi_schema = openapi_schema
    return app.openapi_schema


@app.post("/users", response_model=User, status_code=201)
async def create_user(user: User):
    if user is None:
        return JSONResponse(status_code=400, content={"message": "Invalid user data"})
    inserted_user = collection.insert_one(user.dict())
    user.id = str(inserted_user.inserted_id)
    
    return user

@app.get("/users", response_model=List[User])
async def get_users():
    users = []
    for user_data in collection.find():
        user = User(**user_data)
        users.append(user)
    return users
   
if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True, debug=True)

