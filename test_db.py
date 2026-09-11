from sqlalchemy import create_engine, text

from app.backend.core.config import settings


def test_connection():
    print(
        f"Connecting to: "
        f"{settings.DB_HOST}:{settings.DB_PORT}/"
        f"{settings.DB_NAME}..."
    )

    connect_args = {
        "ssl": {
            "ssl_mode": "VERIFY_IDENTITY"
        }
    }

    try:
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args=connect_args,
            pool_pre_ping=True
        )

        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT VERSION();")
            )

            version = result.scalar()

            print(
                "\nKết nối thành công tới TiDB Cloud."
            )

            print(
                f"TiDB Version: {version}"
            )

    except Exception as error:
        print(
            "\nKết nối tới TiDB Cloud thất bại."
        )

        print(
            f"Error: {error}"
        )


if __name__ == "__main__":
    test_connection()