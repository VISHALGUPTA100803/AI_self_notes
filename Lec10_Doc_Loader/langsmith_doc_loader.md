What the LangSmith document loader does

LangSmithLoader loads examples from a LangSmith dataset and turns each one into a LangChain Document. It is not for loading traces or runs. It reads the labeled input and output examples you stored in a LangSmith dataset, so you can reuse them in a pipeline.

How it works
text
LangSmith dataset --> LangSmithLoader --> list of Document objects
   (examples)                              page_content = chosen input field
                                           metadata = example id, outputs, etc.
You give it a dataset_id or dataset_name.
It fetches the examples from LangSmith through the LangSmith client, using your LANGSMITH_API_KEY.
For each example, it picks one field from the example inputs (set by content_key) as the page_content.
The rest of the example information goes into the metadata.
Example
python
from langchain_core.document_loaders import LangSmithLoader

loader = LangSmithLoader(
    dataset_name="my-qa-dataset",
    content_key="question",   # which input field becomes page_content
    limit=50,
)

docs = loader.load()
print(docs[0].page_content)
print(docs[0].metadata)