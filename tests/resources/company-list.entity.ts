import {
  Column,
  Entity,
  PrimaryGeneratedColumn,
} from "typeorm";
import { IsString, MaxLength, IsNumber, IsDateString, IsOptional } from 'class-validator';

@Entity("Company_List", { schema: "dbo" })
export class Company {
  @PrimaryGeneratedColumn({ type: "smallint", name: "CompanyId" })
  @IsNumber()
  companyId: number;

  @Column("varchar", { name: "CompanyName", nullable: true, length: 60 })
  @IsOptional()
  @IsString()
  @MaxLength(60)
  companyName?: string | null;

  @Column("money", {
    name: "BaseRate",
    nullable: true,
    default: () => "(0)",
  })
  @IsOptional()
  @IsNumber()
  baseRate?: number | null = 0;

  @Column("smallint", {
    name: "DefaultCurrencyId",
    nullable: true,
    default: () => "(1)",
  })
  @IsOptional()
  @IsNumber()
  defaultCurrencyId?: number | null = 1;

  @Column("int", { name: "EnterUserId" })
  @IsNumber()
  enterUserId: number;

  @Column("datetime", {
    name: "EnterDate",
    default: () => "[XUtils].[GetCurrentDateTime]()",
  })
  @IsDateString()
  enterDate: Date;

  @Column("float", { name: "TaxRate", nullable: true, precision: 53 })
  @IsOptional()
  @IsNumber()
  taxRate?: number | null;

}
