from typing import Optional, List
from uuid import UUID
from datetime import datetime, date, timedelta

from sqlalchemy import select, and_, or_, func, case
from sqlalchemy.orm import Session

from app.models.user import User
from app.repos.base import GenericRepository


class UserRepository(GenericRepository[User]):

    def __init__(self, session: Session):
        super().__init__(User, session)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = self.session.execute(stmt)
        return result.scalar_one_or_none()

    def email_exists(
        self,
        email: str,
        exclude_user_id: Optional[UUID] = None
    ) -> bool:
        query = select(User.id).where(
            and_(
                User.email == email,
                User.deleted_at.is_(None)
            )
        )

        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)

        result = self.session.execute(query)
        return result.scalar_one_or_none() is not None

    def search_users(
        self,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
        is_email_verified: Optional[bool] = None,
        role_id: Optional[UUID] = None,
        segment: Optional["UserSegment"] = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[List[User], int]:
        from app.api.v1.enums.user_enum import UserSegment
        query = (
            select(User)
            .where(User.deleted_at.is_(None))
        )
        # Use distinct count to avoid duplicates when joining with roles
        count_query = select(func.count(func.distinct(User.id))).where(User.deleted_at.is_(None))

        filters = []

        if search:
            filters.append(
                or_(
                    User.email.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%")
                )
            )

        if is_active is not None:
            filters.append(User.is_active == is_active)

        if is_superuser is not None:
            filters.append(User.is_superuser == is_superuser)

        if is_email_verified is not None:
            filters.append(User.is_email_verified == is_email_verified)

        # Role filtering is disabled in basic-auth mode.
        if role_id:
            return [], 0

        if segment:
            now = datetime.utcnow()
            if segment == UserSegment.NEW:
                first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                filters.append(User.joined_date >= first_of_month)
            elif segment == UserSegment.ACTIVE:
                thirty_days_ago = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
                filters.append(User.last_login_at >= thirty_days_ago)
            elif segment == UserSegment.VIP:
                filters.append(User.is_vip == True)

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        total = self.session.execute(count_query).scalar_one()

        result = self.session.execute(
            query.order_by(User.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(result.scalars().all()), total

    def increment_failed_login(self, user_id: UUID) -> None:
        user = self.get_by_id(user_id)
        if user:
            user.failed_login_attempts += 1
            self.session.flush()

    def reset_failed_login(self, user_id: UUID) -> None:
        user = self.get_by_id(user_id)
        if user:
            user.failed_login_attempts = 0
            user.locked_until = None
            self.session.flush()

    def lock_account(self, user_id: UUID, until: datetime) -> None:
        user = self.get_by_id(user_id)
        if user:
            user.locked_until = until
            self.session.commit()

    def unlock_account(self, user_id: UUID) -> None:
        user = self.get_by_id(user_id)
        if user:
            user.failed_login_attempts = 0
            user.locked_until = None
            self.session.commit()

    def verify_email(self, user_id: UUID) -> None:
        user = self.get_by_id(user_id)
        if user:
            user.is_email_verified = True
            user.email_verified_at = datetime.utcnow()
            self.session.commit()

    def update_last_login(self, user_id: UUID, ip_address: str) -> None:
        user = self.get_by_id(user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            user.last_login_ip = ip_address
            self.session.commit()

    def count_total_users(self) -> int:
        return self.session.execute(
            select(func.count(User.id)).where(User.deleted_at.is_(None))
        ).scalar_one()

    def count_active_users(self) -> int:
        return self.session.execute(
            select(func.count(User.id)).where(
                and_(User.is_active == True, User.deleted_at.is_(None))
            )
        ).scalar_one()

    def count_inactive_users(self) -> int:
        return self.session.execute(
            select(func.count(User.id)).where(
                and_(User.is_active == False, User.deleted_at.is_(None))
            )
        ).scalar_one()

    def count_users_by_role(self, role_name: str) -> int:
        return 0

    def count_vendors(self) -> int:
        """Count users with vendor role (case-insensitive matching)"""
        return self.count_users_by_role("vendor")

    def _get_segment_filters(self, segment: Optional["UserSegment"]) -> list:
        from app.api.v1.enums.user_enum import UserSegment
        filters = [User.deleted_at.is_(None)]
        if not segment or segment == UserSegment.ALL:
            return filters
            
        now = datetime.utcnow()
        if segment == UserSegment.NEW:
            first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            filters.append(User.joined_date >= first_of_month)
        elif segment == UserSegment.ACTIVE:
            thirty_days_ago = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
            filters.append(User.last_login_at >= thirty_days_ago)
        elif segment == UserSegment.VIP:
            filters.append(User.is_vip == True)
        return filters

    def get_analytics_summary(self) -> dict:
        """Get counts for user segments: All, New, Active, VIP"""
        now = datetime.utcnow()
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        thirty_days_ago = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
        
        all_count = self.session.execute(
            select(func.count(User.id)).where(User.deleted_at.is_(None))
        ).scalar_one()
        
        new_count = self.session.execute(
            select(func.count(User.id)).where(
                and_(User.joined_date >= first_of_month, User.deleted_at.is_(None))
            )
        ).scalar_one()
        
        active_count = self.session.execute(
            select(func.count(User.id)).where(
                and_(User.last_login_at >= thirty_days_ago, User.deleted_at.is_(None))
            )
        ).scalar_one()
        
        vip_count = self.session.execute(
            select(func.count(User.id)).where(
                and_(User.is_vip == True, User.deleted_at.is_(None))
            )
        ).scalar_one()
        
        return {
            "all": all_count,
            "new": new_count,
            "active": active_count,
            "vip": vip_count
        }

    def get_age_demographics(self, segment: Optional["UserSegment"] = None) -> List[dict]:
        from app.api.v1.enums.user_enum import UserSegment
        """Group users by age ranges"""
        filters = self._get_segment_filters(segment)
        filters.append(User.date_of_birth.is_not(None))
        
        # Calculate age using SQL to be efficient
        age_expr = func.extract('year', func.age(User.date_of_birth))
        
        stmt = (
            select(
                case(
                    (age_expr < 25, "18-24"),
                    (age_expr < 35, "25-34"),
                    (age_expr < 45, "35-44"),
                    (age_expr < 55, "45-54"),
                    else_="55+"
                ).label("group"),
                func.count(User.id).label("count")
            )
            .where(and_(*filters))
            .group_by("group")
            .order_by("group")
        )
        
        result = self.session.execute(stmt).all()
        return [{"group": r.group, "count": r.count} for r in result]

    def get_geographic_distribution(self, segment: Optional["UserSegment"] = None) -> List[dict]:
        """Group users by UAE city buckets with fixed response keys and real DB counts."""
        filters = self._get_segment_filters(segment)

        stmt = (
            select(
                User.location.label("city"),
                func.count(User.id).label("count")
            )
            .where(and_(*filters))
            .group_by(User.location)
        )

        result = self.session.execute(stmt).all()

        # Keep these 5 fixed buckets in response order.
        buckets = {
            "Dubai": 0,
            "Abu Dhabi": 0,
            "Sharjah": 0,
            "Ajman": 0,
            "Others": 0,
        }

        def normalize_bucket(city_value: Optional[str]) -> str:
            if not city_value:
                return "Others"

            normalized = city_value.strip().lower()
            normalized = normalized.replace("-", " ")
            normalized = " ".join(normalized.split())

            if normalized in {"dubai"}:
                return "Dubai"
            if normalized in {"abu dhabi", "abudhabi", "abu dabi"}:
                return "Abu Dhabi"
            if normalized in {"sharjah", "sharja"}:
                return "Sharjah"
            if normalized in {"ajman", "ajmaan"}:
                return "Ajman"
            return "Others"

        for row in result:
            bucket = normalize_bucket(row.city)
            buckets[bucket] += int(row.count or 0)

        total = sum(buckets.values())
        denominator = total if total > 0 else 1

        return [
            {
                "city": city,
                "count": count,
                "percentage": round((count / denominator) * 100, 1),
            }
            for city, count in buckets.items()
        ]