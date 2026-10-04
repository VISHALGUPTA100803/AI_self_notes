What TypedDict is

It lets you describe the expected shape of a dictionary, which keys it should have and what type each value should be, without creating an actual class with real enforcement like Pydantic does.

python
from typing import TypedDict

class Movie(TypedDict):
    title: str
    year: int

movie: Movie = {"title": "Inception", "year": 2010}

This looks almost identical to a regular dict, because it is one at runtime. TypedDict exists purely to tell your editor/type-checker "this variable should be a dict shaped like this," for documentation and tooling purposes.

Proof that it does NOT validate: this runs with zero errors
python
from typing import TypedDict

class Movie(TypedDict):
    title: str
    year: int

bad_movie: Movie = {"title": "Inception", "year": "two thousand ten"}  # wrong type!
bad_movie2: Movie = {"title": "Inception"}  # missing required key!
bad_movie3: Movie = {"title": "Inception", "year": 2010, "extra": "oops"}  # extra key!

print(bad_movie)   # runs completely fine, no error
print(bad_movie2)  # runs completely fine, no error
print(bad_movie3)  # runs completely fine, no error

None of these throw an error when you actually run the script. TypedDict only exists in the type-checking layer, if you ran mypy your_script.py (a separate static analysis tool), that would flag these as type errors. But Python's interpreter itself never looks at the TypedDict definition while executing your code, it's invisible at runtime, purely a hint for tools and humans reading the code.