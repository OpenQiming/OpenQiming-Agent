from pydantic import BaseModel

class ModelConfig(BaseModel):
    opening_statement: str | None = None
    suggested_questions: list
    model: dict
    user_input_form: list
    pre_prompt: str | None = None
    agent_mode: dict