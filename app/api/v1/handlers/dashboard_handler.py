from sqlalchemy.orm import Session

from app.api.v1.actions.dashboard_actions import DashboardActions


class DashboardHandler:
    def __init__(self, db: Session):
        self.actions = DashboardActions(db)

    def handle_summary(self):
        return self.actions.get_summary()
