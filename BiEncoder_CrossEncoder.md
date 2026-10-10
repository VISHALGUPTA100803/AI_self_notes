Plain Text

Query -----------------> Encoder ----------> Query Vector

 

Document -------------> Encoder ----------> Doc Vector

 

Query Vector

vs

Doc Vector

↓

Cosine Similarity

The query and document are encoded separately.

Cross-Encoder

Plain Text

[CLS] Query [SEP] Document [SEP]

↓

Transformer

↓

Relevance Score

The query and document are fed into the model together.

Let's Understand the Transformer Internals

Suppose the query is:

Plain Text

Where should I park my rainy-day fund?

Document:

Plain Text

Keep emergency savings in a high-yield savings account.

Bi-Encoder Internal Flow

Step 1: Query Tokens

Plain Text

Where

should

I

park

my

rainy-day

fund

↓

Tokenizer

Plain Text

["where", "should", "park", "rainy", "day", "fund"]

↓

Embeddings

Plain Text

e1

e2

e3

e4

e5

e6

↓

Transformer Encoder

Attention Inside Query Only

Each query token can attend to other query tokens.

Plain Text

where ←→ fund

park ←→ rainy

rainy ←→ day

But it cannot see document words.

Result:

Plain Text

Query Vector

 

Q = [0.22, 0.91, ...]

Step 2: Document

Document:

Plain Text

Keep emergency savings in a high-yield savings account

↓

Tokenizer

Plain Text

keep

emergency

savings

high

yield

savings

account

↓

Transformer

Attention Inside Document Only

Plain Text

emergency ↔ savings

high ↔ yield

savings ↔ account

Again:

Plain Text

document tokens cannot see query tokens

Result:

Plain Text

Doc Vector

 

D = [0.19, 0.88, ...]

Step 3: Similarity

Now compare:

Plain Text

Q = [0.22, 0.91...]

 

D = [0.19, 0.88...]

Cosine:

Plain Text

0.94

Done.

Important Limitation

Suppose:

Query:

Plain Text

How to reset password?

Document A:

Plain Text

Reset your password here.

Document B:

Plain Text

Do NOT reset your password here.

`

A bi-encoder may produce similar vectors.

Why?

Because:

Plain Text

reset

password

appear strongly in both.

The model never directly compares:

Plain Text

question

to

Plain Text

NOT

``

inside one attention graph.

Cross-Encoder Internal Flow

Now let's look at the same example.

Input becomes:

Plain Text

[CLS]

 

How to reset password?

 

[SEP]

 

Do NOT reset your password here.

 

[SEP]

Tokens:

Plain Text

CLS

how

to

reset

password

SEP

do

not

reset

your

password

here

SEP

 

Attention Matrix

This is where magic happens.

Every token can attend to every token.

Plain Text

query token

↓

password

↓

document token

password

``

Plain Text

query token

↓

reset

↓

document token

reset

 

Plain Text

query token

↓

reset

↓

document token

NOT

The model can literally observe:

Plain Text

reset

and

Plain Text

NOT

together.

This is impossible in a bi-encoder.

Visual Attention

Bi-Encoder:

Plain Text

Query Side

 

A ↔ B ↔ C

 

Document Side

 

X ↔ Y ↔ Z

No cross communication.

Cross-Encoder:

Plain Text

A ↔ B ↔ C

↕ ↕ ↕

X ↔ Y ↔ Z

Everything talks with everything.

Why Cross Encoders Are More Accurate

Consider:

Query:

Plain Text

Which bank account is best for emergency savings?

Doc 1

Plain Text

Emergency savings should be stored in a high-yield savings account.

`

Doc 2

Plain Text

Emergency savings should not be stored in a bank account.

A cross encoder can attend:

Plain Text

best

bank

account

 

↓

 

not

stored

bank

account

and understand that the answer quality differs.

Why Bi-Encoders Scale

Suppose:

Plain Text

57,000 documents

Bi-Encoder

Compute once:

Plain Text

Doc1 -> vector

Doc2 -> vector

...

Doc57000 -> vector

 

Store them.

At query time:

Plain Text

Query -> vector

Then:

Plain Text

57,000 cosine similarities

 

Very fast.

Milliseconds.

Why Cross Encoders Do Not Scale

For one query:

Plain Text

(Query, Doc1)

(Query, Doc2)

(Query, Doc3)

...

(Query, Doc57000)

``

Need:

Plain Text

57,000 full transformer passes

Every query.

Very expensive.

Complexity Intuition

Bi Encoder

Offline:

Plain Text

57k transformer runs

(one-time indexing)

Query time:

Plain Text

1 transformer run

+

vector comparisons

Fast.

Cross Encoder

Query time:

Plain Text

57k transformer runs

for every search.

Not practical.

That's Why RAG Uses Both

Retrieval

Use bi-encoder.

Plain Text

57,000 docs

↓

Top 50 candidates

Fast.

Reranking

Use cross-encoder.

Plain Text

50 candidates

↓

Top 10 best

Accurate.

One-Line Interview Answer

Bi-Encoder:

Query and document are encoded independently into vectors. Retrieval is performed using vector similarity. This allows document embeddings to be precomputed, making search very fast but less interaction-aware.

Cross-Encoder:

Query and document are concatenated and processed together by the transformer. Self-attention operates across both query and document tokens, enabling fine-grained relevance reasoning and producing a direct relevance score. This is much more accurate but computationally expensive because it must be run for every query-document pair.