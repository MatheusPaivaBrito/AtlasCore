from auth_api.infrastructure.settings import AuthSettings
from core_api.infrastructure.settings import CoreSettings
from eventing_api.infrastructure.settings import EventingSettings
from notification_api.infrastructure.settings import NotificationSettings
from observability_api.infrastructure.settings import ObservabilitySettings


def test_service_settings_read_api_specific_service_names() -> None:
    assert CoreSettings(CORE_SERVICE_NAME="core_local").SERVICE_NAME == "core_local"
    assert AuthSettings(AUTH_SERVICE_NAME="auth_local").SERVICE_NAME == "auth_local"
    assert EventingSettings(EVENTING_SERVICE_NAME="eventing_local").SERVICE_NAME == "eventing_local"
    assert (
        NotificationSettings(NOTIFICATION_SERVICE_NAME="notification_local").SERVICE_NAME
        == "notification_local"
    )
    assert (
        ObservabilitySettings(OBSERVABILITY_SERVICE_NAME="observability_local").SERVICE_NAME
        == "observability_local"
    )
