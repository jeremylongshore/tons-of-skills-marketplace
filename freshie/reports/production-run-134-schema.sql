-- Stock SQLite runtime schema used for the run-134 restore proof.
-- Public table/column definitions only; no row data.

CREATE TABLE agent_compliance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_path TEXT,
        total_fields INTEGER,
        anthropic_fields INTEGER,
        missing_fields TEXT,
        has_invalid_fields INTEGER,
        invalid_fields TEXT,
        is_plugin_agent INTEGER,
        error_count INTEGER,
        warning_count INTEGER,
        validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        validator_version TEXT,
        run_id INTEGER,
        UNIQUE(agent_path, run_id)
    );

CREATE TABLE agent_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT, plugin_path TEXT, pack_name TEXT, plugin_name TEXT,
    filename TEXT, fm_name TEXT, fm_description TEXT,
    fm_capabilities TEXT, fm_expertise_level TEXT, fm_activation_priority TEXT,
    fm_effort TEXT, fm_max_turns INTEGER, fm_disallowed_tools TEXT,
    fm_all_keys TEXT, line_count INTEGER, word_count INTEGER
, run_id INTEGER, fm_tools TEXT, fm_skills TEXT, fm_memory TEXT, fm_background INTEGER, fm_isolation TEXT, fm_permission_mode TEXT);

CREATE TABLE anomalies (
    id INTEGER PRIMARY KEY AUTOINCREMENT, anomaly_type TEXT,
    path TEXT, count INTEGER, evidence TEXT, notes TEXT
, run_id INTEGER);

CREATE TABLE ci_workflows (
    id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, name TEXT,
    triggers TEXT, jobs_json TEXT, scripts_called TEXT, env_vars TEXT
, run_id INTEGER);

CREATE TABLE command_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT, plugin_path TEXT, pack_name TEXT, plugin_name TEXT,
    filename TEXT, fm_name TEXT, fm_description TEXT, fm_shortcut TEXT,
    fm_category TEXT, fm_difficulty TEXT, fm_all_keys TEXT,
    line_count INTEGER, word_count INTEGER
, run_id INTEGER);

CREATE TABLE content_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT, skill_path TEXT, pack_name TEXT,
    plugin_name TEXT, line_count INTEGER, word_count INTEGER,
    code_block_count INTEGER, comment_only_code_block_count INTEGER,
    import_code_block_count INTEGER, url_code_block_count INTEGER,
    real_url_count INTEGER, real_import_count INTEGER,
    placeholder_step INTEGER, placeholder_todo INTEGER,
    placeholder_implementation INTEGER, placeholder_add INTEGER,
    placeholder_your INTEGER, placeholder_api_key INTEGER,
    placeholder_token INTEGER, placeholder_api_example INTEGER,
    placeholder_example INTEGER, placeholder_table_error INTEGER
, run_id INTEGER);

CREATE TABLE cross_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT, source_path TEXT,
    target_path_or_entity TEXT, linkage_type TEXT,
    direct_or_inferred TEXT, confidence TEXT, evidence TEXT
, run_id INTEGER);

CREATE TABLE discovery_runs (
    id INTEGER PRIMARY KEY, run_date TEXT, commit_hash TEXT,
    total_packs INTEGER, total_plugins INTEGER, total_skills INTEGER,
    total_files INTEGER, total_root_files INTEGER
);

CREATE TABLE docs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, doc_type TEXT,
    apparent_subject TEXT, subject_type TEXT, line_count INTEGER,
    word_count INTEGER
, run_id INTEGER);

CREATE TABLE duplicate_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT, sha256 TEXT,
    file_count INTEGER, file_paths_json TEXT
, run_id INTEGER);

CREATE TABLE field_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT, field_name TEXT,
    source TEXT, data_type TEXT, found_in_count INTEGER,
    found_in_total INTEGER, value_patterns TEXT, example TEXT,
    validated_by TEXT, notes TEXT
, run_id INTEGER);

