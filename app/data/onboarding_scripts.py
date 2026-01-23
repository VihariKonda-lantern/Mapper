# --- onboarding_scripts.py ---
"""Generate onboarding SQL scripts for CDAP database setup."""
from typing import Any, Dict, List, Optional
import pandas as pd  # type: ignore[import-not-found]
from datetime import datetime


def generate_onboarding_sql_script(
    client_name: str,
    plan_sponsor_name: str,
    domain_name: str = "PlanSponsorClaims",
    preprocessor_name: Optional[str] = None,
    file_name_date_format: str = "yyyyMMdd",
    file_name_regex_pattern: Optional[str] = None,
    primary_key: Optional[str] = None,
    preprocessing_primary_key: Optional[str] = None,
    entity_type: str = "Medical",
    demographic_match_tier_config: str = "tier1,tier2",
    sort_col_name: Optional[str] = None,
    null_threshold_percentage: int = 15,
    process_curation: bool = True,
    inbound_path: str = "/mnt/data/inbound/raw/",
    file_format: str = "csv",
    file_separator: str = "\t",
    file_has_header: bool = False,
    file_date_format: str = "yyyyMd",
    mapping_date_format: str = "yyyy-MM-dd",
    layout_df: Optional[Any] = None,
    final_mapping: Optional[Dict[str, Dict[str, Any]]] = None,
    file_master_id: int = 2490
) -> str:
    """
    Generate SQL script for CDAP client onboarding.
    
    Args:
        client_name: Client name (e.g., "LibertyCocaCola_Aetna")
        plan_sponsor_name: Plan sponsor name (e.g., "Aetna")
        domain_name: Domain name (default: "PlanSponsorClaims")
        preprocessor_name: Preprocessor name (auto-generated if None)
        file_name_date_format: Date format for file names
        file_name_regex_pattern: Regex pattern for file names
        primary_key: Primary key columns (comma-separated)
        preprocessing_primary_key: Preprocessing primary key column
        entity_type: Entity type (default: "Medical")
        demographic_match_tier_config: Demographic match tier config
        sort_col_name: Sort column name
        null_threshold_percentage: Null threshold percentage
        process_curation: Process curation flag
        inbound_path: Inbound path for files
        file_format: File format (csv, txt, etc.)
        file_separator: File separator (tab, comma, etc.)
        file_has_header: Whether file has header
        file_date_format: Date format in file
        mapping_date_format: Date format for mapping
        layout_df: Layout DataFrame for column mapping
        final_mapping: Field mapping dictionary
        file_master_id: File master ID (default: 2490)
        
    Returns:
        SQL script as string
    """
    if preprocessor_name is None:
        preprocessor_name = f"{client_name.lower().replace('_', '_')}_{domain_name.lower()}_prep"
    
    sql_lines = []
    
    # Header
    sql_lines.append(f"-- CDAP Onboarding Script for {client_name}")
    sql_lines.append(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sql_lines.append(f"-- Domain: {domain_name}")
    sql_lines.append(f"-- Plan Sponsor: {plan_sponsor_name}")
    sql_lines.append("")
    
    # Client setup
    sql_lines.append("-- ============================================")
    sql_lines.append("-- CLIENT SETUP")
    sql_lines.append("-- ============================================")
    sql_lines.append("MERGE CDAP.Client AS C")
    sql_lines.append(f"            USING (Select '{client_name}' as client, coalesce(max(clientkey),0)+1 as max_clientkey from cdap.client) AS S")
    sql_lines.append(f"                ON lower(C.DAPClientName) = lower(S.client)")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (ClientKey, ClientCode, ClientShortName, Name, DAPClientName, IsActive, EffectiveDate, EffectiveThruDate)")
    sql_lines.append(f"                VALUES (S.max_clientkey, S.client, S.client, S.client, S.client, 1, GETDATE(), '9999-12-31');")
    sql_lines.append("")
    
    # Domain setup
    sql_lines.append("MERGE CDAP.Domain AS D")
    sql_lines.append(f"            USING (Select '{domain_name}' as domain) AS S")
    sql_lines.append(f"                ON lower(D.DomainName) = lower(S.domain)")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (DomainName, Description, IsActive)")
    sql_lines.append(f"                VALUES (S.domain, S.domain, 1);")
    sql_lines.append("")
    
    # Plan Sponsor setup
    sql_lines.append("MERGE CDAP.PlanSponsor AS P")
    sql_lines.append(f"            USING (Select '{plan_sponsor_name}' as plansponsor) AS S")
    sql_lines.append(f"                ON lower(P.PlanSponsorName) = lower(S.plansponsor)")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (PlanSponsorName, IsActive)")
    sql_lines.append(f"                VALUES (S.plansponsor, 1);")
    sql_lines.append("")
    
    # Preprocessor setup
    sql_lines.append("MERGE CDAP.Preprocessor AS D")
    sql_lines.append(f"            USING (Select '{preprocessor_name}' as PreprocessorName) AS S")
    sql_lines.append(f"                ON lower(D.PreprocessorName) = lower(S.PreprocessorName)")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (PreprocessorName, Description)")
    sql_lines.append(f"                VALUES (S.PreprocessorName, S.PreprocessorName);")
    sql_lines.append("")
    
    # Domain-Client relationship
    sql_lines.append("MERGE CDAP.DomainClient AS P")
    sql_lines.append(f"            USING (Select c.ClientKey, d.DomainId, concat(d.DomainName,':',c.DAPClientName) as Description")
    sql_lines.append(f"                    from CDAP.Client c")
    sql_lines.append(f"                    join CDAP.Domain d on (1=1)")
    sql_lines.append(f"                    where c.DAPClientName = '{client_name}'")
    sql_lines.append(f"                    and d.DomainName = '{domain_name}') AS S")
    sql_lines.append(f"                ON (P.ClientKey = S.ClientKey and P.DomainId = S.DomainId)")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (DomainId, ClientKey, Description, IsActive)")
    sql_lines.append(f"                VALUES (S.DomainId, S.ClientKey, S.Description, 1);")
    sql_lines.append("")
    
    # Client-Sponsor relationship
    sql_lines.append("MERGE CDAP.ClientSponsor AS P")
    sql_lines.append(f"            USING (Select c.ClientKey, p.PlanSponsorId, concat(c.DAPClientName,':',p.PlanSponsorName) as Description")
    sql_lines.append(f"                    from CDAP.Client c")
    sql_lines.append(f"                    join CDAP.PlanSponsor p on (1=1)")
    sql_lines.append(f"                    where c.DAPClientName = '{client_name}'")
    sql_lines.append(f"                    and p.PlanSponsorName = '{plan_sponsor_name}') AS S")
    sql_lines.append(f"                ON (P.ClientKey = S.ClientKey and P.PlanSponsorId = S.PlanSponsorId)")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (PlanSponsorId, ClientKey, Description, IsActive)")
    sql_lines.append(f"                VALUES (S.PlanSponsorId, S.ClientKey, S.Description, 1);")
    sql_lines.append("")
    
    # Domain-Sponsor relationship
    sql_lines.append("MERGE CDAP.DomainSponsor AS P")
    sql_lines.append(f"            USING (Select d.DomainId, p.PlanSponsorId, concat(d.DomainName,':',p.PlanSponsorName) as Description")
    sql_lines.append(f"                    from CDAP.Domain d")
    sql_lines.append(f"                    join CDAP.PlanSponsor p on (1=1)")
    sql_lines.append(f"                    where d.DomainName = '{domain_name}'")
    sql_lines.append(f"                    and p.PlanSponsorName = '{plan_sponsor_name}') AS S")
    sql_lines.append(f"                ON (P.DomainId = S.DomainId and P.PlanSponsorId = S.PlanSponsorId)")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (PlanSponsorId, DomainId, Description, IsActive)")
    sql_lines.append(f"                VALUES (S.PlanSponsorId, S.DomainId, S.Description, 1);")
    sql_lines.append("")
    
    # Ingestion Config
    sql_lines.append("MERGE CDAP.IngestionConfig AS P")
    sql_lines.append(f"            USING (Select dc.DomainClientId, cs.ClientSponsorId, ds.DomainSponsorId,")
    sql_lines.append(f"                        pp.PreprocessorId as PreprocessorId, {file_master_id} as FileMasterId")
    sql_lines.append(f"                    from CDAP.Domain d")
    sql_lines.append(f"                    join CDAP.Client c on (1=1)")
    sql_lines.append(f"                    join CDAP.PlanSponsor p on (1=1)")
    sql_lines.append(f"                    join CDAP.Preprocessor pp on (1=1)")
    sql_lines.append(f"                    join CDAP.DomainClient dc on (dc.DomainId = d.DomainId and dc.ClientKey=c.ClientKey)")
    sql_lines.append(f"                    join CDAP.ClientSponsor cs on (cs.ClientKey = c.ClientKey and cs.PlanSponsorId = p.PlanSponsorId)")
    sql_lines.append(f"                    join CDAP.DomainSponsor ds on (ds.DomainId = d.DomainId and ds.PlanSponsorId = p.PlanSponsorId)")
    sql_lines.append(f"                    where d.DomainName = '{domain_name}'")
    sql_lines.append(f"                    and c.DAPClientName = '{client_name}'")
    sql_lines.append(f"                    and p.PlanSponsorName = '{plan_sponsor_name}'")
    sql_lines.append(f"                    and pp.PreprocessorName = '{preprocessor_name}') AS S")
    sql_lines.append(f"                ON (P.DomainClientId = S.DomainClientId and P.ClientSponsorId = S.ClientSponsorId and P.DomainSponsorId = S.DomainSponsorId)")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (PreprocessorId, FileMasterId, DomainClientId, ClientSponsorId, DomainSponsorId, IsActive)")
    sql_lines.append(f"                VALUES (S.PreprocessorId, S.FileMasterId, S.DomainClientId, S.ClientSponsorId, S.DomainSponsorId, 1);")
    sql_lines.append("")
    
    # Parameter Types
    sql_lines.append("-- ============================================")
    sql_lines.append("-- PARAMETER TYPES")
    sql_lines.append("-- ============================================")
    
    # Domain configurations parameter types
    domain_params = [
        'entity', 'primary_key', 'preprocessing_primary_key', 'file_name_date_format',
        'file_name_date_regex_pattern', 'client_name', 'demographic_match_tier_config',
        'sort_col_name', 'null_threshold_percentage', 'process_curation', 'inbound_path'
    ]
    
    for param in domain_params:
        sql_lines.append(f"MERGE CDAP.IngestionParameterType AS C")
        sql_lines.append(f"        	USING (Select 'domain_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, '{param}' as ParamName) AS S")
        sql_lines.append(f"		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))")
        sql_lines.append(f"            WHEN NOT MATCHED THEN")
        sql_lines.append(f"                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)")
        sql_lines.append(f"                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));")
        sql_lines.append("")
    
    # Reading configurations parameter types
    reading_params = ['format']
    read_kwargs_params = ['inferSchema', 'mergeSchema', 'sep', 'header', 'dateFormat']
    
    for param in reading_params:
        sql_lines.append(f"MERGE CDAP.IngestionParameterType AS C")
        sql_lines.append(f"        	USING (Select 'reading_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, '{param}' as ParamName) AS S")
        sql_lines.append(f"		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))")
        sql_lines.append(f"            WHEN NOT MATCHED THEN")
        sql_lines.append(f"                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)")
        sql_lines.append(f"                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));")
        sql_lines.append("")
    
    for param in read_kwargs_params:
        sql_lines.append(f"MERGE CDAP.IngestionParameterType AS C")
        sql_lines.append(f"        	USING (Select 'reading_configurations' as GroupName, (case when 'read_kwargs' = '' then null else 'read_kwargs' end) as SubGroupName, '{param}' as ParamName) AS S")
        sql_lines.append(f"		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))")
        sql_lines.append(f"            WHEN NOT MATCHED THEN")
        sql_lines.append(f"                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)")
        sql_lines.append(f"                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));")
        sql_lines.append("")
    
    # Read prep configurations
    sql_lines.append(f"MERGE CDAP.IngestionParameterType AS C")
    sql_lines.append(f"        	USING (Select 'read_prep_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'function_name' as ParamName) AS S")
    sql_lines.append(f"		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)")
    sql_lines.append(f"                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));")
    sql_lines.append("")
    
    # Prep configurations
    sql_lines.append(f"MERGE CDAP.IngestionParameterType AS C")
    sql_lines.append(f"        	USING (Select 'prep_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'transformations' as ParamName) AS S")
    sql_lines.append(f"		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)")
    sql_lines.append(f"                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));")
    sql_lines.append("")
    
    # Mapping configurations
    mapping_params = ['dateformat', 'demographic_match', 'retain_not_null_cols']
    for param in mapping_params:
        sql_lines.append(f"MERGE CDAP.IngestionParameterType AS C")
        sql_lines.append(f"        	USING (Select 'mapping_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, '{param}' as ParamName) AS S")
        sql_lines.append(f"		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))")
        sql_lines.append(f"            WHEN NOT MATCHED THEN")
        sql_lines.append(f"                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)")
        sql_lines.append(f"                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));")
        sql_lines.append("")
    
    # Curation configurations
    curation_params = ['tagging', 'demographic_match']
    for param in curation_params:
        sql_lines.append(f"MERGE CDAP.IngestionParameterType AS C")
        sql_lines.append(f"        	USING (Select 'curation_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, '{param}' as ParamName) AS S")
        sql_lines.append(f"		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))")
        sql_lines.append(f"            WHEN NOT MATCHED THEN")
        sql_lines.append(f"                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)")
        sql_lines.append(f"                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));")
        sql_lines.append("")
    
    # Access configurations
    sql_lines.append(f"MERGE CDAP.IngestionParameterType AS C")
    sql_lines.append(f"        	USING (Select 'access_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'process_type' as ParamName) AS S")
    sql_lines.append(f"		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)")
    sql_lines.append(f"                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));")
    sql_lines.append("")
    
    # Parameters
    sql_lines.append("-- ============================================")
    sql_lines.append("-- PARAMETERS")
    sql_lines.append("-- ============================================")
    
    # Domain configuration parameters
    if entity_type:
        sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
        sql_lines.append(f"    USING (Select ParameterTypeId, (case when '{entity_type}' = '' then null else '{entity_type}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'entity') AS S")
        sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
        sql_lines.append(f"    WHEN NOT MATCHED THEN")
        sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
        sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
        sql_lines.append("")
    
    if primary_key:
        sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
        sql_lines.append(f"    USING (Select ParameterTypeId, (case when '{primary_key}' = '' then null else '{primary_key}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'primary_key') AS S")
        sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
        sql_lines.append(f"    WHEN NOT MATCHED THEN")
        sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
        sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
        sql_lines.append("")
    
    if preprocessing_primary_key:
        sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
        sql_lines.append(f"    USING (Select ParameterTypeId, (case when '{preprocessing_primary_key}' = '' then null else '{preprocessing_primary_key}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'preprocessing_primary_key') AS S")
        sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
        sql_lines.append(f"    WHEN NOT MATCHED THEN")
        sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
        sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
        sql_lines.append("")
    
    if file_name_date_format:
        sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
        sql_lines.append(f"    USING (Select ParameterTypeId, (case when '{file_name_date_format}' = '' then null else '{file_name_date_format}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'file_name_date_format') AS S")
        sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
        sql_lines.append(f"    WHEN NOT MATCHED THEN")
        sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
        sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
        sql_lines.append("")
    
    if file_name_regex_pattern:
        sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
        sql_lines.append(f"    USING (Select ParameterTypeId, (case when '{file_name_regex_pattern}' = '' then null else '{file_name_regex_pattern}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'file_name_date_regex_pattern') AS S")
        sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
        sql_lines.append(f"    WHEN NOT MATCHED THEN")
        sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
        sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
        sql_lines.append("")
    
    # Client name (use client_name as-is, or extract display name)
    client_display_name = client_name.replace('_', ' ')
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"    USING (Select ParameterTypeId, (case when '{client_display_name}' = '' then null else '{client_display_name}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'client_name') AS S")
    sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"    WHEN NOT MATCHED THEN")
    sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    if demographic_match_tier_config:
        sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
        sql_lines.append(f"    USING (Select ParameterTypeId, (case when '{demographic_match_tier_config}' = '' then null else '{demographic_match_tier_config}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'demographic_match_tier_config') AS S")
        sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
        sql_lines.append(f"    WHEN NOT MATCHED THEN")
        sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
        sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
        sql_lines.append("")
    
    if sort_col_name:
        sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
        sql_lines.append(f"    USING (Select ParameterTypeId, (case when '{sort_col_name}' = '' then null else '{sort_col_name}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'sort_col_name') AS S")
        sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
        sql_lines.append(f"    WHEN NOT MATCHED THEN")
        sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
        sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
        sql_lines.append("")
    
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"    USING (Select ParameterTypeId, (case when '{null_threshold_percentage}' = '' then null else '{null_threshold_percentage}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'null_threshold_percentage') AS S")
    sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"    WHEN NOT MATCHED THEN")
    sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    process_curation_val = 'Y' if process_curation else 'N'
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"    USING (Select ParameterTypeId, (case when '{process_curation_val}' = '' then null else '{process_curation_val}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'process_curation') AS S")
    sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"    WHEN NOT MATCHED THEN")
    sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"    USING (Select ParameterTypeId, (case when '{inbound_path}' = '' then null else '{inbound_path}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'inbound_path') AS S")
    sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"    WHEN NOT MATCHED THEN")
    sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    # Reading configuration parameters
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"    USING (Select ParameterTypeId, (case when '{file_format}' = '' then null else '{file_format}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'reading_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'format') AS S")
    sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"    WHEN NOT MATCHED THEN")
    sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    # Read kwargs
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"    USING (Select ParameterTypeId, (case when 'N' = '' then null else 'N' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'reading_configurations' AND coalesce(SubGroupName,'') = 'read_kwargs' AND ParamName = 'inferSchema') AS S")
    sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"    WHEN NOT MATCHED THEN")
    sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"    USING (Select ParameterTypeId, (case when 'Y' = '' then null else 'Y' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'reading_configurations' AND coalesce(SubGroupName,'') = 'read_kwargs' AND ParamName = 'mergeSchema') AS S")
    sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"    WHEN NOT MATCHED THEN")
    sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    # Escape separator for SQL
    sep_escaped = file_separator.replace("'", "''").replace("\t", "\\t")
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"    USING (Select ParameterTypeId, (case when '{sep_escaped}' = '' then null else '{sep_escaped}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'reading_configurations' AND coalesce(SubGroupName,'') = 'read_kwargs' AND ParamName = 'sep') AS S")
    sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"    WHEN NOT MATCHED THEN")
    sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    header_val = 'Y' if file_has_header else 'N'
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"    USING (Select ParameterTypeId, (case when '{header_val}' = '' then null else '{header_val}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'reading_configurations' AND coalesce(SubGroupName,'') = 'read_kwargs' AND ParamName = 'header') AS S")
    sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"    WHEN NOT MATCHED THEN")
    sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"    USING (Select ParameterTypeId, (case when '{file_date_format}' = '' then null else '{file_date_format}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'reading_configurations' AND coalesce(SubGroupName,'') = 'read_kwargs' AND ParamName = 'dateFormat') AS S")
    sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"    WHEN NOT MATCHED THEN")
    sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    # Read prep configurations
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"    USING (Select ParameterTypeId, (case when '{preprocessor_name}' = '' then null else '{preprocessor_name}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'read_prep_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'function_name') AS S")
    sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"    WHEN NOT MATCHED THEN")
    sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    # Prep configurations - transformations
    # Get insurance_plan_name from final_mapping if available, otherwise use client_display_name
    insurance_plan_name = client_display_name  # Default fallback
    if final_mapping:
        insurance_plan_mapping = final_mapping.get("Insurance_Plan_Name", {})
        if insurance_plan_mapping and insurance_plan_mapping.get("value"):
            insurance_plan_name = insurance_plan_mapping.get("value")
    
    transformations_json = f'{{"client_name":"{client_display_name}","plan_sponsor_name":"{plan_sponsor_name}","insurance_plan_name":"{insurance_plan_name}"}}'
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"    USING (Select ParameterTypeId, (case when '{transformations_json}' = '' then null else '{transformations_json}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'prep_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'transformations') AS S")
    sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"    WHEN NOT MATCHED THEN")
    sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    # Mapping configurations
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"    USING (Select ParameterTypeId, (case when '{mapping_date_format}' = '' then null else '{mapping_date_format}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'mapping_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'dateformat') AS S")
    sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"    WHEN NOT MATCHED THEN")
    sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"    USING (Select ParameterTypeId, (case when '' = '' then null else '' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'mapping_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'demographic_match') AS S")
    sql_lines.append(f"        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"    WHEN NOT MATCHED THEN")
    sql_lines.append(f"        INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"        VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    # Ingestion Config Parameters
    sql_lines.append("-- ============================================")
    sql_lines.append("-- INGESTION CONFIG PARAMETERS")
    sql_lines.append("-- ============================================")
    
    # Helper function to generate IngestionConfigParameter MERGE statements
    def add_config_parameter(group_name: str, sub_group: str, param_name: str, param_value: str):
        sub_group_condition = f"coalesce(ipt.SubGroupName,'') = '{sub_group}'" if sub_group else "coalesce(ipt.SubGroupName,'') = ''"
        sql_lines.append(f"MERGE CDAP.IngestionConfigParameter AS C")
        sql_lines.append(f"    USING (select a.IngestionConfigId, b.ParameterId from")
        sql_lines.append(f"            (select ic.IngestionConfigId from")
        sql_lines.append(f"            CDAP.IngestionConfig ic")
        sql_lines.append(f"            join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)")
        sql_lines.append(f"            join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)")
        sql_lines.append(f"            join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)")
        sql_lines.append(f"            join CDAP.Domain d on (d.domainid = dc.domainid)")
        sql_lines.append(f"            join CDAP.Client c on (c.clientkey = dc.clientkey)")
        sql_lines.append(f"            join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)")
        sql_lines.append(f"            where c.DAPClientName = '{client_name}' and d.DomainName='{domain_name}'")
        sql_lines.append(f"            and ps.PlanSponsorName = '{plan_sponsor_name}'")
        sql_lines.append(f"            ) a")
        sql_lines.append(f"            join")
        sql_lines.append(f"            (select ParameterId from")
        sql_lines.append(f"            CDAP.IngestionParameter ip")
        sql_lines.append(f"            join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)")
        sql_lines.append(f"            where ipt.GroupName = '{group_name}'")
        sql_lines.append(f"            and {sub_group_condition}")
        sql_lines.append(f"            and ipt.ParamName = '{param_name}'")
        sql_lines.append(f"            and coalesce(ip.ParamValue,'') = '{param_value}') b")
        sql_lines.append(f"            on (1=1)) AS S")
        sql_lines.append(f"        ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)")
        sql_lines.append(f"        WHEN NOT MATCHED THEN")
        sql_lines.append(f"            INSERT (IngestionConfigId, ParameterId)")
        sql_lines.append(f"            VALUES (S.IngestionConfigId, S.ParameterId);")
        sql_lines.append("")
    
    # Add all config parameters
    if entity_type:
        add_config_parameter('domain_configurations', '', 'entity', entity_type)
    if primary_key:
        add_config_parameter('domain_configurations', '', 'primary_key', primary_key)
    if preprocessing_primary_key:
        add_config_parameter('domain_configurations', '', 'preprocessing_primary_key', preprocessing_primary_key)
    if file_name_date_format:
        add_config_parameter('domain_configurations', '', 'file_name_date_format', file_name_date_format)
    if file_name_regex_pattern:
        add_config_parameter('domain_configurations', '', 'file_name_date_regex_pattern', file_name_regex_pattern)
    add_config_parameter('domain_configurations', '', 'client_name', client_display_name)
    if demographic_match_tier_config:
        add_config_parameter('domain_configurations', '', 'demographic_match_tier_config', demographic_match_tier_config)
    if sort_col_name:
        add_config_parameter('domain_configurations', '', 'sort_col_name', sort_col_name)
    add_config_parameter('domain_configurations', '', 'null_threshold_percentage', str(null_threshold_percentage))
    add_config_parameter('domain_configurations', '', 'process_curation', process_curation_val)
    add_config_parameter('domain_configurations', '', 'inbound_path', inbound_path)
    
    add_config_parameter('reading_configurations', '', 'format', file_format)
    add_config_parameter('reading_configurations', 'read_kwargs', 'inferSchema', 'N')
    add_config_parameter('reading_configurations', 'read_kwargs', 'mergeSchema', 'Y')
    add_config_parameter('reading_configurations', 'read_kwargs', 'sep', sep_escaped)
    add_config_parameter('reading_configurations', 'read_kwargs', 'header', header_val)
    add_config_parameter('reading_configurations', 'read_kwargs', 'dateFormat', file_date_format)
    
    add_config_parameter('read_prep_configurations', '', 'function_name', preprocessor_name)
    add_config_parameter('prep_configurations', '', 'transformations', transformations_json)
    add_config_parameter('mapping_configurations', '', 'dateformat', mapping_date_format)
    add_config_parameter('mapping_configurations', '', 'demographic_match', '')
    
    # Column mappings (if layout_df and final_mapping provided)
    if layout_df is not None and final_mapping is not None:
        try:
            sql_lines.append("-- ============================================")
            sql_lines.append("-- COLUMN MAPPINGS")
            sql_lines.append("-- ============================================")
            
            # Get internal field column name
            from core.domain_config import get_domain_config
            config = get_domain_config()
            internal_field_col = config.internal_field_name
            
            # Helper function to format column names: remove special chars, replace spaces with underscores
            def format_column_name(column_name: str, client_name: str) -> str:
                """Format column name: remove special chars (including apostrophes and hyphens), replace spaces with underscores."""
                import re
                # Remove special characters: -, [, ], $, ' (apostrophe)
                cleaned = re.sub(r"[-\[\]$']", "", column_name)
                # Replace spaces with underscores
                cleaned = cleaned.replace(' ', '_')
                # Remove any remaining special characters except underscores
                cleaned = re.sub(r"[^a-zA-Z0-9_]", "", cleaned)
                # Return cleaned column name without client prefix
                return cleaned
            
            # Generate ColumnDetail for each internal field - MUST come BEFORE TableColumn
            try:
                for idx, row in layout_df.iterrows():
                    internal_field = str(row.get(internal_field_col, '')).strip()
                    if not internal_field or internal_field.lower() == 'nan':
                        continue
                    
                    data_type_col = config.layout_columns.get("data_type", "Data Type")
                    data_type = str(row.get(data_type_col, 'string')).strip().lower()
                    if data_type == 'date':
                        data_type = 'date'
                    else:
                        data_type = 'string'
                    
                    formatted_field_name = format_column_name(internal_field, client_name)
                    sql_lines.append(f"MERGE CDAP.ColumnDetail AS C")
                    sql_lines.append(f"        	USING (Select '{formatted_field_name}' as ColumnName, '{data_type}' as DataType")
                    sql_lines.append(f"                    ) AS S")
                    sql_lines.append(f"		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))")
                    sql_lines.append(f"            WHEN NOT MATCHED THEN")
                    sql_lines.append(f"                INSERT (ColumnName, DataType)")
                    sql_lines.append(f"                VALUES (S.ColumnName, S.DataType);")
                    sql_lines.append("")
            except Exception:
                # If iterating layout_df fails, skip column detail generation
                pass
            
            # Generate ZoneTable for raw and prep zones
            raw_table_name = f"{client_name.lower()}_layout"
            prep_table_name = f"{domain_name.lower()}_{entity_type.lower()}_{client_name.lower()}"
            
            sql_lines.append(f"MERGE CDAP.ZoneTable AS C")
            sql_lines.append(f"    USING (select TOP 1 pz.ZoneId, '{raw_table_name}' as TableName from CDAP.ProcessingZone pz")
            sql_lines.append(f"            where pz.name = 'raw') AS S")
            sql_lines.append(f"        ON (C.ZoneId = S.ZoneId AND C.TableName = S.TableName)")
            sql_lines.append(f"    WHEN NOT MATCHED THEN")
            sql_lines.append(f"        INSERT (ZoneId, TableName)")
            sql_lines.append(f"        VALUES (S.ZoneId, S.TableName);")
            sql_lines.append("")
            
            sql_lines.append(f"MERGE CDAP.ZoneTable AS C")
            sql_lines.append(f"    USING (select TOP 1 pz.ZoneId, '{prep_table_name}' as TableName from CDAP.ProcessingZone pz")
            sql_lines.append(f"            where pz.name = 'prep') AS S")
            sql_lines.append(f"        ON (C.ZoneId = S.ZoneId AND C.TableName = S.TableName)")
            sql_lines.append(f"    WHEN NOT MATCHED THEN")
            sql_lines.append(f"        INSERT (ZoneId, TableName)")
            sql_lines.append(f"        VALUES (S.ZoneId, S.TableName);")
            sql_lines.append("")
            
            # Generate ColumnDetail for raw zone (source columns) - MUST come BEFORE TableColumn
            source_columns = []
            for internal_field, mapping_info in final_mapping.items():
                if isinstance(mapping_info, dict) and 'value' in mapping_info:
                    source_col = mapping_info['value']
                    if source_col and source_col not in source_columns:
                        source_columns.append(source_col)
            
            # First, create ColumnDetail for all source columns
            for source_col in source_columns:
                formatted_col_name = format_column_name(source_col, client_name)
                sql_lines.append(f"MERGE CDAP.ColumnDetail AS C")
                sql_lines.append(f"        	USING (Select '{formatted_col_name}' as ColumnName, 'string' as DataType")
                sql_lines.append(f"                    ) AS S")
                sql_lines.append(f"		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))")
                sql_lines.append(f"            WHEN NOT MATCHED THEN")
                sql_lines.append(f"                INSERT (ColumnName, DataType)")
                sql_lines.append(f"                VALUES (S.ColumnName, S.DataType);")
                sql_lines.append("")
            
            # Then, create TableColumn for raw zone (source columns) - AFTER ColumnDetail
            for col_order, source_col in enumerate(source_columns, 1):
                formatted_col_name = format_column_name(source_col, client_name)
                sql_lines.append(f"MERGE CDAP.TableColumn AS C")
                sql_lines.append(f"                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, {col_order} as ColumnOrder")
                sql_lines.append(f"                        from CDAP.ZoneTable zt")
                sql_lines.append(f"                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)")
                sql_lines.append(f"                        join CDAP.ColumnDetail cd on (1=1)")
                sql_lines.append(f"                        where pz.name = 'raw'")
                sql_lines.append(f"                        and zt.TableName = '{raw_table_name}'")
                sql_lines.append(f"                        and cd.ColumnName = '{formatted_col_name}'")
                sql_lines.append(f"                        and cd.DataType = 'string') AS S")
                sql_lines.append(f"                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)")
                sql_lines.append(f"                WHEN NOT MATCHED THEN")
                sql_lines.append(f"                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)")
                sql_lines.append(f"                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);")
                sql_lines.append("")
            
            # Generate TableColumn for prep zone (internal fields) - AFTER ColumnDetail
            try:
                for col_order, (idx, row) in enumerate(layout_df.iterrows(), 1):
                    internal_field = str(row.get(internal_field_col, '')).strip()
                    if not internal_field or internal_field.lower() == 'nan':
                        continue
                    
                    data_type_col = config.layout_columns.get("data_type", "Data Type")
                    data_type = str(row.get(data_type_col, 'string')).strip().lower()
                    if data_type == 'date':
                        data_type = 'date'
                    else:
                        data_type = 'string'
                    
                    usage_col = config.internal_usage_name
                    usage = str(row.get(usage_col, '')).strip()
                    is_nullable = 1 if usage.lower() == 'optional' else 0
                    
                    formatted_field_name = format_column_name(internal_field, client_name)
                    sql_lines.append(f"MERGE CDAP.TableColumn AS C")
                    sql_lines.append(f"                USING (select zt.TableId, cd.ColumnDetailId, {is_nullable} as IsNullable, {col_order} as ColumnOrder")
                    sql_lines.append(f"                        from CDAP.ZoneTable zt")
                    sql_lines.append(f"                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)")
                    sql_lines.append(f"                        join CDAP.ColumnDetail cd on (1=1)")
                    sql_lines.append(f"                        where pz.name = 'prep'")
                    sql_lines.append(f"                        and zt.TableName = '{prep_table_name}'")
                    sql_lines.append(f"                        and cd.ColumnName = '{formatted_field_name}'")
                    sql_lines.append(f"                        and cd.DataType = '{data_type}') AS S")
                    sql_lines.append(f"                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)")
                    sql_lines.append(f"                WHEN NOT MATCHED THEN")
                    sql_lines.append(f"                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)")
                    sql_lines.append(f"                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);")
                    sql_lines.append("")
            except Exception:
                # If iterating layout_df fails, skip table column generation
                pass
            
            # Generate ColumnMapping: raw → prep (source columns to internal fields)
            sql_lines.append("-- Column Mappings: raw → prep")
            for internal_field, mapping_info in final_mapping.items():
                if isinstance(mapping_info, dict) and 'value' in mapping_info:
                    source_col = mapping_info['value']
                    if not source_col:
                        continue
                    
                    # Use formatted column names (with client prefix)
                    formatted_source = format_column_name(source_col, client_name)
                    formatted_internal = format_column_name(internal_field, client_name)
                    
                    sql_lines.append(f"MERGE CDAP.ColumnMapping AS C")
                    sql_lines.append(f"    USING (select ic.IngestionConfigId, ftc.tablecolumnid as SourceTableColumnId, ttc.tablecolumnid as TargetTableColumnId")
                    sql_lines.append(f"            from cdap.IngestionConfig ic")
                    sql_lines.append(f"            join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)")
                    sql_lines.append(f"            join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)")
                    sql_lines.append(f"            join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)")
                    sql_lines.append(f"            join CDAP.Domain d on (d.domainid = dc.domainid)")
                    sql_lines.append(f"            join CDAP.Client c on (c.clientkey = dc.clientkey)")
                    sql_lines.append(f"            join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)")
                    sql_lines.append(f"            join CDAP.ProcessingZone fpz on (fpz.name = 'raw')")
                    sql_lines.append(f"            join CDAP.ProcessingZone tpz on (tpz.name = 'prep')")
                    sql_lines.append(f"            join CDAP.ZoneTable fzt on (fzt.TableName = '{raw_table_name}' and fpz.zoneid=fzt.zoneid)")
                    sql_lines.append(f"            join CDAP.ZoneTable tzt on (tzt.TableName = '{prep_table_name}' and tpz.zoneid = tzt.zoneid)")
                    sql_lines.append(f"            join CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)")
                    sql_lines.append(f"            join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)")
                    sql_lines.append(f"            join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName = '{formatted_source}')")
                    sql_lines.append(f"            join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName = '{formatted_internal}')")
                    sql_lines.append(f"            where c.DAPClientName = '{client_name}' and d.DomainName='{domain_name}'")
                    sql_lines.append(f"            and ps.PlanSponsorName = '{plan_sponsor_name}') AS S")
                    sql_lines.append(f"        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)")
                    sql_lines.append(f"    WHEN NOT MATCHED THEN")
                    sql_lines.append(f"        INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId)")
                    sql_lines.append(f"        VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId);")
                    sql_lines.append("")
            
            # Generate ColumnMapping: prep → structured (basic mappings)
            # Note: This requires knowledge of standard field names. Generating basic mappings based on common patterns.
            sql_lines.append("-- Column Mappings: prep → structured")
            sql_lines.append("-- NOTE: Review and customize these mappings based on your standard schema")
            sql_lines.append("-- The structured zone uses standard field names (e.g., claim_id, patient_dob)")
            sql_lines.append("-- You may need to manually adjust these mappings to match your standard schema")
            sql_lines.append("")
            
            # Common field mappings (prep internal field → structured standard field)
            common_mappings = {
                'file_date': 'file_effective_date',
                'claim_id': 'claim_id',
                'patient_dob': 'patient_dob',
                'patient_first_name': 'patient_first_name',
                'patient_last_name': 'patient_last_name',
                'patient_sex': 'patient_sex',
            }
            
            structured_table_name = f"{domain_name.lower()}_{entity_type.lower()}_standard"
            
            for internal_field, mapping_info in final_mapping.items():
                if isinstance(mapping_info, dict) and 'value' in mapping_info:
                    # Try to find standard field name
                    internal_lower = internal_field.lower()
                    standard_field = None
                    
                    # Check common mappings first
                    for prep_field, std_field in common_mappings.items():
                        if prep_field in internal_lower:
                            standard_field = std_field
                            break
                    
                    # If no common mapping, try to infer from internal field name
                    if not standard_field:
                        # Simple normalization: remove numbers and underscores, convert to standard format
                        normalized = internal_lower.replace('_', ' ').strip()
                        # This is a basic heuristic - may need manual adjustment
                        standard_field = None  # Leave as None to skip for now
                    
                    if standard_field:
                        sql_lines.append(f"MERGE CDAP.ColumnMapping AS C")
                        sql_lines.append(f"    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid,")
                        sql_lines.append(f"            '' SVMRule")
                        sql_lines.append(f"            from cdap.IngestionConfig ic")
                        sql_lines.append(f"            join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)")
                        sql_lines.append(f"            join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)")
                        sql_lines.append(f"            join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)")
                        sql_lines.append(f"            join CDAP.Domain d on (d.domainid = dc.domainid)")
                        sql_lines.append(f"            join CDAP.Client c on (c.clientkey = dc.clientkey)")
                        sql_lines.append(f"            join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)")
                        sql_lines.append(f"            join CDAP.ProcessingZone fpz on (fpz.name = 'prep')")
                        sql_lines.append(f"            join CDAP.ProcessingZone tpz on (tpz.name = 'structured')")
                        sql_lines.append(f"            join CDAP.ZoneTable fzt on (fzt.TableName = '{prep_table_name}' and fpz.zoneid=fzt.zoneid)")
                        sql_lines.append(f"            join CDAP.ZoneTable tzt on (tzt.TableName = '{structured_table_name}' and tpz.zoneid = tzt.zoneid)")
                        sql_lines.append(f"            join CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)")
                        sql_lines.append(f"            join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)")
                        formatted_internal = format_column_name(internal_field, client_name)
                        sql_lines.append(f"            join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName = '{formatted_internal}')")
                        sql_lines.append(f"            join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName = '{standard_field}')")
                        sql_lines.append(f"            where c.DAPClientName = '{client_name}' and d.DomainName='{domain_name}'")
                        sql_lines.append(f"            and ps.PlanSponsorName = '{plan_sponsor_name}') AS S")
                        sql_lines.append(f"        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)")
                        sql_lines.append(f"    WHEN NOT MATCHED THEN")
                        sql_lines.append(f"        INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)")
                        sql_lines.append(f"        VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);")
                        sql_lines.append("")
        except Exception:
            # If column mapping generation fails, add a note but continue
            sql_lines.append("-- NOTE: Column mapping generation encountered an error.")
            sql_lines.append("-- Please review and add column mappings manually if needed.")
            sql_lines.append("")
    
    sql_lines.append("-- ============================================")
    sql_lines.append("-- END OF SCRIPT")
    sql_lines.append("-- ============================================")
    sql_lines.append("-- NOTE: Review and customize as needed:")
    sql_lines.append("-- 1. Column mappings (if not generated)")
    sql_lines.append("-- 2. Date formats")
    sql_lines.append("-- 3. File name patterns")
    sql_lines.append("-- 4. Additional parameters")
    
    return "\n".join(sql_lines)
