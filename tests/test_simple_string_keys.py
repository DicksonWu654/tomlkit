from typing import Any

import pytest

from tomlkit import parse
from tomlkit.items import String
from tomlkit.parser import Parser


class GeneralParser(Parser):
    pass


@pytest.mark.parametrize("parse_comment", [False, True])
@pytest.mark.parametrize(
    "text",
    [
        'name = "package"',
        "\tname  \t= \t'package' \t# comment\r\n",
        'name="snow 雪 and a tab\t" # comment\nnext = 1',
        "path = 'C:\\users\\package'",
        'a=""',
        "a=''",
        'a="""multiline\nvalue"""',
        "a='''literal\nvalue'''",
        'a="escaped\\tvalue"',
        '"quoted key" = "value"',
        'a.b = "value"',
        'a="value", next=1',
    ],
)
def test_string_key_value_preserves_source_and_trivia(
    text: str, parse_comment: bool
) -> None:
    observations = []
    for cls in (Parser, GeneralParser):
        parser = cls(text)
        try:
            key, value = parser._parse_key_value(parse_comment)
            result: Any = (
                type(key),
                key.as_string(),
                key.sep,
                type(value),
                value.as_string(),
                value.unwrap(),
                value.trivia,
            )
        except Exception as exc:
            result = type(exc), str(exc)
        observations.append(
            (result, parser._idx, parser._current, parser._marker, parser.extract())
        )
    assert observations[0] == observations[1]


@pytest.mark.parametrize("quote", ['"', "'"])
@pytest.mark.parametrize("control", ["\0", "\x08", "\n", "\r", "\x1f", "\x7f"])
def test_simple_string_control_errors_match_general_parser(
    quote: str, control: str
) -> None:
    text = f"key = {quote}start{control}end{quote}\n"
    errors = []
    for cls in (Parser, GeneralParser):
        with pytest.raises(Exception) as info:
            cls(text).parse()
        errors.append((type(info.value), str(info.value)))
    assert errors[0] == errors[1]


def test_simple_strings_in_inline_tables_and_array_tables() -> None:
    text = (
        '[[package]]\nname = "first"\n'
        "files = [{file='first.whl', hash='sha256:abc'}, {file='second.whl'}]\n"
        '[[package]]\nname = "second"\n'
    )
    doc = parse(text)
    assert doc.as_string() == text
    assert isinstance(doc["package"][0]["name"], String)
    assert doc.unwrap() == GeneralParser(text).parse().unwrap()
