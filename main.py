import io
import json
import sys
from typing import List
import requests
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import time


class User:
    Id: int
    Username: str
    Password: str
    Uuid: str
    Level: int

    def __init__(self, id, username, password):
        self.Id = id
        self.Username = username
        self.Password = password


class UpdateUser(BaseModel):
    Password: str


global logged_in_user_admin
logged_in_user_admin = False
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


def checkAdmin(username: str, password: str):
    data = {'Username': username, 'Password': password}
    response = requests.post("http://127.0.0.1:8000/login", json=data)
    if response.status_code == 200:
        res1 = json.loads(response.text)
    response = requests.get("http://127.0.0.1:8000/user/admin")
    res2 = json.loads(response.text)
    if res2["Id"] == res1:
        global admin_id
        admin_id = res1
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
    global logged_in_user_admin
    while True:
        if logged_in_user and not logged_in_user_admin:
            print("1. Change Password")
            print("2. Delete User")
            print("3. Logout")
            print("4. Exit")
        elif logged_in_user_admin and logged_in_user:
            print("1. Change Password")
            print("2. Delete Users")
            print("3. Logout")
            print("4. Exit")
        else:
            print("1. Signup")
            print("2. Login")
            print("3. Exit")
        choice = input("Choose an option: ")

        if choice == "1" and not logged_in_user:
            username = input("Enter username: ")
            password = input("Enter password: ")

            successful = addUser(username, password)
            if successful:
                print("User registered successfully")
            else:
                print("Wrong Input/Username already exists!")

        elif choice == "2" and not logged_in_user:
            username = input("Enter username: ")
            password = input("Enter password: ")

            successful = checkUser(username, password)
            if successful:
                print("Logged in")
                if checkAdmin(username, password):
                    logged_in_user_admin = True
            else:
                print("Wrong Input/User not found")

        elif choice == "1" and logged_in_user:
            new_password = input("Enter new password: ")
            successful = updatePassword(logged_in_user.Id, new_password)
            if successful:
                print("Password updated!")
            else:
                print("Wrong Input/Password is the same")

        elif choice == "2" and logged_in_user and not logged_in_user_admin:
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

        elif choice == "2" and logged_in_user and logged_in_user_admin:
            response = requests.get("http://127.0.0.1:8000/user")
            res = json.loads(response.text)
            for i in res:
                print(str(i["Id"]) + ". " + i["Username"])
                y = i["Id"]
            x = input("Which user do you want to delete?\n")
            if x == "":
                print("Wrong input!")
            else:
                try:
                    x = int(x)
                except ValueError:
                    x = sys.maxsize
                if x > int(y):
                    print("Wrong Input!")
                elif x == admin_id:
                    print("You cant delete an Admin Account!")
                else:
                    successful = deleteUser(x)
                    if successful:
                        print("User deleted!")
                    else:
                        print("Error!")

        elif choice == "3" and logged_in_user:
            logged_in_user_admin = False
            logged_in_user = None
            print("Logged out successfully")

        elif choice == "3" and not logged_in_user or choice == "4" and logged_in_user:
            break

        else:
            print("Invalid option")


main()
