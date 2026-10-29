from fastapi import Depends, Request, Form
from fastapi.responses import HTMLResponse,RedirectResponse
from ..db import getDB
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
router = APIRouter()

#routes starts here
@router.post("/login") #receive login data from form post
async def login(
	request: Request,
	username: str = Form(...),
	password: str = Form(...),
	db=Depends(getDB)
):
	cur=await db.execute("SELECT * FROM users where id=%s and pwd=%s;",(username,password))
	data= await cur.fetchone()
	if data:
		#save the login status in session variable
		request.session["user"] = data["nickname"]
		#redirect to the home page URL
		return RedirectResponse(url="/", status_code=302)
	return HTMLResponse("Invalid credentials", status_code=401)

@router.get("/logout")
async def logout(request: Request):
	#clear all session variables
	request.session.clear()
	return RedirectResponse(url="/")

