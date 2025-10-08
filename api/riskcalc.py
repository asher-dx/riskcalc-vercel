from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Risk Assessment API", version="1.0")

SAA = {
    "Conservative": {"EQ": 20, "IG Bonds": 60, "HY": 10, "Cash": 10},
    "Balanced": {"EQ": 50, "IG Bonds": 40, "HY": 5, "Cash": 5},
    "Growth": {"EQ": 70, "IG Bonds": 20, "HY": 5, "Alts": 5}
}

class Allocation(BaseModel):
    asset_class: str
    weight_pct: float

class RequestBody(BaseModel):
    risk_profile: str
    current_allocation: List[Allocation]

@app.post("/risk/assess")
def assess_risk(body: RequestBody):
    profile = body.risk_profile
    target = SAA.get(profile)
    if not target:
        raise HTTPException(400, f"Unknown profile: {profile}")
    deviations = []
    for item in body.current_allocation:
        delta = item.weight_pct - target.get(item.asset_class, 0)
        if abs(delta) >= 5:
            deviations.append({
                "asset": item.asset_class,
                "delta": round(delta, 2),
                "status": "Overweight" if delta > 0 else "Underweight"
            })
    return {"risk_profile": profile, "deviations": deviations}