CREATE TABLE forge_proofs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plugin_name TEXT NOT NULL,
        jrig_run_id INTEGER,
        verification_type TEXT NOT NULL,
        passed INTEGER NOT NULL,
        evidence TEXT,
        layers_passed INTEGER DEFAULT NULL,
        total_layers INTEGER DEFAULT 7,
        baseline_delta REAL DEFAULT NULL,
        verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, discovery_run_id INTEGER REFERENCES discovery_runs(id), evidence_class TEXT NOT NULL DEFAULT 'E0' CHECK(evidence_class IN ('E0', 'E1', 'E2', 'E3')), artifact_sha256 TEXT, artifact_uri TEXT, spec_sha256 TEXT, tool_version TEXT, kernel_version TEXT, provider TEXT, model TEXT, recorded_by_identity TEXT, producing_identity TEXT,
        UNIQUE(plugin_name, verification_type, jrig_run_id)
    );

CREATE TABLE frontmatter_fields (
    id INTEGER PRIMARY KEY AUTOINCREMENT, field_name TEXT, data_types TEXT,
    count INTEGER, percentage REAL, unique_value_count INTEGER,
    value_pattern TEXT, sample_values_json TEXT, blank_count INTEGER
, run_id INTEGER);

CREATE TABLE frontmatter_shapes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, keys TEXT,
    count INTEGER, key_count INTEGER
, run_id INTEGER);

CREATE TABLE frontmatter_values (
    id INTEGER PRIMARY KEY AUTOINCREMENT, skill_path TEXT,
    field_name TEXT, raw_value TEXT
, run_id INTEGER);

CREATE TABLE marketplace_catalog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, source TEXT, description TEXT, version TEXT,
    category TEXT, keywords TEXT, author TEXT,
    components TEXT, verification TEXT,
    featured INTEGER, mcp_tools TEXT, plugin_count INTEGER,
    pricing TEXT, zcf_metadata TEXT, external_sync TEXT,
    all_keys TEXT, raw_json TEXT
, run_id INTEGER);

CREATE TABLE npm_discovery_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT,
    completed_at TEXT,
    source_repo_path TEXT,
    notes TEXT
);

CREATE TABLE npm_dist_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_name TEXT,
    tag_name TEXT,
    version TEXT,
    fetched_at TEXT
);

CREATE TABLE npm_download_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_name TEXT,
    period TEXT,
    downloads INTEGER,
    window_start TEXT,
    window_end TEXT,
    fetched_at TEXT
);

CREATE TABLE npm_fetch_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_name TEXT,
    fetch_kind TEXT,
    success_flag INTEGER,
    status_code INTEGER,
    fetched_at TEXT,
    notes TEXT
);

CREATE TABLE npm_package_dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_name TEXT,
    version TEXT,
    dependency_name TEXT,
    dependency_type TEXT,
    dependency_range TEXT,
    fetched_at TEXT
);

CREATE TABLE npm_packages (
    package_name TEXT PRIMARY KEY,
    scope_name TEXT,
    unscoped_name TEXT,
    latest_version TEXT,
    latest_tag TEXT,
    description TEXT,
    homepage TEXT,
    license TEXT,
    repository_url TEXT,
    bugs_url TEXT,
    author_summary TEXT,
    maintainers_summary TEXT,
    deprecated_flag INTEGER DEFAULT 0,
    deprecated_message TEXT,
    created_at TEXT,
    modified_at TEXT,
    fetched_at TEXT,
    fetch_status TEXT,
    fetch_error_summary TEXT
);

CREATE TABLE npm_publish_history_summary (
    package_name TEXT PRIMARY KEY,
    version_count INTEGER,
    first_published_at TEXT,
    latest_published_at TEXT,
    publish_cadence_summary TEXT,
    fetched_at TEXT
);

CREATE TABLE npm_version_comparisons (
    comparison_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file_path TEXT,
    source_entity_type TEXT,
    source_entity_name TEXT,
    package_name TEXT,
    declared_version_range TEXT,
    latest_version TEXT,
    latest_tag TEXT,
    exact_declared_version TEXT,
    appears_outdated_flag INTEGER DEFAULT 0,
    declared_matches_latest_flag INTEGER DEFAULT 0,
    notes TEXT,
    compared_at TEXT
);

