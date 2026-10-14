Only partly. LCEL has shorthand for sequence, parallel and lambda, but not for branch.

1. RunnableSequence: the | operator

python
chain = prompt | model | parser
# same as RunnableSequence(prompt, model, parser)
# also same as prompt.pipe(model, parser)

2. RunnableParallel: a plain dict

When a dict appears in a chain, LangChain automatically converts it to a RunnableParallel. Each value runs on the same input and the results come back as a dict with the same keys.

python
chain = {
    "context": retriever,
    "question": RunnablePassthrough(),
} | prompt | model | parser

# same as
RunnableParallel(context=retriever, question=RunnablePassthrough()) | prompt | model | parser

One catch: the dict must be combined with a runnable through | for the conversion to happen. A dict on its own is just a dict.

3. RunnableLambda: a plain Python function or lambda

Any function placed in a chain is automatically wrapped as a RunnableLambda.

python
def to_upper(x):
    return x.upper()

chain = prompt | model | parser | to_upper
chain = prompt | model | (lambda msg: msg.content)

You can also use the @chain decorator, which turns a function into a RunnableLambda explicitly:

python
from langchain_core.runnables import chain

@chain
def my_step(x):
    return x.upper()

4. RunnableBranch: no shorthand, explicit class only

python
from langchain_core.runnables import RunnableBranch

branch = RunnableBranch(
    (lambda x: "math" in x["topic"], math_chain),
    (lambda x: "code" in x["topic"], code_chain),
    general_chain,   # default, last argument
)

The conditions are checked in order, the first true one runs, and the last argument is the fallback.

A popular alternative to RunnableBranch

Many people prefer a RunnableLambda that returns a runnable. LangChain invokes the returned runnable automatically, so you get routing with normal Python if and else logic.

python
def route(info):
    if "math" in info["topic"]:
        return math_chain
    elif "code" in info["topic"]:
        return code_chain
    return general_chain

full_chain = {"topic": classifier_chain, "question": lambda x: x["question"]} | RunnableLambda(route)

Related helpers worth knowing

RunnablePassthrough() passes the input through unchanged.
RunnablePassthrough.assign(new_key=some_runnable) keeps the input dict and adds a new computed key to it.
.with_retry(), .with_fallbacks() and .with_config() wrap any runnable with extra behavior.


You’re right, and I overstated it. A dict or function is ordinary Python, not LCEL syntax. What LangChain does is accept them as shorthand and convert them into runnables when they are composed with |.

Strictly speaking

Runnable	LCEL way to create it	Shortcut LangChain tolerates
RunnableSequence	| operator (or .pipe())	none needed, this is the LCEL operator
RunnableParallel	RunnableParallel(...) class	a dict next to |, converted automatically
RunnableLambda	RunnableLambda(fn) class or @chain decorator	a function next to |, converted automatically
RunnableBranch	RunnableBranch(...) class	none

So your original question has this answer: | is the only real LCEL operator. For parallel, lambda and branch, the proper way is to use the explicit classes.

The dict and function shortcuts are just coercion. LangChain checks “is this thing a Runnable? If not, is it a dict or a callable?” and wraps it for you. That is a convenience, and it only works when one side of the | is already a runnable. 


# dict as one argument
RunnableParallel({
    "tweet": RunnableSequence(prompt1, model, parser),
    "linkedin": RunnableSequence(prompt2, model, parser),
})

# keyword arguments
RunnableParallel(
    tweet=RunnableSequence(prompt1, model, parser),
    linkedin=RunnableSequence(prompt2, model, parser),
)