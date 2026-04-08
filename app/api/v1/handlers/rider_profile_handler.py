from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.v1.actions.rider_profile_actions import RiderProfileActions
from app.api.v1.schemas.rider_profile_schema import RiderProfileCreateRequest, RiderProfileUpdateRequest
from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User


class RiderProfileHandler:
    @staticmethod
    def create_rider(
        payload: RiderProfileCreateRequest,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return RiderProfileActions.create_rider(payload, session, current_user)

    @staticmethod
    def list_riders(
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return RiderProfileActions.list_riders(session, current_user)

    @staticmethod
    def get_rider(
        rider_id: UUID,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return RiderProfileActions.get_rider(rider_id, session, current_user)

    @staticmethod
    def update_rider(
        rider_id: UUID,
        payload: RiderProfileUpdateRequest,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return RiderProfileActions.update_rider(rider_id, payload, session, current_user)

    @staticmethod
    def delete_rider(
        rider_id: UUID,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return RiderProfileActions.delete_rider(rider_id, session, current_user)
