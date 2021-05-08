import copy
from enum import Enum

import demjson

# --------------------------------- CONSTANTS ---------------------------------


class ColumnType(Enum):
    STRING = 1
    NUM = 2
    DATE = 3
    BOOL = 4
    OTHER = 5


relations = ["ManyToOne", "OneToMany", "OneToOne", "ManyToMany", "JoinColumn"]

col_indicators = ('@Column', '@Primary')

type_mapping = {
    'string': ColumnType.STRING,
    'number': ColumnType.NUM,
    'Date': ColumnType.DATE,
    'boolean': ColumnType.BOOL,
    'Buffer': ColumnType.OTHER,
}

decorators = {
    ColumnType.STRING: "  @IsString()",
    ColumnType.NUM: "  @IsNumber()",
    ColumnType.DATE: "  @IsDateString()",
    ColumnType.BOOL: "  @IsBoolean()",
    ColumnType.OTHER: "",
}


used_validator_imports = {
    ColumnType.STRING: False,
    ColumnType.NUM: False,
    ColumnType.DATE: False,
    ColumnType.BOOL: False,
    "OPTIONAL": False,
}

# --------------------------------- FUNCTIONS ---------------------------------


def find_type(line):
    """Take the line declaring field and type and return (type, isOptional)"""
    type_string = line.split(':')[-1].strip(";\n ")
    isOptional = False
    if "|" in type_string:
        isOptional = True
        type_string = type_string.split(' | ')[0].strip()

    column_type = type_mapping[type_string]

    register_imports(column_type, isOptional)

    return (column_type, isOptional)


def register_imports(column_type, isOptional):
    """Register validator decorators as used"""
    used_validator_imports[column_type] = True
    if isOptional:
        used_validator_imports["OPTIONAL"] = True


def build_validator_import_statement():
    """Build import statement for used validator decorators"""
    import_list = []
    for column_type, decorator in decorators.items():
        if column_type in used_validator_imports and used_validator_imports[column_type]:
            import_fn = decorator.strip().strip("@()")
            import_list.append(import_fn)
            if column_type == ColumnType.STRING:
                import_list.append("MaxLength")

    if used_validator_imports["OPTIONAL"]:
        import_list.append("IsOptional")

    imports = ", ".join(import_list)
    return f"import {{ {imports} }} from 'class-validator';"


def filter_imports(imports):
    """Filter out TypeORM imports to remove relations, index, joined tables"""
    import_list = imports.split("\n")
    import_list = filter(lambda line: "./" not in line and line.strip(" ,\n")
                         not in relations + ["Index"], import_list)
    return "\n".join(import_list)


def find_length_object(line):
    """Take the line containing the object declaring length and extract the length"""
    line = line.replace('}', '{')
    description_js = "{" + line.split('{')[-2].strip() + "}"
    try:
        description = demjson.decode(description_js)
    except:
        exit(line)
    if "length" not in description:
        return -1
    return description["length"]


def find_length(line):
    """Extract length x from line in form 'length: x,'"""
    tokens = line.split(':')
    length = int(tokens[-1].strip(", "))
    return length


def remove_tail(col_lines):
    """Remove trailing single-character tails of "}" or whatever in a split token list"""
    while len(col_lines[-1]) < 2:
        col_lines.pop()


def separate_default(line):
    """Return object declaration and default separately"""
    tokens = line.split("default: ")
    default = tokens[-1].strip('() =>}{",\n')
    if "XUtils" in default:
        default = ""

    if tokens[0] != "":
        tokens[0] += "})"

    return (tokens[0], default)


def add_optional(line):
    """Adds optional indicator to variable"""
    newline = line.replace(":", "?:", 1)
    return newline


def add_default(line, default):
    """Adds default value to variable"""
    if "XUtils" in default:
        return line
    return line.strip(";") + " = " + default + ";"


def build_result(imports, column_list):
    """Produce final output"""
    ret = filter_imports(imports) + "\n"
    ret += build_validator_import_statement() + "\n"
    ret += "\n"

    for col in column_list:
        ret += col.output() + "\n\n"
    ret += "}"

    return ret


class Column():
    def __init__(self, col_desc):
        self.col_lines = col_desc.split('\n')
        col_lines = copy.deepcopy(self.col_lines)
        # get rid of trailing }s or newlines
        remove_tail(col_lines)

        # type declaring line should always be last, since we're stripping the extra } away
        self.type, self.is_optional = find_type(col_lines[-1])

        # flag value
        self.length = -1
        self.default = ""

        # gleaning attributes
        for line in col_lines:
            line = line.strip()
            if "default: (" in line:
                line, self.default = separate_default(line)
            if self.type == ColumnType.STRING:
                if line.startswith(col_indicators) and all(obj in line for obj in ["{", "}"]):
                    self.length = find_length_object(line)
                elif "length: " in line:
                    self.length = find_length(line)

    def print_desc(self):
        """Print attributes"""
        print(self.type)
        print(self.is_optional)
        print(self.length)

    def remove_index(self):
        """Remove index decorators, even if they span multiple lines. No-op if '@Index' not in first line."""
        if "@Index" not in self.col_lines[0]:
            return

        while not self.col_lines[0].startswith('@Entity'):
            self.col_lines.pop(0)

    def output(self):
        """Return formatted ts output"""
        col_lines = copy.deepcopy(self.col_lines)
        remove_tail(col_lines)
        if self.is_optional:
            col_lines[-1] = add_optional(col_lines[-1])
            col_lines.insert(-1, "  @IsOptional()")

        if self.default != "":
            col_lines[-1] = add_default(col_lines[-1], self.default)

        col_lines.insert(-1, decorators[self.type])

        if self.length != -1:
            col_lines.insert(-1, f"  @MaxLength({self.length})")

        return "\n".join(col_lines)

# --------------------------------- ACTUAL SCRIPT ---------------------------------


def build(fpath):
    column_list = []
    imports = ""

    with open(fpath, 'r') as entity:
        # entries separated by blank line
        entry_list = entity.read().split('\n\n')
        # create Column objects from relevant entries
        for col_desc in entry_list:
            if col_desc.startswith('import'):
                imports = col_desc
                continue
            if any(relation in col_desc for relation in relations):
                continue
            col = Column(col_desc)
            column_list.append(col)

    # remove @Index lines
    column_list[0].remove_index()

    # output
    return build_result(imports, column_list)
