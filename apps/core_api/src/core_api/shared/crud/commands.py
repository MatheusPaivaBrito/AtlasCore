from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel


@dataclass(frozen=True)
class CreateResourceCommand:
    payload: BaseModel


@dataclass(frozen=True)
class UpdateResourceCommand:
    resource_id: UUID
    payload: BaseModel


@dataclass(frozen=True)
class DeleteResourceCommand:
    resource_id: UUID


@dataclass(frozen=True)
class RestoreResourceCommand:
    resource_id: UUID
