from datetime import datetime
import psycopg2
from fastapi import FastAPI, HTTPException
import hashlib
from validations.users import UserCreate, UserLogin, UserResetPassword, UserDeleteRequest
from utils.validation import is_strong_password
from db.connection import connect_db , create_users_table ,create_passwords_table
from my_app import app

@app.post("/signup")
async def create_account(user: UserCreate):
    username = user.username
    password = user.password

    if not is_strong_password(password):
        raise HTTPException(
            status_code = 400,
            detail = "Password must be atleast 8 characters long, contain an uppercase letter, a lower case letter , a digit and a special character"
        )
    hashed_password = hashlib.sha256(password.encode()).hexdigest() 
    created_at = datetime.now()

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users(username, password, created_at) VALUES(%s,%s,%s)",(username,hashed_password,created_at))
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Usernae alraedy exists.Please Choose another one.")
    finally:
        cursor.close()
        conn.close()

    return {"message": "Account Created Successfully!"}

@app.post("/login")
async def login(user: UserLogin):
    username = user.username
    password = user.password

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT password FROM users WHERE username = %s",(username,))
        result = cursor.fetchone()
        if result and result[0] == hashed_password:
            return {"message" : "Login Successful!" , "username" : username}
        else:
            raise HTTPException(status_code=401, detail="Invalid Username or password")
        
    finally:
        cursor.close()
        conn.close()

@app.post("/reset-password")
async def reset_password(user: UserResetPassword):
    username = user.username
    current_password = user.current_password
    new_password = user.new_password

    hashed_current_password = hashlib.sha256(current_password.encode()).hexdigest()

    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT password from users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code = 401, detail = "Username not found.")
        
        if result[0] != hashed_current_password:
            raise HTTPException(status_code = 401, detail = "Current Password is incorrect.")
        
        if not is_strong_password(new_password):
            raise HTTPException(
                status_code = 400,
                detail = "Password must be atleast 8 characters long, contain an uppercase letter, a lower case letter , a digit and a special character"
            )
        
        hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()

        cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_new_password,username))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    
    return {"message":"Password reset Successfully!"}

@app.post("/delete-account")
async def delete_account(user: UserDeleteRequest):
    username = user.username
    password = user.password

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code = 401, detail = "Username not found.")
        
        if result[0] != hashed_password:
            raise HTTPException(status_code = 401, detail = "Current Password is incorrect.")
        
        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
        conn.commit()

    finally:
        
        cursor.close()
        conn.close()

    return {"message" : " Your Account Deleted Successfully!"}