CREATE TABLE npm_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_name TEXT,
    version TEXT,
    published_at TEXT,
    deprecated_flag INTEGER DEFAULT 0,
    dist_integrity TEXT,
    dist_shasum TEXT,
    tarball_url TEXT,
    unpacked_size INTEGER,
    fetched_at TEXT
);

CREATE TABLE pack_aggregates (
    id INTEGER PRIMARY KEY AUTOINCREMENT, pack_name TEXT,
    skill_count INTEGER, total_lines INTEGER, total_words INTEGER,
    total_code_blocks INTEGER, total_comment_only INTEGER,
    total_placeholders INTEGER, total_real_urls INTEGER,
    total_real_imports INTEGER
, run_id INTEGER);

CREATE TABLE pack_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT, pack_name TEXT,
    files_present TEXT, category_indicators TEXT
, run_id INTEGER);

CREATE TABLE packs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, path TEXT,
    plugin_count INTEGER, skill_count INTEGER, file_count INTEGER,
    has_readme INTEGER, has_changelog INTEGER, has_package_json INTEGER,
    category_indicator TEXT
, run_id INTEGER);

CREATE TABLE planned_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT, filename TEXT, extension TEXT,
    line_count INTEGER, word_count INTEGER, size_bytes INTEGER,
    apparent_skill_name TEXT
, run_id INTEGER);

CREATE TABLE plugin_companions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, plugin_path TEXT,
    plugin_json_path TEXT, pack_name TEXT,
    has_readme INTEGER, has_package_json INTEGER, has_mcp_json INTEGER,
    has_src_dir INTEGER, has_commands_dir INTEGER,
    has_agents_dir INTEGER, has_skills_dir INTEGER, file_count INTEGER
, run_id INTEGER, has_hooks_dir INTEGER, has_lsp_json INTEGER, has_settings_json INTEGER, has_license INTEGER, has_changelog INTEGER);

CREATE TABLE plugin_compliance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plugin_path TEXT,
        plugin_json_valid INTEGER,
        plugin_json_fields INTEGER,
        skill_count INTEGER,
        skill_avg_score REAL,
        agent_count INTEGER,
        has_hooks_json INTEGER,
        has_mcp_json INTEGER,
        has_license INTEGER,
        has_changelog INTEGER,
        overall_score REAL,
        error_count INTEGER,
        warning_count INTEGER,
        validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        validator_version TEXT,
        run_id INTEGER,
        UNIQUE(plugin_path, run_id)
    );

CREATE TABLE plugin_fields (
    id INTEGER PRIMARY KEY AUTOINCREMENT, field_name TEXT, data_types TEXT,
    count INTEGER, percentage REAL, unique_value_count INTEGER,
    sample_values_json TEXT, blank_count INTEGER
, run_id INTEGER);

CREATE TABLE plugin_shapes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, keys TEXT,
    count INTEGER, key_count INTEGER
, run_id INTEGER);

CREATE TABLE plugin_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT, filename TEXT, extension TEXT,
    line_count INTEGER, size_bytes INTEGER, template_type TEXT
, run_id INTEGER);

CREATE TABLE plugin_values (
    id INTEGER PRIMARY KEY AUTOINCREMENT, plugin_path TEXT,
    field_name TEXT, raw_value TEXT
, run_id INTEGER);

CREATE TABLE plugins (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, path TEXT,
    pack_name TEXT, has_readme INTEGER, has_package_json INTEGER,
    plugin_json_shape TEXT, file_count INTEGER
, run_id INTEGER);

CREATE TABLE repo_package_sources (
    source_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER,
    source_file_path TEXT,
    source_entity_type TEXT,
    source_entity_name TEXT,
    package_name TEXT,
    dependency_type TEXT,
    declared_version_range TEXT,
    raw_section_name TEXT,
    evidence TEXT
);

