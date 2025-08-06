import pyrebase

firebase_config = {
    "apiKey": "AIzaSyAqKb9WDjTB_6A7ulQHrbFRxJFI7daVNPQ",
    "authDomain": "prenatal-nutrition-app.firebaseapp.com",
    "databaseURL": "",
    "projectId": "prenatal-nutrition-app",
    "storageBucket": "prenatal-nutrition-app.appspot.com",  # 修正這行
    "messagingSenderId": "755425179379",
    "appId": "1:755425179379:web:d8bbad9283110072ff6986"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user  # user 包含 idToken、refreshToken 等資訊
    except Exception as e:
        print("登入失敗:", e)
        return None

