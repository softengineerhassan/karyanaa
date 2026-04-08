from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.v1.handlers.dashboard_handler import DashboardHandler
from app.api.v1.schemas.common_schema import StandardResponse
from app.api.v1.schemas.dashboard_schema import DashboardSummaryResponse
from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.core.response import success_response

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=StandardResponse[DashboardSummaryResponse], status_code=status.HTTP_200_OK)
def get_dashboard_summary(
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    handler = DashboardHandler(session)
    summary = handler.handle_summary()
    return success_response(data=summary, message="Dashboard summary retrieved successfully")
