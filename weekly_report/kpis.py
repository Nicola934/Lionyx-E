from __future__ import annotations


from dataclasses import dataclass
from typing import Any, Dict


import pandas as pd


from .config import ColumnMap



@dataclass(frozen=True)
class KPIResult:
    total_reponses: int
    satisfaction_rate: float | None
    recommendation_rate: float | None
    most_used_service: str | None
    top_region: str | None

def compute_kpis(df: pd.DataFrame, cm: ColumnMap) -> KPIResult: # Accepts a DataFrame and ColumnMap class object and returns a KPIResult class object
    total = int(len(df)) # The total number of rows in the DataFrame df
    
    if total == 0:
        return KPIResult(0, None, None, None, None)  

    sat_rate = float(df[cm.satisfied_col].mean())   # boolean mean. A boolean mean is the proportion of True values in a boolean series

    rec_rate = float(df[cm.recommend_col].mean())

    most_used_service = df[cm.service_col].value_counts().idxmax()
    top_region = df[cm.region_col].value_counts().idxmax()

    return KPIResult(
        total_responses=total,
        satisfaction_rate=sat_rate,
        recommmendation_rate=rec_rate,
        most_used_service=str(most_used_service),
        top_region=str(top_region),
    )
    
def kpi_to_dict(k: KPIResult) -> Dict[str, Any]:
    return {
        "total_responses": k.total_responses,
        "satisfaction_rate": k.satisfaction_rate,
        "recommendation_rate": k.recommendation_rate,
        "most_used_service": k.most_used_service,
        "top_region": k.top_region,
    }

    