MERGE CDAP.Client AS C
            USING (Select 'NorthsideHospital_Ameriben' as client, coalesce(max(clientkey),0)+1 as max_clientkey from cdap.client) AS S
                ON lower(C.DAPClientName) = lower(S.client)
            WHEN NOT MATCHED THEN
                INSERT (ClientKey, ClientCode, ClientShortName, Name, DAPClientName, IsActive, EffectiveDate, EffectiveThruDate)
                VALUES (S.max_clientkey, S.client, S.client, S.client, S.client, 1, GETDATE(), '9999-12-31');

MERGE CDAP.Domain AS D
            USING (Select 'PlanSponsorClaims' as domain) AS S
                ON lower(D.DomainName) = lower(S.domain)
            WHEN NOT MATCHED THEN
                INSERT (DomainName, Description, IsActive)
                VALUES (S.domain, S.domain, 1);

MERGE CDAP.PlanSponsor AS P
            USING (Select 'Ameriben' as plansponsor) AS S
                ON lower(P.PlanSponsorName) = lower(S.plansponsor)
            WHEN NOT MATCHED THEN
                INSERT (PlanSponsorName, IsActive)
                VALUES (S.plansponsor, 1);

MERGE CDAP.Preprocessor AS D
            USING (Select 'common_PlanSponsorClaims_prep' as PreprocessorName) AS S
                ON lower(D.PreprocessorName) = lower(S.PreprocessorName)
            WHEN NOT MATCHED THEN
                INSERT (PreprocessorName, Description)
                VALUES (S.PreprocessorName, S.PreprocessorName);

MERGE CDAP.DomainClient AS P
            USING (Select c.ClientKey, d.DomainId, concat(d.DomainName,':',c.DAPClientName) as Description
                    from CDAP.Client c 
                    join CDAP.Domain d on (1=1)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' 
                    and d.DomainName = 'PlanSponsorClaims') AS S
                ON (P.ClientKey = S.ClientKey and P.DomainId = S.DomainId)
            WHEN NOT MATCHED THEN
                INSERT (DomainId, ClientKey, Description, IsActive)
                VALUES (S.DomainId, S.ClientKey, S.Description, 1);

MERGE CDAP.ClientSponsor AS P
            USING (Select c.ClientKey, p.PlanSponsorId, concat(c.DAPClientName,':',p.PlanSponsorName) as Description
                    from CDAP.Client c 
                    join CDAP.PlanSponsor p on (1=1)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' 
                    and p.PlanSponsorName = 'Ameriben') AS S
                ON (P.ClientKey = S.ClientKey and P.PlanSponsorId = S.PlanSponsorId)
            WHEN NOT MATCHED THEN
                INSERT (PlanSponsorId, ClientKey, Description, IsActive)
                VALUES (S.PlanSponsorId, S.ClientKey, S.Description, 1);

MERGE CDAP.DomainSponsor AS P
            USING (Select d.DomainId, p.PlanSponsorId, concat(d.DomainName,':',p.PlanSponsorName) as Description
                    from CDAP.Domain d 
                    join CDAP.PlanSponsor p on (1=1)
                    where d.DomainName = 'PlanSponsorClaims'  
                    and p.PlanSponsorName = 'Ameriben') AS S
                ON (P.DomainId = S.DomainId and P.PlanSponsorId = S.PlanSponsorId)
            WHEN NOT MATCHED THEN
                INSERT (PlanSponsorId, DomainId, Description, IsActive)
                VALUES (S.PlanSponsorId, S.DomainId, S.Description, 1);

