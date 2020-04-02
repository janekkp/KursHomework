from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}
