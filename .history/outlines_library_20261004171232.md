1. LangChain usually asks another system to enforce the structure
For your OpenAI example:
structured_model = model.with_structured_output(    Review,    method="json_schema",    strict=True,)


LangChain prepares the schema, sends the appropriate API parameters, and parses the response. OpenAI’s inference system performs the generation-time enforcement.
The same distinction applies to the strict function-calling example we discussed: LangChain prepares the tool definition; the provider enforces the argument structure. LangChain’s wrapper itself isn’t manipulating OpenAI’s token logits. github.com
2. With a local model, your software runs the generation loop
Suppose you load an open model through Hugging Face Transformers. The model’s weights are on your machine, and the runtime repeatedly does something conceptually like this:
# Simplified pseudocodewhile not finished:    logits = model(current_tokens)    next_token = select_token(logits)    current_tokens.append(next_token)


The neural network calculates logits. The surrounding software decides which token to select, appends it, and runs the next step.
That surrounding software is where a library can intervene.
3. Outlines inserts a logits processor before token selection
With grammar enforcement, the loop becomes:
# Simplified pseudocodewhile not finished:    logits = model(current_tokens)    allowed_tokens = grammar.allowed_next_tokens()    logits[~allowed_tokens] = float("-inf")    next_token = select_token(logits)    current_tokens.append(next_token)    grammar.accept(next_token)


Outlines builds a processor from your output constraint and supplies it to a supported local runtime. The runtime calls that processor during generation.
So the library can enforce structure because it has access between the model producing its scores and the sampler selecting a token. Outlines documents this direct access through logits processors for local models. Outlines
Think of the logits as an ordinary array:
logits = [2.1, 7.4, 3.6, ...]


Once the neural network produces that array, another piece of code can modify it. No retraining is required to set forbidden entries to -inf.
4. They generally write integrations for runtimes, rather than a new masking algorithm for every model
Llama, Qwen, and other supported models can run through the same runtime, such as Transformers.
That runtime provides a common interface:
“Here are the generated token IDs and next-token scores. Apply your processor.”

The grammar logic works through that interface. It doesn’t need to know how many attention heads the model has or how its internal layers are organized.
There are still differences to handle:
Difference	What the integration needs to handle
Tokenizer	Which characters or bytes each token ID represents
Vocabulary	Which token IDs exist and how many scores the model produces
Runtime	How to register and call the logits processor
Generation behavior	State management for batches, stopping, and other supported features


So there is separate integration code for different runtimes, and sometimes compatibility handling for particular models. But the core constraint engine is reusable. Outlines separates model integrations from backends that turn constraints into logits processors. Outlines
5. Outlines cannot directly mask a remote provider’s tokens from your machine
If you call OpenAI’s API, you don’t control its internal generation loop. An Outlines wrapper therefore relies on the provider’s supported structured-output features.
Similarly, when an inference server already supports grammar constraints, Outlines can pass the constraint to that server and let the server enforce it. Its documentation distinguishes these server/API integrations from local models whose logits it can directly steer


![alt text](image.png)