MERGE CDAP.IngestionConfig AS P
            USING (Select dc.DomainClientId, cs.ClientSponsorId, ds.DomainSponsorId, 
                        pp.PreprocessorId as PreprocessorId, 2490 as FileMasterId
                    from CDAP.Domain d 
                    join CDAP.Client c on (1=1)
                    join CDAP.PlanSponsor p on (1=1)
                    join CDAP.Preprocessor pp on (1=1)
                    join CDAP.DomainClient dc on (dc.DomainId = d.DomainId and dc.ClientKey=c.ClientKey)
                    join CDAP.ClientSponsor cs on (cs.ClientKey = c.ClientKey and cs.PlanSponsorId = p.PlanSponsorId)
                    join CDAP.DomainSponsor ds on (ds.DomainId = d.DomainId and ds.PlanSponsorId = p.PlanSponsorId)
                    where d.DomainName = 'PlanSponsorClaims' 
                    and c.DAPClientName = 'NorthsideHospital_Ameriben'
                    and p.PlanSponsorName = 'Ameriben'
                    and pp.PreprocessorName = 'common_PlanSponsorClaims_prep') AS S
                ON (P.DomainClientId = S.DomainClientId and P.ClientSponsorId = S.ClientSponsorId and P.DomainSponsorId = S.DomainSponsorId)
            WHEN NOT MATCHED THEN
                INSERT (PreprocessorId, FileMasterId, DomainClientId, ClientSponsorId, DomainSponsorId, IsActive)
                VALUES (S.PreprocessorId, S.FileMasterId, S.DomainClientId, S.ClientSponsorId, S.DomainSponsorId, 1);

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'domain_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'entity' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'domain_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'primary_key' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'domain_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'preprocessing_primary_key' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'domain_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'file_name_date_format' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'domain_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'file_name_date_regex_pattern' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'domain_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'client_name' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'domain_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'demographic_match_tier_config' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'domain_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'demographic_match_tiers' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'domain_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'sort_col_name' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'domain_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'null_threshold_percentage' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'domain_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'process_curation' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'domain_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'inbound_path' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'reading_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'format' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'reading_configurations' as GroupName, (case when 'read_kwargs' = '' then null else 'read_kwargs' end) as SubGroupName, 'inferSchema' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'reading_configurations' as GroupName, (case when 'read_kwargs' = '' then null else 'read_kwargs' end) as SubGroupName, 'mergeSchema' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'reading_configurations' as GroupName, (case when 'read_kwargs' = '' then null else 'read_kwargs' end) as SubGroupName, 'sep' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'reading_configurations' as GroupName, (case when 'read_kwargs' = '' then null else 'read_kwargs' end) as SubGroupName, 'header' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'reading_configurations' as GroupName, (case when 'read_kwargs' = '' then null else 'read_kwargs' end) as SubGroupName, 'dateFormat' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'read_prep_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'function_name' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'prep_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'transformations' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'mapping_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'dateformat' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'mapping_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'demographic_match' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'mapping_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'retain_not_null_cols' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'curation_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'tagging' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'curation_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'demographic_match' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameterType AS C
        	USING (Select 'access_configurations' as GroupName, (case when '' = '' then null else '' end) as SubGroupName, 'process_type' as ParamName) AS S
		        ON (lower(C.GroupName) = lower(S.GroupName) AND lower(coalesce(C.SubGroupName,'')) = lower(coalesce(S.SubGroupName,'')) AND lower(C.ParamName) = lower(S.ParamName))
            WHEN NOT MATCHED THEN
                INSERT (GroupName, SubGroupName, ParamName, ParamDescription)
                VALUES (S.GroupName, S.SubGroupName, S.ParamName, Concat(S.GroupName, ':', S.SubGroupName, ':', S.ParamName));

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'Medical' = '' then null else 'Medical' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'entity') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'Claim_ID,Claim_Line' = '' then null else 'Claim_ID,Claim_Line' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'primary_key') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'Claim_ID,Claim_Line_ID' = '' then null else 'Claim_ID,Claim_Line_ID' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'preprocessing_primary_key') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'yyyyMMdd' = '' then null else 'yyyyMMdd' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'file_name_date_format') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'Northside_SurgeryPlus_Claims_(\d+)$' = '' then null else 'Northside_SurgeryPlus_Claims_(\d+)$' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'file_name_date_regex_pattern') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'Northside Hospital' = '' then null else 'Northside Hospital' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'client_name') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'tier1,tier2' = '' then null else 'tier1,tier2' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'demographic_match_tier_config') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when '{ "tier1": "patient_first_name,patient_last_name,patient_sex,patient_dob,patient_relationship_code", "tier2": "patient_first_name,patient_last_name,patient_sex,patient_dob"}' = '' then null else '{ "tier1": "patient_first_name,patient_last_name,patient_sex,patient_dob,patient_relationship_code", "tier2": "patient_first_name,patient_last_name,patient_sex,patient_dob"}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'demographic_match_tiers') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'date_of_service_start' = '' then null else 'date_of_service_start' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'sort_col_name') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when '15' = '' then null else '15' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'null_threshold_percentage') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'Y' = '' then null else 'Y' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'process_curation') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when '/mnt/data/inbound/raw/' = '' then null else '/mnt/data/inbound/raw/' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'inbound_path') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'csv' = '' then null else 'csv' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'reading_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'format') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'N' = '' then null else 'N' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'reading_configurations' AND coalesce(SubGroupName,'') = 'read_kwargs' AND ParamName = 'inferSchema') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'Y' = '' then null else 'Y' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'reading_configurations' AND coalesce(SubGroupName,'') = 'read_kwargs' AND ParamName = 'mergeSchema') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when ',' = '' then null else ',' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'reading_configurations' AND coalesce(SubGroupName,'') = 'read_kwargs' AND ParamName = 'sep') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'Y' = '' then null else 'Y' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'reading_configurations' AND coalesce(SubGroupName,'') = 'read_kwargs' AND ParamName = 'header') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'yyyyMd' = '' then null else 'yyyyMd' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'reading_configurations' AND coalesce(SubGroupName,'') = 'read_kwargs' AND ParamName = 'dateFormat') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'common_PlanSponsorClaims_prep' = '' then null else 'common_PlanSponsorClaims_prep' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'read_prep_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'function_name') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when '{"client_name":"Northside Hospital","plan_sponsor_name":"Ameriben","insurance_plan_name":"Northside Hospital"}' = '' then null else '{"client_name":"Northside Hospital","plan_sponsor_name":"Ameriben","insurance_plan_name":"Northside Hospital"}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'prep_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'transformations') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'yyyyMMdd' = '' then null else 'yyyyMMdd' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'mapping_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'dateformat') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when '' = '' then null else '' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'mapping_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'demographic_match') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when '' = '' then null else '' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'mapping_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'retain_not_null_cols') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'Y' = '' then null else 'Y' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'curation_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'tagging') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'Y' = '' then null else 'Y' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'curation_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'demographic_match') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'iterable_sync' = '' then null else 'iterable_sync' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'access_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'process_type') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'domain_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'entity'
                    and coalesce(ip.ParamValue,'') = 'Medical') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'domain_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'primary_key'
                    and coalesce(ip.ParamValue,'') = 'Claim_ID,Claim_Line') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'domain_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'preprocessing_primary_key'
                    and coalesce(ip.ParamValue,'') = 'Claim_ID,Claim_Line_ID') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'domain_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'file_name_date_format'
                    and coalesce(ip.ParamValue,'') = 'yyyyMMdd') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'domain_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'file_name_date_regex_pattern'
                    and coalesce(ip.ParamValue,'') = 'Northside_SurgeryPlus_Claims_(\d+)$') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'domain_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'client_name'
                    and coalesce(ip.ParamValue,'') = 'Northside Hospital') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'domain_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'demographic_match_tier_config'
                    and coalesce(ip.ParamValue,'') = 'tier1,tier2') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'domain_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'demographic_match_tiers'
                    and coalesce(ip.ParamValue,'') = '{ "tier1": "patient_first_name,patient_last_name,patient_sex,patient_dob,patient_relationship_code", "tier2": "patient_first_name,patient_last_name,patient_sex,patient_dob"}') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'domain_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'sort_col_name'
                    and coalesce(ip.ParamValue,'') = 'date_of_service_start') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'domain_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'null_threshold_percentage'
                    and coalesce(ip.ParamValue,'') = '15') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'domain_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'process_curation'
                    and coalesce(ip.ParamValue,'') = 'Y') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'domain_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'inbound_path'
                    and coalesce(ip.ParamValue,'') = '/mnt/data/inbound/raw/') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'reading_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'format'
                    and coalesce(ip.ParamValue,'') = 'csv') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'reading_configurations'
                    and coalesce(ipt.SubGroupName,'') = 'read_kwargs'
                    and ipt.ParamName = 'inferSchema'
                    and coalesce(ip.ParamValue,'') = 'N') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'reading_configurations'
                    and coalesce(ipt.SubGroupName,'') = 'read_kwargs'
                    and ipt.ParamName = 'mergeSchema'
                    and coalesce(ip.ParamValue,'') = 'Y') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'reading_configurations'
                    and coalesce(ipt.SubGroupName,'') = 'read_kwargs'
                    and ipt.ParamName = 'sep'
                    and coalesce(ip.ParamValue,'') = ',') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'reading_configurations'
                    and coalesce(ipt.SubGroupName,'') = 'read_kwargs'
                    and ipt.ParamName = 'header'
                    and coalesce(ip.ParamValue,'') = 'Y') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'reading_configurations'
                    and coalesce(ipt.SubGroupName,'') = 'read_kwargs'
                    and ipt.ParamName = 'dateFormat'
                    and coalesce(ip.ParamValue,'') = 'yyyyMd') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'read_prep_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'function_name'
                    and coalesce(ip.ParamValue,'') = 'common_PlanSponsorClaims_prep') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'prep_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'transformations'
                    and coalesce(ip.ParamValue,'') = '{"client_name":"Northside Hospital","plan_sponsor_name":"Ameriben","insurance_plan_name":"Northside Hospital"}') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'mapping_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'dateformat'
                    and coalesce(ip.ParamValue,'') = 'yyyyMMdd') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'mapping_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'demographic_match'
                    and coalesce(ip.ParamValue,'') = '') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'mapping_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'retain_not_null_cols'
                    and coalesce(ip.ParamValue,'') = '') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'curation_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'tagging'
                    and coalesce(ip.ParamValue,'') = 'Y') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'curation_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'demographic_match'
                    and coalesce(ip.ParamValue,'') = 'Y') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.IngestionConfigParameter AS C
        	USING (select a.IngestionConfigId, b.ParameterId from
                    (select ic.IngestionConfigId from 
                    CDAP.IngestionConfig ic 
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'access_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'process_type'
                    and coalesce(ip.ParamValue,'') = 'iterable_sync') b
                    on (1=1)) AS S
            ON (C.IngestionConfigId = S.IngestionConfigId) AND (C.ParameterId = S.ParameterId)
            WHEN NOT MATCHED THEN
                INSERT (IngestionConfigId, ParameterId)
                VALUES (S.IngestionConfigId, S.ParameterId);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'sponsor' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'subscriber ssn' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient ssn' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient dob' as ColumnName, 'date' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient first name' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient last name' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient gender' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dependent beneficiary no' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient relationship' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient address' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient address 2' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient city' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient state' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient zip' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'date of service start' as ColumnName, 'date' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'date of service end' as ColumnName, 'date' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'claim id' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'claim line id' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'icd version' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx code 1' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx code 2' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx code 3' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx code 4' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx code 5' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx code 6' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx code 7' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx code 8' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx code 9' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx code 10' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx code 11' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx code 12' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx code 13' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx code 14' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx code 15' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx code 16' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx code 17' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx code 18' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'drg code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'procedure code 1' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'procedure code 2' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'place of service' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'service location zip' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'referring provider npi' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'rending provider npi' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'sponsor' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'subscriber_ssn' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient_ssn' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient_dob' as ColumnName, 'date' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient_first_name' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient_last_name' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient_gender' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dependent_beneficiary_no' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient_relationship' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient_address' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient_address_2' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient_city' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient_state' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'patient_zip' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'date_of_service_start' as ColumnName, 'date' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'date_of_service_end' as ColumnName, 'date' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'claim_id' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'claim_line_id' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'icd_version' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx_code_1' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx_code_2' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx_code_3' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx_code_4' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx_code_5' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx_code_6' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx_code_7' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx_code_8' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx_code_9' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx_code_10' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx_code_11' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx_code_12' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx_code_13' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx_code_14' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx_code_15' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx_code_16' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx_code_17' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'dx_code_18' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'drg_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'procedure_code_1' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'procedure_code_2' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'place_of_service' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'service_location_zip' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'referring_provider_npi' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'rending_provider_npi' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'file_date' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'created_timestamp' as ColumnName, 'timestamp' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'modified_timestamp' as ColumnName, 'timestamp' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select 'validation_results' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ZoneTable AS C
        	USING (select TOP 1 pz.ZoneId, 'northsidehospital_ameriben_layout' as TableName from CDAP.ProcessingZone pz
                    where pz.name = 'raw') AS S
		        ON (C.ZoneId = S.ZoneId AND C.TableName = S.TableName)
            WHEN NOT MATCHED THEN
                INSERT (ZoneId, TableName)
                VALUES (S.ZoneId, S.TableName);

