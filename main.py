from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, HttpUrl, Field
from pymongo import MongoClient
import json
import random
from typing import List
from fastapi import status
from bson import ObjectId
from openai import OpenAI
import os
from fastapi.encoders import jsonable_encoder
from fastapi import Request
from fastapi.responses import JSONResponse
import pydantic
pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str



OPENAI_API_KEY = ""
openAIClient = OpenAI(api_key=OPENAI_API_KEY)


# FastAPI 인스턴스 생성
app = FastAPI()

# MongoDB 연결 설정
client = MongoClient("mongodb://localhost:27017/")  
db = client["stogee"] 

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 

    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    email: EmailStr
    password: str

class Category(BaseModel):
    name: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    categories: List[Category]


class LinkCreate(BaseModel):
    linkUrl: HttpUrl
    title: str
    email: EmailStr
    
class PieceCreate(BaseModel):
    linkUrl: HttpUrl
    sentence: str
    email: EmailStr
    
class UserCategory(BaseModel):
    id: str 
    name: str
    
class UserCategoriesResponse(BaseModel):
    categories: List[UserCategory]
    

    
@app.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    existing_user = db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    categories_with_ids = [{"_id": ObjectId(), **category.dict()} for category in user.categories]
    
    user_data = {
        "email": user.email,
        "password": user.password,
        "categories": categories_with_ids
    }
    
    db.users.insert_one(user_data)
    
    # 응답 시 비밀번호를 숨기기
    return User(email=user.email, password="****")


@app.post("/login/")
def login(user: User):
    # MongoDB에서 사용자 정보를 조회
    user_info = db.users.find_one({"email": user.email})
    if not user_info or user_info['password'] != user.password:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return {"message": "Login successful"}


@app.post("/links/", status_code=201)
def create_link(link_data: LinkCreate):
    print("링크 데이터:", link_data)
    user_info = db.users.find_one({"email": link_data.email})
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    category_name = []
    for category in user_info['categories']:
        category_name.append(category['name'])
        
    print('카테고리 이름:', category_name)
    
    # # OPENAI API 호출코드 (실제 사용 시 주석 해제 필요)
    # messages = [{"role": "system", "content": "title:str, categories:str[]이 입력값으로 제공되면 너는 category와 keywords를 리턴할거야. category는 title에 해당하는 카테고리를 categories 배열중에서 한개만 골라. keywords는 title과 관련된 키워드를 단어로 5개 만들어서 함께 반환해. 반환형태는 Json으로, category는 str, keywords도 str 배열로."}]
    # messages.append({"role": "user", "content": "{'title' : {link_data.title}, 'categories' : {category_name}}"})
    
    # completion  = openAIClient.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=messages,
    #     temperature=1,
    #     top_p=1,
    # )
    # answer = json.loads(completion.choices[0].message.content)
    
    # 테스트용 OPENAI API 응답 예시
    answer = {'category': 'technology', 'keywords': ['fastapi', 'data science', 'backend', 'software development', 'project']}
    print("응답",answer)
    
    
    selected_category = None
    for category in user_info['categories']:
        if category['name'] == answer['category']:
            selected_category = category
            print("선택된 카테고리:", selected_category)
            break

    # 새로운 링크 문서 생성
    link_document = {
        "userId": user_info["_id"],
        "linkUrl": link_data.linkUrl,
        "title": link_data.title,
        "category": selected_category,
        "keywords": answer['keywords']
    }
    db.links.insert_one(link_document)
    
    return {"message": "Link created successfully", "link": link_document}

@app.post("/pieces/", status_code=201)
def create_piece(piece_data: PieceCreate):
    print("조각 데이터:", piece_data)
    user_info = db.users.find_one({"email": piece_data.email})
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    category_name = []
    for category in user_info['categories']:
        category_name.append(category['name'])
        
    print('카테고리 이름:', category_name)
    
    # # OPENAI API 호출코드 (실제 사용 시 주석 해제 필요)
    # messages = [{"role": "system", "content": "sentence:str, categories:str[]이 입력값으로 제공되면 너는 category와 keywords 와 title을 리턴할거야. category는 sentence에 해당하는 카테고리를 categories 배열중에서 한개만 골라. keywords는 sentence와 관련된 키워드를 단어로 5개 만들어서 함께 반환해. title은 니가 알맞는 제목을 지어봐. 반환형태는 Json으로, category는 str, keywords도 str 배열로. title은 str로."}]
    # messages.append({"role": "user", "content": "{'title' : {piece_data.title}, 'categories' : {category_name}}"})
    
    # completion  = openAIClient.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=messages,
    #     temperature=1,
    #     top_p=1,
    # )
    # answer = json.loads(completion.choices[0].message.content)
    
    # 테스트용 OPENAI API 응답 예시
    answer = {'category': 'travel', 'keywords': ['일본여행', '일본 벚꽃', '오사카', '오사카 벚꽃', '도톤보리'], 'title': '오사카 벚꽃 여행'}
    print("응답",answer)
    
    
    selected_category = None
    for category in user_info['categories']:
        if category['name'] == answer['category']:
            selected_category = category
            print("선택된 카테고리:", selected_category)
            break

    # 새로운 링크 문서 생성
    link_document = {
        "userId": user_info["_id"],
        "linkUrl": piece_data.linkUrl,
        "sentence": piece_data.sentence,
        "category": selected_category,
        'title' : answer['title'],
        "keywords": answer['keywords']
    }
    db.pieces.insert_one(link_document)
    
    return {"message": "Link created successfully", "link": link_document}

@app.get("/user/{email}/categories", response_model=UserCategoriesResponse)
def get_user_categories(email: str):
    # MongoDB에서 사용자 데이터를 조회
    user_info = db.users.find_one({"email": email})
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")

    categories = [
         {"id": str(category["_id"]), "name": category["name"]}
        for category in user_info.get('categories', [])
    ]

    return UserCategoriesResponse(categories=categories)

@app.get("/link/categories/{categoryId}/content")
def get_links_by_category(categoryId: str):
    # MongoDB에서 category_id가 categoryId와 일치하는 모든 링크를 검색
    print("카테고리 ID:", categoryId)
    links = list(db.links.find({"category._id": ObjectId(categoryId)}))
    return links
    # 검색된 링크가 없을 경우 404 에러 처리
    if not links:
        raise HTTPException(status_code=404, detail="No links found for this category")

@app.get("/piece/categories/{categoryId}/content")
def get_links_by_category(categoryId: str):
    # MongoDB에서 category_id가 categoryId와 일치하는 모든 링크를 검색
    print("카테고리 ID:", categoryId)
    links = list(db.pieces.find({"category._id": ObjectId(categoryId)}))
    return links
    # 검색된 링크가 없을 경우 404 에러 처리
    if not links:
        raise HTTPException(status_code=404, detail="No links found for this category")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)