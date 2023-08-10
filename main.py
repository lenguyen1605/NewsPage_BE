from fastapi import FastAPI, HTTPException
import firebase_admin
from datetime import date, time, datetime
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, time, datetime
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import firestore, credentials
from pydantic import BaseModel
from typing import List
# import datetime
from datetime import datetime
import uuid

cred = credentials.Certificate("./credentials.json")
firebase_admin.initialize_app(cred)

app = FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class User(BaseModel):
    email: str
    password: str
    username: str
    id_post: List[str]
    # author: False


class Post(BaseModel):
    categories: List[str]
    content: str
    # date_created: datetime
    # id_author: str
    image: str
    likes: int
    title: str
    summary: str


@app.post("/Signup")
def create_user(user_data: User):
    db = firestore.client()
    try:
        new_user = db.collection('users').document()
        new_user.set({"email": user_data.email, "password": user_data.password, "username": user_data.username})
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/setPost")
def set_post(post_info: Post):
    db = firestore.client()
    try:
        random_id = uuid.uuid4()
        new_post = db.collection('post').document(str(random_id))
        doc_categories = [db.collection('categories').document(category) for category in post_info.categories]
        print(doc_categories)

        new_post.set({"content": post_info.content, "date_created": datetime.now(),
                      "id_author": db.collection('users').document('le'), "likes": post_info.likes,
                      "title": post_info.title, "image": post_info.image,
                      "summary": post_info.summary, "categories": doc_categories, "id": str(random_id)})
        for category in post_info.categories:
            cat_ref = db.collection('categories').document(category)
            new_post_list = cat_ref.get().get("posts")
            new_post_list.append(db.collection('post').document(str(random_id)))
            cat_ref.update({"posts": new_post_list})

        return {"message": "Post created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/getAllPost")
def get_all_post():
    db = firestore.client()
    try:
        all_posts = []
        docs = db.collection('post').stream()
        for doc in docs:
            data = doc.to_dict()
            data['id_author'] = doc.get("id_author").id
            data['categories'] = [category_ref.id for category_ref in doc.get("categories")]
            # data['date_created'] = datetime.datetime.fromtimestamp(doc.get('date_created').timestamp())
            nanoseconds_datetime = data['date_created']

            # Convert to standard Python datetime object
            standard_datetime = datetime(
                year=nanoseconds_datetime.year,
                month=nanoseconds_datetime.month,
                day=nanoseconds_datetime.day,
                hour=nanoseconds_datetime.hour,
                minute=nanoseconds_datetime.minute,
                second=nanoseconds_datetime.second,
                microsecond=nanoseconds_datetime.nanosecond // 1000,

            )
            data['date_created'] = standard_datetime
            author_name = db.collection('users').document(doc.get('id_author').id)
            data['author_name'] = author_name.get().get("username")
            # print(data)
            print(data)
            all_posts.append(data)
        # print(all_posts)
        return all_posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/getPostbyID")
def get_post_by_id(id):
    db = firestore.client()
    try:
        this_post = []
        post_ref = db.collection('post').document(id)
        post = post_ref.get().to_dict()
        post['id_author'] = post_ref.get().get("id_author").id
        post['categories'] = [category_ref.id for category_ref in post_ref.get().get("categories")]

        nanoseconds_datetime = post['date_created']

        # Convert to standard Python datetime object
        standard_datetime = datetime(
            year=nanoseconds_datetime.year,
            month=nanoseconds_datetime.month,
            day=nanoseconds_datetime.day,
            hour=nanoseconds_datetime.hour,
            minute=nanoseconds_datetime.minute,
            second=nanoseconds_datetime.second,
            microsecond=nanoseconds_datetime.nanosecond // 1000,

        )
        post['date_created'] = standard_datetime
        author_name = db.collection('users').document(post_ref.get().get('id_author').id)

        post['author_name'] = author_name.get().get("username")

        # print(post)
        # this_post.append(post)
        # print(this_post)
        return post
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/getPostByCategory")
def get_post_by_category(category):
    db = firestore.client()
    try:
        all_posts = []

        cat_ref = db.collection('categories').document(category)
        print("cat_ref", cat_ref)
        cat = cat_ref.get().to_dict()
        print("cat here", cat)
        for post in cat["posts"]:
            data = post.get().to_dict()
            data["id_author"] = post.get().get("id_author").id
            data["categories"] = [category_ref.id for category_ref in post.get().get("categories")]
            nanoseconds_datetime = data['date_created']

            # Convert to standard Python datetime object
            standard_datetime = datetime(
                year=nanoseconds_datetime.year,
                month=nanoseconds_datetime.month,
                day=nanoseconds_datetime.day,
                hour=nanoseconds_datetime.hour,
                minute=nanoseconds_datetime.minute,
                second=nanoseconds_datetime.second,
                microsecond=nanoseconds_datetime.nanosecond // 1000,

            )
            data['date_created'] = standard_datetime
            author_name = db.collection('users').document(post.get().get('id_author').id)

            data['author_name'] = author_name.get().get("username")
            print("data", data)
            all_posts.append(data)
        print("all_post", all_posts)
        return all_posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
