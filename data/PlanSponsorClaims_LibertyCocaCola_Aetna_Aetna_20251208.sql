MERGE CDAP.Client AS C
            USING (Select 'LibertyCocaCola_Aetna' as client, coalesce(max(clientkey),0)+1 as max_clientkey from cdap.client) AS S
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
            USING (Select 'Aetna' as plansponsor) AS S
                ON lower(P.PlanSponsorName) = lower(S.plansponsor)
            WHEN NOT MATCHED THEN
                INSERT (PlanSponsorName, IsActive)
                VALUES (S.plansponsor, 1);

MERGE CDAP.Preprocessor AS D
            USING (Select 'florida_aetna_PlanSponsorClaims_prep' as PreprocessorName) AS S
                ON lower(D.PreprocessorName) = lower(S.PreprocessorName)
            WHEN NOT MATCHED THEN
                INSERT (PreprocessorName, Description)
                VALUES (S.PreprocessorName, S.PreprocessorName);

MERGE CDAP.DomainClient AS P
            USING (Select c.ClientKey, d.DomainId, concat(d.DomainName,':',c.DAPClientName) as Description
                    from CDAP.Client c 
                    join CDAP.Domain d on (1=1)
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' 
                    and d.DomainName = 'PlanSponsorClaims') AS S
                ON (P.ClientKey = S.ClientKey and P.DomainId = S.DomainId)
            WHEN NOT MATCHED THEN
                INSERT (DomainId, ClientKey, Description, IsActive)
                VALUES (S.DomainId, S.ClientKey, S.Description, 1);

MERGE CDAP.ClientSponsor AS P
            USING (Select c.ClientKey, p.PlanSponsorId, concat(c.DAPClientName,':',p.PlanSponsorName) as Description
                    from CDAP.Client c 
                    join CDAP.PlanSponsor p on (1=1)
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' 
                    and p.PlanSponsorName = 'Aetna') AS S
                ON (P.ClientKey = S.ClientKey and P.PlanSponsorId = S.PlanSponsorId)
            WHEN NOT MATCHED THEN
                INSERT (PlanSponsorId, ClientKey, Description, IsActive)
                VALUES (S.PlanSponsorId, S.ClientKey, S.Description, 1);

