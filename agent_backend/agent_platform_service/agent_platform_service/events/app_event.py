from blinker import signal

# sender: app
app_was_created = signal('app-was-created')
app_was_created_async = signal('app-was-created-async')
# sender: app
app_was_published = signal('app-was-published')
app_was_published_async = signal('app-was-published_async')

# sender: app
app_was_installed = signal('app-was-installed')

# sender: app, kwargs: published_workflow
app_published_workflow_was_updated = signal('app-published-workflow-was-updated')

# sender: app, kwargs: synced_draft_workflow
app_draft_workflow_was_synced = signal('app-draft-workflow-was-synced')
app_draft_workflow_was_synced_async = signal('app-draft-workflow-was-synced-async')

# sender: app, kwargs: published_model_config
app_published_model_config_was_updated = signal('app-published-model-config-was-updated')
app_published_model_config_was_updated_async = signal('app-published-model-config-was-updated_async')

# sender: app, kwargs: published_model_config
app_draft_model_config_was_synced = signal('app-draft-model-config-was-synced')
