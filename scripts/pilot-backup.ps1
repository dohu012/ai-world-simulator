param(
    [Parameter(Mandatory=$true)][string]$OutputDirectory,
    [string]$Database = "simulator",
    [string]$Username = "simulator",
    [string]$DatabaseHost = "",
    [string]$Password = "",
    [string]$ComposeFile = "deploy/compose.pilot.yml"
)
$ErrorActionPreference = "Stop"
$resolved = (Resolve-Path -LiteralPath $OutputDirectory).Path
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$target = Join-Path $resolved "pilot-$stamp.dump"
$hostArguments = @()
if ($DatabaseHost) { $hostArguments = @("--host=$DatabaseHost") }
$execArguments = @("compose", "-f", $ComposeFile, "exec", "-T")
if ($Password) { $execArguments += @("-e", "PGPASSWORD=$Password") }
$execArguments += @(
    "postgres", "pg_dump", "--format=custom", "--no-owner", "--no-acl",
    "--username=$Username", "--file=/tmp/pilot.dump"
) + $hostArguments + @($Database)
& docker @execArguments
if ($LASTEXITCODE -ne 0) { throw "pg_dump failed" }
docker compose -f $ComposeFile cp postgres:/tmp/pilot.dump $target
if ($LASTEXITCODE -ne 0) { throw "copying the dump failed" }
docker compose -f $ComposeFile exec -T postgres rm -f /tmp/pilot.dump
Get-FileHash -Algorithm SHA256 -LiteralPath $target
