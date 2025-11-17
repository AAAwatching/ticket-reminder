from pydantic import BaseModel, Field, HttpUrl, root_validator
from typing import Optional, Dict, Any

class Config(BaseModel):
    send_email_notifications: bool = Field(True, description="Whether to send email notifications when tickets are available.")
    target_url: Optional[HttpUrl] = Field(None, description="Initial URL to navigate to. If None, user navigates manually.")
    check_interval_seconds: int = Field(30, ge=1, description="Time interval between checks in seconds.")
    smtp_server: str = Field(..., description="SMTP server address.")
    smtp_port: int = Field(587, description="SMTP server port.")
    smtp_user: str = Field(..., description="SMTP username (usually email address).")
    smtp_password: str = Field(..., description="SMTP password or app-specific password.")
    notification_email: Optional[str] = Field(None, description="Email address for sending and receiving notifications. If not provided, smtp_user is used.")

    @root_validator(pre=False, skip_on_failure=True)
    def set_notification_email_if_not_provided(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not values.get('notification_email'):
            values['notification_email'] = values.get('smtp_user')
        return values
