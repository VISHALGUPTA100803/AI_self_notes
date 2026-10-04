First, the normal (unconstrained) generation process, as a baseline

At each step, a decoder-only transformer outputs a probability distribution over its entire vocabulary (tens of thousands of possible next tokens), for GPT-class models, often 100k+ tokens. Normally:

The model computes logits (raw scores) for every token in its vocabulary
These get converted to probabilities via softmax
A token gets sampled (or greedily picked) based on that probability distribution
That token gets appended to the sequence, and the process repeats

Nothing here cares about "is this valid JSON" or "does this match my schema", it's pure next-token prediction based on learned patterns.

What changes with response_format / JSON schema constraints: constrained decoding

This is the actual mechanism, and it happens after the model produces its logits, as an additional filtering step, not by changing the transformer's internal weights or attention computation at all.

Step 1: The JSON schema gets compiled into a formal grammar

Your schema (property names, types, the enum: ["pos", "neg"] constraint, required fields, additionalProperties: false) gets converted into something like a context-free grammar or finite state machine, a formal specification of exactly which sequences of characters/tokens are even syntactically possible at each position. Think of it like a flowchart: "after {, the only valid next things are a key name from this specific list" → "after \"sentiment\": , the only valid next tokens are \"pos\" or \"neg\"" → and so on.

Step 2: At every single decoding step, the grammar masks invalid tokens before sampling

This is the core mechanism, often called constrained decoding or grammar-based sampling. Before the model samples its next token, the inference engine checks the grammar's current state and asks "given everything generated so far, which tokens in the vocabulary are even grammatically valid right now?" Every token that would violate the schema gets its probability forced to zero (or its logit set to negative infinity), regardless of what the transformer's raw output would have naturally favored.

Concretely, for your sentiment: Literal["pos", "neg"] field: once the grammar reaches the state "we're now generating the value for the sentiment key," it restricts the valid next tokens down to only those that could spell out "pos" or "neg", every other token in the entire 100k+ vocabulary gets masked out completely. The model isn't being "persuaded" to pick one of these, it is structurally incapable of picking anything else, the probability mass gets redistributed entirely among just the valid options, then sampling proceeds as normal from that drastically narrowed set.

Step 3: This repeats token by token until the full JSON structure is complete

As generation proceeds, the grammar's "current valid state" keeps advancing, after a key name, only : is valid; after that, only the value type for that key is valid; after a value, only , or } is valid, depending on whether more required fields remain; and so on. The transformer keeps producing its normal probability distribution at every step, but a layer sitting between the model's raw output and the actual token selection continuously enforces "you may only choose from this grammatically valid subset."

Why this is categorically different from a text-based prompt instruction

This is the deep distinction worth sitting with: when you write "please format your response as JSON" in a prompt (the json_mode/manual-instruction approach), you're relying on the transformer's learned behavior to follow natural-language instructions, it's probabilistic, it can fail, it can produce almost-valid JSON with a trailing comma or a missing bracket. With grammar-constrained decoding (json_schema + strict=True), invalid output is not merely discouraged, it's made mathematically impossible to sample, because those tokens are excluded from the probability distribution entirely before sampling happens. The transformer's internal computation (attention, feed-forward layers, everything that makes it "understand" the content) is completely unchanged, it still decides what to say based on learned patterns, but an external constraint layer decides which exact tokens it's allowed to say it with.

Where strict: false (or unset) breaks down, connecting back to your earlier bug

This finally explains the TypedDict issue completely, mechanically. With strict=True, the additionalProperties: false rule becomes part of the compiled grammar itself, the grammar's state machine simply has no valid transition that allows generating any key name outside your defined schema, structurally impossible, not just discouraged. Without strict enabled, OpenAI's API treats the schema as a much softer guide rather than a compiled grammar, closer to "strongly bias toward this shape" via prompt-level conditioning and some looser decode-time nudging, but without the hard, token-by-token masking that makes deviation literally impossible. That gap, soft bias versus hard grammatical constraint, is exactly why extra fields could slip through once, then differently a second time, true grammar-constrained decoding would have made both of those outcomes structurally unreachable.

One honest caveat on precision here

The exact implementation details (whether OpenAI uses a full context-free grammar compiler, a simpler finite-state automaton for JSON specifically, or some hybrid) are not publicly documented by OpenAI in full technical detail, they treat this as proprietary infrastructure. What I've described is the well-established general technique (grammar-constrained/guided decoding) known from open research and open-source implementations (e.g., outlines, guidance, llama.cpp's grammar sampling), which OpenAI's Structured Outputs feature is understood to be built on the same principles of, but I can't point you to OpenAI's literal source code confirming the precise implementation, since it isn't public.