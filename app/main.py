from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import shutil
import bcrypt

app = FastAPI()

##################
# Upload Endpoints
##################

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("index.html", "r") as f:
        return f.read()

#Creates a new endpoint that accepts POST requests at the path "/upload/".
@app.post("/upload/")
def upload_file(file: UploadFile = File(...)):
    #Define where the file will be saved
    file_location = f"uploads/{file.filename}" #Saves inside the 'uploads/' folder using its original filename

    #Open a buffer and save the upload file to the local directory
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename}

#GET endpoint that uses a path parameter {filename}
#allowing the server to accept any filename provided in the URL
@app.get("/files/{filename}") 
def get_file(filename: str):
    #This function locates the file within the 'uploads/' directory and serves it so it can be 
    #downloaded or played directly in the browser
    return FileResponse(path=f"uploads/{filename}", filename=filename)


###################
# User Security Features
###################

users = {}

# POST endpoint for user registration that accepts a username and password as form data
@app.post("/register/")
def register(username: str, password: str):
    if username in users:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    #Hash the password using bcrypt: encode it first, then us a salt to generate a secure hash
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    #Store the username and hashed password in the users dictionary
    #NOT the plaintext
    users[username] = hashed_password
    return {"message": "User registered successfully"}

# POST endpoint for user login that accepts a username and password as form data
@app.post("/login/")
def login(username: str, password: str):
    if username not in users:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    #Check if the provided password matches the stored hashed password using bcrypt's checkpw function
    if bcrypt.checkpw(password.encode(), users[username]):
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")