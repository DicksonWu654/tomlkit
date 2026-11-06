from __future__ import annotations

import pytest

from tomlkit import parse
from tomlkit.exceptions import KeyAlreadyPresent
from tomlkit.parser import Parser


@pytest.mark.parametrize(
    "body",
    [
        'name = "pkg", version = "1.2.3", optional = true',
        'x.y=1, z="two", x.z=[3, 4]',
        'x={y=1}, z=[{a="b"}, {c=2}]',
        "a=1979-05-27, b=07:32:00, c=1.5, d=false",
        'a="""multi\nline""", b=2',
        '"quoted key" = 1, "a.b" = 2',
    ],
)
def test_inline_values_preserve_general_parser_behavior(body: str) -> None:
    class GeneralParser(Parser):
        pass

    content = f"a = {{ {body}, # end\n }}\n"
    doc = parse(content)
    general = GeneralParser(content).parse()
    assert doc.as_string() == general.as_string() == content
    assert doc.unwrap() == general.unwrap()
    assert [type(v) for _, v in doc["a"].value.body] == [
        type(v) for _, v in general["a"].value.body
    ]


@pytest.mark.parametrize("body", ["x=1, x=2", "x.y=1, x=2", "x=1, x.y=2", '"x"=1, x=2'])
def test_inline_values_preserve_duplicate_validation(body: str) -> None:
    with pytest.raises(KeyAlreadyPresent, match=r'Key "x" already exists\.'):
        parse(f"a = {{ {body} }}")
