from sqlalchemy import text
from sqlalchemy.orm import Session


def get_sales_summary(db: Session, period: str) -> dict:
    if period not in {"daily", "monthly"}:
        raise ValueError("Period must be daily or monthly")

    date_condition = (
        "DATE(t.created_at) = CURRENT_DATE"
        if period == "daily"
        else "DATE_TRUNC('month', t.created_at) = DATE_TRUNC('month', CURRENT_DATE)"
    )

    summary_query = text(
        f"""
        SELECT
            COUNT(DISTINCT t.id) AS total_transactions,
            COALESCE(SUM(t.total_amount), 0) AS total_revenue,
            COALESCE(SUM(ti.cost_price * ti.qty), 0) AS total_cost,
            COALESCE(SUM(t.total_amount) - SUM(ti.cost_price * ti.qty), 0) AS gross_profit
        FROM transactions t
        LEFT JOIN transaction_items ti ON ti.transaction_id = t.id
        WHERE {date_condition}
        """
    )

    result = db.execute(summary_query).mappings().first()
    return {
        "period": period,
        "total_transactions": int(result["total_transactions"] or 0),
        "total_revenue": float(result["total_revenue"] or 0),
        "total_cost": float(result["total_cost"] or 0),
        "gross_profit": float(result["gross_profit"] or 0),
    }


def get_sales_breakdown(db: Session, period: str) -> list[dict]:
    bucket = "DATE(t.created_at)" if period == "daily" else "TO_CHAR(t.created_at, 'YYYY-MM-DD')"

    query = text(
        f"""
        SELECT
            {bucket} AS bucket,
            COUNT(DISTINCT t.id) AS transactions,
            COALESCE(SUM(t.total_amount), 0) AS revenue,
            COALESCE(SUM(ti.cost_price * ti.qty), 0) AS cost
        FROM transactions t
        LEFT JOIN transaction_items ti ON ti.transaction_id = t.id
        GROUP BY bucket
        ORDER BY bucket DESC
        LIMIT 31
        """
    )

    rows = db.execute(query).mappings().all()
    return [
        {
            "bucket": str(row["bucket"]),
            "transactions": int(row["transactions"]),
            "revenue": float(row["revenue"]),
            "cost": float(row["cost"]),
            "profit": float(row["revenue"]) - float(row["cost"]),
        }
        for row in rows
    ]
