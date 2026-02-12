from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.schemas.transaction import ReportSummary
from app.services.report_service import get_sales_breakdown, get_sales_summary

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/summary", response_model=ReportSummary)
def sales_summary(
    period: str = Query(default="daily", pattern="^(daily|monthly)$"),
    db: Session = Depends(get_db),
    _: object = Depends(require_admin),
):
    return get_sales_summary(db, period)


@router.get("/breakdown")
def sales_breakdown(
    period: str = Query(default="daily", pattern="^(daily|monthly)$"),
    db: Session = Depends(get_db),
    _: object = Depends(require_admin),
):
    return {"period": period, "rows": get_sales_breakdown(db, period)}
