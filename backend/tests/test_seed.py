from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import seed_data
from app.core.database import Base
from app.models.user import User


def test_default_admin_seed_is_idempotent(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    monkeypatch.setattr(seed_data, "SessionLocal", Session)

    seed_data.seed()
    seed_data.seed()

    db = Session()
    admins = db.query(User).filter(User.role == "admin").all()
    assert len(admins) == 1
    assert admins[0].full_name == "Venkatesh"
    assert admins[0].username == "venkatesh"
    assert admins[0].email == "admin@example.com"
    db.close()