MERGE CDAP.DomainSponsor AS P
            USING (Select d.DomainId, p.PlanSponsorId, concat(d.DomainName,':',p.PlanSponsorName) as Description
                    from CDAP.Domain d 
                    join CDAP.PlanSponsor p on (1=1)
                    where d.DomainName = 'PlanSponsorClaims'  
                    and p.PlanSponsorName = 'Aetna') AS S
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
                    and c.DAPClientName = 'LibertyCocaCola_Aetna'
                    and p.PlanSponsorName = 'Aetna'
                    and pp.PreprocessorName = 'florida_aetna_PlanSponsorClaims_prep') AS S
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
        	USING (Select ParameterTypeId, (case when '33_source_specific_transaction_id_number' = '' then null else '33_source_specific_transaction_id_number' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'preprocessing_primary_key') AS S
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
        	USING (Select ParameterTypeId, (case when 'UMED_CLMDATA___(\d+)_(\d+)$' = '' then null else 'UMED_CLMDATA___(\d+)_(\d+)$' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'file_name_date_regex_pattern') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'Liberty Coca-Cola' = '' then null else 'Liberty Coca-Cola' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'client_name') AS S
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
        	USING (Select ParameterTypeId, (case when '60_Date_Service_Started' = '' then null else '60_Date_Service_Started' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'domain_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'sort_col_name') AS S
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
        	USING (Select ParameterTypeId, (case when '\t' = '' then null else '\t' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'reading_configurations' AND coalesce(SubGroupName,'') = 'read_kwargs' AND ParamName = 'sep') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'N' = '' then null else 'N' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'reading_configurations' AND coalesce(SubGroupName,'') = 'read_kwargs' AND ParamName = 'header') AS S
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
        	USING (Select ParameterTypeId, (case when 'florida_aetna_PlanSponsorClaims_prep' = '' then null else 'florida_aetna_PlanSponsorClaims_prep' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'read_prep_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'function_name') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when '{"client_name":"Liberty Coca-Cola","plan_sponsor_name":"Aetna","insurance_plan_name":"Liberty Coca-Cola"}' = '' then null else '{"client_name":"Liberty Coca-Cola","plan_sponsor_name":"Aetna","insurance_plan_name":"Liberty Coca-Cola"}' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'prep_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'transformations') AS S
		        ON (C.ParameterTypeId = S.ParameterTypeId) AND coalesce(C.ParamValue,'') = coalesce(S.ParamValue,'')
            WHEN NOT MATCHED THEN
                INSERT (ParameterTypeId, ParamValue)
                VALUES (S.ParameterTypeId, S.ParamValue);

MERGE CDAP.IngestionParameter AS C
        	USING (Select ParameterTypeId, (case when 'yyyy-MM-dd' = '' then null else 'yyyy-MM-dd' end) as ParamValue from cdap.IngestionParameterType where GroupName = 'mapping_configurations' AND coalesce(SubGroupName,'') = '' AND ParamName = 'dateformat') AS S
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'domain_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'preprocessing_primary_key'
                    and coalesce(ip.ParamValue,'') = '33_source_specific_transaction_id_number') b
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'domain_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'file_name_date_regex_pattern'
                    and coalesce(ip.ParamValue,'') = 'UMED_CLMDATA___(\d+)_(\d+)$') b
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'domain_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'client_name'
                    and coalesce(ip.ParamValue,'') = 'Liberty Coca-Cola') b
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'domain_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'sort_col_name'
                    and coalesce(ip.ParamValue,'') = '60_Date_Service_Started') b
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'reading_configurations'
                    and coalesce(ipt.SubGroupName,'') = 'read_kwargs'
                    and ipt.ParamName = 'sep'
                    and coalesce(ip.ParamValue,'') = '\t') b
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'reading_configurations'
                    and coalesce(ipt.SubGroupName,'') = 'read_kwargs'
                    and ipt.ParamName = 'header'
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'read_prep_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'function_name'
                    and coalesce(ip.ParamValue,'') = 'florida_aetna_PlanSponsorClaims_prep') b
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'prep_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'transformations'
                    and coalesce(ip.ParamValue,'') = '{"client_name":"Liberty Coca-Cola","plan_sponsor_name":"Aetna","insurance_plan_name":"Liberty Coca-Cola"}') b
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
                    ) a
                    join 
                    (select ParameterId from
                    CDAP.IngestionParameter ip
                    join CDAP.IngestionParameterType ipt on (ipt.ParameterTypeId = ip.ParameterTypeId)
                    where ipt.GroupName = 'mapping_configurations'
                    and coalesce(ipt.SubGroupName,'') = ''
                    and ipt.ParamName = 'dateformat'
                    and coalesce(ip.ParamValue,'') = 'yyyy-MM-dd') b
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
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
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna'
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
        	USING (Select '1_hierarchy_level_1_most_summarized' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '2_hierarchy_level_2' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '3_hierarchy_level_3' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '4_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '5_hierarchy_level_5' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '6_hierarchy_level_6_most_granular' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '7_source_system_platform' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '8_adjustment_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '9_preferred_vs_non_preferred_benefit_level' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '10_general_category_of_health_plan' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '11_line_of_business' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '12_classification_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '13_benefit_identification_code_bic' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '14_plan_code_or_extension_of_hierarchy' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '15_benefit_tier' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '16_funding_arrangement' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '17_employees_ssn' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '18_employees_last_name' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '19_employees_first_name_or_initial' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '20_employees_gender' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '21_employees_date_of_birth' as ColumnName, 'date' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '22_employees_zip_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '23_employees_state' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '24_coverage_enrollment_tier' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '25_members_ssn' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '26_members_id_assigned_in_data_warehouse' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '27_members_number' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '28_members_last_name' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '29_members_first_name' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '30_members_gender' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '31_members_relationship_to_employee' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '32_members_date_of_birth' as ColumnName, 'date' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '33_source_specific_transaction_id_number' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '34_acas_generation_segment_number' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '35_acas_pointer_back_to_previous_gen_seg' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '36_traditional_claim_id' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '37_expense_pay_line_number' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '38_claim_line_id_assigned_in_data_warehouse' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '39_employees_network_id' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '40_servicing_providers_network_id' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '41_referral_type' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '42_pcps_irs_tax_identification_number_tin_format_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '43_pcps_irs_tax_identification_number_tin' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '44_pcps_name_last_or_full' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '45_servicing_providers_tax_id_number_tin_format_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '46_servicing_providers_tax_id_number_tin' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '47_servicing_providers_pin' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '48_servicing_providers_name_last_or_full' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '49_servicing_providers_street_address_1' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '50_servicing_providers_street_address_2' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '51_servicing_providers_city' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '52_servicing_providers_state' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '53_servicing_providers_zip_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '54_servicing_provider_type' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '55_servicing_providers_specialty_code_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '56_assignment_of_benefits_to_provider_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '57_participating_provider_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '58_date_claim_submission_received' as ColumnName, 'date' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '59_date_processed_non_hmo_only' as ColumnName, 'date' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '60_date_service_started' as ColumnName, 'date' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '61_date_service_stopped' as ColumnName, 'date' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '62_date_processed_all' as ColumnName, 'date' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '63_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '64_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '65_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '66_major_diagnostic_category_mdc_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '67_diagnosis_related_group_drg_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '68_line_level_procedure_code_cpt_hcpcs_ada_cdt_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '69_line_level_procedure_code_modifier_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '70_line_level_procedure_code_type_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '71_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '72_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '73_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '74_type_of_service_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '75_service_benefit_code_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '76_tooth_number' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '77_place_of_service' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '78_ub92_patient_discharge_status_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '79_ub92_revenue_center_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '80_ub92_bill_type_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '81_number_units_of_service' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '82_source_number_units_of_service' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '83_gross_submitted_expense__***' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '84_net_submitted_expense__***' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '85_not_covered_amount_1' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '86_not_covered_amount_2' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '87_not_covered_amount_3' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '88_action_or_reason_code_1' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '89_action_or_reason_code_2' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '90_action_or_reason_code_3' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '91_covered_expense' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '92_allowed_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '93_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '94_copayment_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '95_source_copayment_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '96_deductible_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '97_coinsurance' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '98_source_coinsurance_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '99_benefit_payable' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '100_paid_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '101_cob_paid_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '102_aetna_health_fund_before_fund_deductible' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '103_aetna_health_fund_payable_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '104_savings_negotiated_fee__***' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '105_savings_r&c' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '106_savings_cob' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '107_savings_source_cob' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '108_medicare_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '109_type_of_expense_cob' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '110_cob_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '111_national_drug_code_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '112_members_cumbid' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '113_status_of_claim' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '114_non_ssn_employees_id' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '115_reversal_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '116_admit_counter' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '117_administrative_savings_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '118_aexcel_provider_designation_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '119_aexcel_plan_design_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '120_aexcel_benefit_tier_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '121_aexcel_designated_provider_specialty' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '122_product_distinction_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '123_billed_eligible_amount_do_not_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '124_servicing_provider_class_code_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '125_present_on_admission_code_1_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '126_present_on_admission_code_2_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '127_present_on_admission_code_3_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '128_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '129_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '130_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '131_pricing_method_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '132_servicing_provider_type_class_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '133_servicing_provider_specialty_category_code_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '134_servicing_provider_npi' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '135_total_deductible_met_indicator' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '136_total_interest_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '137_total_surcharge_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '138_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '139_hcfa_place_of_service_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '140_hcfa_admit_source_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '141_hcfa_admit_type_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '142_admission_date' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '143_discharge_date' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '144_line_level_procedure_code_modifier_2' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '145_line_level_procedure_code_modifier_3' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '146_present_on_admission_code_4_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '147_present_on_admission_code_5_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '148_present_on_admission_code_6_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '149_present_on_admission_code_7_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '150_present_on_admission_code_8_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '151_present_on_admission_code_9_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '152_present_on_admission_code_10_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '153_diagnosis_code_1_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '154_diagnosis_code_2_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '155_diagnosis_code_3_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '156_diagnosis_code_4_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '157_diagnosis_code_5_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '158_diagnosis_code_6_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '159_diagnosis_code_7_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '160_diagnosis_code_8_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '161_diagnosis_code_9_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '162_diagnosis_code_10_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '163_icd_procedure_code_1_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '164_icd_procedure_code_2_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '165_icd_procedure_code_3_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '166_icd_procedure_code_4_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '167_icd_procedure_code_5_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '168_icd_procedure_code_6_*' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '169_aetna_health_fund_determination_order_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '170_aetna_health_fund_member_share_of_coinsurance_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '171_aetna_health_fund_member_copay_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '172_aetna_health_fund_member_deductible_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '173_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '174_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '175_icd_10_indicator' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '176_exchange_id' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '177_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '178_end_of_record_marker' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '1_hierarchy_level_1_most_summarized' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '2_hierarchy_level_2' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '3_hierarchy_level_3' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '4_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '5_hierarchy_level_5' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '6_hierarchy_level_6_most_granular' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '7_source_system_platform' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '8_adjustment_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '9_preferred_vs_non_preferred_benefit_level' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '10_general_category_of_health_plan' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '11_line_of_business' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '12_classification_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '13_benefit_identification_code_bic' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '14_plan_code_or_extension_of_hierarchy' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '15_benefit_tier' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '16_funding_arrangement' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '17_employees_ssn' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '18_employees_last_name' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '19_employees_first_name_or_initial' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '20_employees_gender' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '21_employees_date_of_birth' as ColumnName, 'date' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '22_employees_zip_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '23_employees_state' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '24_coverage_enrollment_tier' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '25_members_ssn' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '26_members_id_assigned_in_data_warehouse' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '27_members_number' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '28_members_last_name' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '29_members_first_name' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '30_members_gender' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '31_members_relationship_to_employee' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '32_members_date_of_birth' as ColumnName, 'date' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '33_source_specific_transaction_id_number' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '34_acas_generation_segment_number' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '35_acas_pointer_back_to_previous_gen_seg' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '36_traditional_claim_id' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '37_expense_pay_line_number' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '38_claim_line_id_assigned_in_data_warehouse' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '39_employees_network_id' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '40_servicing_providers_network_id' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '41_referral_type' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '42_pcps_irs_tax_identification_number_tin_format_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '43_pcps_irs_tax_identification_number_tin' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '44_pcps_name_last_or_full' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '45_servicing_providers_tax_id_number_tin_format_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '46_servicing_providers_tax_id_number_tin' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '47_servicing_providers_pin' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '48_servicing_providers_name_last_or_full' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '49_servicing_providers_street_address_1' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '50_servicing_providers_street_address_2' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '51_servicing_providers_city' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '52_servicing_providers_state' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '53_servicing_providers_zip_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '54_servicing_provider_type' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '55_servicing_providers_specialty_code__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '56_assignment_of_benefits_to_provider_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '57_participating_provider_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '58_date_claim_submission_received' as ColumnName, 'date' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '59_date_processed_non_hmo_only' as ColumnName, 'date' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '60_date_service_started' as ColumnName, 'date' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '61_date_service_stopped' as ColumnName, 'date' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '62_date_processed_all' as ColumnName, 'date' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '63_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '64_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '65_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '66_major_diagnostic_category_mdc__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '67_diagnosis_related_group_drg__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '68_line_level_procedure_code_cpt_hcpcs_ada_cdt__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '69_line_level_procedure_code_modifier__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '70_line_level_procedure_code_type__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '71_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '72_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '73_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '74_type_of_service__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '75_service_benefit_code__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '76_tooth_number' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '77_place_of_service' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '78_ub92_patient_discharge_status__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '79_ub92_revenue_center__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '80_ub92_bill_type__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '81_number_units_of_service' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '82_source_number_units_of_service' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '83_gross_submitted_expense_____' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '84_net_submitted_expense_____' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '85_not_covered_amount_1' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '86_not_covered_amount_2' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '87_not_covered_amount_3' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '88_action_or_reason_code_1' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '89_action_or_reason_code_2' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '90_action_or_reason_code_3' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '91_covered_expense' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '92_allowed_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '93_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '94_copayment_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '95_source_copayment_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '96_deductible_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '97_coinsurance' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '98_source_coinsurance_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '99_benefit_payable' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '100_paid_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '101_cob_paid_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '102_aetna_health_fund_before_fund_deductible' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '103_aetna_health_fund_payable_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '104_savings_negotiated_fee_____' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '105_savings_rc' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '106_savings_cob' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '107_savings_source_cob' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '108_medicare_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '109_type_of_expense_cob' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '110_cob_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '111_national_drug_code__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '112_members_cumbid' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '113_status_of_claim' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '114_non_ssn_employees_id' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '115_reversal_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '116_admit_counter' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '117_administrative_savings_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '118_aexcel_provider_designation_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '119_aexcel_plan_design_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '120_aexcel_benefit_tier_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '121_aexcel_designated_provider_specialty' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '122_product_distinction_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '123_billed_eligible_amount_do_not_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '124_servicing_provider_class_code__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '125_present_on_admission_code_1__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '126_present_on_admission_code_2__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '127_present_on_admission_code_3__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '128_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '129_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '130_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '131_pricing_method_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '132_servicing_provider_type_class_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '133_servicing_provider_specialty_category_code__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '134_servicing_provider_npi' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '135_total_deductible_met_indicator' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '136_total_interest_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '137_total_surcharge_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '138_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '139_hcfa_place_of_service_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '140_hcfa_admit_source_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '141_hcfa_admit_type_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '142_admission_date' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '143_discharge_date' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '144_line_level_procedure_code_modifier_2' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '145_line_level_procedure_code_modifier_3' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '146_present_on_admission_code_4__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '147_present_on_admission_code_5__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '148_present_on_admission_code_6__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '149_present_on_admission_code_7__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '150_present_on_admission_code_8__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '151_present_on_admission_code_9__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '152_present_on_admission_code_10__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '153_diagnosis_code_1__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '154_diagnosis_code_2__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '155_diagnosis_code_3__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '156_diagnosis_code_4__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '157_diagnosis_code_5__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '158_diagnosis_code_6__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '159_diagnosis_code_7__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '160_diagnosis_code_8__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '161_diagnosis_code_9__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '162_diagnosis_code_10__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '163_icd_procedure_code_1__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '164_icd_procedure_code_2__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '165_icd_procedure_code_3__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '166_icd_procedure_code_4__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '167_icd_procedure_code_5__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '168_icd_procedure_code_6__' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '169_aetna_health_fund_determination_order_code' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '170_aetna_health_fund_member_share_of_coinsurance_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '171_aetna_health_fund_member_copay_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '172_aetna_health_fund_member_deductible_amount' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '173_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '174_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '175_icd_10_indicator' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '176_exchange_id' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '177_filler_space_reserved_for_future_use' as ColumnName, 'string' as DataType
                    ) AS S
		        ON (lower(C.ColumnName) = lower(S.ColumnName) AND lower(coalesce(C.DataType,'')) = lower(coalesce(S.DataType,'')))
            WHEN NOT MATCHED THEN
                INSERT (ColumnName, DataType)
                VALUES (S.ColumnName, S.DataType);

