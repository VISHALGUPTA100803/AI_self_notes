Both use the same response_format field, but they differ in exactly the dimension you'd expect by now, whether a schema actually gets enforced or not. Let's compare them directly against the docstring's own descriptions.

json_schema: schema-aware, with real enforcement
json
"response_format": {
  "type": "json_schema",
  "json_schema": {
    "name": "Review",
    "strict": true,
    "schema": { /* your full JSON Schema: properties, types, enum, required, additionalProperties */ }
  }
}

OpenAI's API receives your entire schema, field names, types, the enum: ["pos", "neg"] constraint, required list, everything. This is what enables the grammar-based constrained decoding we went through in detail, the inference engine compiles your schema into a grammar and masks invalid tokens at generation time (especially with strict=True). The model is structurally guided toward your exact shape.

json_mode: schema-blind, only guarantees syntax
json
"response_format": {
  "type": "json_object"
}

That's it, no schema, no field names, no types, nothing. This is the entirety of what gets sent. OpenAI's only guarantee here: the output will be syntactically parseable JSON ({...} with proper quoting, brackets, commas), full stop. It has zero knowledge of what shape you actually want, no idea you expect a sentiment key, no idea pros should be a list of strings, nothing.

This is exactly why the docstring explicitly warns: "if using JSON mode then you must include instructions for formatting the output into the desired schema into the model call." The schema has to live entirely in your prompt text, in plain English, since there's no structured channel carrying it anymore.