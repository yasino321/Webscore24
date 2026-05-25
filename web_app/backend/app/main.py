from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import json
import tempfile
import os

from . import models, schemas, auth, database, services

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="WebScore API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.put("/users/me/keys", response_model=schemas.User)
async def update_keys(keys: schemas.UserUpdateKeys, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    if keys.gemini_api_key is not None:
        current_user.gemini_api_key = keys.gemini_api_key
    if keys.openai_api_key is not None:
        current_user.openai_api_key = keys.openai_api_key
    if keys.google_places_api_key is not None:
        current_user.google_places_api_key = keys.google_places_api_key
    db.commit()
    db.refresh(current_user)
    return current_user

@app.get("/leads", response_model=List[schemas.Lead])
def get_leads(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    return db.query(models.Lead).filter(models.Lead.owner_id == current_user.id).all()

@app.post("/leads", response_model=schemas.Lead)
def create_lead(lead: schemas.LeadCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    db_lead = models.Lead(**lead.model_dump(), owner_id=current_user.id)
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

@app.post("/find-leads")
async def find_leads_endpoint(req: schemas.FindLeadsRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    try:
        leads_data = services.find_leads_service(req.branche, req.ort, req.radius, current_user)
        added_leads = []
        for l in leads_data:
            exists = db.query(models.Lead).filter(models.Lead.url == l['url'], models.Lead.owner_id == current_user.id).first()
            if not exists:
                new_lead = models.Lead(**l, owner_id=current_user.id)
                db.add(new_lead)
                added_leads.append(new_lead)
        db.commit()
        return {"message": f"{len(added_leads)} neue Leads gefunden."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/leads/{lead_id}/analyse")
async def analyse_lead(lead_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id, models.Lead.owner_id == current_user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    try:
        analysis = services.analyse_service(lead.url, current_user)
        lead.score_total = analysis['gesamt']
        lead.score_details = json.dumps(analysis)
        lead.status = "qualifiziert" if lead.score_total < 60 else "analysiert"
        db.commit()
        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/leads/{lead_id}/report")
async def get_lead_report(lead_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id, models.Lead.owner_id == current_user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    if not lead.score_details:
        raise HTTPException(status_code=400, detail="Lead must be analysed first")

    analysis = json.loads(lead.score_details)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        report_path = tmp.name

    try:
        services.create_report_pdf(lead, analysis, "", report_path)
        return FileResponse(report_path, media_type="application/pdf", filename=f"{lead.name}_report.pdf")
    except Exception as e:
        if os.path.exists(report_path): os.remove(report_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/leads/{lead_id}")
def delete_lead(lead_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id, models.Lead.owner_id == current_user.id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    db.delete(lead)
    db.commit()
    return {"message": "Lead deleted"}
