from fastapi import APIRouter, Depends, HTTPException

from database.orm import User
from database.repository import UserRepository
from schema.request import SignUpRequest, LogInRequest
from schema.response import UserResponse, JWTResponse
from service.user import UserService

router = APIRouter(prefix="/users")


@router.post("/sign-up", status_code=201)
def user_sign_up_handler(
        request: SignUpRequest,
        user_service: UserService = Depends(),
        user_repo: UserRepository = Depends()
):
    # 1. request body : username, password
    # 2. hash password
    hashed_password: str = user_service.hash_password(
        plain_password=request.password
    )
    # 3. User(username, hashed password)
    user: User = User.create(
        username=request.username,
        hashed_password=hashed_password
    )
    # 4. database save
    user: User = user_repo.save_user(user=user)
    # 5. return response
    return UserResponse.from_orm(user)


@router.post("/log-in")
def user_log_in_handler(
        request: LogInRequest,
        user_repo: UserRepository = Depends(),
        user_service: UserService = Depends()
):
    # 1. request body(username, password)
    # 2. db read user
    user: User | None = user_repo.get_user_by_username(
        username=request.username
    )
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found!")
    # 3. determine user.password(hashed), request.password(plain)
    verified: bool = user_service.verify_password(
        request.password,   # password at request
        user.password       # password saved in DB
    )
    if not verified:
        raise HTTPException(status_code=401, detail="User Not Authorized!")
    # 4. create jwt : jwt is json type web token for authorizing user's role
    access_token: str = user_service.create_jwt(username=user.username)
    # 5. return jwt
    return JWTResponse(access_token=access_token)
