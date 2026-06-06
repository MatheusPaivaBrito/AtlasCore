from pydantic import BaseModel, Field


class RelationshipExample(BaseModel):
    name: str
    description: str


class LibraryModelDescription(BaseModel):
    bounded_context: str = Field(default="library")
    examples: list[RelationshipExample]
