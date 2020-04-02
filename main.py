from fastapi import FastAPI

app = FastAPI()


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