MERGE CDAP.ZoneTable AS C
        	USING (select TOP 1 pz.ZoneId, 'plansponsorclaims_medical_northsidehospital_ameriben' as TableName from CDAP.ProcessingZone pz
                    where pz.name = 'prep') AS S
		        ON (C.ZoneId = S.ZoneId AND C.TableName = S.TableName)
            WHEN NOT MATCHED THEN
                INSERT (ZoneId, TableName)
                VALUES (S.ZoneId, S.TableName);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 1 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'sponsor'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 2 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'subscriber ssn'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 3 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'patient ssn'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 4 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'patient dob'
                        and cd.DataType = 'date') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 5 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'patient first name'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 6 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'patient last name'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 7 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'patient gender'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 8 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'dependent beneficiary no'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 9 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'patient relationship'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 10 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'patient address'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 11 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'patient address 2'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 12 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'patient city'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 13 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'patient state'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 14 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'patient zip'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 15 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'date of service start'
                        and cd.DataType = 'date') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 16 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'date of service end'
                        and cd.DataType = 'date') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 17 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'claim id'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 18 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'claim line id'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 19 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'icd version'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 20 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'dx code 1'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 21 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'dx code 2'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 22 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'dx code 3'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 23 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'dx code 4'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 24 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'dx code 5'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 25 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'dx code 6'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 26 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'dx code 7'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 27 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'dx code 8'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 28 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'dx code 9'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 29 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'dx code 10'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 30 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'dx code 11'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 31 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'dx code 12'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 32 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'dx code 13'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 33 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'dx code 14'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 34 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'dx code 15'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 35 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'dx code 16'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 36 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'dx code 17'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 37 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'dx code 18'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 38 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'drg code'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 39 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'procedure code 1'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 40 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'procedure code 2'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 41 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'place of service'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 42 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'service location zip'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 43 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'referring provider npi'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 44 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'northsidehospital_ameriben_layout'
                        and cd.ColumnName = 'rending provider npi'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 1 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'sponsor'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 2 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'subscriber_ssn'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 3 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'patient_ssn'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 4 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'patient_dob'
                    and cd.DataType = 'date') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 5 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'patient_first_name'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 6 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'patient_last_name'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 7 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'patient_gender'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 8 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'dependent_beneficiary_no'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 9 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'patient_relationship'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 10 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'patient_address'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 11 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'patient_address_2'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 12 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'patient_city'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 13 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'patient_state'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 14 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'patient_zip'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 15 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'date_of_service_start'
                    and cd.DataType = 'date') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 16 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'date_of_service_end'
                    and cd.DataType = 'date') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 17 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'claim_id'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 18 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'claim_line_id'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 19 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'icd_version'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 20 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'dx_code_1'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 21 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'dx_code_2'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 22 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'dx_code_3'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 23 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'dx_code_4'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 24 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'dx_code_5'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 25 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'dx_code_6'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 26 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'dx_code_7'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 27 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'dx_code_8'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 28 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'dx_code_9'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 29 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'dx_code_10'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 30 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'dx_code_11'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 31 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'dx_code_12'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 32 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'dx_code_13'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 33 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'dx_code_14'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 34 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'dx_code_15'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 35 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'dx_code_16'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 36 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'dx_code_17'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 37 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'dx_code_18'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 38 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'drg_code'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 39 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'procedure_code_1'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 40 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'procedure_code_2'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 41 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'place_of_service'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 42 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'service_location_zip'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 43 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'referring_provider_npi'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 44 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'rending_provider_npi'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 45 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'file_date'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 46 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'created_timestamp'
                    and cd.DataType = 'timestamp') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 47 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'modified_timestamp'
                    and cd.DataType = 'timestamp') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 48 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben'
                    and cd.ColumnName = 'validation_results'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.IngestionConfigId, ftc.tablecolumnid as SourceTableColumnId, ttc.tablecolumnid as TargetTableColumnId
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'raw')
					join CDAP.ProcessingZone tpz on (tpz.name = 'prep')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'northsidehospital_ameriben_layout' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid)
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName=REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(LTRIM(RTRIM(REPLACE(REPLACE(fcd.ColumnName, CHAR(160), ' '), CHAR(9), ' ')   )),  '   ', ' '),'  ', ' '), ' ', '_'),'.',''),':',''),',',''),CHAR(10),''),'(',''),')',''),'/',''),'&',''),'#',''),'*','_'))
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='file_date')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='file_effective_date')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='claim_id')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='claim_id')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='claim_id')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='claim_type')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='claim_id')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='claim_tob')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='Sponsor')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insurance_plan_name')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='static_plan_sponsor_name')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='plan_sponsor_name')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_id')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_group_number')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_first_name')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_last_name')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_middle_initial')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='subscriber_ssn')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_ssn')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_dob')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_sex')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_address')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_address2')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_city')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_state')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_zip')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_phone')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_email')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='patient_first_name')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_first_name')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='patient_last_name')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_last_name')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_middle_initial')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='patient_ssn')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_ssn')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='patient_dob')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_dob')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='patient_gender')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_sex')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='patient_address')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_address')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='patient_address_2')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_address2')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='patient_city')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_city')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='patient_state')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_state')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='patient_zip')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_zip')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_phone')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_email')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        'source_value,replace_value
SELF,1
SPOUSE,2
CHILD,3' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='patient_relationship')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_relationship_code')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        'source_value,replace_value
SELF,Self
SPOUSE,Spouse
CHILD,Child' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='patient_relationship')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_relationship_desc')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='ICD_Version')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='icd_version')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='dx_code_1')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_1')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='dx_code_2')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_2')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='dx_code_3')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_3')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='dx_code_4')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_4')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='dx_code_5')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_5')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='dx_code_6')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_6')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='dx_code_7')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_7')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='dx_code_8')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_8')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='dx_code_9')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_9')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='dx_code_10')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_10')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='dx_code_11')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_11')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='dx_code_12')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_12')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='drg_code')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='drg_code')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='date_of_service_start')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='begin_date')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='date_of_service_end')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='end_date')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='pos_code')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='procedure_code_2')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='procedure_code')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='revenue_code')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='revenue_code_description')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='ndc')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='mod_1')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='rendering_provider_name')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='rendering_provider_npi')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='facility_name')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='facility_npi')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='facility_zip')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='claim_line_id')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='claim_line')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='member_sequence_number')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='client_name')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='client_name')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='created_timestamp')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='created_timestamp')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        '' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_northsidehospital_ameriben' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='modified_timestamp')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='modified_timestamp')
                    where c.DAPClientName = 'NorthsideHospital_Ameriben' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Ameriben') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);