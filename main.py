from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.responses import Response, RedirectResponse
from hashlib import sha256
import http




app = FastAPI()
app.counter = 0
app.data = []
app.secret_key = "secret"
app.users = {"trudnY": "PaC13Nt"}
app.tokens = []

@app.get('/')
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}


@app.get('/welcome')
def welcome():
    return {"message": "Welcome to the server"}

@app.post('/method')
def method_post():
    return {"method": "POST"}


@app.get('/method')
def method_get():
    return {'method': "GET"}


@app.put('/method')
def method_put():
    return {'method': "PUT"}


@app.delete('/method')
def method_delate():
    return {"method": "DELETE"}


class Patient(BaseModel):
    name: str
    surename: str


def counter():
    app.counter += 1
    return (int(app.counter) - 1)

@app.post("/patient")
def make_item(item: Patient):
    tmp_json = jsonable_encoder(item)
    app.data.append(tmp_json)
    new_dict = {"id": counter(), "patient": tmp_json}
    json_compatible_item_data = jsonable_encoder(new_dict)
    return JSONResponse(content=json_compatible_item_data)


@app.get("/patient/{pk}")
def show_patient(pk: int):
    try:
        return app.data[pk]
    except:
        return Response(status_code=http.HTTPStatus.NO_CONTENT)


security = HTTPBasic


@app.get("/users/me")
def read_current_user(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username in app.users.keys() and app.users[credentials.username] == credentials.password:
        session_token = sha256(bytes(f"{credentials.username}{credentials.password}{app.secret_key}", encoding="utf8")).hexdigest()
        response.set_cookie(key="session_token", value=session_token)
        app.tokens += session_token
        response.set_cookie(key="session_token", value=session_token)
        response.headers["Location"] = "/welcome"
        response.status_code = status.HTTP_302_FOUND
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
