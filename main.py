import io
import json
from typing import List
import requests
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import time


class User:
    Id: int
    Username: str
    Password: str

    def __init__(self, id, username, password):
        self.Id = id
        self.Username = username
        self.Password = password


class UpdateUser(BaseModel):
    Password: str


global logged_in_user
logged_in_user = None


def getUsers():
    try:
        response = requests.get("http://127.0.0.1:8000/user")
        res = json.loads(response.text)
    except FileNotFoundError:
        res = []

    users: List[User] = []
    for entry in res:
        users.append(User(entry["Id"], entry["Username"], entry["Password"]))

    return users


def checkUser(username: str, password: str):
    data = {'Username': username, 'Password': password}
    response = requests.post("http://127.0.0.1:8000/login", json=data)
    if response.status_code == 200:
        res = json.loads(response.text)
        global logged_in_user
        logged_in_user = User(res, "", "")
        return True
    else:
        return False


def addUser(username: str, password: str):
    if username == "" or password == "":
        return False
    else:
        data = {'Username': username, 'Password': password}
        response = requests.post("http://127.0.0.1:8000/user", json=data)
        return response.status_code == 200


def updatePassword(user_id: int, password: str):
    if password == "":
        return False
    else:
        data = {'Password': password}
        response = requests.put("http://127.0.0.1:8000/user/" + str(user_id), json=data)
        if response.status_code == 200:
            return True
        else:
            return False


def deleteUser(user_id: int):
    response = requests.delete("http://127.0.0.1:8000/user/" + str(user_id))
    if response.status_code == 200:
        return True
    else:
        return False


def writeUsersToJson(users):
    json_compatible_item_data = jsonable_encoder(users)
    with io.open('data.txt', 'w', encoding='utf-8') as f:
        f.write(str(json_compatible_item_data).replace("'", '"'))

    return json_compatible_item_data


def main():
    global logged_in_user
    while True:
        if logged_in_user:
            print("1. Change Password")
            print("2. Delete User")
            print("3. Logout")
            print("4. Exit")
        else:
            print("1. Signup")
            print("2. Login")
            print("3. Exit")
        choice = input("Choose an option: ")
        time.sleep(1)

        if choice == "1" and not logged_in_user:
            username = input("Enter username: ")
            password = input("Enter password: ")

            successful = addUser(username, password)
            if successful:
                print("User registered successfully")
            else:
                print("Wrong Input/Username already exists!")
            time.sleep(1)

        elif choice == "2" and not logged_in_user:
            username = input("Enter username: ")
            password = input("Enter password: ")

            successful = checkUser(username, password)
            if successful:
                print("Logged in")
            else:
                print("Wrong Input/User not found")
            time.sleep(1)

        elif choice == "1" and logged_in_user:
            new_password = input("Enter new password: ")
            successful = updatePassword(logged_in_user.Id, new_password)
            if successful:
                print("Password updated!")
            else:
                print("Wrong Input/Password is the same")
            time.sleep(1)

        elif choice == "2" and logged_in_user:
            print("Are you sure that you want to delete your User? (y/n)")
            x = input()
            if x == "y":
                successful = deleteUser(logged_in_user.Id)
                if successful:
                    print("User deleted!")
                    logged_in_user = None
                else:
                    print("Error!")
            else:
                print("User not deleted")
            time.sleep(1)

        elif choice == "3" and logged_in_user:
            logged_in_user = None
            print("Logged out successfully")
            time.sleep(1)

        elif choice == "3" and not logged_in_user or choice == "4" and logged_in_user:
            break

        else:
            print("Invalid option")
            time.sleep(1)


main()
