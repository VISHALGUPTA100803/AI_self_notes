Good clarifying question, and there's an important distinction hiding in it: additional_kwargs and response_metadata are fields that exist on all message types structurally, but they're only ever meaningfully populated on AIMessage. SystemMessage and HumanMessage are messages you construct and send, there's no "response" to attach metadata to, since nothing generated them, you wrote them. Let's break down what each field actually does, using outputs you've already seen in this conversation.

additional_kwargs

Purpose: a catch-all bucket for provider-specific extras that don't fit LangChain's standard AIMessage schema, but that the provider included in its raw response anyway.

Remember this from way back in your OpenAI response:

python
additional_kwargs={'refusal': None}

refusal is an OpenAI-specific field (used when their moderation layer blocks/refuses part of a response), it's not something Anthropic or Gemini's API returns, so it doesn't belong as a first-class field on the universal AIMessage schema. Rather than forcing every provider's oddities into rigid top-level fields, LangChain dumps whatever provider-specific extras exist into additional_kwargs, keeping the main schema clean while still preserving that data if you need it.

For Anthropic and Gemini responses you generated earlier, additional_kwargs came back as {}, empty, because those providers didn't attach any extra non-standard fields to those particular responses.

response_metadata

Purpose: the raw, provider-native response details, unprocessed, exactly as that provider's API returned them. This is the field we spent a lot of time comparing earlier across OpenAI, Anthropic, and Gemini.

Recall the side-by-side comparison you asked for:

python
# OpenAI
response_metadata={'token_usage': {...}, 'finish_reason': 'length', 'model_name': 'gpt-5-nano-2025-08-07', 'system_fingerprint': None, ...}

# Anthropic
response_metadata={'id': 'msg_...', 'model': 'claude-haiku-4-5-20251001', 'stop_reason': 'end_turn', 'usage': {...}, ...}

# Gemini
response_metadata={'finish_reason': 'STOP', 'model_name': 'gemini-3.1-flash-lite', 'safety_ratings': [], ...}

Each provider structures this completely differently (finish_reason vs stop_reason, different casing, different nested fields), because LangChain doesn't normalize this field at all, it's a direct passthrough of whatever that provider's raw API response contained. It's your "escape hatch" to access provider-specific details (safety ratings, system fingerprints, exact stop reasons) that aren't part of LangChain's universal AIMessage interface.

Why only AIMessage has these populated meaningfully
	SystemMessage	HumanMessage	AIMessage
Who creates it	You, before sending	You, before sending	The model, as its response
Has real additional_kwargs?	Technically exists on the class, but empty, since you wrote it, there's no provider response to attach extras from	Same, empty	Populated, whatever extras the provider included
Has real response_metadata?	Same, empty	Same, empty	Populated, the provider's raw response details

If you were to print a SystemMessage or HumanMessage you constructed yourself, you'd technically see these fields exist (they're part of the base BaseMessage class all message types inherit from), but they'd just be empty dicts {}, since nothing generated a "response" for a message you wrote yourself, there's nothing for the provider to attach.