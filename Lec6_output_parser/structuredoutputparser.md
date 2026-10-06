    Yes—get_format_instructions() generates those formatting instructions internally. Your PromptTemplate combines them with the topic to create the complete prompt.
    But the parser has two separate jobs:
    BEFORE the LLM
    parser.get_format_instructions()
        → Generates instructions to include in the prompt

    AFTER the LLM
    parser.invoke(response)
        → Reads the returned JSON and checks that the required keys exist
        → Returns a Python dictionary

    This is the prompt text the LLM receives, with the newline (\n) and tab (\t) characters displayed normally:
    give 3 facts on a human body

    The output should be a markdown code snippet formatted in the following
    schema, including the leading and trailing "```json" and "```":

    ```json
    {
        "fact_1": string  // Fact 1 about the topic
        "fact_2": string  // Fact 2 about the topic
        "fact_3": string  // Fact 3 about the topic
    }
    ```

    Checking required keys is validation. My earlier wording was imprecise.
    StructuredOutputParser performs limited validation:
    - It checks that the response can be parsed as JSON.
    - It checks that the required keys exist.
    - It doesn’t check whether their values match the declared types.
    For example, if fact_1 should be a string:
    {"fact_1": 123}
    The key check passes because "fact_1" exists. A type check would fail because 123 isn’t a string—but StructuredOutputParser doesn’t perform that check.
    So saying “it does no validation” is too broad. It validates key presence, but doesn’t fully validate the schema.