import {
  Column,
  Entity,
  PrimaryGeneratedColumn,
} from "typeorm";

@Index("PK_Locations", ["companyId"], { unique: true })
@Entity("Company_List", { schema: "dbo" })
export class Company {
  @PrimaryGeneratedColumn({ type: "smallint", name: "CompanyId" })
  companyId: number;

  @Column("varchar", { name: "CompanyName", nullable: true, length: 60 })
  companyName: string | null;

  @Column("money", {
    name: "BaseRate",
    nullable: true,
    default: () => "(0)",
  })
  baseRate: number | null;

  @Column("smallint", {
    name: "DefaultCurrencyId",
    nullable: true,
    default: () => "(1)",
  })
  defaultCurrencyId: number | null;

  @Column("int", { name: "EnterUserId" })
  enterUserId: number;

  @Column("datetime", {
    name: "EnterDate",
    default: () => "[XUtils].[GetCurrentDateTime]()",
  })
  enterDate: Date;

  @Column("float", { name: "TaxRate", nullable: true, precision: 53 })
  taxRate: number | null;

  @ManyToOne(
    () => CompanyGroups,
    (companyGroups) => companyGroups.companies
  )
  @JoinColumn([
    { name: "CompanyGroupId", referencedColumnName: "companyGroupId" },
  ])
  companyGroup: AdminCompanyGroups;

  @OneToMany(
    () => ExternalSupplyCompany,
    (externalSupplyCompany) => externalSupplyCompany.company
  )
  externalSupplyCompanys: ExternalSupplyCompany[];

  @OneToMany(() => QuoteSummary, (quoteSummary) => quoteSummary.company)
  quoteSummarys: QuoteSummary[];
}
