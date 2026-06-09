from __future__ import annotations

import string

from auth_api.infrastructure.settings import settings
from auth_api.shared.exceptions import AuthWeakPasswordError


class PasswordPolicy:
    @staticmethod
    def validate(password: str) -> None:
        missing_requirements: list[str] = []

        if len(password) < settings.AUTH_PASSWORD_MIN_LENGTH:
            missing_requirements.append("min_length")
        if settings.AUTH_PASSWORD_REQUIRE_UPPERCASE and not any(character.isupper() for character in password):
            missing_requirements.append("uppercase")
        if settings.AUTH_PASSWORD_REQUIRE_LOWERCASE and not any(character.islower() for character in password):
            missing_requirements.append("lowercase")
        if settings.AUTH_PASSWORD_REQUIRE_NUMBER and not any(character.isdigit() for character in password):
            missing_requirements.append("number")
        if settings.AUTH_PASSWORD_REQUIRE_SPECIAL and not any(character in string.punctuation for character in password):
            missing_requirements.append("special")

        if missing_requirements:
            raise AuthWeakPasswordError(missing_requirements=missing_requirements)


password_policy = PasswordPolicy()
