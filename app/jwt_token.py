import jwt
import datetime
import time


JWT_SECRETKEY = "wordChecker_password"


def jwt_encode(data, hours=24 * 7):  # expires in 7 days(24 hours times 7) by default
    exp = datetime.datetime.now() + datetime.timedelta(hours=hours)
    payload_data = {"data": data, "exp": exp}

    token = jwt.encode(
        payload=payload_data,
        key=JWT_SECRETKEY,
    )

    return token


def jwt_decode(token):
    try:
        data = jwt.decode(token, key=JWT_SECRETKEY, algorithms=["HS256"])
        if time.time() <= data["exp"]:
            data.update({"status": "success"})
            return data
        else:
            return {"status": "failed"}
    except:
        return {"status": "failed"}
