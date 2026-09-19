param([int]$Port = 8000, [ValidateSet('extractive','local','ollama')][string]$NarrativeProvider = 'extractive')
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$env:AML_LLM_PROVIDER = $NarrativeProvider
& ./.venv/Scripts/python.exe -m uvicorn aml.api:app --host 127.0.0.1 --port $Port
