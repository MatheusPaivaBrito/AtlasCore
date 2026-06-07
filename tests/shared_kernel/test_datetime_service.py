from datetime import UTC, datetime

from shared_kernel.time import DateTimeService


def test_datetime_service_returns_timezone_aware_utc_now() -> None:
    value = DateTimeService.utc_now()

    assert value.tzinfo is UTC


def test_datetime_service_converts_naive_values_to_utc() -> None:
    value = datetime(2026, 6, 6, 12, 0, 0)

    converted = DateTimeService.to_utc(value)

    assert converted.tzinfo is UTC
    assert converted.hour == 12


def test_datetime_service_falls_back_to_utc_for_invalid_timezone() -> None:
    value = DateTimeService.to_iso(
        datetime(2026, 6, 6, 12, 0, 0, tzinfo=UTC),
        timezone="Invalid/Timezone",
    )

    assert value == "2026-06-06T12:00:00+00:00"
