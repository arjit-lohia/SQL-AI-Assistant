from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

Dialect = Literal["sqlite", "postgres", "mysql"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Turn(StrictModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)
    sql: str | None = Field(default=None, max_length=12000)
    dialect: Dialect = "sqlite"


class ChatRequest(StrictModel):
    message: str = Field(min_length=1, max_length=4000)
    dialect: Dialect = "sqlite"
    mode: Literal["generate", "optimize", "debug"] = "generate"
    execute: bool = False
    history: list[Turn] = Field(default_factory=list, max_length=16)

    @model_validator(mode="after")
    def bounded(self):
        if not self.message.strip():
            raise ValueError("Please enter a SQL or database question.")
        if sum(len(t.content) + len(t.sql or "") for t in self.history) > 24000:
            raise ValueError("Conversation context is too long. Start a new conversation.")
        return self


class ExecuteRequest(StrictModel):
    sql: str = Field(min_length=1, max_length=12000)
    dialect: Dialect = "sqlite"


class ModelOutput(StrictModel):
    status: Literal["success", "refused", "clarification"]
    sql: str | None = Field(default=None, max_length=12000)
    explanation: str = Field(default="", max_length=4000)
    message: str = Field(default="", max_length=2000)
    assumptions: list[str] = Field(default_factory=list, max_length=10)
    suggestions: list[str] = Field(default_factory=list, max_length=10)

    @model_validator(mode="after")
    def sql_matches_status(self):
        if (self.status == "success") != bool(self.sql and self.sql.strip()):
            raise ValueError("Only successful responses must include SQL.")
        if any(len(s) > 1000 for s in self.assumptions + self.suggestions):
            raise ValueError("Model notes exceeded the size limit.")
        return self
