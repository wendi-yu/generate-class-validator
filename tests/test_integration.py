from class_validator import *


def test_integration():
    expected = ""
    with open("tests/resources/company-list.entity.ts") as expected_file:
        expected = "".join(expected_file.readlines())

    result = build("tests/resources/CompanyList.ts")

    assert result.strip() == expected.strip()
