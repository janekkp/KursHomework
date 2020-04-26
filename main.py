from fastapi import FastAPI, Depends, HTTPException, status, Cookie, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse, RedirectResponse
from hashlib import sha256
import http




app = FastAPI()
app.counter = 0
app.data = []
app.secret = "secret"
app.users = {"trudnY": "PaC13Nt", "admin": "admin"}
app.tokens = []


@app.get('/')
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}



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


@app.get('/welcome')
def welcoming():
        return {"message": "Welcome to the server"}



@app.post("/login")
def loging(response: Response, credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    if credentials.username in app.users and app.users[credentials.username] == credentials.password:
        session_token = sha256(bytes(f"{credentials.username}{credentials.password}{app.secret}", encoding="utf8")).hexdigest()
        response.set_cookie(key="session_token", value=session_token)
        app.tokens.append(session_token)
        response.status_code = 302
        response.headers["Location"] = 'welcome'
        return response
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

