Field is Pydantic's way of attaching extra configuration and metadata to a model's attribute, beyond just its type hint. You've been using it throughout your Review class without us ever stopping to define it directly, so let's do that now.

Without Field: just a type hint, bare minimum
python
from pydantic import BaseModel

class Review(BaseModel):
    sentiment: str

This works, but Pydantic only knows the type. No description, no validation rules, no default value, nothing extra.

With Field: you attach metadata and constraints to that same attribute
python
from pydantic import BaseModel, Field

class Review(BaseModel):
    sentiment: str = Field(description="Return sentiment as pos or neg")

The syntax looks like you're "assigning a value" to sentiment, but you're not giving it a default value here, Field(...) is a special marker Pydantic recognizes and unpacks into configuration, not an actual runtime value for that attribute.

What Field can configure, the common parameters

description — the one you've used throughout this conversation. Becomes part of the generated JSON Schema ("description": "..."), this is literally how the model learned "pos means positive" earlier, straight from this parameter.

default — makes the field optional, used when a value isn't provided:

python
pros: Optional[list[str]] = Field(default=None, description="...")

(Exactly the pattern from your earlier question about whether default=None is needed for Optional fields.)

default_factory — like default, but for mutable defaults (lists, dicts) that shouldn't be shared across instances:

python
tags: list[str] = Field(default_factory=list)

Validation constraints — numeric/string/collection limits:

python
rating: float = Field(ge=0, le=10)           # ge = greater-or-equal, le = less-or-equal
username: str = Field(min_length=3, max_length=20)
items: list[str] = Field(min_length=1)        # at least one item required

alias — lets the field be called something different in JSON input/output vs. in your Python code:

python
user_id: int = Field(alias="userId")

title — a human-readable name, distinct from description, used in generated schemas/docs.

Concrete example pulling several together
python
class Review(BaseModel):
    rating: float = Field(ge=0, le=10, description="Overall rating out of 10")
    pros: Optional[list[str]] = Field(default=None, description="List of pros mentioned")
    reviewer_name: str = Field(alias="reviewerName", description="Name of the reviewer")

If you tried Review(rating=15, ...), Pydantic would reject it at validation time, ge=10 and le=10 are enforced, actual runtime checks, not just documentation.

Why Field matters specifically for your with_structured_output work

This connects directly to the strict=True limitation from earlier: "When using Pydantic, our model cannot specify any Field metadata (like min/max constraints) and fields cannot have default values" under strict mode. That's precisely about Field, constraints like ge, le, min_length, and default get stripped out or rejected when OpenAI's strict schema mode is active, because OpenAI's structured-output grammar compiler doesn't support that level of validation richness, it only handles basic types, enums, and required/optional shape. So description survives into strict mode (it's just schema metadata, harmless to the grammar), but numeric/length constraints and defaults don't, which is exactly why your pros/cons/name fields needed to drop their default=None the moment strict=True entered the picture.

One important distinction: is Field required to use Pydantic at all?

No, you can skip it entirely if you don't need descriptions or constraints:

python
class Review(BaseModel):
    sentiment: str
    rating: float

This is perfectly valid Pydantic. Field is purely an opt-in enhancement for cases where the bare type hint alone isn't enough information, which, for structured LLM output specifically, is almost always the case, since description is how you communicate intent to the model, bare type hints alone (sentiment: str) tell the model nothing about what to actually put there.