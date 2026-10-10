Retriever gets candidates (high recall).

Reranker decides the best order (high precision).

Let's build the intuition from scratch.

Stage 1: Retrieval

Suppose you have:

Plain Text

57,000 documents

User asks:

Plain Text

Where should I park my rainy-day fund?

You cannot feed 57k docs to an LLM.

So first you run:

Plain Text

BM25

+

Dense Search

+

RRF

and get:

Plain Text

Top 50 candidate docs

Example:

Plain Text

Rank Doc

1 D123

2 D555

3 D888

...

50 D702

These are "possibly relevant".

Notice:

Plain Text

Possibly relevant ≠ Best relevant

Why Retrieval Is Not Enough

Dense retrieval uses a bi-encoder.

Query:

Plain Text

Where should I park my rainy-day fund?

Document:

Plain Text

Keep emergency cash in a high-yield savings account.

Bi-encoder creates:

Plain Text

Query -> vector

Doc -> vector

``

Then:

Plain Text

cosine_similarity(query_vector, doc_vector)

is computed.

The Problem

The vectors are created independently.

Plain Text

Query Encoder

↓

Query Vector

 

Document Encoder

↓

Document Vector

``

The model never directly compares words inside the query and document.

It only compares the final vectors.

Bi-Encoder Dry Run

Imagine:

Plain Text

Query:

Where should I park my rainy-day fund?

 

Vector:

[0.12, 0.55, 0.88]

Document A:

Plain Text

Rainy day funds belong in safe liquid accounts.

Vector:

Plain Text

[0.11, 0.58, 0.84]

Similarity:

Plain Text

0.95

Document B:

Plain Text

Emergency cash should be kept in a savings account.

Vector:

Plain Text

[0.13, 0.54, 0.86]

Similarity:

Plain Text

0.94

Retriever says:

Plain Text

D-A score 0.95

D-B score 0.94

Looks fine.

But what if:

Document C:

Plain Text

Do NOT keep emergency savings in checking accounts.

The word:

Plain Text

NOT

changes everything.

A bi-encoder may miss subtle differences.

Enter Cross Encoder (Reranker)

Instead of encoding separately:

Plain Text

Query

Doc

 

it combines them.

Input:

Plain Text

[CLS]

 

Where should I park my rainy-day fund?

 

[SEP]

 

Keep emergency cash in a high-yield savings account.

 

[SEP]

Fed into transformer:

Plain Text

Transformer

↓

Single relevance score

Output:

Plain Text

0.98

Why Is This Better?

Now attention layers can directly connect words.

Example:

Plain Text

Query:

rainy day fund

``

To:

Plain Text

Document:

emergency cash

The model learns:

Plain Text

rainy day fund ≈ emergency savings

Another example

Query:

Plain Text

Can I withdraw money immediately?

 

Document A:

Plain Text

Funds are liquid and available immediately.

Score:

Plain Text

0.99

Document B:

Plain Text

Funds cannot be withdrawn for one year.

Score:

Plain Text

0.05

Because the transformer sees:

Plain Text

immediately

versus

Plain Text

cannot

 

inside the same attention computation.

Architecture Comparison

Bi Encoder

Plain Text

Query

↓

Encoder

↓

Vector

 

Document

↓

Encoder

↓

Vector

 

Cosine Similarity

Output:

Plain Text

Fast

Less accurate

Cross Encoder

Plain Text

Query + Document

↓

Transformer

↓

Relevance Score

Output:

Plain Text

Slow

More accurate

Why Not Use Cross Encoder On 57k Docs?

Imagine:

Plain Text

57,000 docs

For every query:

Plain Text

(Query, Doc1)

(Query, Doc2)

(Query, Doc3)

...

(Query, Doc57000)

Need:

Plain Text

57,000 transformer runs

Way too expensive.

Two Stage Pipeline

Stage 1

Cheap retrieval.

Plain Text

57k docs

↓

BM25

+

Dense Search

↓

Top 50 Docs

Stage 2

Expensive reranking.

Plain Text

50 Docs

↓

Cross Encoder

↓

Top 10

Dry Run of Your Code

Suppose:

Python

candidate_ids = hybrid_candidates(query, candidate_k=50)

returns:

Python

[

"D1",

"D2",

"D3",

...

]

Then:

Python

candidate_texts = [

corpus_by_id.loc[d, "text"]

for d in candidate_ids

]

``

returns:

Python

[

"Rainy day funds should be liquid...",

"Invest emergency cash in stocks...",

...

]

Then:

Python

response = co.rerank(

model="rerank-v4.0-fast",

query=query,

documents=candidate_texts,

top_n=10,

)

Internally Cohere does:

Plain Text

(Query, Doc1) -> 0.97

(Query, Doc2) -> 0.12

(Query, Doc3) -> 0.83

(Query, Doc4) -> 0.91

...

Output might be:

Python

response.results

=

[

(index=0, score=0.97),

(index=3, score=0.91),

(index=2, score=0.83)

]

Notice:

Python

index = 3

means:

Python

candidate_texts[3]

not the document ID.

Then:

Python

return [

(candidate_ids[r.index],

r.relevance_score)

for r in response.results

]

converts:

Python

index=3

back to the original ID.

Result:

Python

[

("D1", 0.97),

("D4", 0.91),

("D3", 0.83)

]

Why Reranking Improves NDCG

Before reranking:

Plain Text

1. Doc A

2. Doc B

3. Doc C

...

12. Correct Answer

The right document exists but is buried.

After reranking:

Plain Text

1. Correct Answer

2. Doc A

3. Doc B

...

Now highly relevant docs move to the top.

Since NDCG rewards:

Plain Text

Relevant docs

+

Higher ranks

the score increases.

That's why adding a cross-encoder reranker often gives a noticeable NDCG@10 improvement even when retrieval recall was already good. The retriever's job is "don't miss good docs", while the reranker's job is "put the best docs at the very top."