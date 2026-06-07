from fastapi import FastAPI

from shared_kernel.errors import register_exception_handlers


def register_api_exception_handlers(app: FastAPI) -> None:
    register_exception_handlers(app, service_name="notification_api")
