from bottle import run, request, template, redirect
import bottle
from pymongo import MongoClient
import requests
import urllib.parse
import geopy.distance


mongo_client = MongoClient("mongo")
db = mongo_client["Personal"]
master_collection = db["Master"]
store_collection = db["Stores"]


@bottle.route("/")
def index():
    return bottle.static_file("index.html", ".")


@bottle.route("/style.css")
def index():
    return bottle.static_file("style.css", ".")


@bottle.post("/find-store")
def index():
    userStreet = request.forms['InputStreet']
    userZip = request.forms['InputZip']
    userCity = request.forms['InputCity']
    userState = request.forms['InputState']
    address = f'{userStreet}, {userCity}, {userState} {userZip}'
    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) + '?format=json'
    response = requests.get(url).json()
    lat = 0
    lon = 0
    try:
        lat = response[0]["lat"]
        lon = response[0]["lon"]
    except IndexError as p:
        errorMessage = "Invalid Address! Please try again."
        redirectLink = "/finder"
        return template("errorPage.html", errorInsert=errorMessage, redirectInsert=redirectLink)
    listLength = 0
    storesInArea = []
    if store_collection.find({"store-zip": userZip, "store-icecream": "Yes"}, {"Lat": 1, "Lon": 1}):
        storeSearch = store_collection.find({"store-zip": userZip, "store-icecream": "Yes"}, {"Lat": 1, "Lon": 1})
        storesInArea = []
        for store in storeSearch:
            storesInArea.append(store)
        listLength = len(storesInArea)
    if listLength == 0:
        if store_collection.find({"store-city": userCity, "store-icecream": "Yes"}, {"Lat": 1, "Lon": 1}):
            storeSearch = store_collection.find({"store-city": userCity, "store-icecream": "Yes"}, {"Lat": 1, "Lon": 1})
            storesInArea = []
            for store in storeSearch:
                storesInArea.append(store)
                listLength = len(storesInArea)
    if listLength == 0:
        if store_collection.find({"store-state": userState, "store-icecream": "Yes"}, {"Lat": 1, "Lon": 1}):
            storeSearch = store_collection.find({"store-state": userState, "store-icecream": "Yes"}, {"Lat": 1, "Lon": 1})
            storesInArea = []
            for store in storeSearch:
                storesInArea.append(store)
            listLength = len(storesInArea)
    if listLength == 0:
        errorMessage = 'There are no nearby stores :('
        redirectLink = '/finder'
        return template("errorPage.html", errorInsert=errorMessage, redirectInsert=redirectLink)
    closestDistance = 1000000000000000
    closestLat = 0.0
    closestLon = 0.0
    for store in storesInArea:
        storeCoords = (float(store["Lat"]), float(store["Lon"]))
        userCoords = (lat, lon)
        distance = geopy.distance.geodesic(storeCoords, userCoords).km
        if distance < closestDistance:
            closestLat = float(store['Lat'])
            closestLon = float(store["Lon"])
            closestDistance = distance
    if closestLat == 0.0 and closestLon == 0.0:
        errorMessage = 'There are no nearby stores :('
        redirectLink = '/finder'
        return template("errorPage.html", errorInsert=errorMessage, redirectInsert=redirectLink)
    url = "https://maps.google.com/maps?t=m&q=loc:" + str(closestLat) + "+" + str(closestLon)
    return redirect(url)


@bottle.route("/finder")
def index():
    return bottle.static_file("finder.html", ".")


@bottle.post("/remove-store")
def index():
    username = request.forms['StoreUsername']
    password = request.forms['password']
    loginAttempt = {"username": username, "password": password}
    if not master_collection.find_one(loginAttempt):
        errorMessage = 'Password is incorrect. Please sign in again for security purposes.'
        redirectLink = '/'
        return template("errorPage.html", errorInsert=errorMessage, redirectInsert=redirectLink)
    storeName = request.forms['StoreName']
    storeIcecream = request.forms['IceCream']
    storeStreet = request.forms['StoreStreet']
    storeZip = request.forms['StoreZip']
    storeCity = request.forms['StoreCity']
    storeState = request.forms['StoreState']
    storeInsert = {"store-owner": username,
                   "store-icecream": storeIcecream,
                   "store-name": storeName,
                   "store-street": storeStreet,
                   "store-zip": storeZip,
                   "store-city": storeCity,
                   "store-state": storeState
                   }
    if not username or not storeName or not storeStreet or not storeZip or not storeCity or not storeState:
        errorMessage = "Please fill out all boxes before submitting! Please sign-in again for security purposes."
        redirectLink = "/"
        return template("errorPage.html", errorInsert=errorMessage, redirectInsert=redirectLink)
    if storeState == "Select a State":
        errorMessage = "Please choose a valid state! Please sign-in again for security purposes."
        redirectLink = "/"
        return template("errorPage.html", errorInsert=errorMessage, redirectInsert=redirectLink)
    if not store_collection.find_one(storeInsert):
        errorMessage = "Store targeted for deletion was not found in the database! Please sign-in again for security purposes."
        redirectLink = "/"
        return template("errorPage.html", errorInsert=errorMessage, redirectInsert=redirectLink)
    store_collection.delete_one(storeInsert)
    errorMessage = "Store successfully removed from database! Please sign-in again for security purposes."
    redirectLink = "/"
    return template("errorPage.html", errorInsert=errorMessage, redirectInsert=redirectLink)


