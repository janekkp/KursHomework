from fastapi import FastAPI, Depends, HTTPException, status, Cookie, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.responses import Response
from hashlib import sha256
import sqlite3
import json

app = FastAPI()
app.counter = 0
app.patients = {}
app.secret = "secret"
app.users = {"trudnY": "PaC13Nt", "admin": "admin"}
app.session_tokens = []


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
def method_delete():
    return {"method": "DELETE"}


class Patient(BaseModel):
    name: str
    surname: str


def counter():
    app.counter += 1
    return int(app.counter) - 1


# @app.post("/patient")
# def make_item(item: Patient):
#     tmp_json = jsonable_encoder(item)
#     app.data.append(tmp_json)
#     new_dict = {"id": counter(), "patient": tmp_json}
#     json_compatible_item_data = jsonable_encoder(new_dict)
#     return JSONResponse(content=json_compatible_item_data)


@app.post('/patient')
def add_patient(response: Response, patient: Patient, session_token: str = Cookie(None)):
    if session_token not in app.session_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    id = counter()
    app.patients[id] = patient.dict()
    response.set_cookie(key="session_token", value=session_token)
    response.status_code = 302
    response.headers["Location"] = f'/patient/{id}'


@app.get('/patient')
def patients(session_token: str = Cookie(None)):
    if session_token not in app.session_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return app.patients


@app.get("/patient/{id}")
def show_patient(id: int, response: Response, session_token: str = Cookie(None)):
    if session_token not in app.session_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    response.set_cookie(key="session_token", value=session_token)
    if id in app.patients.keys():
        return app.patients[id]
    return status.HTTP_204_NO_CONTENT


@app.delete('/patient/{id}')
def delete_patient(id: int, response: Response, session_token: str = Cookie(None)):
    if session_token not in app.session_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    app.patients.pop(id, None)
    response.status_code = status.HTTP_204_NO_CONTENT


templates = Jinja2Templates(directory="templates")


@app.get('/welcome')
def welcoming(request: Request, session_token: str = Cookie(None)):
    if session_token not in app.session_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return templates.TemplateResponse("item.html", {"request": request, "user": "trudnY"})


@app.post("/login")
def login(response: Response, credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    if credentials.username in app.users and app.users[credentials.username] == credentials.password:
        session_token = sha256(
            bytes(f"{credentials.username}{credentials.password}{app.secret}", encoding="utf8")).hexdigest()
        response.set_cookie(key="session_token", value=session_token)
        app.session_tokens.append(session_token)
        response.status_code = 302
        response.headers["Location"] = '/welcome'
        print(session_token)
        return response
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@app.post("/logout")
def logout(response: Response, session_token: str = Cookie(None)):
    if session_token not in app.session_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    response.status_code = 302
    response.headers["Location"] = '/'
    app.session_tokens.remove(session_token)
    return response


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect('chinook.db')


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/tracks")
async def show_tracks(page: int = 0, per_page: int = 10):
    app.db_connection.row_factory = sqlite3.Row
    tracks = app.db_connection.execute('''SELECT * FROM tracks ORDER BY TrackID LIMIT ? OFFSET ?''',
                                       (per_page, per_page * page)).fetchall()
    return tracks


@app.get('/tracks/composers/')
async def show_composer(composer_name: str):
    app.db_connection.row_factory = lambda cur, x:x[0]
    titles = app.db_connection.execute(''' SELECT name FROM tracks WHERE composer = ? ORDER BY name''',
                                       (composer_name,)).fetchall()
    if len(titles) == 0:
        raise HTTPException(status_code=404, detail={"error": "Composer not found"})
    return titles


class Album(BaseModel):
    title: str
    artist_id: int


@app.post('/albums')
async def add_album(response:Response, album: Album):
    cursor = app.db_connection.execute('''SELECT ArtistId FROM artists WHERE ArtistId = "artist_id"''',
                                       {'artist_id': album.artist_id})
    artist = cursor.fetchall()
    if len(artist) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail":{"error:" "No artist"}}
    cursor = app.db_connection.execute('''INSERT INTO albums (Title, ArtistId)  VALUES (:title, :artist_id)''',
                                             {'artist_id': album.artist_id, 'title': album.title})
    app.db_connection.commit()
    response.status_code = 201
    return {"AlbumId": cursor.lastrowid, "Title": album.title, "ArtistId": album.artist_id}



@app.get("/albums/{album_id}")
async def check_album(album_id: int):
    app.db_connection.row_factory = sqlite3.Row
    curosr = app.db_connection.execute("SELECT * FROM albums WHERE AlbumId = :album_id",
        {'album_id': album_id})
    album = curosr.fetchone()
    # if album is None:
    #     raise HTTPException(status_code=404, detail={"error:" "No album"})
    return album


@app.put('/customers/{customer_id}')
async def edit_customer_data(customer_id: int, customer_update_data: dict):
    cursor = app.db_connection.execute(
        "SELECT CustomerId FROM customers WHERE CustomerId = ?", (customer_id,)
    )
    result = cursor.fetchone()
    if result is None:
        raise HTTPException(
            status_code=404, detail={"error": "Customer with given ID does not exist."}
        )
    list_of_possible_fields_to_update = (
        "company",
        "address",
        "city",
        "state",
        "country",
        "postalcode",
        "fax",
    )
    fields_to_update = []

    for key, val in customer_update_data.items():
        if key in list_of_possible_fields_to_update:
            fields_to_update.append(f"{key}='{val}'")

    update_values = ", ".join(fields_to_update)
    sql_stmt = f"UPDATE customers SET {update_values} WHERE customerid={customer_id}"
    cursor = app.db_connection.execute(sql_stmt)
    app.db_connection.commit()

    app.db_connection.row_factory = sqlite3.Row
    cursor = app.db_connection.execute(
        "SELECT * FROM customers WHERE CustomerId = ?", (customer_id,)
    )
    customer = cursor.fetchone()
    return customer