# INTERNAL PROMPT
# Generate the name, age and city of a fictional sri lankan person 
#  The output should be formatted as a JSON instance that conforms to the JSON schema below.

# As an example, for the schema {"properties": {"foo": {"title": "Foo", "description": "a list of strings", "type": "array", "items": {"type": "string"}}}, "required": ["foo"]}
# the object {"foo": ["bar", "baz"]} is a well-formatted instance of the schema. The object {"properties": {"foo": ["bar", "baz"]}} is not well-formatted.

# Here is the output schema:
# ```
# {"properties": {"name": {"description": "Name of the person", "title": "Name", "type": "string"}, "age": {"description": "Age of the person'", "title": "Age", "type": "integer"}, "city": {"description": "Name of the city the person belongs to", "title": "City", "type": "string"}}, "required": ["name", "age", "city"]}
# ```