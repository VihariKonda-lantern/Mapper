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
    sort_col_name: str = "",  # Made mandatory (default to empty string if not provided)
    null_threshold_percentage: int = 15,
    process_curation: bool = True,
    inbound_path: str = "/mnt/data/inbound/raw/",
    file_format: str = "csv",
    file_separator: str = "\t",
    file_has_header: bool = False,
    file_date_format: str = "yyyyMMdd",
    mapping_date_format: Optional[str] = None,  # If None, will use file_date_format
    layout_df: Optional[Any] = None,
    final_mapping: Optional[Dict[str, Dict[str, Any]]] = None,
    file_master_id: int = 2490,
    ch_client_name: Optional[str] = None,  # CH client name (separate from DAPClientName)
    tagging_flag: bool = True,  # Tagging flag for curation_configurations
    claims_df: Optional[Any] = None  # Source file DataFrame - used to get raw file headers
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
        layout_df: Layout DataFrame for column mapping (used for prep->structured mappings)
        final_mapping: Field mapping dictionary
        file_master_id: File master ID (default: 2490)
        claims_df: Source file DataFrame - used to get raw file headers for raw zone
        
    Returns:
        SQL script as string
    """
    if preprocessor_name is None:
        # Default to common_PlanSponsorClaims_prep format (capital P and S)
        if domain_name.lower() == "plansponsorclaims":
            preprocessor_name = "common_PlanSponsorClaims_prep"
        else:
            preprocessor_name = f"common_{domain_name.lower()}_prep"
    
    # DAPClientName format: {client}_{plansponsor}
    # Avoid duplication if client_name already ends with plan_sponsor_name
    client_name_clean = client_name.strip()
    plan_sponsor_clean = plan_sponsor_name.strip()
    
    # Check if client_name already ends with plan_sponsor_name (case-insensitive)
    if client_name_clean.lower().endswith(f"_{plan_sponsor_clean.lower()}"):
        # Client name already includes plan sponsor, use as-is
        dap_client_name = client_name_clean
    else:
        # Append plan sponsor name
        dap_client_name = f"{client_name_clean}_{plan_sponsor_clean}"
    
    # CH client name: use provided value or default to client_name
    if ch_client_name is None:
        ch_client_name = client_name
    
    # Remove .txt extension from file_name_regex_pattern if present
    if file_name_regex_pattern and file_name_regex_pattern.endswith('.txt'):
        file_name_regex_pattern = file_name_regex_pattern[:-4]
    
    # Use file_date_format for mapping_date_format if not provided (should come from file, not hardcoded)
    if mapping_date_format is None:
        mapping_date_format = file_date_format
    
    sql_lines = []
    
    # Client setup - no header comments, direct MERGE statements
    # DAPClientName format: {client}_{plansponsor}
    sql_lines.append("MERGE CDAP.Client AS C")
    sql_lines.append(f"            USING (Select '{dap_client_name}' as client, coalesce(max(clientkey),0)+1 as max_clientkey from cdap.client) AS S")
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
    sql_lines.append(f"                    from CDAP.Client c ")
    sql_lines.append(f"                    join CDAP.Domain d on (1=1)")
    sql_lines.append(f"                    where c.DAPClientName = '{dap_client_name}' ")
    sql_lines.append(f"                    and d.DomainName = '{domain_name}') AS S")
    sql_lines.append(f"                ON (P.ClientKey = S.ClientKey and P.DomainId = S.DomainId)")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (DomainId, ClientKey, Description, IsActive)")
    sql_lines.append(f"                VALUES (S.DomainId, S.ClientKey, S.Description, 1);")
    sql_lines.append("")
    
    # Client-Sponsor relationship
    sql_lines.append("MERGE CDAP.ClientSponsor AS P")
    sql_lines.append(f"            USING (Select c.ClientKey, p.PlanSponsorId, concat(c.DAPClientName,':',p.PlanSponsorName) as Description")
    sql_lines.append(f"                    from CDAP.Client c ")
    sql_lines.append(f"                    join CDAP.PlanSponsor p on (1=1)")
    sql_lines.append(f"                    where c.DAPClientName = '{dap_client_name}' ")
    sql_lines.append(f"                    and p.PlanSponsorName = '{plan_sponsor_name}') AS S")
    sql_lines.append(f"                ON (P.ClientKey = S.ClientKey and P.PlanSponsorId = S.PlanSponsorId)")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (PlanSponsorId, ClientKey, Description, IsActive)")
    sql_lines.append(f"                VALUES (S.PlanSponsorId, S.ClientKey, S.Description, 1);")
    sql_lines.append("")
    
    # Domain-Sponsor relationship
    sql_lines.append("MERGE CDAP.DomainSponsor AS P")
    sql_lines.append(f"            USING (Select d.DomainId, p.PlanSponsorId, concat(d.DomainName,':',p.PlanSponsorName) as Description")
    sql_lines.append(f"                    from CDAP.Domain d ")
    sql_lines.append(f"                    join CDAP.PlanSponsor p on (1=1)")
    sql_lines.append(f"                    where d.DomainName = '{domain_name}'  ")
    sql_lines.append(f"                    and p.PlanSponsorName = '{plan_sponsor_name}') AS S")
    sql_lines.append(f"                ON (P.DomainId = S.DomainId and P.PlanSponsorId = S.PlanSponsorId)")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (PlanSponsorId, DomainId, Description, IsActive)")
    sql_lines.append(f"                VALUES (S.PlanSponsorId, S.DomainId, S.Description, 1);")
    sql_lines.append("")
    
    # Ingestion Config
    sql_lines.append("MERGE CDAP.IngestionConfig AS P")
    sql_lines.append(f"            USING (Select dc.DomainClientId, cs.ClientSponsorId, ds.DomainSponsorId, ")
    sql_lines.append(f"                        pp.PreprocessorId as PreprocessorId, {file_master_id} as FileMasterId")
    sql_lines.append(f"                    from CDAP.Domain d ")
    sql_lines.append(f"                    join CDAP.Client c on (1=1)")
    sql_lines.append(f"                    join CDAP.PlanSponsor p on (1=1)")
    sql_lines.append(f"                    join CDAP.Preprocessor pp on (1=1)")
    sql_lines.append(f"                    join CDAP.DomainClient dc on (dc.DomainId = d.DomainId and dc.ClientKey=c.ClientKey)")
    sql_lines.append(f"                    join CDAP.ClientSponsor cs on (cs.ClientKey = c.ClientKey and cs.PlanSponsorId = p.PlanSponsorId)")
    sql_lines.append(f"                    join CDAP.DomainSponsor ds on (ds.DomainId = d.DomainId and ds.PlanSponsorId = p.PlanSponsorId)")
    sql_lines.append(f"                    where d.DomainName = '{domain_name}' ")
    sql_lines.append(f"                    and c.DAPClientName = '{dap_client_name}'")
    sql_lines.append(f"                    and p.PlanSponsorName = '{plan_sponsor_name}'")
    sql_lines.append(f"                    and pp.PreprocessorName = '{preprocessor_name}') AS S")
    sql_lines.append(f"                ON (P.DomainClientId = S.DomainClientId and P.ClientSponsorId = S.ClientSponsorId and P.DomainSponsorId = S.DomainSponsorId)")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (PreprocessorId, FileMasterId, DomainClientId, ClientSponsorId, DomainSponsorId, IsActive)")
    sql_lines.append(f"                VALUES (S.PreprocessorId, S.FileMasterId, S.DomainClientId, S.ClientSponsorId, S.DomainSponsorId, 1);")
    sql_lines.append("")
    
    # Parameter Types - no section headers
    # Domain configurations parameter types
    domain_params = [
        'entity', 'primary_key', 'preprocessing_primary_key', 'file_name_date_format',
        'file_name_date_regex_pattern', 'client_name', 'demographic_match_tier_config',
        'demographic_match_tiers', 'sort_col_name', 'null_threshold_percentage', 'process_curation', 'inbound_path'
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
    
    # Parameters - no section headers
    
    # CH client name (used in config parameters) - separate from DAPClientName
    # DAPClientName is {client}_{plansponsor}, CH client name comes from CH
    ch_client_display_name = ch_client_name.replace('_', ' ') if ch_client_name else client_name.replace('_', ' ')
    
    # Domain configuration parameters - match reference format exactly
    if entity_type:
        sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
        sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '{entity_type}' = '' then null else '{entity_type}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'entity') AS S")
        sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
        sql_lines.append(f"            WHEN NOT MATCHED THEN")
        sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
        sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
        sql_lines.append("")
    
    if primary_key:
        sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
        sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '{primary_key}' = '' then null else '{primary_key}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'primary_key') AS S")
        sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
        sql_lines.append(f"            WHEN NOT MATCHED THEN")
        sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
        sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
        sql_lines.append("")
    
    if preprocessing_primary_key:
        sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
        sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '{preprocessing_primary_key}' = '' then null else '{preprocessing_primary_key}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'preprocessing_primary_key') AS S")
        sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
        sql_lines.append(f"            WHEN NOT MATCHED THEN")
        sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
        sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
        sql_lines.append("")
    
    if file_name_date_format:
        sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
        sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '{file_name_date_format}' = '' then null else '{file_name_date_format}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'file_name_date_format') AS S")
        sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
        sql_lines.append(f"            WHEN NOT MATCHED THEN")
        sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
        sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
        sql_lines.append("")
    
    if file_name_regex_pattern:
        sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
        sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '{file_name_regex_pattern}' = '' then null else '{file_name_regex_pattern}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'file_name_date_regex_pattern') AS S")
        sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
        sql_lines.append(f"            WHEN NOT MATCHED THEN")
        sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
        sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
        sql_lines.append("")
    
    # client_name parameter uses CH client name (not DAPClientName)
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '{ch_client_display_name}' = '' then null else '{ch_client_display_name}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'client_name') AS S")
    sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    if demographic_match_tier_config:
        sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
        sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '{demographic_match_tier_config}' = '' then null else '{demographic_match_tier_config}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'demographic_match_tier_config') AS S")
        sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
        sql_lines.append(f"            WHEN NOT MATCHED THEN")
        sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
        sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
        sql_lines.append("")
    
    # Add demographic_match_tiers parameter (JSON format)
    # Default tier configuration if not provided
    demographic_match_tiers_json = '{ "tier1": "patient_first_name,patient_last_name,patient_sex,patient_dob,patient_relationship_code", "tier2": "patient_first_name,patient_last_name,patient_sex,patient_dob"}'
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '{demographic_match_tiers_json}' = '' then null else '{demographic_match_tiers_json}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'demographic_match_tiers') AS S")
    sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    # sort_col_name is mandatory
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '{sort_col_name}' = '' then null else '{sort_col_name}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'sort_col_name') AS S")
    sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '{null_threshold_percentage}' = '' then null else '{null_threshold_percentage}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'null_threshold_percentage') AS S")
    sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    process_curation_val = 'Y' if process_curation else 'N'
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '{process_curation_val}' = '' then null else '{process_curation_val}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'process_curation') AS S")
    sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '{inbound_path}' = '' then null else '{inbound_path}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'inbound_path') AS S")
    sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    # Reading configuration parameters
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '{file_format}' = '' then null else '{file_format}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'reading_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'format') AS S")
    sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    # Read kwargs
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"        	USING (Select ParameterTypeId, (case when 'N' = '' then null else 'N' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'reading_configurations' AND coalesce(SubGroupName,'') = 'read_kwargs' AND ParamName = 'inferSchema') AS S")
    sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"        	USING (Select ParameterTypeId, (case when 'Y' = '' then null else 'Y' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'reading_configurations' AND coalesce(SubGroupName,'') = 'read_kwargs' AND ParamName = 'mergeSchema') AS S")
    sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    # Escape separator for SQL
    sep_escaped = file_separator.replace("'", "''").replace("\t", "\\t")
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '{sep_escaped}' = '' then null else '{sep_escaped}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'reading_configurations' AND coalesce(SubGroupName,'') = 'read_kwargs' AND ParamName = 'sep') AS S")
    sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    header_val = 'Y' if file_has_header else 'N'
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '{header_val}' = '' then null else '{header_val}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'reading_configurations' AND coalesce(SubGroupName,'') = 'read_kwargs' AND ParamName = 'header') AS S")
    sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '{file_date_format}' = '' then null else '{file_date_format}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'reading_configurations' AND coalesce(SubGroupName,'') = 'read_kwargs' AND ParamName = 'dateFormat') AS S")
    sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    # Read prep configurations
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '{preprocessor_name}' = '' then null else '{preprocessor_name}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'read_prep_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'function_name') AS S")
    sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    # Prep configurations - transformations
    # Get insurance_plan_name from final_mapping if available, otherwise use ch_client_display_name
    insurance_plan_name = ch_client_display_name  # Default fallback
    if final_mapping:
        insurance_plan_mapping = final_mapping.get("insurance_plan_name", {})
        if insurance_plan_mapping and insurance_plan_mapping.get("value"):
            insurance_plan_name = insurance_plan_mapping.get("value")
    
    transformations_json = f'{{"client_name":"{ch_client_display_name}","plan_sponsor_name":"{plan_sponsor_name}","insurance_plan_name":"{insurance_plan_name}"}}'
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '{transformations_json}' = '' then null else '{transformations_json}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'prep_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'transformations') AS S")
    sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    # Mapping configurations - dateformat can be comma-separated for multiple formats (e.g., "yyyyMMdd,yyyy-MM-dd")
    # Escape single quotes in mapping_date_format for SQL
    mapping_date_format_escaped = mapping_date_format.replace("'", "''") if mapping_date_format else ''
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '{mapping_date_format_escaped}' = '' then null else '{mapping_date_format_escaped}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'mapping_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'dateformat') AS S")
    sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '' = '' then null else '' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'mapping_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'demographic_match') AS S")
    sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    # Curation configurations
    # Tagging flag
    tagging_val = 'Y' if tagging_flag else 'N'
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"        	USING (Select ParameterTypeId, (case when '{tagging_val}' = '' then null else '{tagging_val}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'curation_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'tagging') AS S")
    sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    # Demographic match
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"        	USING (Select ParameterTypeId, (case when 'Y' = '' then null else 'Y' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'curation_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'demographic_match') AS S")
    sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    # Access configurations
    sql_lines.append(f"MERGE CDAP.IngestionParameter AS C")
    sql_lines.append(f"        	USING (Select ParameterTypeId, (case when 'iterable_sync' = '' then null else 'iterable_sync' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'access_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'process_type') AS S")
    sql_lines.append(f"		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')")
    sql_lines.append(f"            WHEN NOT MATCHED THEN")
    sql_lines.append(f"                INSERT (ParameterTypeId, ParamValue)")
    sql_lines.append(f"                VALUES (S.ParameterTypeId, S.ParamValue);")
    sql_lines.append("")
    
    # Ingestion Config Parameters - no section headers
    
    # Helper function to generate IngestionConfigParameter MERGE statements
    def add_config_parameter(group_name: str, sub_group: str, param_name: str, param_value: str):
        # Escape single quotes in param_value for SQL safety (handles comma-separated values like "yyyyMMdd,yyyy-MM-dd")
        param_value_escaped = param_value.replace("'", "''") if param_value else ''
        sub_group_condition = f"coalesce(ipt.SubGroupName,'') = '{sub_group}'" if sub_group else "coalesce(ipt.SubGroupName,'') = ''"
        sql_lines.append(f"MERGE CDAP.IngestionConfigParameter AS C")
        sql_lines.append(f"            USING (select a.IngestionConfigId, b.ParameterId from")
        sql_lines.append(f"                    (select ic.IngestionConfigId from")
        sql_lines.append(f"                    CDAP.IngestionConfig ic")
        sql_lines.append(f"                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)")
        sql_lines.append(f"                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)")
        sql_lines.append(f"                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)")
        sql_lines.append(f"                    join CDAP.Domain d on (d.domainid = dc.domainid)")
        sql_lines.append(f"                    join CDAP.Client c on (c.clientkey = dc.clientkey)")
        sql_lines.append(f"                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)")
        sql_lines.append(f"                    where c.DAPClientName = '{dap_client_name}' and d.DomainName='{domain_name}'")
        sql_lines.append(f"                    and ps.PlanSponsorName = '{plan_sponsor_name}'")
        sql_lines.append(f"                    ) a")
        sql_lines.append(f"                    join")
        sql_lines.append(f"                    (select ParameterId from")
        sql_lines.append(f"                    CDAP.IngestionParameter ip")
        sql_lines.append(f"                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)")
        sql_lines.append(f"                    where ipt.GroupName = '{group_name}'")
        sql_lines.append(f"                    and {sub_group_condition}")
        sql_lines.append(f"                    and ipt.ParamName = '{param_name}'")
        sql_lines.append(f"                    and coalesce(ip.ParamValue,'') = '{param_value_escaped}') b")
        sql_lines.append(f"                    on (1=1)) AS S")
        sql_lines.append(f"                ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)")
        sql_lines.append(f"                WHEN NOT MATCHED THEN")
        sql_lines.append(f"                    INSERT (IngestionConfigId, ParameterId)")
        sql_lines.append(f"                    VALUES (S.IngestionConfigId, S.ParameterId);")
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
    add_config_parameter('domain_configurations', '', 'client_name', ch_client_display_name)
    if demographic_match_tier_config:
        add_config_parameter('domain_configurations', '', 'demographic_match_tier_config', demographic_match_tier_config)
    add_config_parameter('domain_configurations', '', 'demographic_match_tiers', demographic_match_tiers_json)
    # sort_col_name is mandatory
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
    add_config_parameter('curation_configurations', '', 'tagging', tagging_val)
    add_config_parameter('curation_configurations', '', 'demographic_match', 'Y')
    add_config_parameter('access_configurations', '', 'process_type', 'iterable_sync')
    
    # Column mappings (if layout_df and final_mapping provided)
    if layout_df is not None and final_mapping is not None:
        try:
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
            
            # Note: ColumnDetail for prep zone will be generated from source columns (same as raw but cleaned)
            # Prep zone uses actual file layout (source columns) with special characters cleaned
            
            # Generate ZoneTable for raw, prep, and structured zones
            # Use DAPClientName (dap_client_name) for table names, not client_name
            raw_table_name = f"{dap_client_name.lower()}_layout"
            prep_table_name = f"{domain_name.lower()}_{entity_type.lower()}_{dap_client_name.lower()}"
            structured_table_name = f"{domain_name.lower()}_{entity_type.lower()}_standard"
            
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
            
            sql_lines.append(f"MERGE CDAP.ZoneTable AS C")
            sql_lines.append(f"    USING (select TOP 1 pz.ZoneId, '{structured_table_name}' as TableName from CDAP.ProcessingZone pz")
            sql_lines.append(f"            where pz.name = 'structured') AS S")
            sql_lines.append(f"        ON (C.ZoneId = S.ZoneId AND C.TableName = S.TableName)")
            sql_lines.append(f"    WHEN NOT MATCHED THEN")
            sql_lines.append(f"        INSERT (ZoneId, TableName)")
            sql_lines.append(f"        VALUES (S.ZoneId, S.TableName);")
            sql_lines.append("")
            
            # Generate ColumnDetail for raw zone (source columns from source file headers)
            # Raw file layout comes from source file headers (claims_df), not from final_mapping
            source_columns = []
            if claims_df is not None and not claims_df.empty:
                # Get all columns from source file (raw file layout)
                source_columns = list(claims_df.columns)
            else:
                # Fallback: extract from final_mapping if claims_df not available
                for internal_field, mapping_info in final_mapping.items():
                    if isinstance(mapping_info, dict) and 'value' in mapping_info:
                        source_col = mapping_info['value']
                        if source_col and source_col not in source_columns:
                            source_columns.append(source_col)
            
            # First, create ColumnDetail for all source columns (from raw file headers)
            for source_col in source_columns:
                # formatted_col_name = format_column_name(source_col, client_name)
                formatted_col_name = source_col.lower()
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
                # formatted_col_name = format_column_name(source_col, client_name)
                formatted_col_name = source_col.lower()
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
            
            prep_columns = source_columns + ['file_date', 'created_timestamp', 'modified_timestamp']
            # create ColumnDetail for all prep columns
            for source_col in prep_columns:
                formatted_col_name = format_column_name(source_col, client_name)
                formatted_col_name = formatted_col_name.lower()
                sql_lines.append(f"MERGE CDAP.ColumnDetail AS C")
                sql_lines.append(f"        	USING (Select '{formatted_col_name}' as ColumnName, 'string' as DataType")
                sql_lines.append(f"                    ) AS S")
                sql_lines.append(f"		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))")
                sql_lines.append(f"            WHEN NOT MATCHED THEN")
                sql_lines.append(f"                INSERT (ColumnName, DataType)")
                sql_lines.append(f"                VALUES (S.ColumnName, S.DataType);")
                sql_lines.append("")

            # Generate TableColumn for prep zone (source columns with cleaned names) - AFTER ColumnDetail
            # Prep zone uses actual file layout (source columns) with special characters cleaned, same as raw
            for col_order, source_col in enumerate(prep_columns, 1):
                formatted_col_name = format_column_name(source_col, client_name)
                formatted_col_name = formatted_col_name.lower()
                sql_lines.append(f"MERGE CDAP.TableColumn AS C")
                sql_lines.append(f"                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, {col_order} as ColumnOrder")
                sql_lines.append(f"                        from CDAP.ZoneTable zt")
                sql_lines.append(f"                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)")
                sql_lines.append(f"                        join CDAP.ColumnDetail cd on (1=1)")
                sql_lines.append(f"                        where pz.name = 'prep'")
                sql_lines.append(f"                        and zt.TableName = '{prep_table_name}'")
                sql_lines.append(f"                        and cd.ColumnName = '{formatted_col_name}'")
                sql_lines.append(f"                        and cd.DataType = 'string') AS S")
                sql_lines.append(f"                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)")
                sql_lines.append(f"                WHEN NOT MATCHED THEN")
                sql_lines.append(f"                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)")
                sql_lines.append(f"                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);")
                sql_lines.append("")
            
            # Generate ColumnMapping: raw → prep (ALL raw columns to prep using transformation function)
            # Raw columns come from source file headers (claims_df)
            # Prep columns come from source file headers (claims_df) with special characters cleaned
            # The transformation function cleans column names (removes special chars, replaces spaces with underscores)
            # This matches the reference file pattern - single MERGE that maps all columns using transformation
            sql_lines.append(f"MERGE CDAP.ColumnMapping AS C")
            sql_lines.append(f"        	    USING (select ic.IngestionConfigId, ftc.tablecolumnid as SourceTableColumnId, ttc.tablecolumnid as TargetTableColumnId")
            sql_lines.append(f"                    from cdap.IngestionConfig ic")
            sql_lines.append(f"                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)")
            sql_lines.append(f"                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)")
            sql_lines.append(f"                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)")
            sql_lines.append(f"                    join CDAP.Domain d on (d.domainid = dc.domainid)")
            sql_lines.append(f"                    join CDAP.Client c on (c.clientkey = dc.clientkey)")
            sql_lines.append(f"                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)")
            sql_lines.append(f"					join CDAP.ProcessingZone fpz on (fpz.name = 'raw')")
            sql_lines.append(f"					join CDAP.ProcessingZone tpz on (tpz.name = 'prep')")
            sql_lines.append(f"					join CDAP.ZoneTable fzt on (fzt.TableName = '{raw_table_name}' and fpz.zoneid=fzt.zoneid) ")
            sql_lines.append(f"					join CDAP.ZoneTable tzt on (tzt.TableName = '{prep_table_name}' and tpz.zoneid = tzt.zoneid)")
            sql_lines.append(f"					join CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)")
            sql_lines.append(f"					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)")
            sql_lines.append(f"					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid)")
            sql_lines.append(f"					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName=REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(LTRIM(RTRIM(REPLACE(REPLACE(fcd.ColumnName, CHAR(160), ' '), CHAR(9), ' ')   )),  '   ', ' '),'  ', ' '), ' ', '_'),'.',''),':',''),',',''),CHAR(10),''),'(',''),')',''),'/',''),'&',''),'#',''),'*','_'))")
            sql_lines.append(f"                    where c.DAPClientName = '{dap_client_name}' and d.DomainName='{domain_name}'")
            sql_lines.append(f"                    and ps.PlanSponsorName = '{plan_sponsor_name}') AS S")
            sql_lines.append(f"		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)")
            sql_lines.append(f"                WHEN NOT MATCHED THEN")
            sql_lines.append(f"                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId)")
            sql_lines.append(f"                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId);")
            sql_lines.append("")
            
            # Generate ColumnMapping: prep → structured
            # Based on team feedback: prep->structured should be 38 columns mapping (not 134)
            # Layout input is used to map from prep -> structured (CDM)
            # These columns will only be present in prep->structured mapping
            # Generate mappings dynamically from layout_df columns
            # Common field name mappings for structured zone
            common_mappings = {
                'file_date': 'file_effective_date',
                'claim_id': 'claim_id',
                'claim_type': 'claim_type',
                'patient_dob': 'patient_dob',
                'patient_first_name': 'patient_first_name',
                'patient_last_name': 'patient_last_name',
                'patient_sex': 'patient_sex',
                'patient_gender': 'patient_sex',
                'patient_ssn': 'patient_ssn',
                'subscriber_ssn': 'subscriber_ssn',
                'service_date_start': 'service_date_start',
                'service_date_end': 'service_date_end',
                'date_of_service_start': 'service_date_start',
                'date_of_service_end': 'service_date_end',
            }
            
            #default mapping for file_effective_date 
            sql_lines.append(f"MERGE CDAP.ColumnMapping AS C")
            sql_lines.append(f"        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, ")
            sql_lines.append(f"                        '' SVMRule")
            sql_lines.append(f"                    from cdap.IngestionConfig ic")
            sql_lines.append(f"                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)")
            sql_lines.append(f"                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)")
            sql_lines.append(f"                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)")
            sql_lines.append(f"                    join CDAP.Domain d on (d.domainid = dc.domainid)")
            sql_lines.append(f"                    join CDAP.Client c on (c.clientkey = dc.clientkey)")
            sql_lines.append(f"                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)")
            sql_lines.append(f"					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')")
            sql_lines.append(f"					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')")
            sql_lines.append(f"					join CDAP.ZoneTable fzt on (fzt.TableName = '{prep_table_name}' and fpz.zoneid=fzt.zoneid) ")
            sql_lines.append(f"					join CDAP.ZoneTable tzt on (tzt.TableName = '{structured_table_name}' and tpz.zoneid = tzt.zoneid)")
            sql_lines.append(f"					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)")
            sql_lines.append(f"					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)")
            sql_lines.append(f"					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='file_date')")
            sql_lines.append(f"					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='file_effective_date')")
            sql_lines.append(f"                    where c.DAPClientName = '{dap_client_name}' and d.DomainName='{domain_name}'")
            sql_lines.append(f"                    and ps.PlanSponsorName = '{plan_sponsor_name}') AS S")
            sql_lines.append(f"		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)")
            sql_lines.append(f"                WHEN NOT MATCHED THEN")
            sql_lines.append(f"                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)")
            sql_lines.append(f"                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);")
            sql_lines.append("")

            #default mapping for created_timestamp 
            sql_lines.append(f"MERGE CDAP.ColumnMapping AS C")
            sql_lines.append(f"        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, ")
            sql_lines.append(f"                        '' SVMRule")
            sql_lines.append(f"                    from cdap.IngestionConfig ic")
            sql_lines.append(f"                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)")
            sql_lines.append(f"                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)")
            sql_lines.append(f"                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)")
            sql_lines.append(f"                    join CDAP.Domain d on (d.domainid = dc.domainid)")
            sql_lines.append(f"                    join CDAP.Client c on (c.clientkey = dc.clientkey)")
            sql_lines.append(f"                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)")
            sql_lines.append(f"					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')")
            sql_lines.append(f"					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')")
            sql_lines.append(f"					join CDAP.ZoneTable fzt on (fzt.TableName = '{prep_table_name}' and fpz.zoneid=fzt.zoneid) ")
            sql_lines.append(f"					join CDAP.ZoneTable tzt on (tzt.TableName = '{structured_table_name}' and tpz.zoneid = tzt.zoneid)")
            sql_lines.append(f"					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)")
            sql_lines.append(f"					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)")
            sql_lines.append(f"					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='created_timestamp')")
            sql_lines.append(f"					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='created_timestamp')")
            sql_lines.append(f"                    where c.DAPClientName = '{dap_client_name}' and d.DomainName='{domain_name}'")
            sql_lines.append(f"                    and ps.PlanSponsorName = '{plan_sponsor_name}') AS S")
            sql_lines.append(f"		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)")
            sql_lines.append(f"                WHEN NOT MATCHED THEN")
            sql_lines.append(f"                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)")
            sql_lines.append(f"                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);")
            sql_lines.append("")

            #default mapping for modified_timestamp 
            sql_lines.append(f"MERGE CDAP.ColumnMapping AS C")
            sql_lines.append(f"        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, ")
            sql_lines.append(f"                        '' SVMRule")
            sql_lines.append(f"                    from cdap.IngestionConfig ic")
            sql_lines.append(f"                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)")
            sql_lines.append(f"                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)")
            sql_lines.append(f"                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)")
            sql_lines.append(f"                    join CDAP.Domain d on (d.domainid = dc.domainid)")
            sql_lines.append(f"                    join CDAP.Client c on (c.clientkey = dc.clientkey)")
            sql_lines.append(f"                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)")
            sql_lines.append(f"					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')")
            sql_lines.append(f"					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')")
            sql_lines.append(f"					join CDAP.ZoneTable fzt on (fzt.TableName = '{prep_table_name}' and fpz.zoneid=fzt.zoneid) ")
            sql_lines.append(f"					join CDAP.ZoneTable tzt on (tzt.TableName = '{structured_table_name}' and tpz.zoneid = tzt.zoneid)")
            sql_lines.append(f"					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)")
            sql_lines.append(f"					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)")
            sql_lines.append(f"					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='modified_timestamp')")
            sql_lines.append(f"					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='modified_timestamp')")
            sql_lines.append(f"                    where c.DAPClientName = '{dap_client_name}' and d.DomainName='{domain_name}'")
            sql_lines.append(f"                    and ps.PlanSponsorName = '{plan_sponsor_name}') AS S")
            sql_lines.append(f"		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)")
            sql_lines.append(f"                WHEN NOT MATCHED THEN")
            sql_lines.append(f"                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)")
            sql_lines.append(f"                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);")
            sql_lines.append("")

            # Generate mappings for all prep columns from layout_df (should be ~38 based on actual layout)
            try:
                for idx, row in layout_df.iterrows():
                    internal_field = str(row.get(internal_field_col, '')).strip()
                    if not internal_field or internal_field.lower() == 'nan':
                        continue
                    
                    prep_col = None
                    formatted_internal = format_column_name(internal_field, client_name)
                    internal_lower = formatted_internal.lower()
                
                    if final_mapping and internal_field in final_mapping:
                        source_col = final_mapping[internal_field].get("value", None)
                        if source_col and source_col.strip():
                            # Check if source_col exists in source_columns (from claims_df)
                            if source_col in source_columns:
                                # Format the source column name (same as prep zone formatting)
                                prep_col = format_column_name(source_col, client_name)
                            # If source_col is not in source_columns, it might be a manual text entry
                            # For manual entries, we still format it
                            elif source_col.strip():
                                prep_col = format_column_name(source_col, client_name)

                    prep_col = prep_col.lower() if prep_col else ''

                    # Special handling for Patient_Relationship: maps to both patient_relationship_code and patient_relationship_desc
                    if internal_field == "patient_relationship_code" or formatted_internal.lower() == "patient_relationship_code":
                        value_mapping = None
                        # Get value mapping from final_mapping if available
                        value_mapping = final_mapping[internal_field].get("value_mapping", None)
                        
                        # Map to patient_relationship_code (with value mapping if provided)
                        svm_rule_code = value_mapping if value_mapping else ''
                        # Escape single quotes in SVMRule for SQL
                        svm_rule_code_escaped = svm_rule_code.replace("'", "''") if svm_rule_code else ''
                        
                        sql_lines.append(f"MERGE CDAP.ColumnMapping AS C")
                        sql_lines.append(f"        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, ")
                        sql_lines.append(f"                        '{svm_rule_code_escaped}' SVMRule")
                        sql_lines.append(f"                    from cdap.IngestionConfig ic")
                        sql_lines.append(f"                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)")
                        sql_lines.append(f"                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)")
                        sql_lines.append(f"                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)")
                        sql_lines.append(f"                    join CDAP.Domain d on (d.domainid = dc.domainid)")
                        sql_lines.append(f"                    join CDAP.Client c on (c.clientkey = dc.clientkey)")
                        sql_lines.append(f"                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)")
                        sql_lines.append(f"					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')")
                        sql_lines.append(f"					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')")
                        sql_lines.append(f"					join CDAP.ZoneTable fzt on (fzt.TableName = '{prep_table_name}' and fpz.zoneid=fzt.zoneid) ")
                        sql_lines.append(f"					join CDAP.ZoneTable tzt on (tzt.TableName = '{structured_table_name}' and tpz.zoneid = tzt.zoneid)")
                        sql_lines.append(f"					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)")
                        sql_lines.append(f"					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)")
                        sql_lines.append(f"					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='{prep_col}')")
                        sql_lines.append(f"					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_relationship_code')")
                        sql_lines.append(f"                    where c.DAPClientName = '{dap_client_name}' and d.DomainName='{domain_name}'")
                        sql_lines.append(f"                    and ps.PlanSponsorName = '{plan_sponsor_name}') AS S")
                        sql_lines.append(f"		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)")
                        sql_lines.append(f"                WHEN NOT MATCHED THEN")
                        sql_lines.append(f"                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)")
                        sql_lines.append(f"                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);")
                        sql_lines.append("")
                        continue  # Skip normal mapping for Patient_Relationship_Code
                    
                    if internal_field == "patient_relationship_desc" or formatted_internal.lower() == "patient_relationship_desc":
                        value_mapping = None
                        # Get value mapping from final_mapping if available
                        value_mapping = final_mapping[internal_field].get("value_mapping", None)
                        
                        # Map to patient_relationship_desc (with value mapping if provided)
                        svm_rule_code = value_mapping if value_mapping else ''
                        # Escape single quotes in SVMRule for SQL
                        svm_rule_code_escaped = svm_rule_code.replace("'", "''") if svm_rule_code else ''
                        
                        # Map to patient_relationship_desc (without value mapping)
                        sql_lines.append(f"MERGE CDAP.ColumnMapping AS C")
                        sql_lines.append(f"        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, ")
                        sql_lines.append(f"                        '{svm_rule_code_escaped}' SVMRule")
                        sql_lines.append(f"                    from cdap.IngestionConfig ic")
                        sql_lines.append(f"                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)")
                        sql_lines.append(f"                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)")
                        sql_lines.append(f"                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)")
                        sql_lines.append(f"                    join CDAP.Domain d on (d.domainid = dc.domainid)")
                        sql_lines.append(f"                    join CDAP.Client c on (c.clientkey = dc.clientkey)")
                        sql_lines.append(f"                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)")
                        sql_lines.append(f"					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')")
                        sql_lines.append(f"					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')")
                        sql_lines.append(f"					join CDAP.ZoneTable fzt on (fzt.TableName = '{prep_table_name}' and fpz.zoneid=fzt.zoneid) ")
                        sql_lines.append(f"					join CDAP.ZoneTable tzt on (tzt.TableName = '{structured_table_name}' and tpz.zoneid = tzt.zoneid)")
                        sql_lines.append(f"					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)")
                        sql_lines.append(f"					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)")
                        sql_lines.append(f"					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='{prep_col}')")
                        sql_lines.append(f"					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_relationship_desc')")
                        sql_lines.append(f"                    where c.DAPClientName = '{dap_client_name}' and d.DomainName='{domain_name}'")
                        sql_lines.append(f"                    and ps.PlanSponsorName = '{plan_sponsor_name}') AS S")
                        sql_lines.append(f"		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)")
                        sql_lines.append(f"                WHEN NOT MATCHED THEN")
                        sql_lines.append(f"                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)")
                        sql_lines.append(f"                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);")
                        sql_lines.append("")
                        continue  # Skip normal mapping for Patient_Relationship_Desc
                    
                    # Determine structured column name for other fields
                    structured_col = None
                    
                    # Check common mappings first
                    for prep_field, std_field in common_mappings.items():
                        if prep_field in internal_lower or internal_lower == prep_field:
                            structured_col = std_field
                            break
                    
                    # If no common mapping, use the formatted internal field name as structured column name
                    # (structured zone typically uses same names as prep zone)
                    if not structured_col:
                        structured_col = formatted_internal
                    
                    # Generate mapping for this prep column to structured column
                    struct_col = structured_col.lower() if structured_col else ''
    
                    sql_lines.append(f"MERGE CDAP.ColumnMapping AS C")
                    sql_lines.append(f"        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, ")
                    sql_lines.append(f"                        '' SVMRule")
                    sql_lines.append(f"                    from cdap.IngestionConfig ic")
                    sql_lines.append(f"                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)")
                    sql_lines.append(f"                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)")
                    sql_lines.append(f"                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)")
                    sql_lines.append(f"                    join CDAP.Domain d on (d.domainid = dc.domainid)")
                    sql_lines.append(f"                    join CDAP.Client c on (c.clientkey = dc.clientkey)")
                    sql_lines.append(f"                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)")
                    sql_lines.append(f"					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')")
                    sql_lines.append(f"					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')")
                    sql_lines.append(f"					join CDAP.ZoneTable fzt on (fzt.TableName = '{prep_table_name}' and fpz.zoneid=fzt.zoneid) ")
                    sql_lines.append(f"					join CDAP.ZoneTable tzt on (tzt.TableName = '{structured_table_name}' and tpz.zoneid = tzt.zoneid)")
                    sql_lines.append(f"					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)")
                    sql_lines.append(f"					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)")
                    sql_lines.append(f"					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='{prep_col}')")
                    sql_lines.append(f"					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='{struct_col}')")
                    sql_lines.append(f"                    where c.DAPClientName = '{dap_client_name}' and d.DomainName='{domain_name}'")
                    sql_lines.append(f"                    and ps.PlanSponsorName = '{plan_sponsor_name}') AS S")
                    sql_lines.append(f"		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)")
                    sql_lines.append(f"                WHEN NOT MATCHED THEN")
                    sql_lines.append(f"                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)")
                    sql_lines.append(f"                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);")
                    sql_lines.append("")
            except Exception:
                # If generating prep → structured mappings fails, skip silently
                pass
        except Exception:
            # If column mapping generation fails, skip silently
            pass
    
    return "\n".join(sql_lines)
