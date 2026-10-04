Temperature is a scalar hyperparameter applied at the final softmax step of a transformer's output layer, and it controls how sharply peaked or flat the probability distribution over the next token is. It changes nothing about the model's weights or its reasoning. It only reshapes the probabilities the model already computed, right before sampling.

Where it sits in the forward pass

The transformer's final layer produces logits: one raw, unnormalized real number per token in the vocabulary (for GPT-4 class models, vocabularies run to roughly 100k–200k tokens). These logits come from a linear projection of the last hidden state, often called the language modeling head or unembedding matrix.
Normally these logits are converted to probabilities with softmax:
𝑃
(
𝑡
𝑜
𝑘
𝑒
𝑛
𝑖
)
=
𝑒
𝑧
𝑖
∑
𝑗
𝑒
𝑧
𝑗
P(token
i
	​

)=
∑
j
	​

e
z
j
	​

e
z
i
	​

	​

Temperature T is inserted by dividing every logit by T before the exponential:
𝑃
(
𝑡
𝑜
𝑘
𝑒
𝑛
𝑖
)
=
𝑒
𝑧
𝑖
/
𝑇
∑
𝑗
𝑒
𝑧
𝑗
/
𝑇
P(token
i
	​

)=
∑
j
	​

e
z
j
	​

/T
e
z
i
	​

/T
	​


That single division is the entire mechanism. Everything else, attention, feed forward layers, all 96 or however many transformer blocks, runs identically regardless of temperature. Temperature is a post hoc, decode time transformation, not part of the network's computation.

Why dividing logits changes the shape

T = 1 leaves the distribution unchanged, this is the model's raw learned distribution.
T < 1 (for example 0.2) divides logits by a number less than one, which scales them up. Since exponentiation is convex, scaling up the gaps between logits before exponentiating makes the largest logit dominate even more. The resulting distribution becomes sharper, concentrated on the few highest probability tokens. As T → 0, this becomes argmax: the model always picks the single most likely token, fully deterministic (aside from floating point ties).
T > 1 (for example 1.5) divides logits by a number greater than one, which shrinks the gaps between them. Exponentiating smaller, closer together values makes probabilities more uniform across the vocabulary. Low probability tokens get relatively more mass, which increases the chance of sampling something surprising or unusual.
T → ∞ pushes every logit toward 0 after division, so e^0 is 1 for all tokens, meaning the distribution becomes uniform random over the whole vocabulary, completely ignoring what the model learned.

A tiny concrete example with logits [4, 2, 1] for three candidate tokens:

At T=1: softmax gives roughly [0.84, 0.11, 0.05].
At T=0.5 (logits become [8, 4, 2]): roughly [0.97, 0.02, 0.01], much sharper.
At T=2 (logits become [2, 1, 0.5]): roughly [0.53, 0.29, 0.18], much flatter.

Why this matters for output behavior

Low temperature favors the highest probability continuation at every step, which tends toward the same, most conventional phrasing the training data reinforced most strongly. Good for code generation, math, factual Q&A, function calling, anything where you want the single best answer and reproducibility.
High temperature lets the sampler occasionally pick tokens the model considers less likely but still plausible. Good for creative writing, brainstorming, varied phrasing, but it also raises the chance of incoherence or hallucination, since low probability tokens can still be wrong ones.
Temperature interacts with the sampling method applied after it. Common combinations:
Greedy decoding: always take argmax, equivalent to T→0.
Top-k sampling: keep only the k highest probability tokens, renormalize, then sample. Often combined with temperature.
Top-p (nucleus) sampling: keep the smallest set of tokens whose cumulative probability exceeds p, then sample. This is usually applied after temperature scaling, so temperature reshapes the distribution first, then top-p trims its tail.

What temperature does NOT do

It does not change attention patterns, hidden states, or which facts the model retrieved internally, those were fixed the moment the forward pass finished.
It is not applied per layer, only once, at the very last step, on the final logits.
It does not add noise to embeddings or weights, sampling randomness comes only from drawing from the reshaped probability distribution.
It is unrelated to context length, attention heads or the number of parameters, purely a decoding time knob.

In LangChain / API terms

python
from langchain_openai import ChatOpenAI

precise = ChatOpenAI(model="gpt-4o", temperature=0)     # near deterministic
creative = ChatOpenAI(model="gpt-4o", temperature=1.2)  # more varied, riskier

Most providers accept temperature in the range 0 to 2, with 0 being effectively greedy and defaults typically around 0.7 to 1.0.

Interview tip: if asked to explain temperature mechanistically, say it divides the pre-softmax logits by T before exponentiation, which sharpens the distribution as T drops toward 0 (approaching argmax) and flattens it as T rises (approaching uniform random), and that this happens entirely at the output sampling stage with no effect on the transformer's internal computation.

One-liner for your notes: Temperature scales the transformer's final logits by dividing them by T before softmax, sharpening the next token distribution toward the top choice as T approaches 0 and flattening it toward uniform randomness as T grows, without altering any internal computation of the model itself.