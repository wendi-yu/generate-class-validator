import textwrap

from class_validator import *


def reset_used_imports():
    used_validator_imports[ColumnType.STRING] = False
    used_validator_imports[ColumnType.NUM] = False
    used_validator_imports[ColumnType.DATE] = False
    used_validator_imports[ColumnType.BOOL] = False
    used_validator_imports["OPTIONAL"] = False


def test_import_reset():
    used_validator_imports["OPTIONAL"] = True

    reset_used_imports()

    assert not used_validator_imports["OPTIONAL"]


def test_find_type():
    num_line = "companyId: number;"
    str_optional_line = "companyName?: string | null;"
    date_line = "enterDate: Date;"
    bool_line = "isDeleted: boolean | null;"

    assert find_type(num_line) == (ColumnType.NUM, False)
    assert find_type(str_optional_line) == (ColumnType.STRING, True)
    assert find_type(date_line) == (ColumnType.DATE, False)
    assert find_type(bool_line) == (ColumnType.BOOL, True)

    for used in used_validator_imports.values():
        assert used

    reset_used_imports()


def test_register_imports():
    register_imports(ColumnType.STRING, True)

    for col_type, used in used_validator_imports.items():
        if col_type not in [ColumnType.STRING, "OPTIONAL"]:
            assert not used
        else:
            assert used

    reset_used_imports()


def test_build_validator_import():
    for col_type in used_validator_imports.keys():
        used_validator_imports[col_type] = True

    import_statement = build_validator_import_statement()
    assert import_statement == \
        "import { IsString, MaxLength, IsNumber, IsDateString, IsBoolean, IsOptional } from 'class-validator';"
    reset_used_imports()


def test_filter_imports():
    unfiltered = textwrap.dedent("""
    import {
        Column,
        Entity,
        Index,
        JoinColumn,
        ManyToOne,
        OneToMany,
        PrimaryGeneratedColumn,
    } from "typeorm";
    import { QuoteModelsPriceAddersXrf } from "./QuoteModelsPriceAddersXrf";
    import { Quotes } from "./Quotes";
    import { IsString, IsDateString, MaxLength, IsOptional, IsNumber, IsBoolean } from 'class-validator';
    """)

    filtered = textwrap.dedent("""
    import {
        Column,
        Entity,
        PrimaryGeneratedColumn,
    } from "typeorm";
    import { IsString, IsDateString, MaxLength, IsOptional, IsNumber, IsBoolean } from 'class-validator';
    """)

    assert filter_imports(unfiltered) == filtered
    reset_used_imports()


def test_find_length_object():
    length = 60
    line = f'@Column("varchar", {{ name: "CompanyName", nullable: true, length: {length} }})'

    assert find_length_object(line) == length

    non_string_line = '@PrimaryGeneratedColumn({ type: "smallint", name: "CompanyId" })'
    assert find_length_object(non_string_line) == -1
    reset_used_imports()


def test_separate_default():
    number_default = '@Column("tinyint", { name: "Exclude", nullable: true, default: () => "(0)" })'
    assert separate_default(number_default) == (
        '@Column("tinyint", { name: "Exclude", nullable: true, })',
        '0'
    )

    XUtils_default = '@Column("tinyint", { name: "Exclude", nullable: true, default: () => "[XUtils].[GetCurrentDateTime]()" })'
    assert separate_default(XUtils_default) == (
        '@Column("tinyint", { name: "Exclude", nullable: true, })',
        ""
    )
    reset_used_imports()


def test_add_optional():
    field = "exclude: number | null;"
    assert add_optional(field) == "exclude?: number | null;"
    reset_used_imports()


def test_add_default():
    field = "exclude: number;"
    default = "1"

    assert add_default(field, default) == "exclude: number = 1;"
    reset_used_imports()