MERGE CDAP.ColumnDetail AS C
        	USING (Select '178_end_of_record_marker' as ColumnName, 'string' as DataType
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
        	USING (select TOP 1 pz.ZoneId, 'libertycocacola_aetna_layout' as TableName from CDAP.ProcessingZone pz
                    where pz.name = 'raw') AS S
		        ON (C.ZoneId = S.ZoneId AND C.TableName = S.TableName)
            WHEN NOT MATCHED THEN
                INSERT (ZoneId, TableName)
                VALUES (S.ZoneId, S.TableName);

MERGE CDAP.ZoneTable AS C
        	USING (select TOP 1 pz.ZoneId, 'plansponsorclaims_medical_libertycocacola_aetna' as TableName from CDAP.ProcessingZone pz
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '1_hierarchy_level_1_most_summarized'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '2_hierarchy_level_2'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '3_hierarchy_level_3'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 4 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '4_filler_space_reserved_for_future_use'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 5 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '5_hierarchy_level_5'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 6 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '6_hierarchy_level_6_most_granular'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 7 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '7_source_system_platform'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '8_adjustment_code'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 9 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '9_preferred_vs_non_preferred_benefit_level'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '10_general_category_of_health_plan'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '11_line_of_business'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '12_classification_code'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '13_benefit_identification_code_bic'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '14_plan_code_or_extension_of_hierarchy'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 15 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '15_benefit_tier'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 16 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '16_funding_arrangement'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 17 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '17_employees_ssn'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 18 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '18_employees_last_name'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 19 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '19_employees_first_name_or_initial'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '20_employees_gender'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 21 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '21_employees_date_of_birth'
                        and cd.DataType = 'date') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 22 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '22_employees_zip_code'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 23 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '23_employees_state'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '24_coverage_enrollment_tier'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '25_members_ssn'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '26_members_id_assigned_in_data_warehouse'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '27_members_number'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 28 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '28_members_last_name'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '29_members_first_name'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 30 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '30_members_gender'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 31 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '31_members_relationship_to_employee'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 32 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '32_members_date_of_birth'
                        and cd.DataType = 'date') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 33 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '33_source_specific_transaction_id_number'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '34_acas_generation_segment_number'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '35_acas_pointer_back_to_previous_gen_seg'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '36_traditional_claim_id'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '37_expense_pay_line_number'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '38_claim_line_id_assigned_in_data_warehouse'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '39_employees_network_id'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 40 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '40_servicing_providers_network_id'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '41_referral_type'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '42_pcps_irs_tax_identification_number_tin_format_code'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '43_pcps_irs_tax_identification_number_tin'
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
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '44_pcps_name_last_or_full'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 45 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '45_servicing_providers_tax_id_number_tin_format_code'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 46 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '46_servicing_providers_tax_id_number_tin'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 47 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '47_servicing_providers_pin'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 48 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '48_servicing_providers_name_last_or_full'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 49 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '49_servicing_providers_street_address_1'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 50 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '50_servicing_providers_street_address_2'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 51 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '51_servicing_providers_city'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 52 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '52_servicing_providers_state'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 53 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '53_servicing_providers_zip_code'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 54 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '54_servicing_provider_type'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 55 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '55_servicing_providers_specialty_code_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 56 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '56_assignment_of_benefits_to_provider_code'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 57 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '57_participating_provider_code'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 58 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '58_date_claim_submission_received'
                        and cd.DataType = 'date') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 59 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '59_date_processed_non_hmo_only'
                        and cd.DataType = 'date') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 60 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '60_date_service_started'
                        and cd.DataType = 'date') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 61 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '61_date_service_stopped'
                        and cd.DataType = 'date') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 62 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '62_date_processed_all'
                        and cd.DataType = 'date') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 63 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '63_filler_space_reserved_for_future_use'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 64 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '64_filler_space_reserved_for_future_use'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 65 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '65_filler_space_reserved_for_future_use'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 66 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '66_major_diagnostic_category_mdc_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 67 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '67_diagnosis_related_group_drg_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 68 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '68_line_level_procedure_code_cpt_hcpcs_ada_cdt_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 69 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '69_line_level_procedure_code_modifier_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 70 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '70_line_level_procedure_code_type_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 71 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '71_filler_space_reserved_for_future_use'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 72 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '72_filler_space_reserved_for_future_use'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 73 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '73_filler_space_reserved_for_future_use'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 74 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '74_type_of_service_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 75 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '75_service_benefit_code_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 76 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '76_tooth_number'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 77 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '77_place_of_service'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 78 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '78_ub92_patient_discharge_status_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 79 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '79_ub92_revenue_center_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 80 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '80_ub92_bill_type_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 81 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '81_number_units_of_service'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 82 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '82_source_number_units_of_service'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 83 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '83_gross_submitted_expense__***'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 84 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '84_net_submitted_expense__***'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 85 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '85_not_covered_amount_1'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 86 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '86_not_covered_amount_2'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 87 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '87_not_covered_amount_3'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 88 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '88_action_or_reason_code_1'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 89 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '89_action_or_reason_code_2'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 90 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '90_action_or_reason_code_3'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 91 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '91_covered_expense'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 92 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '92_allowed_amount'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 93 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '93_filler_space_reserved_for_future_use'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 94 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '94_copayment_amount'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 95 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '95_source_copayment_amount'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 96 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '96_deductible_amount'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 97 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '97_coinsurance'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 98 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '98_source_coinsurance_amount'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 99 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '99_benefit_payable'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 100 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '100_paid_amount'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 101 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '101_cob_paid_amount'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 102 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '102_aetna_health_fund_before_fund_deductible'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 103 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '103_aetna_health_fund_payable_amount'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 104 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '104_savings_negotiated_fee__***'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 105 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '105_savings_r&c'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 106 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '106_savings_cob'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 107 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '107_savings_source_cob'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 108 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '108_medicare_code'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 109 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '109_type_of_expense_cob'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 110 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '110_cob_code'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 111 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '111_national_drug_code_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 112 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '112_members_cumbid'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 113 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '113_status_of_claim'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 114 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '114_non_ssn_employees_id'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 115 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '115_reversal_code'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 116 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '116_admit_counter'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 117 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '117_administrative_savings_amount'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 118 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '118_aexcel_provider_designation_code'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 119 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '119_aexcel_plan_design_code'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 120 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '120_aexcel_benefit_tier_code'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 121 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '121_aexcel_designated_provider_specialty'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 122 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '122_product_distinction_code'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 123 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '123_billed_eligible_amount_do_not_use'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 124 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '124_servicing_provider_class_code_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 125 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '125_present_on_admission_code_1_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 126 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '126_present_on_admission_code_2_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 127 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '127_present_on_admission_code_3_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 128 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '128_filler_space_reserved_for_future_use'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 129 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '129_filler_space_reserved_for_future_use'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 130 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '130_filler_space_reserved_for_future_use'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 131 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '131_pricing_method_code'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 132 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '132_servicing_provider_type_class_code'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 133 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '133_servicing_provider_specialty_category_code_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 134 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '134_servicing_provider_npi'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 135 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '135_total_deductible_met_indicator'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 136 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '136_total_interest_amount'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 137 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '137_total_surcharge_amount'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 138 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '138_filler_space_reserved_for_future_use'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 139 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '139_hcfa_place_of_service_code'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 140 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '140_hcfa_admit_source_code'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 141 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '141_hcfa_admit_type_code'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 142 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '142_admission_date'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 143 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '143_discharge_date'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 144 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '144_line_level_procedure_code_modifier_2'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 145 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '145_line_level_procedure_code_modifier_3'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 146 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '146_present_on_admission_code_4_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 147 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '147_present_on_admission_code_5_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 148 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '148_present_on_admission_code_6_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 149 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '149_present_on_admission_code_7_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 150 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '150_present_on_admission_code_8_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 151 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '151_present_on_admission_code_9_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 152 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '152_present_on_admission_code_10_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 153 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '153_diagnosis_code_1_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 154 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '154_diagnosis_code_2_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 155 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '155_diagnosis_code_3_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 156 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '156_diagnosis_code_4_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 157 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '157_diagnosis_code_5_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 158 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '158_diagnosis_code_6_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 159 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '159_diagnosis_code_7_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 160 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '160_diagnosis_code_8_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 161 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '161_diagnosis_code_9_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 162 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '162_diagnosis_code_10_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 163 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '163_icd_procedure_code_1_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 164 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '164_icd_procedure_code_2_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 165 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '165_icd_procedure_code_3_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 166 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '166_icd_procedure_code_4_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 167 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '167_icd_procedure_code_5_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 168 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '168_icd_procedure_code_6_*'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 169 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '169_aetna_health_fund_determination_order_code'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 170 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '170_aetna_health_fund_member_share_of_coinsurance_amount'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 171 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '171_aetna_health_fund_member_copay_amount'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 172 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '172_aetna_health_fund_member_deductible_amount'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 173 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '173_filler_space_reserved_for_future_use'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 174 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '174_filler_space_reserved_for_future_use'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 175 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '175_icd_10_indicator'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 176 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '176_exchange_id'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 177 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '177_filler_space_reserved_for_future_use'
                        and cd.DataType = 'string') AS S
                    ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
                WHEN NOT MATCHED THEN
                    INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                    VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
                USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 178 as ColumnOrder 
                        from CDAP.ZoneTable zt
                        join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                        join CDAP.ColumnDetail cd on (1=1)
                        where pz.name = 'raw'
                        and zt.TableName = 'libertycocacola_aetna_layout'
                        and cd.ColumnName = '178_end_of_record_marker'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '1_hierarchy_level_1_most_summarized'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '2_hierarchy_level_2'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '3_hierarchy_level_3'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 4 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '4_filler_space_reserved_for_future_use'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 5 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '5_hierarchy_level_5'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 6 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '6_hierarchy_level_6_most_granular'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 7 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '7_source_system_platform'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '8_adjustment_code'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 9 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '9_preferred_vs_non_preferred_benefit_level'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '10_general_category_of_health_plan'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '11_line_of_business'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '12_classification_code'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '13_benefit_identification_code_bic'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '14_plan_code_or_extension_of_hierarchy'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 15 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '15_benefit_tier'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 16 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '16_funding_arrangement'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 17 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '17_employees_ssn'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 18 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '18_employees_last_name'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 19 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '19_employees_first_name_or_initial'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '20_employees_gender'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 21 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '21_employees_date_of_birth'
                    and cd.DataType = 'date') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 22 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '22_employees_zip_code'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 23 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '23_employees_state'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '24_coverage_enrollment_tier'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '25_members_ssn'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '26_members_id_assigned_in_data_warehouse'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '27_members_number'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 28 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '28_members_last_name'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '29_members_first_name'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 30 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '30_members_gender'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 31 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '31_members_relationship_to_employee'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 32 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '32_members_date_of_birth'
                    and cd.DataType = 'date') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 33 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '33_source_specific_transaction_id_number'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '34_acas_generation_segment_number'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '35_acas_pointer_back_to_previous_gen_seg'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '36_traditional_claim_id'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '37_expense_pay_line_number'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '38_claim_line_id_assigned_in_data_warehouse'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '39_employees_network_id'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 40 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '40_servicing_providers_network_id'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '41_referral_type'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '42_pcps_irs_tax_identification_number_tin_format_code'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '43_pcps_irs_tax_identification_number_tin'
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
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '44_pcps_name_last_or_full'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 45 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '45_servicing_providers_tax_id_number_tin_format_code'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 46 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '46_servicing_providers_tax_id_number_tin'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 47 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '47_servicing_providers_pin'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 48 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '48_servicing_providers_name_last_or_full'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 49 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '49_servicing_providers_street_address_1'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 50 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '50_servicing_providers_street_address_2'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 51 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '51_servicing_providers_city'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 52 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '52_servicing_providers_state'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 53 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '53_servicing_providers_zip_code'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 54 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '54_servicing_provider_type'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 55 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '55_servicing_providers_specialty_code__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 56 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '56_assignment_of_benefits_to_provider_code'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 57 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '57_participating_provider_code'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 58 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '58_date_claim_submission_received'
                    and cd.DataType = 'date') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 59 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '59_date_processed_non_hmo_only'
                    and cd.DataType = 'date') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 60 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '60_date_service_started'
                    and cd.DataType = 'date') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 61 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '61_date_service_stopped'
                    and cd.DataType = 'date') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 62 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '62_date_processed_all'
                    and cd.DataType = 'date') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 63 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '63_filler_space_reserved_for_future_use'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 64 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '64_filler_space_reserved_for_future_use'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 65 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '65_filler_space_reserved_for_future_use'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 66 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '66_major_diagnostic_category_mdc__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 67 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '67_diagnosis_related_group_drg__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 68 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '68_line_level_procedure_code_cpt_hcpcs_ada_cdt__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 69 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '69_line_level_procedure_code_modifier__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 70 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '70_line_level_procedure_code_type__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 71 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '71_filler_space_reserved_for_future_use'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 72 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '72_filler_space_reserved_for_future_use'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 73 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '73_filler_space_reserved_for_future_use'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 74 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '74_type_of_service__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 75 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '75_service_benefit_code__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 76 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '76_tooth_number'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 77 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '77_place_of_service'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 78 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '78_ub92_patient_discharge_status__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 79 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '79_ub92_revenue_center__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 80 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '80_ub92_bill_type__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 81 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '81_number_units_of_service'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 82 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '82_source_number_units_of_service'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 83 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '83_gross_submitted_expense_____'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 84 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '84_net_submitted_expense_____'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 85 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '85_not_covered_amount_1'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 86 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '86_not_covered_amount_2'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 87 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '87_not_covered_amount_3'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 88 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '88_action_or_reason_code_1'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 89 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '89_action_or_reason_code_2'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 90 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '90_action_or_reason_code_3'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 91 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '91_covered_expense'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 92 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '92_allowed_amount'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 93 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '93_filler_space_reserved_for_future_use'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 94 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '94_copayment_amount'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 95 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '95_source_copayment_amount'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 96 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '96_deductible_amount'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 97 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '97_coinsurance'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 98 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '98_source_coinsurance_amount'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 99 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '99_benefit_payable'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 100 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '100_paid_amount'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 101 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '101_cob_paid_amount'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 102 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '102_aetna_health_fund_before_fund_deductible'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 103 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '103_aetna_health_fund_payable_amount'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 104 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '104_savings_negotiated_fee_____'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 105 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '105_savings_rc'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 106 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '106_savings_cob'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 107 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '107_savings_source_cob'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 108 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '108_medicare_code'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 109 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '109_type_of_expense_cob'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 110 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '110_cob_code'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 111 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '111_national_drug_code__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 112 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '112_members_cumbid'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 113 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '113_status_of_claim'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 114 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '114_non_ssn_employees_id'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 115 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '115_reversal_code'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 116 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '116_admit_counter'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 117 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '117_administrative_savings_amount'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 118 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '118_aexcel_provider_designation_code'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 119 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '119_aexcel_plan_design_code'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 120 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '120_aexcel_benefit_tier_code'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 121 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '121_aexcel_designated_provider_specialty'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 122 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '122_product_distinction_code'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 123 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '123_billed_eligible_amount_do_not_use'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 124 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '124_servicing_provider_class_code__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 125 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '125_present_on_admission_code_1__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 126 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '126_present_on_admission_code_2__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 127 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '127_present_on_admission_code_3__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 128 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '128_filler_space_reserved_for_future_use'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 129 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '129_filler_space_reserved_for_future_use'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 130 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '130_filler_space_reserved_for_future_use'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 131 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '131_pricing_method_code'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 132 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '132_servicing_provider_type_class_code'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 133 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '133_servicing_provider_specialty_category_code__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 134 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '134_servicing_provider_npi'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 135 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '135_total_deductible_met_indicator'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 136 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '136_total_interest_amount'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 137 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '137_total_surcharge_amount'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 138 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '138_filler_space_reserved_for_future_use'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 139 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '139_hcfa_place_of_service_code'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 140 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '140_hcfa_admit_source_code'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 141 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '141_hcfa_admit_type_code'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 142 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '142_admission_date'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 143 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '143_discharge_date'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 144 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '144_line_level_procedure_code_modifier_2'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 145 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '145_line_level_procedure_code_modifier_3'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 146 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '146_present_on_admission_code_4__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 147 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '147_present_on_admission_code_5__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 148 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '148_present_on_admission_code_6__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 149 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '149_present_on_admission_code_7__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 150 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '150_present_on_admission_code_8__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 151 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '151_present_on_admission_code_9__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 152 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '152_present_on_admission_code_10__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 153 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '153_diagnosis_code_1__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 154 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '154_diagnosis_code_2__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 155 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '155_diagnosis_code_3__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 156 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '156_diagnosis_code_4__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 157 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '157_diagnosis_code_5__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 158 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '158_diagnosis_code_6__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 159 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '159_diagnosis_code_7__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 160 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '160_diagnosis_code_8__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 161 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '161_diagnosis_code_9__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 162 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '162_diagnosis_code_10__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 163 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '163_icd_procedure_code_1__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 164 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '164_icd_procedure_code_2__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 165 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '165_icd_procedure_code_3__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 166 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '166_icd_procedure_code_4__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 167 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '167_icd_procedure_code_5__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 168 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '168_icd_procedure_code_6__'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 169 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '169_aetna_health_fund_determination_order_code'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 170 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '170_aetna_health_fund_member_share_of_coinsurance_amount'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 171 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '171_aetna_health_fund_member_copay_amount'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 172 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '172_aetna_health_fund_member_deductible_amount'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 173 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '173_filler_space_reserved_for_future_use'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 174 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '174_filler_space_reserved_for_future_use'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 175 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '175_icd_10_indicator'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 176 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '176_exchange_id'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 177 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '177_filler_space_reserved_for_future_use'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 178 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = '178_end_of_record_marker'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 179 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = 'file_date'
                    and cd.DataType = 'string') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 180 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = 'created_timestamp'
                    and cd.DataType = 'timestamp') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 0 as IsNullable, 181 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
                    and cd.ColumnName = 'modified_timestamp'
                    and cd.DataType = 'timestamp') AS S
		        ON (C.TableId = S.TableId AND C.ColumnDetailId = S.ColumnDetailId)
            WHEN NOT MATCHED THEN
                INSERT (TableId, ColumnDetailId, IsNullable, ColumnOrder)
                VALUES (S.TableId, S.ColumnDetailId, S.IsNullable, S.ColumnOrder);

