What actually happens server-side, as two separate paths

Path 1: messages → goes to the model

json
"messages": [{"role": "user", "content": "I recently upgraded..."}]

This gets tokenized and fed into the transformer as its actual input context, same as always. This is the only part the model's attention layers actually process and "read."

Path 2: response_format → does NOT go to the model as text, it configures the decoding layer

json
"response_format": {"type": "json_schema", "json_schema": {...}}

This is not injected into the model's input tokens. It's read by OpenAI's inference server infrastructure, the layer sitting around the model, and used to compile the grammar/constraint I described earlier. The model's internal weights never see this JSON schema as text to read or reason about, it's configuration for the sampling mechanism, not content for the language model to interpret.

A clearer mental picture
Request arrives at OpenAI's servers
        │
        ├── "messages" ──────────► tokenized ──► fed into the transformer ──► model generates logits per step
        │
        └── "response_format" ──► compiled into a grammar/constraint ──► applied to mask the transformer's logits at each step, BEFORE sampling

The transformer itself just keeps doing what it always does, predicting a probability distribution over the next token, based purely on the messages content it was given. It has no idea a JSON schema even exists. The schema lives entirely in the surrounding inference pipeline, which intercepts the model's raw output distribution at each step and zeroes out any token that would violate the grammar, before the final token gets sampled and appended.

Why this distinction actually matters

This is precisely why constrained decoding is more reliable than prompt-based instructions: the model isn't being "asked" to follow the schema (which it could misunderstand or ignore), the schema is enforced externally, mechanically, on every single token, regardless of what the model "wants" to generate. If the model's raw preference at some step was to generate "reviewer" instead of "name", grammar enforcement simply makes "reviewer" an impossible choice at that position, the token gets masked to zero probability before sampling ever happens. The model never "decides" to follow the schema, it's structurally unable to deviate from it.