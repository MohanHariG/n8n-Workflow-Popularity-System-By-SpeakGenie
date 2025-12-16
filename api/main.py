# api/main.py
from fastapi import FastAPI, Query
from db import SessionLocal
from api.models import Workflow
from fastapi.responses import JSONResponse

app = FastAPI(title="n8n Workflow Popularity API")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/workflows")
def list_workflows(platform: str = Query(None), country: str = Query(None), limit: int = 50, offset: int = 0):
    session = SessionLocal()
    q = session.query(Workflow)
    if platform:
        q = q.filter(Workflow.platform == platform)
    if country:
        q = q.filter(Workflow.country == country)
    items = q.order_by(Workflow.views.desc()).offset(offset).limit(limit).all()
    res = []
    for it in items:
        res.append({
            "workflow": it.workflow_name,
            "platform": it.platform,
            "popularity_metrics": {
                "views": int(it.views or 0),
                "likes": int(it.likes or 0),
                "comments": int(it.comments or 0),
                "replies": int(it.replies or 0),
                "contributors": int(it.contributors or 0),
                "like_to_view_ratio": float((it.likes or 0) / (it.views or 1)) if (it.views or 0) else 0,
                "comment_to_view_ratio": float((it.comments or 0) / (it.views or 1)) if (it.views or 0) else 0
            },
            "country": it.country,
            "source_url": it.source_url
        })
    session.close()
    return JSONResponse({"count": len(res), "data": res})