MERGE CDAP.TableColumn AS C
        	USING (select zt.TableId, cd.ColumnDetailId, 1 as IsNullable, 182 as ColumnOrder 
                    from CDAP.ZoneTable zt
                    join CDAP.ProcessingZone pz on (pz.zoneid = zt.zoneid)
                    join CDAP.ColumnDetail cd on (1=1)
                    where pz.name = 'prep'
                    and zt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna'
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'libertycocacola_aetna_layout' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid)
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName=REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(LTRIM(RTRIM(REPLACE(REPLACE(fcd.ColumnName, CHAR(160), ' '), CHAR(9), ' ')   )),  '   ', ' '),'  ', ' '), ' ', '_'),'.',''),':',''),',',''),CHAR(10),''),'(',''),')',''),'/',''),'&',''),'#',''),'*','_'))
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='file_date')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='file_effective_date')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='33_source_specific_transaction_id_number')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='claim_id')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='claim_type')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='claim_tob')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='plan_name')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insurance_plan_name')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='static_plan_sponsor_name')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='plan_sponsor_name')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='112_members_cumbid')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_id')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_group_number')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='19_employees_first_name_or_initial')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_first_name')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='18_employees_last_name')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_last_name')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_middle_initial')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='17_employees_ssn')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_ssn')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='21_employees_date_of_birth')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_dob')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='20_employees_gender')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_sex')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_address')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_address2')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_city')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='23_employees_state')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_state')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='22_employees_zip_code')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_zip')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_phone')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='insured_email')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='29_members_first_name')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_first_name')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='28_members_last_name')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_last_name')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_middle_initial')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_ssn')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='32_members_date_of_birth')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_dob')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='30_members_gender')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_sex')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_address')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_address2')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_city')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_state')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_zip')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_phone')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_email')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        'source_value,replace_value
E,1
S,2
C,3' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='31_members_relationship_to_employee')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_relationship_code')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);

