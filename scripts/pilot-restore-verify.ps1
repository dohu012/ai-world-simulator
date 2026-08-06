param(
    [Parameter(Mandatory=$true)][string]$DumpPath,
    [string]$Username = "simulator",
    [string]$ComposeFile = "deploy/compose.pilot.yml"
)
$ErrorActionPreference = "Stop"
$resolved = (Resolve-Path -LiteralPath $DumpPath).Path
$database = "pilot_restore_check"

docker compose -f $ComposeFile cp $resolved postgres:/tmp/pilot-restore.dump
if ($LASTEXITCODE -ne 0) { throw "copying the dump failed" }
docker compose -f $ComposeFile exec -T postgres `
    dropdb --if-exists --username=$Username $database
if ($LASTEXITCODE -ne 0) { throw "dropping the isolated restore database failed" }
docker compose -f $ComposeFile exec -T postgres `
    createdb --username=$Username $database
if ($LASTEXITCODE -ne 0) { throw "creating the isolated restore database failed" }
docker compose -f $ComposeFile exec -T postgres `
    pg_restore --exit-on-error --no-owner --no-acl --username=$Username `
    --dbname=$database /tmp/pilot-restore.dump
if ($LASTEXITCODE -ne 0) { throw "pg_restore failed" }
docker compose -f $ComposeFile exec -T postgres `
    psql --username=$Username --dbname=$database --tuples-only `
    --command="SELECT version_num FROM alembic_version;"
if ($LASTEXITCODE -ne 0) { throw "restored database integrity check failed" }
docker compose -f $ComposeFile exec -T postgres rm -f /tmp/pilot-restore.dump
