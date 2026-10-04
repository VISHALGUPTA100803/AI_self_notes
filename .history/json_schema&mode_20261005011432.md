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

Side-by-side
	json_schema	json_mode
Schema sent to OpenAI?	Yes, full JSON Schema	No, nothing
Guarantee	Valid JSON matching your exact shape (especially with strict=True)	Valid JSON syntax only, any shape
Where the shape comes from	The schema itself, enforced via constrained decoding	Your prompt wording, pure instruction-following, no enforcement
Field descriptions (Field(description=...)) reach the model?	Yes, embedded in the schema the model effectively operates under	No, you'd have to manually restate them in prose
Risk of wrong/missing/extra keys	Low, especially with strict=True	High, entirely dependent on the model correctly following your written instructions
Literal["pos", "neg"] enforced as only possible values?	Yes, mechanically, via enum in the schema	No, the model could technically write "positive" instead, nothing stops it syntactically
Concrete illustration using your own Review example

With json_schema: the model is mechanically prevented from writing anything except "pos" or "neg" for sentiment, that constraint comes from the compiled grammar.

With json_mode, using the docstring's own example pattern:

python
structured_model.invoke(
    "Answer the following question. "
    "Make sure to return a JSON blob with keys 'answer' and 'justification'.\n\n"
    "What's heavier a pound of bricks or a pound of feathers?"
)

Notice the key names ('answer', 'justification') are spelled out in the prompt text itself, not in any schema field. If you wanted sentiment restricted to "pos"/"neg" under json_mode, you'd have to write something like "...and a 'sentiment' key whose value must be exactly the string 'pos' or 'neg', nothing else" directly into your prompt, and even then, it's just an instruction the model is trying to follow, not a structural guarantee, it could still occasionally slip and write "positive" instead, since there's no grammar masking blocking that token sequence.