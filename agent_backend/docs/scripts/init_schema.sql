DO $$
BEGIN


-- DROP FUNCTION public.uuid_generate_v1();

CREATE OR REPLACE FUNCTION public.uuid_generate_v1()
 RETURNS uuid
 LANGUAGE c
 PARALLEL SAFE STRICT
AS '$libdir/uuid-ossp', $function$uuid_generate_v1$function$
;
--这个表用来标记单APP应用的权限
--This table is used to mark the permissions for a single APP.
CREATE TABLE user_permissions (
    id uuid DEFAULT uuid_generate_v4() NOT NULL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    app_id VARCHAR(255) NOT NULL,
    can_view BOOLEAN DEFAULT FALSE,
    can_edit BOOLEAN DEFAULT FALSE,
    operator VARCHAR(255),  -- 创建者
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, app_id)
);
-- 这个全局权限分组映射（系统管理员或超管）
-- This table is used for mapping global permission groups (system administrators or superusers).
CREATE TABLE global_user_permissions (
    id uuid DEFAULT uuid_generate_v4() NOT NULL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    can_view_all BOOLEAN DEFAULT FALSE,
    can_edit_all BOOLEAN DEFAULT FALSE,
    operator VARCHAR(255),  -- 创建者
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id)
);

-- Permissions

ALTER FUNCTION public.uuid_generate_v1() OWNER TO agent_platform_user;
GRANT ALL ON FUNCTION public.uuid_generate_v1() TO agent_platform_user;

-- DROP FUNCTION public.uuid_generate_v1mc();

CREATE OR REPLACE FUNCTION public.uuid_generate_v1mc()
 RETURNS uuid
 LANGUAGE c
 PARALLEL SAFE STRICT
AS '$libdir/uuid-ossp', $function$uuid_generate_v1mc$function$
;

-- Permissions

ALTER FUNCTION public.uuid_generate_v1mc() OWNER TO agent_platform_user;
GRANT ALL ON FUNCTION public.uuid_generate_v1mc() TO agent_platform_user;

-- DROP FUNCTION public.uuid_generate_v3(uuid, text);

CREATE OR REPLACE FUNCTION public.uuid_generate_v3(namespace uuid, name text)
 RETURNS uuid
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/uuid-ossp', $function$uuid_generate_v3$function$
;

-- Permissions

ALTER FUNCTION public.uuid_generate_v3(uuid, text) OWNER TO agent_platform_user;
GRANT ALL ON FUNCTION public.uuid_generate_v3(uuid, text) TO agent_platform_user;

-- DROP FUNCTION public.uuid_generate_v4();

CREATE OR REPLACE FUNCTION public.uuid_generate_v4()
 RETURNS uuid
 LANGUAGE c
 PARALLEL SAFE STRICT
AS '$libdir/uuid-ossp', $function$uuid_generate_v4$function$
;

-- Permissions

ALTER FUNCTION public.uuid_generate_v4() OWNER TO agent_platform_user;
GRANT ALL ON FUNCTION public.uuid_generate_v4() TO agent_platform_user;

-- DROP FUNCTION public.uuid_generate_v5(uuid, text);

CREATE OR REPLACE FUNCTION public.uuid_generate_v5(namespace uuid, name text)
 RETURNS uuid
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/uuid-ossp', $function$uuid_generate_v5$function$
;

-- Permissions

ALTER FUNCTION public.uuid_generate_v5(uuid, text) OWNER TO agent_platform_user;
GRANT ALL ON FUNCTION public.uuid_generate_v5(uuid, text) TO agent_platform_user;

-- DROP FUNCTION public.uuid_nil();

CREATE OR REPLACE FUNCTION public.uuid_nil()
 RETURNS uuid
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/uuid-ossp', $function$uuid_nil$function$
;

-- Permissions

ALTER FUNCTION public.uuid_nil() OWNER TO agent_platform_user;
GRANT ALL ON FUNCTION public.uuid_nil() TO agent_platform_user;

-- DROP FUNCTION public.uuid_ns_dns();

CREATE OR REPLACE FUNCTION public.uuid_ns_dns()
 RETURNS uuid
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/uuid-ossp', $function$uuid_ns_dns$function$
;

-- Permissions

ALTER FUNCTION public.uuid_ns_dns() OWNER TO agent_platform_user;
GRANT ALL ON FUNCTION public.uuid_ns_dns() TO agent_platform_user;

-- DROP FUNCTION public.uuid_ns_oid();

CREATE OR REPLACE FUNCTION public.uuid_ns_oid()
 RETURNS uuid
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/uuid-ossp', $function$uuid_ns_oid$function$
;

-- Permissions

ALTER FUNCTION public.uuid_ns_oid() OWNER TO agent_platform_user;
GRANT ALL ON FUNCTION public.uuid_ns_oid() TO agent_platform_user;

-- DROP FUNCTION public.uuid_ns_url();

CREATE OR REPLACE FUNCTION public.uuid_ns_url()
 RETURNS uuid
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/uuid-ossp', $function$uuid_ns_url$function$
;

-- Permissions

ALTER FUNCTION public.uuid_ns_url() OWNER TO agent_platform_user;
GRANT ALL ON FUNCTION public.uuid_ns_url() TO agent_platform_user;

-- DROP FUNCTION public.uuid_ns_x500();

CREATE OR REPLACE FUNCTION public.uuid_ns_x500()
 RETURNS uuid
 LANGUAGE c
 IMMUTABLE PARALLEL SAFE STRICT
AS '$libdir/uuid-ossp', $function$uuid_ns_x500$function$
;

-- Permissions

ALTER FUNCTION public.uuid_ns_x500() OWNER TO agent_platform_user;
GRANT ALL ON FUNCTION public.uuid_ns_x500() TO agent_platform_user;

-- DROP SEQUENCE public.invitation_codes_id_seq;

CREATE SEQUENCE public.invitation_codes_id_seq
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 2147483647
	START 1
	CACHE 1
	NO CYCLE;

-- Permissions

ALTER SEQUENCE public.invitation_codes_id_seq OWNER TO agent_platform_user;
GRANT ALL ON SEQUENCE public.invitation_codes_id_seq TO agent_platform_user;

-- DROP SEQUENCE public.task_id_sequence;

CREATE SEQUENCE public.task_id_sequence
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;

-- Permissions

ALTER SEQUENCE public.task_id_sequence OWNER TO agent_platform_user;
GRANT ALL ON SEQUENCE public.task_id_sequence TO agent_platform_user;

-- DROP SEQUENCE public.taskset_id_sequence;

CREATE SEQUENCE public.taskset_id_sequence
	INCREMENT BY 1
	MINVALUE 1
	MAXVALUE 9223372036854775807
	START 1
	CACHE 1
	NO CYCLE;

-- Permissions

ALTER SEQUENCE public.taskset_id_sequence OWNER TO agent_platform_user;
GRANT ALL ON SEQUENCE public.taskset_id_sequence TO agent_platform_user;

-- public.account_integrates definition

-- Drop table

-- DROP TABLE public.account_integrates;

CREATE TABLE public.account_integrates (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	account_id uuid NOT NULL,
	provider varchar(16) NOT NULL,
	open_id varchar(255) NOT NULL,
	encrypted_token varchar(255) NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT account_integrate_pkey PRIMARY KEY (id),
	CONSTRAINT unique_account_provider UNIQUE (account_id, provider),
	CONSTRAINT unique_provider_open_id UNIQUE (provider, open_id)
);

-- Permissions

ALTER TABLE public.account_integrates OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.account_integrates TO agent_platform_user;


CREATE TABLE api_info (
    id SERIAL PRIMARY KEY, -- 主键，自动递增
    interface_name_zh VARCHAR(255) NOT NULL, -- 接口中文名
    interface_name_en VARCHAR(255), -- 接口英文名
    api_id VARCHAR(100) UNIQUE NOT NULL, -- APIID，唯一标识
    interface_type VARCHAR(50) NOT NULL, -- 接口类型
    eop_protocol VARCHAR(50), -- EOP协议
    eop_call_address TEXT, -- EOP调用地址
    service_protocol VARCHAR(50), -- 服务协议
    interface_description TEXT, -- 接口说明
    auth_policy VARCHAR(100), -- 认证策略
    timeout INTEGER, -- 超时时长，单位秒
    open_scope VARCHAR(100), -- 开放范围
    is_public BOOLEAN, -- 是否公网
    system_belonged_to VARCHAR(255), -- 所属系统
    region VARCHAR(100), -- 区域
    application_scenario TEXT, -- 应用场景
    headers TEXT, -- 请求头
    request_script TEXT, -- 请求脚本
    input_params TEXT, -- 输入参数
    request_example TEXT, -- 请求示例
    output_params TEXT, -- 输出参数
    response_example TEXT, -- 返回示例
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 创建时间，默认为当前时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 更新时间，默认为当前时间，并且在记录更新时自动更新
    created_by VARCHAR(255), -- 创建人
    updated_by VARCHAR(255) -- 更新人
);
-- 创建索引
CREATE INDEX idx_interface_name ON api_info (interface_name_zh);
CREATE INDEX idx_application_scenario ON api_info (application_scenario);
CREATE INDEX idx_api_id_type ON api_info (api_id, interface_type);

