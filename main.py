# -*- coding: utf-8 -*-
# main.py
from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from .db import getDB, lifespan
from fastapi.staticfiles import StaticFiles

from starlette.middleware.sessions import SessionMiddleware
#from routes import router as all_routes
#from routes.upload import router as upload_router
#from routes import users


templates = Jinja2Templates(directory="templates")
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key",
	max_age=None, #86400,  # 1 day
    same_site="lax",  # Options: 'lax', 'strict', 'none'
    https_only=False,  # Set to True in production with HTTPS,
)
# Include the router
from .routes.login import router as loginRoute #取個別名避免同名變數衝突
app.include_router(loginRoute, prefix="/user") #mount every thing from ./routes/ to url under prefix

def chkLogin():
	def checker(request: Request): #fastAPI will auto-inject request to dependency function
		loginUser = request.session.get("user") #get identity from session
		if loginUser:
			return loginUser #return whatever you need
		else:
			#raise HTTPException(status_code=403, detail="Forbidden")
			return None
	return checker

@app.get("/")
async def home(request: Request, user=Depends(chkLogin())): 
	print(user)
	if user is None:
		return RedirectResponse(url="/w/login.html", status_code=302)
	else:
		return HTMLResponse(f"Welcome {user}! <a href='/logout'>logout</a>")
# Include the router
#app.include_router("routes/r", prefix="/") #mount every thing from ./routes/ to url under prefix

@app.get("/students/list")
async def read_users(db=Depends(getDB)):
    cur=await db.execute("SELECT * FROM students")
    return await cur.fetchall()

@app.post("/login") #receive login data from form post
async def login(
	request: Request,
	username: str = Form(...),
	password: str = Form(...),
	db=Depends(getDB)
):
	cur=await db.execute("SELECT * FROM users where id=%s and pwd=%s",(username, password))
	data= await cur.fetchone()
	#you can replace this with a DB SQL query
	if data:
		#save the login status in session variable
		request.session["user"] = data["nickname"]
		#redirect to the home page URL
		return RedirectResponse(url="/", status_code=302)
	return HTMLResponse("Invalid credentials", status_code=401)

@app.get("/logout")
async def logout(request: Request):
	#clear all session variables
	request.session.clear()
	return RedirectResponse(url="/")

@app.get("/students/list/template")
async def stuList(request:Request, db=Depends(getDB)):
    cur=await db.execute("SELECT * FROM students order by stuid;")
    data= await cur.fetchall()
    return templates.TemplateResponse(name="studentList.html", request=request,context={"students": data})

@app.get("/student/edit/{stuid}")
async def stuEdit(stuid:int,request:Request, db=Depends(getDB)):
    cur=await db.execute("SELECT * FROM students where stuid=%s",(stuid,))
    data= await cur.fetchone()
    return templates.TemplateResponse(name="studentEdit.html", request=request,context={"data": data})

@app.get("/student/delete/{stuid}")
async def stuDelete(stuid: int,request:Request, db = Depends(getDB)):
    cur=await db.execute("DELETE FROM students WHERE stuid=%s", (stuid,))
    await db.commit()
    return RedirectResponse(url="/students/list/template", status_code=303)

@app.post("/student/update")
async def stuUpdate(stuid:int=Form(...), name:str=Form(...), height:int=Form(...), db=Depends(getDB)):
    print(stuid, name, height)
    await db.execute("update students set name=%s, height=%s where stuid=%s;", (name, height, stuid))
    return RedirectResponse(url="/students/list/template",status_code=303) #use 303 to switch to GET

@app.get("/student/add") #點Add後會出現studentAdd.html
async def stuAddForm(request: Request):
    return templates.TemplateResponse(name="studentAdd.html", request=request)

@app.post("/student/add")
async def stuAdd(
    stuid: int = Form(...),
    name: str = Form(...),
	height: int = Form(...),
    db = Depends(getDB)
):
    await db.execute(
        "INSERT INTO students (stuid, name, height) VALUES (%s, %s, %s)",(stuid, name , height )
    )
    await db.commit()
    return RedirectResponse(url="/students/list/template", status_code=303)
#定義靜態網頁的目錄
app.mount("/w", StaticFiles(directory="www"))
