from PydanticFile import addPasswordRequest, retrievePassword, updatePassword, deletePassword,viewServices
from db import connect_db,create_passwords_table
import hashlib, psycopg2
from fastapi import FastAPI, HTTPException
from cryptography.fernet import Fernet


app = FastAPI()
create_passwords_table()

def encrypt_password(plain_text, key):
    fernet = Fernet(key)
    return fernet.encrypt(plain_text.encode()).decode()

def decrypt_password(encrypted_password: str, key: str) -> str:
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_password.encode()).decode()

@app.post("/add-password")
async def add_password(user: addPasswordRequest):
    username = user.username
    password = user.password
    service = user.service
    service_password = user.service_password

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=401, detail="Username not found.")
        
        user_id, stored_hashed_password = result

        if stored_hashed_password != hashed_password:
            raise HTTPException(status_code=401, detail="Incorrect Password.")
        
        # Encrypt the service password before storing
        key = hashlib.sha256(username.encode()).digest()
        encrypted_password = encrypt_password(service_password, key)
        
        cursor.execute(
            "INSERT INTO passwords (user_id, services, password) VALUES (%s, %s, %s)",
            (user_id, service, encrypted_password),
        )
        conn.commit()

    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Password for this service already exists.")

    finally:
        cursor.close()
        conn.close()

    return {"message": "Password added successfully for the service!"}

@app.post("/retrieve-password")
async def retrieve_password(user: retrievePassword):
    username = user.username
    password = user.password
    service = user.service

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Verify username and password
        cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=401, detail="Username not found.")

        user_id, stored_hashed_password = result

        if stored_hashed_password != hashed_password:
            raise HTTPException(status_code=401, detail="Incorrect Password.")

        # Fetch the encrypted service password for the given service
        cursor.execute(
            "SELECT password FROM passwords WHERE user_id = %s AND services = %s",
            (user_id, service),
        )
        service_password = cursor.fetchone()

        if not service_password:
            raise HTTPException(
                status_code=404, detail=f"No password found for the service '{service}'."
            )

        # Decrypt the password
        try:
            key = hashlib.sha256(username.encode()).digest()  # Derive the encryption key
            decrypted_password = decrypt_password(service_password[0], key)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to decrypt password: {str(e)}")

    finally:
        cursor.close()
        conn.close()

    return {"service": service, "password": decrypted_password}

@app.put("/update-password")
async def update_password(request: updatePassword):
    username = request.username
    password = request.password
    service = request.service
    new_service_password = request.new_service_password

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Verify username and password
        cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=401, detail="Username not found.")

        user_id, stored_hashed_password = result

        if stored_hashed_password != hashed_password:
            raise HTTPException(status_code=401, detail="Incorrect Password.")

        # Check if the service exists for the user
        cursor.execute(
            "SELECT password FROM passwords WHERE user_id = %s AND services = %s",
            (user_id, service),
        )
        service_password = cursor.fetchone()

        if not service_password:
            raise HTTPException(
                status_code=404, detail=f"No password found for the service '{service}'."
            )

        # Encrypt the new password before updating
        try:
            key = hashlib.sha256(username.encode()).digest()  # Derive encryption key
            encrypted_password = encrypt_password(new_service_password, key)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to encrypt the new password: {str(e)}"
            )

        # Update the password in the database
        cursor.execute(
            "UPDATE passwords SET password = %s WHERE user_id = %s AND services = %s",
            (encrypted_password, user_id, service),
        )
        conn.commit()

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    finally:
        cursor.close()
        conn.close()

    return {"message": f"Password for service '{service}' updated successfully!"}

@app.delete("/delete-password")
async def delete_password(request: deletePassword):
    username = request.username
    password = request.password
    service = request.service

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Verify username and password
        cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=401, detail="Username not found.")

        user_id, stored_hashed_password = result

        if stored_hashed_password != hashed_password:
            raise HTTPException(status_code=401, detail="Incorrect Password.")

        # Check if the service exists for the user
        cursor.execute(
            "SELECT id FROM passwords WHERE user_id = %s AND services = %s",
            (user_id, service),
        )
        service_entry = cursor.fetchone()

        if not service_entry:
            raise HTTPException(
                status_code=404, detail=f"No password found for the service '{service}'."
            )

        # Delete the password for the specified service
        cursor.execute(
            "DELETE FROM passwords WHERE id = %s", (service_entry[0],)
        )
        conn.commit()

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    finally:
        cursor.close()
        conn.close()

    return {"message": f"Password for service '{service}' deleted successfully!"}

@app.get("/view-all-services")
async def view_all_services(request: viewServices):
    username = request.username
    password = request.password

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Verify username and password
        cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=401, detail="Username not found.")

        user_id, stored_hashed_password = result

        if stored_hashed_password != hashed_password:
            raise HTTPException(status_code=401, detail="Incorrect Password.")

        # Fetch all services for the user
        cursor.execute("SELECT services FROM passwords WHERE user_id = %s", (user_id,))
        services = cursor.fetchall()

        if not services:
            return {"message": "No services found for this user."}

        # Extract the list of services from the query results
        services_list = [service[0] for service in services]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    finally:
        cursor.close()
        conn.close()

    return {"services": services_list}
