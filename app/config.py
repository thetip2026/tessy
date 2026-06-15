from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    bot_token: str = Field(alias="BOT_TOKEN")
    bot_username: str = Field(alias="BOT_USERNAME")
    base_url: str = Field(alias="BASE_URL")

    # Security
    webhook_secret: str = Field(alias="WEBHOOK_SECRET")
    admin_chat_ids: str = Field(alias="ADMIN_CHAT_IDS")
    admin_api_key: str = Field(alias="ADMIN_API_KEY")
    admin_username: str = Field(alias="ADMIN_USERNAME")
    admin_password: str = Field(alias="ADMIN_PASSWORD")
    session_secret: str = Field(alias="SESSION_SECRET")

    # Database
    database_url: str = Field(alias="DATABASE_URL")

    # NOWPayments
    nowpayments_api_key: str = Field(alias="NOWPAYMENTS_API_KEY")
    nowpayments_ipn_secret: str = Field(alias="NOWPAYMENTS_IPN_SECRET")
    nowpayments_base_url: str = Field(
        alias="NOWPAYMENTS_BASE_URL",
        default="https://api.nowpayments.io/v1",
    )
    default_currency: str = Field(alias="DEFAULT_CURRENCY", default="gbp")
    order_expiry_minutes: int = Field(alias="ORDER_EXPIRY_MINUTES", default=90)

    # Redis / Cookies
    redis_url: str = Field(alias="REDIS_URL", default="redis://localhost:6379/0")
    secure_cookies: bool = Field(alias="SECURE_COOKIES", default=True)

    @property
    def admin_ids(self) -> list[int]:
        return [int(x.strip()) for x in self.admin_chat_ids.split(",") if x.strip()]


settings = Settings()