CREATE TABLE restructure_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT, observation_type TEXT,
    paths_json TEXT, evidence TEXT, category TEXT
, run_id INTEGER);

CREATE TABLE root_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, extension TEXT,
    line_count INTEGER, size_bytes INTEGER, inferred_purpose TEXT
, run_id INTEGER);

CREATE TABLE root_skills_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT, filename TEXT, extension TEXT,
    line_count INTEGER, word_count INTEGER, size_bytes INTEGER,
    parent_dir TEXT
, run_id INTEGER);

CREATE TABLE scripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, language TEXT,
    purpose TEXT, script_type TEXT, arguments TEXT, inputs TEXT,
    outputs TEXT, dependencies TEXT
, run_id INTEGER);

CREATE TABLE skill_compliance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_path TEXT,
        total_fields INTEGER,
        anthropic_fields INTEGER,
        enterprise_fields INTEGER,
        missing_fields TEXT,
        has_references_dir INTEGER,
        has_examples INTEGER,
        has_scripts_dir INTEGER,
        is_stub INTEGER,
        stub_reasons TEXT,
        score INTEGER,
        grade TEXT,
        error_count INTEGER,
        warning_count INTEGER,
        validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        source_modified_at TIMESTAMP,
        validator_version TEXT,
        run_id INTEGER,
        has_prd INTEGER DEFAULT 0,
        has_ard INTEGER DEFAULT 0,
        has_errors_md INTEGER DEFAULT 0,
        has_examples_md INTEGER DEFAULT 0,
        has_implementation_md INTEGER DEFAULT 0,
        reference_file_count INTEGER DEFAULT 0,
        has_config_dir INTEGER DEFAULT 0,
        gold_standard_pct INTEGER DEFAULT 0,
        jrig_passed INTEGER DEFAULT NULL,
        jrig_tier_blocked INTEGER DEFAULT NULL,
        jrig_baseline_delta REAL DEFAULT NULL,
        UNIQUE(skill_path, run_id)
    );

CREATE TABLE skill_database_vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_name TEXT, path TEXT, file_count INTEGER,
    total_size_bytes INTEGER, file_extensions TEXT,
    sample_fields TEXT
, run_id INTEGER);

CREATE TABLE skill_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, filename TEXT,
    extension TEXT, size_bytes INTEGER, parent_skill TEXT, relative_path TEXT
, run_id INTEGER);

CREATE TABLE skill_structure_shapes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, shape_description TEXT,
    skill_count INTEGER
, run_id INTEGER);

CREATE TABLE skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, path TEXT,
    pack_name TEXT, plugin_name TEXT, structure_shape TEXT,
    file_count INTEGER, has_references INTEGER, has_scripts INTEGER,
    has_assets INTEGER
, run_id INTEGER);

CREATE TABLE unique_extensions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, extension TEXT, count INTEGER
, run_id INTEGER);

CREATE TABLE unique_filenames (
    id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, count INTEGER
, run_id INTEGER);

CREATE TABLE unique_subdirs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, subdir_name TEXT, count INTEGER
, run_id INTEGER);

CREATE TABLE validator_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT, validator_path TEXT,
    field_checked TEXT, rule_description TEXT, scoring_behavior TEXT
, run_id INTEGER);

CREATE TABLE validators (
    id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, entity_type TEXT,
    checks_json TEXT, fields_read TEXT, scoring_behavior TEXT,
    cli_flags TEXT, output_format TEXT
, run_id INTEGER);

CREATE INDEX idx_agent_compliance_run_id ON agent_compliance(run_id);

CREATE INDEX idx_forge_proofs_passed ON forge_proofs(passed);

CREATE INDEX idx_forge_proofs_plugin ON forge_proofs(plugin_name);

CREATE INDEX idx_plugin_compliance_run_id ON plugin_compliance(run_id);

CREATE INDEX idx_skill_compliance_run_id ON skill_compliance(run_id);