@bottle.post("/add-store")
def index():
    username = request.forms['StoreUsername']
    password = request.forms['password']
    loginAttempt = {"username": username, "password": password}
    if not master_collection.find_one(loginAttempt):
        errorMessage = 'Password is incorrect. Please sign in again for security purposes.'
        redirectLink = '/'
        return template("errorPage.html", errorInsert=errorMessage, redirectInsert=redirectLink)
    storeName = request.forms['StoreName']
    storeIcecream = request.forms['IceCream']
    storeStreet = request.forms['StoreStreet']
    storeZip = request.forms['StoreZip']
    storeCity = request.forms['StoreCity']
    storeState = request.forms['StoreState']
    storeInsert = {"store-owner": username,
                   "store-icecream": storeIcecream,
                   "store-name": storeName,
                   "store-street": storeStreet,
                   "store-zip": storeZip,
                   "store-city": storeCity,
                   "store-state": storeState
                   }
    if not username or not storeName or not storeStreet or not storeZip or not storeCity or not storeState:
        errorMessage = "Please fill out all boxes before submitting! Please sign-in again for security purposes."
        redirectLink = "/"
        return template("errorPage.html", errorInsert=errorMessage, redirectInsert=redirectLink)
    if storeState == "Select a State":
        errorMessage = "Please choose a valid state! Please sign-in again for security purposes."
        redirectLink = "/"
        return template("errorPage.html", errorInsert=errorMessage, redirectInsert=redirectLink)
    if store_collection.find_one(storeInsert):
        errorMessage = "This store is already in the database! Please sign-in again for security purposes."
        redirectLink = "/"
        return template("errorPage.html", errorInsert=errorMessage, redirectInsert=redirectLink)
    address = f'{storeStreet}, {storeCity}, {storeState} {storeZip}'
    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) + '?format=json'
    response = requests.get(url).json()
    lat = 0.0
    lon = 0.0
    try:
        lat = response[0]["lat"]
        lon = response[0]["lon"]
    except IndexError as p:
        errorMessage = "Invalid Address! Please sign-in again for security purposes."
        redirectLink = "/"
        return template("errorPage.html", errorInsert=errorMessage, redirectInsert=redirectLink)
    if not lat == 0 and not lon == 0:
        storeInsert['Lat'] = lat
        storeInsert['Lon'] = lon
    store_collection.insert_one(storeInsert)
    errorMessage = "Store successfully added to database! Please sign-in again for security purposes."
    redirectLink = "/"
    return template("errorPage.html", errorInsert=errorMessage, redirectInsert=redirectLink)


@bottle.post("/profile")
def index():
    username = request.forms['username']
    password = request.forms['password']
    loginAttempt = {"username": username, "password": password}
    if not master_collection.find_one(loginAttempt):
        errorMessage = 'Username or Password is incorrect.'
        redirectLink = '/'
        return template("errorPage.html", errorInsert=errorMessage, redirectInsert=redirectLink)
    userStores = list(store_collection.find({"store-owner": username}, {"_id": 0}))
    # storeList = []
    # for store in userStores:
    #     storeList.append(store)
    return template("profile.html", username1=username, data=userStores)


@bottle.route("/register")
def index():
    return bottle.static_file("register.html", ".")


@bottle.post("/register")
def index():
    username = request.forms['username']
    password1 = request.forms['password1']
    password2 = request.forms['password2']
    if not username or not password1 or not password2:
        errorMessage = "Please fill out all boxes before submitting!"
        redirectLink = "/register"
        return template("errorPage.html", errorInsert=errorMessage, redirectInsert=redirectLink)
    if len(password1) < 8:
        errorMessage = "Entered password is too short."
        redirectLink = "/register"
        return template("errorPage.html", errorInsert=errorMessage, redirectInsert=redirectLink)
    if len(password1) > 20:
        errorMessage = "Entered password is too long."
        redirectLink = "/register"
        return template("errorPage.html", errorInsert=errorMessage, redirectInsert=redirectLink)
    if password2 != password1:
        errorMessage = "Entered passwords do not match."
        redirectLink = "/register"
        return template("errorPage.html", errorInsert=errorMessage, redirectInsert=redirectLink)
    if master_collection.find_one({"username": username}):
        errorMessage = "That username already exists."
        redirectLink = "/register"
        return template("errorPage.html", errorInsert=errorMessage, redirectInsert=redirectLink)
    accountCreation = {"username": username, "password": password1}
    master_collection.insert_one(accountCreation)
    return bottle.static_file("index.html", ".")


if __name__ == '__main__':
    run(host='0.0.0.0', port=8000, debug=True, reloader=True)
