import textwrap

from class_validator import *


def test_init():
    desc = textwrap.dedent("""
      @Column("varchar", { name: "FolderLocation", nullable: true, length: 200 })
      folderLocation: string | null;
    """)

    col = Column(desc)

    assert col.default == ""
    assert col.length == 200
    assert col.type == ColumnType.STRING
    assert col.is_optional == True

    num_desc = textwrap.dedent("""
      @Column("money", {
        name: "EngineeringRate",
        default: () => "(0)",
      })
      engineeringRate: number;
    """)

    num_col = Column(num_desc)

    assert num_col.default == "0"
    assert num_col.length == -1
    assert num_col.type == ColumnType.NUM
    assert num_col.is_optional == False


def test_remove_index():
    index = '@Index("PK_Locations", ["companyId"], { unique: true })'
    col_desc = textwrap.dedent("""\
    @Entity("Admin_Company", { schema: "dbo" })
    export class AdminCompany {
      @PrimaryGeneratedColumn({ type: "smallint", name: "CompanyId" })
      companyId: number;
    """)

    index_col = Column(index + "\n" + col_desc)

    index_col.remove_index()

    assert "\n".join(index_col.col_lines) == col_desc

    col = Column(col_desc)
    col.remove_index()
    assert "\n".join(col.col_lines) == col_desc
