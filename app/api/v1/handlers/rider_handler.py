from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.v1.actions.rider_actions import RiderActions
from app.api.v1.schemas.rider_schema import (
    RiderProfileCreateRequest,
    RiderProfileUpdateRequest,
)
from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User


class RiderHandler:
    @staticmethod
    def create_profile(
        payload: RiderProfileCreateRequest,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return RiderActions.create_profile(payload, current_user, session)

    @staticmethod
    def list_profiles(
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return RiderActions.list_profiles(current_user, session)

    @staticmethod
    def get_profile(
        rider_id: UUID,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return RiderActions.get_profile(rider_id, current_user, session)

    @staticmethod
    def update_profile(
        rider_id: UUID,
        payload: RiderProfileUpdateRequest,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return RiderActions.update_profile(rider_id, payload, current_user, session)

    @staticmethod
    def delete_profile(
        rider_id: UUID,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return RiderActions.delete_profile(rider_id, current_user, session)
