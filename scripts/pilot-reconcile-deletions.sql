-- Run after an isolated restore and before that database can become active.
-- The durable tombstone export is kept separately from row-level study backups.
BEGIN;
CREATE TEMP TABLE restored_deletion_tombstones
(LIKE study_deletion_tombstones INCLUDING CONSTRAINTS) ON COMMIT DROP;
COPY restored_deletion_tombstones(code_hash, deleted_at)
FROM :'tombstone_file' WITH (FORMAT CSV, HEADER TRUE);
INSERT INTO study_deletion_tombstones(code_hash, deleted_at)
SELECT code_hash, deleted_at FROM restored_deletion_tombstones
ON CONFLICT (code_hash) DO UPDATE
SET deleted_at = GREATEST(study_deletion_tombstones.deleted_at, EXCLUDED.deleted_at);
DELETE FROM study_participants p
USING study_deletion_tombstones t
WHERE p.opaque_code_hash = t.code_hash;
COMMIT;
