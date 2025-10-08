from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Risk Assessment API", version="1.1")

# --- Enable CORS for all origins (required for GPT Actions) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DBS Strategic Asset Allocation (SAA) ---
SAA = {
    "Conservative": {"EQ": 20, "IG Bonds": 60, "HY": 10, "Cash": 10},
    "Balanced": {"EQ": 50, "IG Bonds": 40, "HY": 5, "Cash": 5},
    "Growth": {"EQ": 70, "IG Bonds": 20, "HY": 5, "Alts": 5}
}

# --- Request schema ---
class Allocation(BaseModel):
    asset_class: str
    weight_pct: float

class RequestBody(BaseModel):
    risk_profile: str
    current_allocation: List[Allocation]

# --- POST endpoint ---
@app.post("/risk/assess")
def assess_risk(body: RequestBody):
    profile = body.risk_profile
    target = SAA.get(profile)
    if not target:
        raise HTTPException(status_code=400, detail=f"Unknown profile: {profile}")

    deviations = []
    for item in body.current_allocation:
        target_weight = target.get(item.asset_class, 0)
        delta = item.weight_pct - target_weight
        if abs(delta) >= 5:
            deviations.append({
                "asset": item.asset_class,
                "delta": round(delta, 2),
                "status": "Overweight" if delta > 0 else "Underweight"
            })

    # Return plain dict (FastAPI will handle JSON + headers correctly)
    return {"risk_profile": profile, "deviations": deviations}

# --- Root endpoint for sanity check ---
@app.get("/")
def root():
    return {"message": "DBS RiskCalc API is running", "endpoints": ["/risk/assess"]}
