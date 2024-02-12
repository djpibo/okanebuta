import bcrypt
from datetime import datetime, timedelta
from jose import jwt


class UserService:
    encoding: str = "UTF-8"
    secret_key: str = "6004ee7950d6310f57004160eb803b18"  # openssl based 32len hex code
    jwt_algoritm: str = "HS256"

    def hash_password(self, plain_password: str) -> str:
        hashed_password: bytes = bcrypt.hashpw(
            plain_password.encode(self.encoding),
            salt=bcrypt.gensalt())
        return hashed_password.decode(self.encoding)  # hash value is bytes type, so decode to cast str type

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode(self.encoding),
            hashed_password.encode(self.encoding)
        )

    def create_jwt(self, username: str) -> str:
        return jwt.encode(
            # this is jwt payload data format
            {
                # subject, should be unique
                "sub": username,
                # expired time
                "exp": datetime.now() + timedelta(days=1)
            },
            self.secret_key,
            algorithm=self.jwt_algoritm)

    def decode_jwt(self, access_token: str) -> str:
        payload: dict = jwt.decode(
            access_token,
            self.secret_key,
            algorithms=[self.jwt_algoritm]
        )
        return payload["sub"]  # username will be returned