MERGE CDAP.ColumnMapping AS C
        	    USING (select ic.ingestionconfigid, ftc.tablecolumnid as sourcetablecolumnid, ttc.tablecolumnid as targettablecolumnid, 
                        'source_value,replace_value
E,Self
S,Spouse
C,Child' SVMRule
                    from cdap.IngestionConfig ic
                    join CDAP.DomainClient dc on (dc.domainclientid = ic.domainclientid)
                    join CDAP.ClientSponsor cs on (cs.clientsponsorid = ic.clientsponsorid)
                    join CDAP.DomainSponsor ds on (ds.domainsponsorid = ic.domainsponsorid)
                    join CDAP.Domain d on (d.domainid = dc.domainid)
                    join CDAP.Client c on (c.clientkey = dc.clientkey)
                    join CDAP.PlanSponsor ps on (ps.plansponsorid = cs.plansponsorid)
					join CDAP.ProcessingZone fpz on (fpz.name = 'prep')
					join CDAP.ProcessingZone tpz on (tpz.name = 'structured')
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='31_members_relationship_to_employee')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='patient_relationship_desc')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='icd_version')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='153_diagnosis_code_1__')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_1')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='154_diagnosis_code_2__')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_2')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='155_diagnosis_code_3__')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_3')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='156_diagnosis_code_4__')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_4')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='157_diagnosis_code_5__')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_5')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='158_diagnosis_code_6__')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_6')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='159_diagnosis_code_7__')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_7')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='160_diagnosis_code_8__')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_8')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='161_diagnosis_code_9__')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_9')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='162_diagnosis_code_10__')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_10')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_11')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='dx_code_12')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='drg_code')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='60_date_service_started')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='begin_date')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='61_date_service_stopped')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='end_date')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='pos_code')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='68_line_level_procedure_code_cpt_hcpcs_ada_cdt__')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='procedure_code')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='revenue_code')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='revenue_code_description')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='ndc')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='mod_1')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='48_servicing_providers_name_last_or_full')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='rendering_provider_name')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='134_servicing_provider_npi')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='rendering_provider_npi')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='facility_name')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='facility_npi')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='facility_zip')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='claim_line')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='member_sequence_number')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='client_name')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='client_name')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='created_timestamp')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='created_timestamp')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
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
					join CDAP.ZoneTable fzt on (fzt.TableName = 'plansponsorclaims_medical_libertycocacola_aetna' and fpz.zoneid=fzt.zoneid) 
					join CDAP.ZoneTable tzt on (tzt.TableName = 'plansponsorclaims_medical_standard' and tpz.zoneid = tzt.zoneid)
					join.CDAP.TableColumn ftc on (ftc.Tableid = fzt.Tableid)
					join CDAP.TableColumn ttc on (ttc.Tableid = tzt.Tableid)
					join CDAP.ColumnDetail fcd on (fcd.ColumnDetailid = ftc.ColumnDetailid and fcd.ColumnName='modified_timestamp')
					join CDAP.ColumnDetail tcd on (tcd.ColumnDetailid = ttc.ColumnDetailid and tcd.ColumnName='modified_timestamp')
                    where c.DAPClientName = 'LibertyCocaCola_Aetna' and d.DomainName='PlanSponsorClaims'
                    and ps.PlanSponsorName = 'Aetna') AS S
		        ON (C.IngestionConfigId = S.IngestionConfigId AND C.SourceTableColumnId = S.SourceTableColumnId AND C.TargetTableColumnId = S.TargetTableColumnId)
                WHEN NOT MATCHED THEN
                    INSERT (IngestionConfigId, SourceTableColumnId, TargetTableColumnId, SVMRule)
                    VALUES (S.IngestionConfigId, S.SourceTableColumnId, S.TargetTableColumnId, S.SVMRule);