-- public.accounts definition

-- Drop table

-- DROP TABLE public.accounts;

CREATE TABLE public.accounts (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	"name" varchar(255) NOT NULL,
	email varchar(255) NULL,
	"password" varchar(255) NULL,
	password_salt varchar(255) NULL,
	avatar varchar(255) NULL,
	interface_language varchar(255) NULL,
	interface_theme varchar(255) NULL,
	timezone varchar(255) NULL,
	last_login_at timestamp NULL,
	last_login_ip varchar(255) NULL,
	status varchar(16) DEFAULT 'active'::character varying NOT NULL,
	initialized_at timestamp NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	last_active_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	employee_number varchar(255) NULL, -- 中国电信人力编号
	username varchar(255) NULL, -- 系统中用户名
	mobile varchar(255) NULL, -- 手机号
    company_name varchar(255) NULL, -- 部门名称
	CONSTRAINT account_pkey PRIMARY KEY (id)
);
CREATE INDEX account_email_idx ON public.accounts USING btree (email);
CREATE INDEX account_employee_number_idx ON public.accounts USING btree (employee_number);

-- Column comments

COMMENT ON COLUMN public.accounts.employee_number IS '中国电信人力编号';
COMMENT ON COLUMN public.accounts.username IS '系统中用户名';
COMMENT ON COLUMN public.accounts.mobile IS '手机号';

-- Permissions

ALTER TABLE public.accounts OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.accounts TO agent_platform_user;


-- public.agent_platform_setups definition

-- Drop table

-- DROP TABLE public.agent_platform_setups;

CREATE TABLE public.agent_platform_setups (
	"version" varchar(255) NOT NULL,
	setup_at timestamp(6) DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT dify_setups_copy1_pkey PRIMARY KEY (version)
);

-- Permissions

ALTER TABLE public.agent_platform_setups OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.agent_platform_setups TO agent_platform_user;


-- public.alembic_version definition

-- Drop table

-- DROP TABLE public.alembic_version;

