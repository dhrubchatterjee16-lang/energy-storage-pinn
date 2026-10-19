"""
FastAPI Microservice for Energy Storage PINN
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

try:
    from fastapi import FastAPI, HTTPException
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

from .sei_pinn import BatterySEIPINN
from .mhc_kinetics import MarcusHushChidseyKinetics, MHCParameters
from .conformal import ConformalBatteryUQ

if HAS_FASTAPI:
    app = FastAPI(
        title="Energy Storage PINN API",
        description="Battery Physics-Informed Degradation & Marcus-Hush-Chidsey Kinetics Service",
        version="1.0.0"
    )

    class ForecastRequest(BaseModel):
        nominal_capacity_Ah: float = Field(2.5, ge=0.1, le=500.0)
        cycles: int = Field(500, ge=1, le=10000)
        c_rate: float = Field(1.0, ge=0.01, le=20.0)
        temp_C: float = Field(25.0, ge=-20.0, le=70.0)
        confidence: float = Field(0.90, ge=0.50, le=0.99)

    class MHCRequest(BaseModel):
        overpotential_v: float = Field(0.15, ge=-2.0, le=2.0)
        reorganization_energy_ev: float = Field(0.85, ge=0.1, le=3.0)
        temperature_k: float = Field(298.15, ge=200.0, le=400.0)

    @app.get("/")
    def root():
        return {
            "service": "Energy Storage PINN",
            "version": "1.0.0",
            "status": "operational"
        }

    @app.post("/battery/forecast")
    def api_forecast(req: ForecastRequest):
        model = BatterySEIPINN(nominal_capacity_Ah=req.nominal_capacity_Ah)
        traj = model.forecast_aging_trajectory(
            cycles=req.cycles,
            c_rate=req.c_rate,
            temp_C=req.temp_C
        )
        uq = ConformalBatteryUQ().predict_soh_interval(
            traj["final_soh_pct"],
            confidence=req.confidence
        )
        return {
            "trajectory_summary": {
                "initial_capacity_Ah": traj["initial_capacity_Ah"],
                "final_capacity_Ah": traj["final_capacity_Ah"],
                "final_soh_pct": traj["final_soh_pct"],
                "final_sei_thickness_nm": traj["final_sei_thickness_nm"],
                "final_r_sei_ohm": traj["final_r_sei_ohm"]
            },
            "conformal_uq": uq,
            "trajectory": traj["soh_trajectory"]
        }

    @app.post("/battery/mhc")
    def api_mhc(req: MHCRequest):
        params = MHCParameters(
            reorganization_energy_ev=req.reorganization_energy_ev,
            temperature_k=req.temperature_k
        )
        kinetics = MarcusHushChidseyKinetics(params)
        rate = kinetics.compute_mhc_rate(req.overpotential_v)
        return {
            "overpotential_v": req.overpotential_v,
            "reorganization_energy_ev": req.reorganization_energy_ev,
            "mhc_rate_m_s": rate
        }
else:
    app = None
