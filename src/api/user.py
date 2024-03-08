from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from database.orm import User
from database.repository import UserRepository
from redis_cache import redis_client
from schema.request import SignUpRequest, LogInRequest, CreateOTPRequest, VerifyOTPRequest
from schema.response import UserResponse, JWTResponse
from security import get_access_token
from service.user import UserService

import requests

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
    response = requests.get(f"https://nid.naver.com/oauth2.0/authorize?client_id={user.username}")
    print("response")
    print(response.content)
    print(response.headers)
    return UserResponse.from_orm(user)


# @router.post("/sign-up", status_code=201)
# def user_sign_up_handler(
#         request: SignUpRequest,
#         user_service: UserService = Depends(),
#         user_repo: UserRepository = Depends()
# ):
#     # 1. request body : username, password
#     # 2. hash password
#     hashed_password: str = user_service.hash_password(
#         plain_password=request.password
#     )
#     # 3. User(username, hashed password)
#     user: User = User.create(
#         username=request.username,
#         hashed_password=hashed_password
#     )
#     # 4. database save
#     user: User = user_repo.save_user(user=user)
#     # 5. return response
#     return UserResponse.from_orm(user)


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


@router.post("/email/otp")
def create_otp_handler(
        request: CreateOTPRequest,
        _: str = Depends(get_access_token),  # for only verify header so script _
        user_service: UserService = Depends()
):
    otp: int = user_service.create_otp()
    redis_client.set(request.email, otp)
    redis_client.expire(request.email, 3 * 60)
    return {"otp": otp}


@router.post("/email/otp/verify")
def verify_otp_handler(
        request: VerifyOTPRequest,
        background_tasks: BackgroundTasks,
        access_token: str = Depends(get_access_token),
        user_service: UserService = Depends(),
        user_repo: UserRepository = Depends()
):
    otp: int | None = int(redis_client.get(request.email))
    if not otp:
        raise HTTPException(status_code=400, detail="Bad Request!")
    if request.otp != otp:
        raise HTTPException(status_code=400, detail="Bad Request!")

    username: str = user_service.decode_jwt(access_token=access_token)
    user: User | None = user_repo.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found!")

    # async
    background_tasks.add_task(
        user_service.send_email_to_user,
        email=request.email
    )

    return UserResponse.from_orm(user)