CREATE TABLE public.alembic_version (
	version_num varchar(32) NOT NULL,
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Permissions

ALTER TABLE public.alembic_version OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.alembic_version TO agent_platform_user;


-- public.api_based_extensions definition

-- Drop table

-- DROP TABLE public.api_based_extensions;

CREATE TABLE public.api_based_extensions (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	"name" varchar(255) NOT NULL,
	api_endpoint varchar(255) NOT NULL,
	api_key text NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT api_based_extension_pkey PRIMARY KEY (id)
);
CREATE INDEX api_based_extension_tenant_idx ON public.api_based_extensions USING btree (tenant_id);

-- Permissions

ALTER TABLE public.api_based_extensions OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.api_based_extensions TO agent_platform_user;


-- public.api_requests definition

-- Drop table

-- DROP TABLE public.api_requests;

CREATE TABLE public.api_requests (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	api_token_id uuid NOT NULL,
	"path" varchar(255) NOT NULL,
	request text NULL,
	response text NULL,
	ip varchar(255) NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT api_request_pkey PRIMARY KEY (id)
);
CREATE INDEX api_request_token_idx ON public.api_requests USING btree (tenant_id, api_token_id);

-- Permissions

ALTER TABLE public.api_requests OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.api_requests TO agent_platform_user;


-- public.api_tokens definition

-- Drop table

-- DROP TABLE public.api_tokens;

CREATE TABLE public.api_tokens (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	app_id uuid NULL,
	"type" varchar(16) NOT NULL,
	"token" varchar(255) NOT NULL,
	last_used_at timestamp NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	tenant_id uuid NULL,
	CONSTRAINT api_token_pkey PRIMARY KEY (id)
);
CREATE INDEX api_token_app_id_type_idx ON public.api_tokens USING btree (app_id, type);
CREATE INDEX api_token_tenant_idx ON public.api_tokens USING btree (tenant_id, type);
CREATE INDEX api_token_token_idx ON public.api_tokens USING btree (token, type);

-- Permissions

ALTER TABLE public.api_tokens OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.api_tokens TO agent_platform_user;


-- public.app_annotation_hit_histories definition

-- Drop table

-- DROP TABLE public.app_annotation_hit_histories;

CREATE TABLE public.app_annotation_hit_histories (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	app_id uuid NOT NULL,
	annotation_id uuid NOT NULL,
	"source" text NOT NULL,
	question text NOT NULL,
	account_id uuid NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	score float8 DEFAULT 0 NOT NULL,
	message_id uuid NOT NULL,
	annotation_question text NOT NULL,
	annotation_content text NOT NULL,
	CONSTRAINT app_annotation_hit_histories_pkey PRIMARY KEY (id)
);
CREATE INDEX app_annotation_hit_histories_account_idx ON public.app_annotation_hit_histories USING btree (account_id);
CREATE INDEX app_annotation_hit_histories_annotation_idx ON public.app_annotation_hit_histories USING btree (annotation_id);
CREATE INDEX app_annotation_hit_histories_app_idx ON public.app_annotation_hit_histories USING btree (app_id);
CREATE INDEX app_annotation_hit_histories_message_idx ON public.app_annotation_hit_histories USING btree (message_id);

-- Permissions

ALTER TABLE public.app_annotation_hit_histories OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.app_annotation_hit_histories TO agent_platform_user;


-- public.app_annotation_settings definition

-- Drop table

-- DROP TABLE public.app_annotation_settings;

CREATE TABLE public.app_annotation_settings (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	app_id uuid NOT NULL,
	score_threshold float8 DEFAULT 0 NOT NULL,
	collection_binding_id uuid NOT NULL,
	created_user_id uuid NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_user_id uuid NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT app_annotation_settings_pkey PRIMARY KEY (id)
);
CREATE INDEX app_annotation_settings_app_idx ON public.app_annotation_settings USING btree (app_id);

-- Permissions

ALTER TABLE public.app_annotation_settings OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.app_annotation_settings TO agent_platform_user;


-- public.app_dataset_joins definition

-- Drop table

-- DROP TABLE public.app_dataset_joins;

CREATE TABLE public.app_dataset_joins (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	app_id uuid NOT NULL,
	dataset_id uuid NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
	CONSTRAINT app_dataset_join_pkey PRIMARY KEY (id)
);
CREATE INDEX app_dataset_join_app_dataset_idx ON public.app_dataset_joins USING btree (dataset_id, app_id);

-- Permissions

ALTER TABLE public.app_dataset_joins OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.app_dataset_joins TO agent_platform_user;


-- public.app_model_configs definition

-- Drop table

-- DROP TABLE public.app_model_configs;

CREATE TABLE public.app_model_configs (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	app_id uuid NOT NULL,
	"version" varchar(255) NOT NULL,
	provider varchar(255) NULL,
	model_id varchar(255) NULL,
	configs json NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	opening_statement text NULL,
	suggested_questions text NULL,
	suggested_questions_after_answer text NULL,
	more_like_this text NULL,
	model text NULL,
	user_input_form text NULL,
	pre_prompt text NULL,
	agent_mode text NULL,
	speech_to_text text NULL,
	sensitive_word_avoidance text NULL,
	retriever_resource text NULL,
	dataset_query_variable varchar(255) NULL,
	prompt_type varchar(255) DEFAULT 'simple'::character varying NOT NULL,
	chat_prompt_config text NULL,
	completion_prompt_config text NULL,
	dataset_configs text NULL,
	external_data_tools text NULL,
	file_upload text NULL,
	text_to_speech text NULL,
    is_enable bool NOT NULL DEFAULT true,
    version_app_name varchar(255),
    version_created_by uuid,
	CONSTRAINT app_model_config_pkey PRIMARY KEY (id)
);
CREATE INDEX app_app_id_idx ON public.app_model_configs USING btree (app_id);

-- Permissions

ALTER TABLE public.app_model_configs OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.app_model_configs TO agent_platform_user;


-- public.apps definition

-- Drop table

-- DROP TABLE public.apps;

CREATE TABLE public.apps (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
    account_id uuid NOT NULL,
	"name" varchar(255) NOT NULL,
	"mode" varchar(255) NOT NULL,
	icon varchar(255) NULL,
	icon_background varchar(255) NULL,
	app_model_config_id uuid NULL,
	status varchar(255) DEFAULT 'normal'::character varying NOT NULL,
	enable_site bool NOT NULL,
	enable_api bool NOT NULL,
	api_rpm int4 DEFAULT 0 NOT NULL,
	api_rph int4 DEFAULT 0 NOT NULL,
	is_demo bool DEFAULT false NOT NULL,
	is_public bool DEFAULT false NOT NULL,
    max_active_requests INTEGER NULL,
    created_by uuid NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
    updated_by uuid NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	is_universal bool DEFAULT false NOT NULL,
	workflow_id uuid NULL,
	description text DEFAULT ''::character varying NOT NULL,
	tracing text NULL,
    use_icon_as_answer_icon boolean DEFAULT false NOT NULL,
    header_image text NULL,
	CONSTRAINT app_pkey PRIMARY KEY (id)
);
CREATE INDEX app_tenant_id_idx ON public.apps USING btree (tenant_id);

-- Permissions

ALTER TABLE public.apps OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.apps TO agent_platform_user;


-- public.celery_taskmeta definition

-- Drop table

-- DROP TABLE public.celery_taskmeta;

CREATE TABLE public.celery_taskmeta (
	id int4 DEFAULT nextval('task_id_sequence'::regclass) NOT NULL,
	task_id varchar(155) NULL,
	status varchar(50) NULL,
	"result" bytea NULL,
	date_done timestamp NULL,
	traceback text NULL,
	"name" varchar(155) NULL,
	args bytea NULL,
	kwargs bytea NULL,
	worker varchar(155) NULL,
	retries int4 NULL,
	queue varchar(155) NULL,
	CONSTRAINT celery_taskmeta_pkey PRIMARY KEY (id),
	CONSTRAINT celery_taskmeta_task_id_key UNIQUE (task_id)
);

-- Permissions

ALTER TABLE public.celery_taskmeta OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.celery_taskmeta TO agent_platform_user;


-- public.celery_tasksetmeta definition

-- Drop table

-- DROP TABLE public.celery_tasksetmeta;

CREATE TABLE public.celery_tasksetmeta (
	id int4 DEFAULT nextval('taskset_id_sequence'::regclass) NOT NULL,
	taskset_id varchar(155) NULL,
	"result" bytea NULL,
	date_done timestamp NULL,
	CONSTRAINT celery_tasksetmeta_pkey PRIMARY KEY (id),
	CONSTRAINT celery_tasksetmeta_taskset_id_key UNIQUE (taskset_id)
);

-- Permissions

ALTER TABLE public.celery_tasksetmeta OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.celery_tasksetmeta TO agent_platform_user;


-- public.conversations definition

-- Drop table

-- DROP TABLE public.conversations;

CREATE TABLE public.conversations (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	app_id uuid NOT NULL,
	app_model_config_id uuid NULL,
	model_provider varchar(255) NULL,
	override_model_configs text NULL,
	model_id varchar(255) NULL,
	"mode" varchar(255) NOT NULL,
	"name" varchar(255) NOT NULL,
	summary text NULL,
	inputs json NULL,
	introduction text NULL,
	system_instruction text NULL,
	system_instruction_tokens int4 DEFAULT 0 NOT NULL,
	status varchar(255) NOT NULL,
	from_source varchar(255) NOT NULL,
	from_end_user_id uuid NULL,
	from_account_id uuid NULL,
	read_at timestamp NULL,
	read_account_id uuid NULL,
    dialogue_count INTEGER default 0,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	is_deleted bool DEFAULT false NOT NULL,
	invoke_from varchar(255) NULL,
	CONSTRAINT conversation_pkey PRIMARY KEY (id)
);
CREATE INDEX conversation_app_from_user_idx ON public.conversations USING btree (app_id, from_source, from_end_user_id);

-- Permissions

ALTER TABLE public.conversations OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.conversations TO agent_platform_user;


-- public.data_source_api_key_auth_bindings definition

-- Drop table

-- DROP TABLE public.data_source_api_key_auth_bindings;

CREATE TABLE public.data_source_api_key_auth_bindings (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	category varchar(255) NOT NULL,
	provider varchar(255) NOT NULL,
	credentials text NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	disabled bool DEFAULT false NULL,
	CONSTRAINT data_source_api_key_auth_binding_pkey PRIMARY KEY (id)
);
CREATE INDEX data_source_api_key_auth_binding_provider_idx ON public.data_source_api_key_auth_bindings USING btree (provider);
CREATE INDEX data_source_api_key_auth_binding_tenant_id_idx ON public.data_source_api_key_auth_bindings USING btree (tenant_id);

-- Permissions

ALTER TABLE public.data_source_api_key_auth_bindings OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.data_source_api_key_auth_bindings TO agent_platform_user;


-- public.data_source_oauth_bindings definition

-- Drop table

-- DROP TABLE public.data_source_oauth_bindings;

CREATE TABLE public.data_source_oauth_bindings (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	access_token varchar(255) NOT NULL,
	provider varchar(255) NOT NULL,
	source_info jsonb NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	disabled bool DEFAULT false NULL,
	CONSTRAINT source_binding_pkey PRIMARY KEY (id)
);
CREATE INDEX source_binding_tenant_id_idx ON public.data_source_oauth_bindings USING btree (tenant_id);
CREATE INDEX source_info_idx ON public.data_source_oauth_bindings USING gin (source_info);

-- Permissions

ALTER TABLE public.data_source_oauth_bindings OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.data_source_oauth_bindings TO agent_platform_user;


-- public.dataset_collection_bindings definition

-- Drop table

-- DROP TABLE public.dataset_collection_bindings;

CREATE TABLE public.dataset_collection_bindings (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	provider_name varchar(40) NOT NULL,
	model_name varchar(40) NOT NULL,
	collection_name varchar(64) NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	"type" varchar(40) DEFAULT 'dataset'::character varying NOT NULL,
	CONSTRAINT dataset_collection_bindings_pkey PRIMARY KEY (id)
);
CREATE INDEX provider_model_name_idx ON public.dataset_collection_bindings USING btree (provider_name, model_name);

-- Permissions

ALTER TABLE public.dataset_collection_bindings OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.dataset_collection_bindings TO agent_platform_user;


-- public.dataset_keyword_tables definition

-- Drop table

-- DROP TABLE public.dataset_keyword_tables;

CREATE TABLE public.dataset_keyword_tables (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	dataset_id uuid NOT NULL,
	keyword_table text NOT NULL,
	data_source_type varchar(255) DEFAULT 'database'::character varying NOT NULL,
	CONSTRAINT dataset_keyword_table_pkey PRIMARY KEY (id),
	CONSTRAINT dataset_keyword_tables_dataset_id_key UNIQUE (dataset_id)
);
CREATE INDEX dataset_keyword_table_dataset_id_idx ON public.dataset_keyword_tables USING btree (dataset_id);

-- Permissions

ALTER TABLE public.dataset_keyword_tables OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.dataset_keyword_tables TO agent_platform_user;


-- public.dataset_process_rules definition

-- Drop table

-- DROP TABLE public.dataset_process_rules;

CREATE TABLE public.dataset_process_rules (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	dataset_id uuid NOT NULL,
	"mode" varchar(255) DEFAULT 'automatic'::character varying NOT NULL,
	rules text NULL,
	created_by uuid NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT dataset_process_rule_pkey PRIMARY KEY (id)
);
CREATE INDEX dataset_process_rule_dataset_id_idx ON public.dataset_process_rules USING btree (dataset_id);

-- Permissions

ALTER TABLE public.dataset_process_rules OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.dataset_process_rules TO agent_platform_user;


-- public.dataset_queries definition

-- Drop table

-- DROP TABLE public.dataset_queries;

CREATE TABLE public.dataset_queries (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	dataset_id uuid NOT NULL,
	"content" text NOT NULL,
	"source" varchar(255) NOT NULL,
	source_app_id uuid NULL,
	created_by_role varchar NOT NULL,
	created_by uuid NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
	CONSTRAINT dataset_query_pkey PRIMARY KEY (id)
);
CREATE INDEX dataset_query_dataset_id_idx ON public.dataset_queries USING btree (dataset_id);

-- Permissions

ALTER TABLE public.dataset_queries OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.dataset_queries TO agent_platform_user;


-- public.dataset_retriever_resources definition

-- Drop table

-- DROP TABLE public.dataset_retriever_resources;

CREATE TABLE public.dataset_retriever_resources (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	message_id uuid NOT NULL,
	"position" int4 NOT NULL,
	dataset_id uuid NOT NULL,
	dataset_name text NOT NULL,
	document_id uuid NOT NULL,
	document_name text NOT NULL,
	data_source_type text NOT NULL,
	segment_id uuid NOT NULL,
	score float8 NULL,
	"content" text NOT NULL,
	hit_count int4 NULL,
	word_count int4 NULL,
	segment_position int4 NULL,
	index_node_hash text NULL,
	retriever_from text NOT NULL,
	created_by uuid NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
	CONSTRAINT dataset_retriever_resource_pkey PRIMARY KEY (id)
);
CREATE INDEX dataset_retriever_resource_message_id_idx ON public.dataset_retriever_resources USING btree (message_id);

-- Permissions

ALTER TABLE public.dataset_retriever_resources OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.dataset_retriever_resources TO agent_platform_user;


-- public.datasets definition

-- Drop table

-- DROP TABLE public.datasets;

CREATE TABLE public.datasets (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	"name" varchar(255) NOT NULL,
	description text NULL,
	provider varchar(255) DEFAULT 'vendor'::character varying NOT NULL,
	"permission" varchar(255) DEFAULT 'only_me'::character varying NOT NULL,
	data_source_type varchar(255) NULL,
	indexing_technique varchar(255) NULL,
	index_struct text NULL,
	created_by uuid NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_by uuid NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	embedding_model varchar(255) DEFAULT 'text-embedding-ada-002'::character varying NULL,
	embedding_model_provider varchar(255) DEFAULT 'openai'::character varying NULL,
	collection_binding_id uuid NULL,
	retrieval_model jsonb NULL,
	CONSTRAINT dataset_pkey PRIMARY KEY (id)
);
CREATE INDEX dataset_tenant_idx ON public.datasets USING btree (tenant_id);
CREATE INDEX retrieval_model_idx ON public.datasets USING gin (retrieval_model);

-- Permissions

ALTER TABLE public.datasets OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.datasets TO agent_platform_user;


-- public.document_segments definition

-- Drop table

-- DROP TABLE public.document_segments;

CREATE TABLE public.document_segments (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	dataset_id uuid NOT NULL,
	document_id uuid NOT NULL,
	"position" int4 NOT NULL,
	"content" text NOT NULL,
	word_count int4 NOT NULL,
	tokens int4 NOT NULL,
	keywords json NULL,
	index_node_id varchar(255) NULL,
	index_node_hash varchar(255) NULL,
	hit_count int4 NOT NULL,
	enabled bool DEFAULT true NOT NULL,
	disabled_at timestamp NULL,
	disabled_by uuid NULL,
	status varchar(255) DEFAULT 'waiting'::character varying NOT NULL,
	created_by uuid NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	indexing_at timestamp NULL,
	completed_at timestamp NULL,
	error text NULL,
	stopped_at timestamp NULL,
	answer text NULL,
	updated_by uuid NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT document_segment_pkey PRIMARY KEY (id)
);
CREATE INDEX document_segment_dataset_id_idx ON public.document_segments USING btree (dataset_id);
CREATE INDEX document_segment_dataset_node_idx ON public.document_segments USING btree (dataset_id, index_node_id);
CREATE INDEX document_segment_document_id_idx ON public.document_segments USING btree (document_id);
CREATE INDEX document_segment_tenant_dataset_idx ON public.document_segments USING btree (dataset_id, tenant_id);
CREATE INDEX document_segment_tenant_document_idx ON public.document_segments USING btree (document_id, tenant_id);
CREATE INDEX document_segment_tenant_idx ON public.document_segments USING btree (tenant_id);

-- Permissions

ALTER TABLE public.document_segments OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.document_segments TO agent_platform_user;


-- public.documents definition

-- Drop table

-- DROP TABLE public.documents;

CREATE TABLE public.documents (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	dataset_id uuid NOT NULL,
	"position" int4 NOT NULL,
	data_source_type varchar(255) NOT NULL,
	data_source_info text NULL,
	dataset_process_rule_id uuid NULL,
	batch varchar(255) NOT NULL,
	"name" varchar(255) NOT NULL,
	created_from varchar(255) NOT NULL,
	created_by uuid NOT NULL,
	created_api_request_id uuid NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	processing_started_at timestamp NULL,
	file_id text NULL,
	word_count int4 NULL,
	parsing_completed_at timestamp NULL,
	cleaning_completed_at timestamp NULL,
	splitting_completed_at timestamp NULL,
	tokens int4 NULL,
	indexing_latency float8 NULL,
	completed_at timestamp NULL,
	is_paused bool DEFAULT false NULL,
	paused_by uuid NULL,
	paused_at timestamp NULL,
	error text NULL,
	stopped_at timestamp NULL,
	indexing_status varchar(255) DEFAULT 'waiting'::character varying NOT NULL,
	enabled bool DEFAULT true NOT NULL,
	disabled_at timestamp NULL,
	disabled_by uuid NULL,
	archived bool DEFAULT false NOT NULL,
	archived_reason varchar(255) NULL,
	archived_by uuid NULL,
	archived_at timestamp NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	doc_type varchar(40) NULL,
	doc_metadata json NULL,
	doc_form varchar(255) DEFAULT 'text_model'::character varying NOT NULL,
	doc_language varchar(255) NULL,
	CONSTRAINT document_pkey PRIMARY KEY (id)
);
CREATE INDEX document_dataset_id_idx ON public.documents USING btree (dataset_id);
CREATE INDEX document_is_paused_idx ON public.documents USING btree (is_paused);
CREATE INDEX document_tenant_idx ON public.documents USING btree (tenant_id);

-- Permissions

ALTER TABLE public.documents OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.documents TO agent_platform_user;


-- public.embeddings definition

-- Drop table

-- DROP TABLE public.embeddings;

CREATE TABLE public.embeddings (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	hash varchar(64) NOT NULL,
	embedding bytea NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	model_name varchar(40) DEFAULT 'text-embedding-ada-002'::character varying NOT NULL,
	provider_name varchar(40) DEFAULT ''::character varying NOT NULL,
	CONSTRAINT embedding_hash_idx UNIQUE (model_name, hash, provider_name),
	CONSTRAINT embedding_pkey PRIMARY KEY (id)
);

-- Permissions

ALTER TABLE public.embeddings OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.embeddings TO agent_platform_user;


-- public.end_users definition

-- Drop table

-- DROP TABLE public.end_users;

CREATE TABLE public.end_users (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	app_id uuid NULL,
	"type" varchar(255) NOT NULL,
	external_user_id varchar(255) NULL,
	"name" varchar(255) NULL,
	is_anonymous bool DEFAULT true NOT NULL,
	session_id varchar(255) NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT end_user_pkey PRIMARY KEY (id)
);
CREATE INDEX end_user_session_id_idx ON public.end_users USING btree (session_id, type);
CREATE INDEX end_user_tenant_session_id_idx ON public.end_users USING btree (tenant_id, session_id, type);

-- Permissions

ALTER TABLE public.end_users OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.end_users TO agent_platform_user;


-- public.installed definition

-- Drop table

-- DROP TABLE public.installed;

create table installed
(
    id                           uuid      default uuid_generate_v4()   not null,
    tenant_id                    uuid                                   not null,
    type                         varchar(255)                           not null,
    relation_app_id              uuid                                   not null,
    relation_app_owner_tenant_id uuid                                   not null,
    "position"                   int4                                   not null,
    status                       varchar(255)                           not null,
    last_used_at                 timestamp,
    created_at                   timestamp default CURRENT_TIMESTAMP(0) not null,
    CONSTRAINT installed_pkey PRIMARY KEY (id),
    CONSTRAINT unique_tenant_relation_app UNIQUE (tenant_id, relation_app_id)
);
CREATE INDEX installed_relation_app_id_idx ON public.installed USING btree (relation_app_id);
CREATE INDEX installed_tenant_id_idx ON public.installed USING btree (tenant_id);

-- Permissions

ALTER TABLE public.installed OWNER TO agent_platform_user;
GRANT
ALL
ON TABLE public.installed TO agent_platform_user;


-- public.installed_apps definition

-- Drop table

-- DROP TABLE public.installed_apps;

CREATE TABLE public.installed_apps (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	app_id uuid NOT NULL,
	app_owner_tenant_id uuid NOT NULL,
	"position" int4 NOT NULL,
	is_pinned bool DEFAULT false NOT NULL,
	last_used_at timestamp NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT installed_app_pkey PRIMARY KEY (id),
	CONSTRAINT unique_tenant_app UNIQUE (tenant_id, app_id)
);
CREATE INDEX installed_app_app_id_idx ON public.installed_apps USING btree (app_id);
CREATE INDEX installed_app_tenant_id_idx ON public.installed_apps USING btree (tenant_id);

-- Permissions

ALTER TABLE public.installed_apps OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.installed_apps TO agent_platform_user;


-- public.invitation_codes definition

-- Drop table

-- DROP TABLE public.invitation_codes;

CREATE TABLE public.invitation_codes (
	id serial4 NOT NULL,
	batch varchar(255) NOT NULL,
	code varchar(32) NOT NULL,
	status varchar(16) DEFAULT 'unused'::character varying NOT NULL,
	used_at timestamp NULL,
	used_by_tenant_id uuid NULL,
	used_by_account_id uuid NULL,
	deprecated_at timestamp NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT invitation_code_pkey PRIMARY KEY (id)
);
CREATE INDEX invitation_codes_batch_idx ON public.invitation_codes USING btree (batch);
CREATE INDEX invitation_codes_code_idx ON public.invitation_codes USING btree (code, status);

-- Permissions

ALTER TABLE public.invitation_codes OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.invitation_codes TO agent_platform_user;


-- public.load_balancing_model_configs definition

-- Drop table

-- DROP TABLE public.load_balancing_model_configs;

CREATE TABLE public.load_balancing_model_configs (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	provider_name varchar(255) NOT NULL,
	model_name varchar(255) NOT NULL,
	model_type varchar(40) NOT NULL,
	"name" varchar(255) NOT NULL,
	encrypted_config text NULL,
	enabled bool DEFAULT true NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT load_balancing_model_config_pkey PRIMARY KEY (id)
);
CREATE INDEX load_balancing_model_config_tenant_provider_model_idx ON public.load_balancing_model_configs USING btree (tenant_id, provider_name, model_type);

-- Permissions

ALTER TABLE public.load_balancing_model_configs OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.load_balancing_model_configs TO agent_platform_user;


-- public.message_agent_thoughts definition

-- Drop table

-- DROP TABLE public.message_agent_thoughts;

CREATE TABLE public.message_agent_thoughts (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	message_id uuid NOT NULL,
	message_chain_id uuid NULL,
	"position" int4 NOT NULL,
	thought text NULL,
	tool text NULL,
	tool_input text NULL,
	observation text NULL,
	tool_process_data text NULL,
	message text NULL,
	message_token int4 NULL,
	message_unit_price numeric NULL,
	answer text NULL,
	answer_token int4 NULL,
	answer_unit_price numeric NULL,
	tokens int4 NULL,
	total_price numeric NULL,
	currency varchar NULL,
	latency float8 NULL,
	created_by_role varchar NOT NULL,
	created_by uuid NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
	message_price_unit numeric(10, 7) DEFAULT 0.001 NOT NULL,
	answer_price_unit numeric(10, 7) DEFAULT 0.001 NOT NULL,
	message_files text NULL,
	tool_labels_str text DEFAULT '{}'::text NOT NULL,
	tool_meta_str text DEFAULT '{}'::text NOT NULL,
	CONSTRAINT message_agent_thought_pkey PRIMARY KEY (id)
);
CREATE INDEX message_agent_thought_message_chain_id_idx ON public.message_agent_thoughts USING btree (message_chain_id);
CREATE INDEX message_agent_thought_message_id_idx ON public.message_agent_thoughts USING btree (message_id);

-- Permissions

ALTER TABLE public.message_agent_thoughts OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.message_agent_thoughts TO agent_platform_user;


-- public.message_annotations definition

-- Drop table

-- DROP TABLE public.message_annotations;

CREATE TABLE public.message_annotations (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	app_id uuid NOT NULL,
	conversation_id uuid NULL,
	message_id uuid NULL,
	"content" text NOT NULL,
	account_id uuid NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	question text NULL,
	hit_count int4 DEFAULT 0 NOT NULL,
	CONSTRAINT message_annotation_pkey PRIMARY KEY (id)
);
CREATE INDEX message_annotation_app_idx ON public.message_annotations USING btree (app_id);
CREATE INDEX message_annotation_conversation_idx ON public.message_annotations USING btree (conversation_id);
CREATE INDEX message_annotation_message_idx ON public.message_annotations USING btree (message_id);

-- Permissions

ALTER TABLE public.message_annotations OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.message_annotations TO agent_platform_user;


-- public.message_chains definition

-- Drop table

-- DROP TABLE public.message_chains;

CREATE TABLE public.message_chains (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	message_id uuid NOT NULL,
	"type" varchar(255) NOT NULL,
	"input" text NULL,
	"output" text NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
	CONSTRAINT message_chain_pkey PRIMARY KEY (id)
);
CREATE INDEX message_chain_message_id_idx ON public.message_chains USING btree (message_id);

-- 流程申请审核表
-- application_audit table
CREATE TABLE application_audit (
    id UUID DEFAULT uuid_generate_v4() NOT NULL PRIMARY KEY,
    application_type VARCHAR(100) NOT NULL, -- 流程类型
    applicant_id VARCHAR(255) NOT NULL, -- 申请人ID
    applicant VARCHAR(255), -- 申请人中文名
    reason TEXT, -- 申请原因
    app_id VARCHAR(255) NOT NULL, -- 应用ID
    app_type VARCHAR(100) NOT NULL, -- 应用类型
    space_id VARCHAR(255) NOT NULL, -- 个人/项目空间Id
    space_name VARCHAR(255), -- 个人/项目空间名称
    status VARCHAR(100) NOT NULL, -- 审核状态
    denial_reason TEXT, -- 不通过原因
    reviewer_id VARCHAR(255), -- 审核人ID
    reviewer VARCHAR(255), -- 审核人
    application_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 申请时间
    reviewed_at TIMESTAMP , -- 审核时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    change_description TEXT,
    need_publish_tool BOOL,
    tool_param TEXT
);
CREATE INDEX idx_application_audit_workflow_type ON application_audit (application_type);
CREATE INDEX idx_application_audit_applicant ON application_audit (applicant);
CREATE INDEX idx_application_audit_space_name ON application_audit (space_name);
CREATE INDEX idx_application_audit_status ON application_audit (status);
CREATE INDEX idx_application_audit_reviewer ON application_audit (reviewer);
-- Permissions

ALTER TABLE public.message_chains OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.message_chains TO agent_platform_user;


-- public.message_feedbacks definition

-- Drop table

-- DROP TABLE public.message_feedbacks;

CREATE TABLE public.message_feedbacks (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	app_id uuid NOT NULL,
	conversation_id uuid NOT NULL,
	message_id uuid NOT NULL,
	rating varchar(255) NOT NULL,
	"content" text NULL,
	from_source varchar(255) NOT NULL,
	from_end_user_id uuid NULL,
	from_account_id uuid NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT message_feedback_pkey PRIMARY KEY (id)
);
CREATE INDEX message_feedback_app_idx ON public.message_feedbacks USING btree (app_id);
CREATE INDEX message_feedback_conversation_idx ON public.message_feedbacks USING btree (conversation_id, from_source, rating);
CREATE INDEX message_feedback_message_idx ON public.message_feedbacks USING btree (message_id, from_source);

-- Permissions

ALTER TABLE public.message_feedbacks OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.message_feedbacks TO agent_platform_user;


-- public.message_files definition

-- Drop table

-- DROP TABLE public.message_files;

CREATE TABLE public.message_files (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	message_id uuid NOT NULL,
	"type" varchar(255) NOT NULL,
	transfer_method varchar(255) NOT NULL,
	url text NULL,
	upload_file_id uuid NULL,
	created_by_role varchar(255) NOT NULL,
	created_by uuid NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	belongs_to varchar(255) NULL,
	CONSTRAINT message_file_pkey PRIMARY KEY (id)
);
CREATE INDEX message_file_created_by_idx ON public.message_files USING btree (created_by);
CREATE INDEX message_file_message_idx ON public.message_files USING btree (message_id);

-- Permissions

ALTER TABLE public.message_files OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.message_files TO agent_platform_user;


-- public.messages definition

-- Drop table

-- DROP TABLE public.messages;

CREATE TABLE public.messages (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	app_id uuid NOT NULL,
	model_provider varchar(255) NULL,
	model_id varchar(255) NULL,
	override_model_configs text NULL,
	conversation_id uuid NOT NULL,
	inputs json NULL,
	query text NOT NULL,
	message json NOT NULL,
	message_tokens int4 DEFAULT 0 NOT NULL,
	message_unit_price numeric(10, 4) NOT NULL,
	answer text NOT NULL,
	answer_tokens int4 DEFAULT 0 NOT NULL,
	answer_unit_price numeric(10, 4) NOT NULL,
	provider_response_latency float8 DEFAULT 0 NOT NULL,
	total_price numeric(10, 7) NULL,
	currency varchar(255) NOT NULL,
	from_source varchar(255) NOT NULL,
	from_end_user_id uuid NULL,
	from_account_id uuid NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	agent_based bool DEFAULT false NOT NULL,
	message_price_unit numeric(10, 7) DEFAULT 0.001 NOT NULL,
	answer_price_unit numeric(10, 7) DEFAULT 0.001 NOT NULL,
    parent_message_id uuid NULL,
	workflow_run_id uuid NULL,
	status varchar(255) DEFAULT 'normal'::character varying NOT NULL,
	error text NULL,
	message_metadata text NULL,
	invoke_from varchar(255) NULL,
	CONSTRAINT message_pkey PRIMARY KEY (id)
);
CREATE INDEX message_account_idx ON public.messages USING btree (app_id, from_source, from_account_id);
CREATE INDEX message_app_id_idx ON public.messages USING btree (app_id, created_at);
CREATE INDEX message_conversation_id_idx ON public.messages USING btree (conversation_id);
CREATE INDEX message_end_user_idx ON public.messages USING btree (app_id, from_source, from_end_user_id);
CREATE INDEX message_workflow_run_id_idx ON public.messages USING btree (conversation_id, workflow_run_id);

-- Permissions

ALTER TABLE public.messages OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.messages TO agent_platform_user;


-- public.operation_logs definition

-- Drop table

-- DROP TABLE public.operation_logs;

CREATE TABLE public.operation_logs (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	account_id uuid NOT NULL,
	"action" varchar(255) NOT NULL,
	"content" json NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	created_ip varchar(255) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT operation_log_pkey PRIMARY KEY (id)
);
CREATE INDEX operation_log_account_action_idx ON public.operation_logs USING btree (tenant_id, account_id, action);

-- Permissions

ALTER TABLE public.operation_logs OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.operation_logs TO agent_platform_user;


-- public.pinned_conversations definition

-- Drop table

-- DROP TABLE public.pinned_conversations;

CREATE TABLE public.pinned_conversations (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	app_id uuid NOT NULL,
	conversation_id uuid NOT NULL,
	created_by uuid NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	created_by_role varchar(255) DEFAULT 'end_user'::character varying NOT NULL,
	CONSTRAINT pinned_conversation_pkey PRIMARY KEY (id)
);
CREATE INDEX pinned_conversation_conversation_idx ON public.pinned_conversations USING btree (app_id, conversation_id, created_by_role, created_by);

-- Permissions

ALTER TABLE public.pinned_conversations OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.pinned_conversations TO agent_platform_user;


-- public.provider_model_settings definition

-- Drop table

-- DROP TABLE public.provider_model_settings;

CREATE TABLE public.provider_model_settings (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	provider_name varchar(255) NOT NULL,
	model_name varchar(255) NOT NULL,
	model_type varchar(40) NOT NULL,
	enabled bool DEFAULT true NOT NULL,
	load_balancing_enabled bool DEFAULT false NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT provider_model_setting_pkey PRIMARY KEY (id)
);
CREATE INDEX provider_model_setting_tenant_provider_model_idx ON public.provider_model_settings USING btree (tenant_id, provider_name, model_type);

-- Permissions

ALTER TABLE public.provider_model_settings OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.provider_model_settings TO agent_platform_user;


-- public.provider_models definition

-- Drop table

-- DROP TABLE public.provider_models;

CREATE TABLE public.provider_models (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	provider_name varchar(255) NOT NULL,
	model_name varchar(255) NOT NULL,
	model_type varchar(40) NOT NULL,
	encrypted_config text NULL,
	is_valid bool DEFAULT false NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
    employee_number varchar(255) NULL,
	CONSTRAINT provider_model_pkey PRIMARY KEY (id),
	CONSTRAINT unique_provider_model_name UNIQUE (tenant_id, provider_name, model_name, model_type)
);
CREATE INDEX provider_model_tenant_id_provider_idx ON public.provider_models USING btree (tenant_id, provider_name);

COMMENT ON COLUMN public.provider_models.employee_number IS '中国电信人力编号';

-- Permissions

ALTER TABLE public.provider_models OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.provider_models TO agent_platform_user;


-- public.provider_orders definition

-- Drop table

-- DROP TABLE public.provider_orders;

CREATE TABLE public.provider_orders (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	provider_name varchar(255) NOT NULL,
	account_id uuid NOT NULL,
	payment_product_id varchar(191) NOT NULL,
	payment_id varchar(191) NULL,
	transaction_id varchar(191) NULL,
	quantity int4 DEFAULT 1 NOT NULL,
	currency varchar(40) NULL,
	total_amount int4 NULL,
	payment_status varchar(40) DEFAULT 'wait_pay'::character varying NOT NULL,
	paid_at timestamp NULL,
	pay_failed_at timestamp NULL,
	refunded_at timestamp NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT provider_order_pkey PRIMARY KEY (id)
);
CREATE INDEX provider_order_tenant_provider_idx ON public.provider_orders USING btree (tenant_id, provider_name);

-- Permissions

ALTER TABLE public.provider_orders OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.provider_orders TO agent_platform_user;


-- public.providers definition

-- Drop table

-- DROP TABLE public.providers;

CREATE TABLE public.providers (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	provider_name varchar(255) NOT NULL,
	provider_type varchar(40) DEFAULT 'custom'::character varying NOT NULL,
	encrypted_config text NULL,
	is_valid bool DEFAULT false NOT NULL,
	last_used timestamp NULL,
	quota_type varchar(40) DEFAULT ''::character varying NULL,
	quota_limit int8 NULL,
	quota_used int8 NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT provider_pkey PRIMARY KEY (id),
	CONSTRAINT unique_provider_name_type_quota UNIQUE (tenant_id, provider_name, provider_type, quota_type)
);
CREATE INDEX provider_tenant_id_provider_idx ON public.providers USING btree (tenant_id, provider_name);

-- Permissions

ALTER TABLE public.providers OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.providers TO agent_platform_user;


-- public.recommended_apps definition

-- Drop table

-- DROP TABLE public.recommended_apps;

CREATE TABLE public.recommended_apps (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	app_id uuid NOT NULL,
	description json NOT NULL,
	copyright varchar(255) NOT NULL,
	privacy_policy varchar(255) NOT NULL,
	category varchar(255) NOT NULL,
	"position" int4 NOT NULL,
	is_listed bool NOT NULL,
	install_count int4 NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	"language" varchar(255) DEFAULT 'en-US'::character varying NOT NULL,
	custom_disclaimer varchar(255) NULL,
	CONSTRAINT recommended_app_pkey PRIMARY KEY (id)
);
CREATE INDEX recommended_app_app_id_idx ON public.recommended_apps USING btree (app_id);
CREATE INDEX recommended_app_is_listed_idx ON public.recommended_apps USING btree (is_listed, language);

-- Permissions

ALTER TABLE public.recommended_apps OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.recommended_apps TO agent_platform_user;


-- public.saved_messages definition

-- Drop table

-- DROP TABLE public.saved_messages;

CREATE TABLE public.saved_messages (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	app_id uuid NOT NULL,
	message_id uuid NOT NULL,
	created_by uuid NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	created_by_role varchar(255) DEFAULT 'end_user'::character varying NOT NULL,
	CONSTRAINT saved_message_pkey PRIMARY KEY (id)
);
CREATE INDEX saved_message_message_idx ON public.saved_messages USING btree (app_id, message_id, created_by_role, created_by);

-- Permissions

ALTER TABLE public.saved_messages OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.saved_messages TO agent_platform_user;


-- public.sites definition

-- Drop table

-- DROP TABLE public.sites;

CREATE TABLE public.sites (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	app_id uuid NOT NULL,
	title varchar(255) NOT NULL,
	icon varchar(255) NULL,
	icon_background varchar(255) NULL,
	description text NULL,
	default_language varchar(255) NOT NULL,
	copyright varchar(255) NULL,
	privacy_policy varchar(255) NULL,
	customize_domain varchar(255) NULL,
	customize_token_strategy varchar(255) NOT NULL,
	prompt_public bool DEFAULT false NOT NULL,
	status varchar(255) DEFAULT 'normal'::character varying NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	code varchar(255) NULL,
	custom_disclaimer varchar(255) NULL,
	show_workflow_steps bool DEFAULT true NOT NULL,
	chat_color_theme varchar(255) NULL,
	chat_color_theme_inverted bool DEFAULT false NOT NULL,
	CONSTRAINT site_pkey PRIMARY KEY (id)
);
CREATE INDEX site_app_id_idx ON public.sites USING btree (app_id);
CREATE INDEX site_code_idx ON public.sites USING btree (code, status);

-- Permissions

ALTER TABLE public.sites OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.sites TO agent_platform_user;


-- public.tag_bindings definition

-- Drop table

-- DROP TABLE public.tag_bindings;

CREATE TABLE public.tag_bindings (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NULL,
	tag_id uuid NULL,
	target_id uuid NULL,
	created_by uuid NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT tag_binding_pkey PRIMARY KEY (id)
);
CREATE INDEX tag_bind_tag_id_idx ON public.tag_bindings USING btree (tag_id);
CREATE INDEX tag_bind_target_id_idx ON public.tag_bindings USING btree (target_id);

-- Permissions

ALTER TABLE public.tag_bindings OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.tag_bindings TO agent_platform_user;


-- public.tags definition

-- Drop table

-- DROP TABLE public.tags;

CREATE TABLE public.tags (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NULL,
	"type" varchar(16) NOT NULL,
	"name" varchar(255) NOT NULL,
	created_by uuid NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT tag_pkey PRIMARY KEY (id)
);
CREATE INDEX tag_name_idx ON public.tags USING btree (name);
CREATE INDEX tag_type_idx ON public.tags USING btree (type);

-- Permissions

ALTER TABLE public.tags OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.tags TO agent_platform_user;


-- public.tenant_account_joins definition

-- Drop table

-- DROP TABLE public.tenant_account_joins;

CREATE TABLE public.tenant_account_joins (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	account_id uuid NOT NULL,
	"role" varchar(16) DEFAULT 'normal'::character varying NOT NULL,
	invited_by uuid NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	"current" bool DEFAULT false NOT NULL,
	CONSTRAINT tenant_account_join_pkey PRIMARY KEY (id),
	CONSTRAINT unique_tenant_account_join UNIQUE (tenant_id, account_id)
);
CREATE INDEX tenant_account_join_account_id_idx ON public.tenant_account_joins USING btree (account_id);
CREATE INDEX tenant_account_join_tenant_id_idx ON public.tenant_account_joins USING btree (tenant_id);

-- Permissions

ALTER TABLE public.tenant_account_joins OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.tenant_account_joins TO agent_platform_user;


-- public.tenant_default_models definition

-- Drop table

-- DROP TABLE public.tenant_default_models;

CREATE TABLE public.tenant_default_models (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	provider_name varchar(255) NOT NULL,
	model_name varchar(255) NOT NULL,
	model_type varchar(40) NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT tenant_default_model_pkey PRIMARY KEY (id)
);
CREATE INDEX tenant_default_model_tenant_id_provider_type_idx ON public.tenant_default_models USING btree (tenant_id, provider_name, model_type);

-- Permissions

ALTER TABLE public.tenant_default_models OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.tenant_default_models TO agent_platform_user;


-- public.tenant_preferred_model_providers definition

-- Drop table

-- DROP TABLE public.tenant_preferred_model_providers;

CREATE TABLE public.tenant_preferred_model_providers (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	provider_name varchar(255) NOT NULL,
	preferred_provider_type varchar(40) NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT tenant_preferred_model_provider_pkey PRIMARY KEY (id)
);
CREATE INDEX tenant_preferred_model_provider_tenant_provider_idx ON public.tenant_preferred_model_providers USING btree (tenant_id, provider_name);

-- Permissions

ALTER TABLE public.tenant_preferred_model_providers OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.tenant_preferred_model_providers TO agent_platform_user;


-- public.tenants definition

-- Drop table

-- DROP TABLE public.tenants;

CREATE TABLE public.tenants (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	"name" varchar(255) NOT NULL,
	encrypt_public_key text NULL,
	plan varchar(255) DEFAULT 'basic'::character varying NOT NULL,
	status varchar(255) DEFAULT 'normal'::character varying NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	custom_config text NULL,
    tenant_desc varchar(255) NULL,
	CONSTRAINT tenant_pkey PRIMARY KEY (id)
);

-- Permissions

ALTER TABLE public.tenants OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.tenants TO agent_platform_user;


-- public.tool_api_providers definition

-- Drop table

-- DROP TABLE public.tool_api_providers;

CREATE TABLE public.tool_api_providers (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
    tool_app_id uuid NULL,
	"name" varchar(40) NOT NULL,
	"schema" text NOT NULL,
	schema_type_str varchar(40) NOT NULL,
	user_id uuid NOT NULL,
	tenant_id uuid NOT NULL,
	tools_str text NOT NULL,
	icon varchar(255) NOT NULL,
	credentials_str text NOT NULL,
	description text NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	privacy_policy varchar(255) NULL,
	custom_disclaimer varchar(255) NULL,
    access_type int4 NULL,
	"version" varchar(255) NULL,
    status varchar(255) DEFAULT '' NOT NULL,
    header_image text NULL,
	CONSTRAINT tool_api_provider_pkey PRIMARY KEY (id),
	CONSTRAINT unique_api_tool_provider UNIQUE (name, tenant_id)
);

-- Permissions

ALTER TABLE public.tool_api_providers OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.tool_api_providers TO agent_platform_user;


-- public.tool_apps definition

-- Drop table

-- DROP TABLE public.tool_apps;

CREATE TABLE public.tool_apps (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	"name" varchar(255) NOT NULL,
	description text DEFAULT ''::character varying NOT NULL,
	tool_api_providers_id uuid NULL,
    header_image text NULL,
	status varchar(255) DEFAULT 'normal'::character varying NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT tool_app_pkey PRIMARY KEY (id)
);
CREATE INDEX tool_app_tenant_id_idx ON public.tool_apps USING btree (tenant_id);

-- Permissions

ALTER TABLE public.tool_apps OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.tool_apps TO agent_platform_user;


-- public.tool_builtin_providers definition

-- Drop table

-- DROP TABLE public.tool_builtin_providers;

CREATE TABLE public.tool_builtin_providers (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NULL,
	user_id uuid NOT NULL,
	provider varchar(40) NOT NULL,
	encrypted_credentials text NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT tool_builtin_provider_pkey PRIMARY KEY (id),
	CONSTRAINT unique_builtin_tool_provider UNIQUE (tenant_id, provider)
);

-- Permissions

ALTER TABLE public.tool_builtin_providers OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.tool_builtin_providers TO agent_platform_user;


-- public.tool_conversation_variables definition

-- Drop table

-- DROP TABLE public.tool_conversation_variables;

CREATE TABLE public.tool_conversation_variables (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	user_id uuid NOT NULL,
	tenant_id uuid NOT NULL,
	conversation_id uuid NOT NULL,
	variables_str text NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT tool_conversation_variables_pkey PRIMARY KEY (id)
);
CREATE INDEX conversation_id_idx ON public.tool_conversation_variables USING btree (conversation_id);
CREATE INDEX user_id_idx ON public.tool_conversation_variables USING btree (user_id);

-- Permissions

ALTER TABLE public.tool_conversation_variables OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.tool_conversation_variables TO agent_platform_user;


-- public.tool_files definition

-- Drop table

-- DROP TABLE public.tool_files;

CREATE TABLE public.tool_files (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	user_id uuid NOT NULL,
	tenant_id uuid NOT NULL,
	conversation_id uuid NULL,
	file_key varchar(255) NOT NULL,
	mimetype varchar(255) NOT NULL,
	original_url varchar(255) NULL,
    name varchar(255) default '',
    size integer default -1,
	CONSTRAINT tool_file_pkey PRIMARY KEY (id)
);
CREATE INDEX tool_file_conversation_id_idx ON public.tool_files USING btree (conversation_id);

-- Permissions

ALTER TABLE public.tool_files OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.tool_files TO agent_platform_user;


-- public.tool_label_bindings definition

-- Drop table

-- DROP TABLE public.tool_label_bindings;

CREATE TABLE public.tool_label_bindings (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tool_id varchar(64) NOT NULL,
	tool_type varchar(40) NOT NULL,
	label_name varchar(40) NOT NULL,
	CONSTRAINT tool_label_bind_pkey PRIMARY KEY (id),
	CONSTRAINT unique_tool_label_bind UNIQUE (tool_id, label_name)
);

-- Permissions

ALTER TABLE public.tool_label_bindings OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.tool_label_bindings TO agent_platform_user;


-- public.tool_model_invokes definition

-- Drop table

-- DROP TABLE public.tool_model_invokes;

CREATE TABLE public.tool_model_invokes (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	user_id uuid NOT NULL,
	tenant_id uuid NOT NULL,
	provider varchar(40) NOT NULL,
	tool_type varchar(40) NOT NULL,
	tool_name varchar(40) NOT NULL,
	model_parameters text NOT NULL,
	prompt_messages text NOT NULL,
	model_response text NOT NULL,
	prompt_tokens int4 DEFAULT 0 NOT NULL,
	answer_tokens int4 DEFAULT 0 NOT NULL,
	answer_unit_price numeric(10, 4) NOT NULL,
	answer_price_unit numeric(10, 7) DEFAULT 0.001 NOT NULL,
	provider_response_latency float8 DEFAULT 0 NOT NULL,
	total_price numeric(10, 7) NULL,
	currency varchar(255) NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT tool_model_invoke_pkey PRIMARY KEY (id)
);

-- Permissions

ALTER TABLE public.tool_model_invokes OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.tool_model_invokes TO agent_platform_user;


-- public.tool_providers definition

-- Drop table

-- DROP TABLE public.tool_providers;

CREATE TABLE public.tool_providers (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	tool_name varchar(40) NOT NULL,
	encrypted_credentials text NULL,
	is_enabled bool DEFAULT false NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT tool_provider_pkey PRIMARY KEY (id),
	CONSTRAINT unique_tool_provider_tool_name UNIQUE (tenant_id, tool_name)
);

-- Permissions

ALTER TABLE public.tool_providers OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.tool_providers TO agent_platform_user;


-- public.tool_workflow_providers definition

-- Drop table

-- DROP TABLE public.tool_workflow_providers;

CREATE TABLE public.tool_workflow_providers (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	"name" varchar(40) NOT NULL,
	icon varchar(255) NOT NULL,
	app_id uuid NOT NULL,
    workflow_id uuid NOT NULL,
	user_id uuid NOT NULL,
	tenant_id uuid NOT NULL,
	description text NOT NULL,
	parameter_configuration text DEFAULT '[]'::text NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	privacy_policy varchar(255) DEFAULT ''::character varying NULL,
	"version" varchar(255) DEFAULT ''::character varying NOT NULL,
	"label" varchar(255) DEFAULT ''::character varying NOT NULL,
    "code_content" text NULL,
	CONSTRAINT tool_workflow_provider_pkey PRIMARY KEY (id),
	CONSTRAINT unique_workflow_tool_provider UNIQUE (name, tenant_id),
	CONSTRAINT unique_workflow_tool_provider_app_id UNIQUE (tenant_id, app_id)
);

-- Permissions

ALTER TABLE public.tool_workflow_providers OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.tool_workflow_providers TO agent_platform_user;


-- public.trace_app_config definition

-- Drop table

-- DROP TABLE public.trace_app_config;

CREATE TABLE public.trace_app_config (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	app_id uuid NOT NULL,
	tracing_provider varchar(255) NULL,
	tracing_config json NULL,
	created_at timestamp DEFAULT now() NOT NULL,
	updated_at timestamp DEFAULT now() NOT NULL,
	is_active bool DEFAULT true NOT NULL,
	CONSTRAINT trace_app_config_pkey PRIMARY KEY (id)
);
CREATE INDEX trace_app_config_app_id_idx ON public.trace_app_config USING btree (app_id);
CREATE INDEX tracing_app_config_app_id_idx ON public.trace_app_config USING btree (app_id);

-- Permissions

ALTER TABLE public.trace_app_config OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.trace_app_config TO agent_platform_user;


-- public.tracing_app_configs definition

-- Drop table

-- DROP TABLE public.tracing_app_configs;

CREATE TABLE public.tracing_app_configs (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	app_id uuid NOT NULL,
	tracing_provider varchar(255) NULL,
	tracing_config json NULL,
	created_at timestamp DEFAULT now() NOT NULL,
	updated_at timestamp DEFAULT now() NOT NULL,
	CONSTRAINT tracing_app_config_pkey PRIMARY KEY (id)
);

-- Permissions

ALTER TABLE public.tracing_app_configs OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.tracing_app_configs TO agent_platform_user;


-- public.upload_files definition

-- Drop table

-- DROP TABLE public.upload_files;

CREATE TABLE public.upload_files (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	storage_type varchar(255) NOT NULL,
	"key" varchar(255) NOT NULL,
	"name" varchar(255) NOT NULL,
	"size" int4 NOT NULL,
	"extension" varchar(255) NOT NULL,
	mime_type varchar(255) NULL,
	created_by uuid NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	used bool DEFAULT false NOT NULL,
	used_by uuid NULL,
	used_at timestamp NULL,
	hash varchar(255) NULL,
	created_by_role varchar(255) DEFAULT 'account'::character varying NOT NULL,
	CONSTRAINT upload_file_pkey PRIMARY KEY (id)
);
CREATE INDEX upload_file_tenant_idx ON public.upload_files USING btree (tenant_id);

-- Permissions

ALTER TABLE public.upload_files OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.upload_files TO agent_platform_user;


-- public.workflow_app_logs definition

-- Drop table

-- DROP TABLE public.workflow_app_logs;

CREATE TABLE public.workflow_app_logs (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	app_id uuid NOT NULL,
	workflow_id uuid NOT NULL,
	workflow_run_id uuid NOT NULL,
	created_from varchar(255) NOT NULL,
	created_by_role varchar(255) NOT NULL,
	created_by uuid NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT workflow_app_log_pkey PRIMARY KEY (id)
);
CREATE INDEX workflow_app_log_app_idx ON public.workflow_app_logs USING btree (tenant_id, app_id);

-- Permissions

ALTER TABLE public.workflow_app_logs OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.workflow_app_logs TO agent_platform_user;


-- public.workflow_node_executions definition

-- Drop table

-- DROP TABLE public.workflow_node_executions;

CREATE TABLE public.workflow_node_executions (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	app_id uuid NOT NULL,
	workflow_id uuid NOT NULL,
	triggered_from varchar(255) NOT NULL,
	workflow_run_id uuid NULL,
	"index" int4 NOT NULL,
	predecessor_node_id varchar(255) NULL,
	node_id varchar(255) NOT NULL,
	node_type varchar(255) NOT NULL,
	title varchar(255) NOT NULL,
	inputs text NULL,
	process_data text NULL,
	outputs text NULL,
	status varchar(255) NOT NULL,
	error text NULL,
	elapsed_time float8 DEFAULT 0 NOT NULL,
	execution_metadata text NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	created_by_role varchar(255) NOT NULL,
	created_by uuid NOT NULL,
	finished_at timestamp NULL,
	CONSTRAINT workflow_node_execution_pkey PRIMARY KEY (id)
);
CREATE INDEX workflow_node_execution_node_run_idx ON public.workflow_node_executions USING btree (tenant_id, app_id, workflow_id, triggered_from, node_id);
CREATE INDEX workflow_node_execution_workflow_run_idx ON public.workflow_node_executions USING btree (tenant_id, app_id, workflow_id, triggered_from, workflow_run_id);

-- Permissions

ALTER TABLE public.workflow_node_executions OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.workflow_node_executions TO agent_platform_user;


-- public.workflow_runs definition

-- Drop table

-- DROP TABLE public.workflow_runs;

CREATE TABLE public.workflow_runs (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	app_id uuid NOT NULL,
	sequence_number int4 NOT NULL,
	workflow_id uuid NOT NULL,
	"type" varchar(255) NOT NULL,
	triggered_from varchar(255) NOT NULL,
	"version" varchar(255) NOT NULL,
	graph text NULL,
	inputs text NULL,
	status varchar(255) NOT NULL,
	outputs text NULL,
	error text NULL,
	elapsed_time float8 DEFAULT 0 NOT NULL,
	total_tokens int4 DEFAULT 0 NOT NULL,
	total_steps int4 DEFAULT 0 NULL,
	created_by_role varchar(255) NOT NULL,
	created_by uuid NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	finished_at timestamp NULL,
	CONSTRAINT workflow_run_pkey PRIMARY KEY (id)
);
CREATE INDEX workflow_run_tenant_app_sequence_idx ON public.workflow_runs USING btree (tenant_id, app_id, sequence_number);
CREATE INDEX workflow_run_triggerd_from_idx ON public.workflow_runs USING btree (tenant_id, app_id, triggered_from);

-- Permissions

ALTER TABLE public.workflow_runs OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.workflow_runs TO agent_platform_user;


-- public.workflows definition

-- Drop table

-- DROP TABLE public.workflows;

CREATE TABLE public.workflows (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	tenant_id uuid NOT NULL,
	app_id uuid NOT NULL,
	"type" varchar(255) NOT NULL,
	"version" varchar(255) NOT NULL,
	graph text NULL,
	features text NULL,
	created_by uuid NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_by uuid NULL,
	updated_at timestamp NULL,
    environment_variables text default '{}' not null,
    conversation_variables text default '{}' not null;
    example text,
    is_enable bool NOT NULL DEFAULT true,
    version_app_name varchar(255),
	CONSTRAINT workflow_pkey PRIMARY KEY (id)
);
CREATE INDEX workflow_version_idx ON public.workflows USING btree (tenant_id, app_id, version);

-- Permissions

ALTER TABLE public.workflows OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.workflows TO agent_platform_user;


-- public.tool_published_apps definition

-- Drop table

-- DROP TABLE public.tool_published_apps;

CREATE TABLE public.tool_published_apps (
	id uuid DEFAULT uuid_generate_v4() NOT NULL,
	app_id uuid NOT NULL,
	user_id uuid NOT NULL,
	description text NOT NULL,
	llm_description text NOT NULL,
	query_description text NOT NULL,
	query_name varchar(40) NOT NULL,
	tool_name varchar(40) NOT NULL,
	author varchar(40) NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0) NOT NULL,
	CONSTRAINT published_app_tool_pkey PRIMARY KEY (id),
	CONSTRAINT unique_published_app_tool UNIQUE (app_id, user_id),
	CONSTRAINT tool_published_apps_app_id_fkey FOREIGN KEY (app_id) REFERENCES public.apps(id)
);

-- Permissions

ALTER TABLE public.tool_published_apps OWNER TO agent_platform_user;
GRANT ALL ON TABLE public.tool_published_apps TO agent_platform_user;



-- public.tool_reference definition

-- Drop table

-- DROP TABLE public.tool_reference;

CREATE TABLE public.tool_reference(
    id uuid DEFAULT uuid_generate_v4() NOT NULL,
    source_id uuid NOT NULL,
    reference_id uuid NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP(0),
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP(0),
    CONSTRAINT tool_reference_primary_key PRIMARY KEY (id),
    CONSTRAINT unique_reference UNIQUE (source_id, reference_id)
);
CREATE INDEX source_id_idx ON public.tool_reference USING btree (source_id);
CREATE INDEX reference_id_idx ON public.tool_reference USING btree (reference_id);


INSERT INTO public.agent_platform_setups ("version", setup_at) VALUES('0.0.1', '2024-07-24 09:15:09.000');
END $$;
