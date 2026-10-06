The prompt asks the model to follow the schema; Python validates the response afterward. PydanticOutputParser does both jobs separately.
Before the model runs:
parser.get_format_instructions()
This generates the instructions you pasted. The model can still disobey them.
After the model responds:
person = parser.invoke(result)
The parser roughly does this internally:
data = parse_json_markdown(response_text)  # JSON → dictionary
person = Person.model_validate(data)       # Pydantic validation
return person
Suppose your Pydantic model is:
class Person(BaseModel):
    name: str
    age: int
    city: str
These responses behave differently:
{"name": "Nimal", "age": 25, "city": "Colombo"}
# Passes → returns a Person object
{"name": "Nimal", "age": "hello", "city": "Colombo"}
# Fails → "hello" cannot be validated as an integer
{"name": "Nimal", "age": 25}
# Fails → required field "city" is missing
Validation failures are reported as OutputParserException.
One detail: Pydantic can convert compatible values by default, so "25" may become integer 25. And age: int alone doesn’t reject negative ages; you must declare a constraint such as Field(ge=0).
Schema → prompt instructions → model response
                                  ↓
                            JSON parsing
                                  ↓
                         Pydantic validation
                                  ↓
                            Person object
The validation comes from the Pydantic code executed after generation, not from the internal prompt. 



Your prompt contains the task, an example explaining JSON Schema, and the schema for your person.
1. The task
Generate the name, age and city of a fictional Sri Lankan person.
This tells the model what information to generate.
2. The formatting instruction
The output should be formatted as a JSON instance
that conforms to the JSON schema below.
A JSON schema describes the structure. A JSON instance is the actual data that follows that structure.
3. The foo example
The example teaches the model that this schema:
{
    "properties": {
        "foo": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["foo"]
}
expects data like:
{"foo": ["bar", "baz"]}
It should not copy the schema’s properties wrapper into its answer:
{"properties": {"foo": ["bar", "baz"]}}
foo is only a generic example; it isn’t a field in your person output.
4. Your actual schema
Here is your schema formatted for readability:
{
    "properties": {
        "name": {
            "description": "Name of the person",
            "title": "Name",
            "type": "string"
        },
        "age": {
            "description": "Age of the person",
            "title": "Age",
            "type": "integer"
        },
        "city": {
            "description": "Name of the city the person belongs to",
            "title": "City",
            "type": "string"
        }
    },
    "required": ["name", "age", "city"]
}
The schema keywords mean:
Keyword	Meaning
properties	Describes the fields the output can contain
type	Expected value type: text for string, whole number for integer
description	Explains what information belongs in the field
title	A readable label for the field
required	Lists fields that must be present


So the model should return actual values, like:
{
    "name": "Nimal Perera",
    "age": 28,
    "city": "Colombo"
}
Then PydanticOutputParser parses this response and validates it against your Python model. The schema checks the declared structure and types 



PydanticOutputParser raises an OutputParserException containing the validation error. It doesn’t automatically retry the model.
You can catch it:
from langchain_core.exceptions import OutputParserException

try:
    person = parser.invoke(result)
    print(person)
except OutputParserException as error:
    print("Validation failed:", error)
Remember: "25" may be converted to integer 25 by default, so that usually passes. "twenty" fails.