from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


app = FastAPI()
app.counter = 0


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
    return int(app.counter)

@app.post("/items")
def make_item(item: Patient):
    tmp_json = jsonable_encoder(item)
    new_dict = {"id": counter(), "patient": tmp_json}
    json_compatible_item_data = jsonable_encoder(new_dict)
    return JSONResponse(content=json_compatible_item_data)

