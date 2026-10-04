At the transformer level, grammar-constrained generation usually works after the model computes its next-token scores. It doesn’t usually change the transformer’s attention mask or its learned weights.
Imagine the model is generating a tool call with this schema:
{"city": "string"}

The process repeats for each generated token:
1. The transformer reads the input and generated prefix.
   For example, it has the user’s request and perhaps has generated the beginning of the arguments: {"ci.
2. The transformer calculates scores for possible next tokens.
   These are called logits: a score for each token in the model’s vocabulary.
3. A grammar tracker checks what can legally come next.
   It keeps track of the generated prefix and the schema. After {"ci, it might allow tokens that continue the key "city"; it would reject a token that would make the JSON invalid or introduce a forbidden key.
4. The system masks out disallowed tokens.
   In a simplified description, it sets their logits to negative infinity. They then have zero probability after the scores are converted into probabilities. The system selects the next token from the remaining options.
5. The process repeats until the model has produced a complete, schema-valid argument object, such as:
   {"city": "Delhi"}