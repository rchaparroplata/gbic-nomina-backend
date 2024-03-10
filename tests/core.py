from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False,
                                   autoflush=False,
                                   bind=engine)


# Dependency to override the get_db dependency in the main app
def ovrd_get_db():
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()
