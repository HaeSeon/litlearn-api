from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import json
from nlp_module import find_closest_words
from nlp_module import find_farthest_words
from nlp_module import find_most_similar_news
from nlp_module import find_most_dissimilar_news
import random

# FastAPI 인스턴스 생성
app = FastAPI()

# MongoDB 연결 설정
client = MongoClient("mongodb://localhost:27017/")  # MongoDB 연결 주소
db = client["helmut"]  # 데이터베이스 이름

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin을 허용하며, 필요에 따라 변경 가능

    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    email: str
    password: str
    interests: list
    domain: list
# 유저 정보를 위한 Pydantic 모델
class UserInterest(BaseModel):
    email: str
    # password: str
    interests: list
    domain: list

class Test(BaseModel):
    email: str
    score : float
# 로그인을 처리하는 엔드포인트
@app.post("/login/")
async def login(user: User):
    users_collection = db["users"]
    user_data = users_collection.find_one({"email": user.email, "password": user.password})
    if user_data:
        return {"message": "로그인 성공"}
    else:
        raise HTTPException(status_code=401, detail="유효하지 않은 사용자")

# 사용자 정보를 추가하는 엔드포인트
@app.post("/user/add_info/")
async def add_user_info(user: UserInterest):
    # MongoDB에서 기존 사용자를 찾음
    users_collection = db["users"]
    existing_user = users_collection.find_one({"email": user.email})

    if existing_user:
        # 기존 사용자 정보에 새로운 데이터 추가
        updated_data = {
            "$push": {
                "interests": {"$each": user.interests},
                "domain": {"$each": user.domain}
            }
        }
        users_collection.update_one({"email": user.email}, updated_data)
        return {"message": "사용자 정보가 업데이트되었습니다."}
    else:
        return {"message": "사용자를 찾을 수 없습니다."}
    
@app.post("/user/add_test/")
async def add_user_info(user: Test):
    # MongoDB에서 기존 사용자를 찾음
    users_collection = db["users"]
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        # 기존 사용자 정보에 새로운 데이터 추가
        if "recentScore" not in existing_user:  
            existing_user["recentScore"] = []

        # 새로운 점수를 recentScore에 추가하고 이전 점수를 prevScore로 유지
        if "score" in user.dict():
            print(existing_user.get("recentScore"),user.dict()["score"])
            existing_user["prevScore"] = existing_user.get("recentScore")
            existing_user["recentScore"] = user.dict()["score"]

            # MongoDB 업데이트
            users_collection.update_one({"email": user.email}, {"$set": existing_user})
            return {"message": "사용자 정보가 업데이트되었습니다."}
        else:
            return {"message": "새로운 점수가 제공되지 않았습니다."}
    else:
        return {"message": "사용자를 찾을 수 없습니다."}
    
class GetUser(BaseModel):
    email : str
@app.post("/users/")
async def get_user_info(user : GetUser):
    # MongoDB에서 사용자 정보 가져오기
    users_collection = db["users"]
    existing_user = users_collection.find_one({"email": user.email})
    print("hele",existing_user)
    result_dict = {}
    result_dict["email"] =existing_user["email"]
    result_dict["domain"] =existing_user["domain"]
    result_dict["interests"] =existing_user["interests"]
    result_dict["recentScore"] =existing_user["recentScore"]
    result_dict["prevScore"] =existing_user["prevScore"]
    return result_dict



@app.post("/smililarity/")
async def get_user_info(user : GetUser):
    users_collection = db["users"]
    existing_user = users_collection.find_one({"email": user.email})
    input = existing_user["interests"] + existing_user["domain"]
    
    vocas = list(db["vocas"].find({}, {"_id": 0}))
    closest = random.sample(find_closest_words(input, vocas),2)
    farthest = random.sample(find_farthest_words(input,vocas),1)
    return closest + farthest



@app.post("/news/smililarity/")
async def get_user_info(user : GetUser):
    users_collection = db["users"]
    existing_user = users_collection.find_one({"email": user.email})
    input = existing_user["interests"] + existing_user["domain"]
    
    news = list(db["news"].find({"개체명(지역)": "대구"}, {"_id": 0}))
    similar_news = random.sample(find_most_similar_news(input, news),2)
    oppsite_news = random.sample(find_most_dissimilar_news(input, news), 1)
    result_news = similar_news + oppsite_news
    response = []
    for item in result_news:
        result_dict = {}
        result_dict['일자'] = item['일자']
        result_dict['언론사'] = item['언론사']
        result_dict['제목'] = item['제목']
        result_dict['주소'] = item['주소']       
        response.append(result_dict) 
    return response
    # return result_news

    

    
