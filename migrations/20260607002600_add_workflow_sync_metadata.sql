ALTER TABLE sessions
  ADD COLUMN IF NOT EXISTS visibility TEXT NOT NULL DEFAULT 'private';

ALTER TABLE chunk_summaries
  ADD COLUMN IF NOT EXISTS user_id UUID NULL;

ALTER TABLE final_pseudocode
  ADD COLUMN IF NOT EXISTS user_id UUID NULL;

ALTER TABLE workflow_insights
  ADD COLUMN IF NOT EXISTS user_id UUID NULL;

ALTER TABLE workflow_templates
  ADD COLUMN IF NOT EXISTS user_id UUID NULL;

ALTER TABLE workflow_templates
  ADD COLUMN IF NOT EXISTS visibility TEXT NOT NULL DEFAULT 'private';

ALTER TABLE workflow_templates
  ADD COLUMN IF NOT EXISTS shared_with_team BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE workflow_search_index
  ADD COLUMN IF NOT EXISTS user_id UUID NULL;

ALTER TABLE workflow_search_index
  ADD COLUMN IF NOT EXISTS visibility TEXT NOT NULL DEFAULT 'private';

ALTER TABLE agent_handoff_queue
  ADD COLUMN IF NOT EXISTS user_id UUID NULL;
