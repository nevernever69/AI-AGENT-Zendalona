from fastapi import APIRouter, HTTPException, status, Depends
from auth.schemas import UserCreate, UserLogin, UserOut
from auth.utils import hash_password, verify_password, create_access_token
from auth.models import UserModel
from utils.mongodb import db

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserOut)
async def register(user: UserCreate):
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)
    user_dict = {
        "fullname": user.fullname,
        "email": user.email,
        "hashed_password": hashed_pw
    }
    result = await db.users.insert_one(user_dict)
    user_out = UserOut(id=str(result.inserted_id), fullname=user.fullname, email=user.email)
    return user_out

@router.post("/login")
async def login(user: UserLogin):
    existing_user = await db.users.find_one({"email": user.email})
    if not existing_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(user.password, existing_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect password")

    token = create_access_token(data={"user_id": str(existing_user["_id"])})
    return {"access_token": token, "token_type": "bearer"}
