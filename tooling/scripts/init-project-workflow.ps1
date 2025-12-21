<#
.SYNOPSIS
    INIT-PROJECT-WORKFLOW - Claude Code Workflow Initialization for Windows

.DESCRIPTION
    Sets up automated development workflow for any project using Claude Code CLI.
    Interactive wizard guides through installation.

.EXAMPLE
    .\init-project-workflow.ps1

.NOTES
    Version: 1.0.0
    Requires: PowerShell 5.1+, Claude Code CLI
#>

#Requires -Version 5.1

$script:ScriptDir = $PSScriptRoot

#region Helper Functions

function Write-Banner {
    Write-Host ""
    Write-Host ("{0}" -f ("=" * 65)) -ForegroundColor Cyan
    Write-Host "         CLAUDE CODE WORKFLOW INITIALIZATION" -ForegroundColor Cyan
    Write-Host ("{0}" -f ("=" * 65)) -ForegroundColor Cyan
    Write-Host "  Automated Development Workflow Setup" -ForegroundColor Cyan
    Write-Host "  Version 1.0 (Windows)" -ForegroundColor Cyan
    Write-Host ("{0}" -f ("=" * 65)) -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param(
        [int]$StepNum,
        [string]$StepTitle
    )
    Write-Host ""
    Write-Host ("{0}" -f ("=" * 65)) -ForegroundColor Magenta
    Write-Host "  STEP $StepNum: $StepTitle" -ForegroundColor Magenta
    Write-Host ("{0}" -f ("=" * 65)) -ForegroundColor Magenta
    Write-Host ""
}

function Read-PromptInput {
    param(
        [string]$Prompt,
        [string]$Default = ""
    )

    if ($Default) {
        Write-Host "$Prompt " -NoNewline -ForegroundColor Yellow
        Write-Host "(default: $Default)" -ForegroundColor Blue
    }
    else {
        Write-Host "$Prompt" -ForegroundColor Yellow
    }

    $result = Read-Host
    if ([string]::IsNullOrWhiteSpace($result)) {
        return $Default
    }
    return $result
}

function Read-YesNo {
    param(
        [string]$Prompt,
        [string]$Default = "y"
    )

    Write-Host "$Prompt (y/n) " -NoNewline -ForegroundColor Yellow
    Write-Host "[default: $Default]" -ForegroundColor Blue
    $response = Read-Host

    if ([string]::IsNullOrWhiteSpace($response)) {
        $response = $Default
    }

    return $response -match '^[Yy]'
}

#endregion

#region Setup Functions

function Get-ProjectType {
    Write-Host ">> Detecting project type..." -ForegroundColor Blue

    $projectType = "generic"

    if (Test-Path "package.json") { $projectType = "node" }
    elseif (Test-Path "pubspec.yaml") { $projectType = "flutter" }
    elseif (Test-Path "Cargo.toml") { $projectType = "rust" }
    elseif (Test-Path "go.mod") { $projectType = "go" }
    elseif (Test-Path "requirements.txt") { $projectType = "python" }
    elseif (Test-Path "pyproject.toml") { $projectType = "python" }
    elseif (Test-Path "Gemfile") { $projectType = "ruby" }
    elseif ((Test-Path "pom.xml") -or (Test-Path "build.gradle") -or (Test-Path "build.gradle.kts")) {
        # Check if it's Android or pure Java/Kotlin
        if ((Test-Path "app\src\main\java") -or (Test-Path "app\src\main\kotlin")) {
            $projectType = "android"
        }
        else {
            $projectType = "java"
        }
    }
    elseif ((Test-Path "Package.swift") -or (Get-ChildItem -Filter "*.xcodeproj" -ErrorAction SilentlyContinue) -or (Get-ChildItem -Filter "*.xcworkspace" -ErrorAction SilentlyContinue)) {
        $projectType = "swift"
    }
    elseif ((Test-Path "settings.gradle.kts") -and (Test-Path "build.gradle.kts")) {
        $projectType = "kotlin"
    }

    Write-Host "  Detected: $projectType" -ForegroundColor Green
    return $projectType
}

function New-DirectoryStructure {
    param([string]$ProjectRoot)

    Write-Host ">> Creating directory structure..." -ForegroundColor Blue

    $dirs = @(
        "tooling\.automation\agents"
        "tooling\.automation\checkpoints"
        "tooling\.automation\logs"
        "tooling\scripts\lib"
        "tooling\docs"
    )

    foreach ($dir in $dirs) {
        $path = Join-Path $ProjectRoot $dir
        if (-not (Test-Path $path)) {
            New-Item -ItemType Directory -Path $path -Force | Out-Null
        }
    }

    Write-Host "  [OK] Directories created" -ForegroundColor Green
}

function Copy-CoreScripts {
    param(
        [string]$ProjectRoot,
        [string]$SourceDir
    )

    Write-Host ">> Copying core automation scripts..." -ForegroundColor Blue

    # Copy library scripts
    $libSource = Join-Path $SourceDir "lib"
    $libDest = Join-Path $ProjectRoot "tooling\scripts\lib"

    $libFiles = @("claude-cli.ps1", "checkpoint-integration.ps1")
    foreach ($file in $libFiles) {
        $src = Join-Path $libSource $file
        if (Test-Path $src) {
            Copy-Item $src -Destination $libDest -Force
        }
    }

    # Copy main scripts
    $mainFiles = @("run-story.ps1", "context_checkpoint.py", "setup-checkpoint-service.ps1", "new-doc.ps1")
    $scriptDest = Join-Path $ProjectRoot "tooling\scripts"

    foreach ($file in $mainFiles) {
        $src = Join-Path $SourceDir $file
        if (Test-Path $src) {
            Copy-Item $src -Destination $scriptDest -Force
        }
    }

    Write-Host "  [OK] Scripts copied" -ForegroundColor Green
}

function New-ConfigFile {
    param(
        [string]$ProjectRoot,
        [string]$ProjectName,
        [string]$ProjectType,
        [string]$ModelDev,
        [string]$ModelPlanning,
        [string]$DisplayCurrency = "USD"
    )

    Write-Host ">> Creating configuration file..." -ForegroundColor Blue

    $configPath = Join-Path $ProjectRoot "tooling\.automation\config.ps1"
    $today = (Get-Date).ToString("yyyy-MM-dd")

    $configContent = @"
<#
.SYNOPSIS
    Automation Configuration for $ProjectName

.NOTES
    Generated: $today
#>

# Project settings
`$env:PROJECT_NAME = "$ProjectName"
`$env:PROJECT_TYPE = "$ProjectType"

# Claude Code CLI settings
`$env:CLAUDE_CLI = if (`$env:CLAUDE_CLI) { `$env:CLAUDE_CLI } else { "claude" }
`$env:CLAUDE_MODEL_DEV = "$ModelDev"
`$env:CLAUDE_MODEL_PLANNING = "$ModelPlanning"

# Default model
`$env:CLAUDE_MODEL = if (`$env:CLAUDE_MODEL) { `$env:CLAUDE_MODEL } else { "$ModelPlanning" }

# Permission mode for automation
`$env:PERMISSION_MODE = if (`$env:PERMISSION_MODE) { `$env:PERMISSION_MODE } else { "dangerouslySkipPermissions" }

# Auto-commit settings
`$env:AUTO_COMMIT = if (`$env:AUTO_COMMIT) { `$env:AUTO_COMMIT } else { "true" }
`$env:AUTO_PR = if (`$env:AUTO_PR) { `$env:AUTO_PR } else { "false" }

# Budget limits (USD)
`$env:MAX_BUDGET_CONTEXT = "3.00"
`$env:MAX_BUDGET_DEV = "15.00"
`$env:MAX_BUDGET_REVIEW = "5.00"

# Cost display settings
`$env:COST_DISPLAY_CURRENCY = "$DisplayCurrency"
`$env:COST_WARNING_PERCENT = "75"
`$env:COST_CRITICAL_PERCENT = "90"
`$env:COST_AUTO_STOP = "true"

# Paths
`$script:AutomationDir = `$PSScriptRoot
`$script:ProjectRoot = (Get-Item "`$script:AutomationDir\..\..").FullName
`$script:ScriptsDir = Join-Path `$script:ProjectRoot "tooling\scripts"
`$script:DocsDir = Join-Path `$script:ProjectRoot "tooling\docs"

# Tool configurations
`$env:CHECKPOINT_THRESHOLDS = "75,85,95"  # Warning, Critical, Emergency
"@

    Set-Content -Path $configPath -Value $configContent
    Write-Host "  [OK] Configuration created" -ForegroundColor Green
}

function New-AgentPersonas {
    param([string]$ProjectRoot)

    Write-Host ">> Creating agent persona definitions..." -ForegroundColor Blue

    $agentsDir = Join-Path $ProjectRoot "tooling\.automation\agents"

    # SM Agent
    $smContent = @"
# Scrum Master Agent

You are an experienced Scrum Master overseeing development workflow.

## Responsibilities
- Story context creation and planning
- Code review and quality assurance
- Story drafting and specification
- Sprint status management

## Approach
- Be thorough but efficient
- Focus on quality and completeness
- Follow Agile best practices
- Ensure acceptance criteria are met

## Communication Style
- Clear and professional
- Action-oriented
- Provide constructive feedback
"@
    Set-Content -Path (Join-Path $agentsDir "sm.md") -Value $smContent

    # DEV Agent
    $devContent = @"
# Developer Agent

You are a senior software developer implementing features.

## Responsibilities
- Implement stories according to specifications
- Write clean, maintainable code
- Create comprehensive tests
- Follow project patterns and conventions

## Approach
- Code first, explain later
- Prioritize working solutions
- Write self-documenting code
- Ensure tests pass before completion

## Communication Style
- Concise and technical
- Focus on implementation details
- Proactive problem-solving
"@
    Set-Content -Path (Join-Path $agentsDir "dev.md") -Value $devContent

    # BA Agent
    $baContent = @"
# Business Analyst Agent

You are a Business Analyst specializing in requirements gathering.

## Responsibilities
- Analyze and document requirements
- Create user stories with INVEST criteria
- Define acceptance criteria
- Identify edge cases and business rules

## Approach
- User-centric thinking
- Detailed documentation
- Clear acceptance criteria
- Consider all scenarios

## Communication Style
- Clear and structured
- Business-focused
- Comprehensive but concise
"@
    Set-Content -Path (Join-Path $agentsDir "ba.md") -Value $baContent

    # Architect Agent
    $architectContent = @"
# Architect Agent

You are a Software Architect designing technical solutions.

## Responsibilities
- Create technical specifications
- Design system architecture
- Define data models and APIs
- Identify technical risks

## Approach
- Think holistically
- Follow architectural patterns
- Consider scalability and maintainability
- Balance pragmatism with quality

## Communication Style
- Technical and precise
- Diagram-driven when helpful
- Consider trade-offs
"@
    Set-Content -Path (Join-Path $agentsDir "architect.md") -Value $architectContent

    Write-Host "  [OK] Agent personas created" -ForegroundColor Green
}

function New-SprintStatus {
    param(
        [string]$ProjectRoot,
        [string]$ProjectName
    )

    Write-Host ">> Creating sprint status tracker..." -ForegroundColor Blue

    $sprintPath = Join-Path $ProjectRoot "tooling\docs\sprint-status.yaml"
    $today = (Get-Date).ToString("yyyy-MM-dd")
    $endDate = (Get-Date).AddDays(14).ToString("yyyy-MM-dd")

    $content = @"
# Sprint Status - $ProjectName
# Updated: $today

sprint:
  number: 1
  start: $today
  end: $endDate

# Story Status Values:
# - backlog: Not yet started
# - drafted: Story specification created
# - ready-for-dev: Context created, ready for implementation
# - in-progress: Currently being worked on
# - review: Implementation complete, awaiting review
# - done: Reviewed and approved

stories:
  # Add your stories here in format:
  # story-key: status
  # Example:
  # 1-1-setup-project: done
  # 1-2-implement-auth: in-progress
"@

    Set-Content -Path $sprintPath -Value $content
    Write-Host "  [OK] Sprint status created" -ForegroundColor Green
}

function New-WorkflowReadme {
    param(
        [string]$ProjectRoot,
        [string]$ProjectName
    )

    Write-Host ">> Creating workflow README..." -ForegroundColor Blue

    $readmePath = Join-Path $ProjectRoot "tooling\README.md"

    $content = @"
# $ProjectName - Development Workflow (Windows)

Automated development workflow powered by Claude Code CLI.

## Quick Start

### Run a Story

``````powershell
cd tooling\scripts
.\run-story.ps1 -StoryKey "1-1"
``````

### Available Commands

``````powershell
# Full pipeline (context + dev + review)
.\run-story.ps1 -StoryKey "1-1"

# Development only
.\run-story.ps1 -StoryKey "1-1" -Develop

# Review only
.\run-story.ps1 -StoryKey "1-1" -Review

# Context creation only
.\run-story.ps1 -StoryKey "1-1" -Context

# Use specific model
.\run-story.ps1 -StoryKey "1-1" -Model opus
``````

### Checkpoint Management

``````powershell
# List checkpoints
python tooling\scripts\context_checkpoint.py --list

# Create manual checkpoint
python tooling\scripts\context_checkpoint.py --checkpoint

# Resume from checkpoint
python tooling\scripts\context_checkpoint.py --resume <checkpoint-id>
``````

### Create New Documentation

``````powershell
.\tooling\scripts\new-doc.ps1 -Type guide -Name "my-guide"
``````

## Directory Structure

``````
tooling\
+-- .automation\
|   +-- agents\          # Agent persona definitions
|   +-- checkpoints\     # Context checkpoints
|   +-- logs\            # Execution logs
|   +-- config.ps1       # Configuration
+-- scripts\
|   +-- lib\             # Script libraries
|   +-- run-story.ps1    # Main automation runner
|   +-- new-doc.ps1      # Documentation generator
+-- docs\
    +-- sprint-status.yaml # Sprint tracking
``````

## Configuration

Edit ``tooling\.automation\config.ps1`` to customize:
- Claude Code models (Opus for dev, Sonnet for planning)
- Budget limits
- Auto-commit settings
- Permission modes

## Agent Personas

The workflow uses multiple agent personas:
- **SM (Scrum Master)**: Planning, context creation, code review
- **DEV (Developer)**: Story implementation
- **BA (Business Analyst)**: Requirements analysis
- **ARCHITECT**: Technical design

## Live Monitoring

The run-story.ps1 script provides live monitoring of:
- Context usage percentage
- Estimated costs
- Agent status
- Elapsed time

Press Ctrl+C to stop monitoring (the task continues in background).

## Next Steps

1. Add your stories to ``tooling\docs\sprint-status.yaml``
2. Create story specifications in ``tooling\docs\``
3. Run your first story: ``.\run-story.ps1 -StoryKey "story-key"``
"@

    Set-Content -Path $readmePath -Value $content
    Write-Host "  [OK] README created" -ForegroundColor Green
}

#endregion

#region Main

function Main {
    Write-Banner

    Write-Host "This wizard will set up automated development workflow for your project." -ForegroundColor Blue
    Write-Host "You'll be guided through the configuration process." -ForegroundColor Blue
    Write-Host ""

    if (-not (Read-YesNo "Continue with setup?")) {
        Write-Host "Setup cancelled." -ForegroundColor Yellow
        return
    }

    # STEP 1: Project Information
    Write-Step -StepNum 1 -StepTitle "Project Information"

    $projectRoot = Read-PromptInput -Prompt "Enter project root directory:" -Default (Get-Location).Path
    $projectName = Read-PromptInput -Prompt "Enter project name:" -Default (Split-Path $projectRoot -Leaf)

    Push-Location $projectRoot
    $projectType = Get-ProjectType

    if (-not (Read-YesNo "Is this correct? Type: $projectType")) {
        $projectType = Read-PromptInput -Prompt "Enter project type manually:" -Default $projectType
    }
    Pop-Location

    # STEP 2: Model Configuration
    Write-Step -StepNum 2 -StepTitle "Claude Model Configuration"

    Write-Host "For optimal cost/quality balance:" -ForegroundColor Blue
    Write-Host "  - Use Opus for code development and review (higher quality)" -ForegroundColor Blue
    Write-Host "  - Use Sonnet for planning and context creation (cost-effective)" -ForegroundColor Blue
    Write-Host ""

    $modelDev = Read-PromptInput -Prompt "Model for development/review:" -Default "opus"
    $modelPlanning = Read-PromptInput -Prompt "Model for planning/context:" -Default "sonnet"

    # Currency Selection
    Write-Host ""
    Write-Host "Select your preferred currency for cost display:" -ForegroundColor Blue
    Write-Host "  1. USD - US Dollar ($)" -ForegroundColor White
    Write-Host "  2. EUR - Euro (€)" -ForegroundColor White
    Write-Host "  3. GBP - British Pound (£)" -ForegroundColor White
    Write-Host "  4. BRL - Brazilian Real (R$)" -ForegroundColor White
    Write-Host "  5. CAD - Canadian Dollar (C$)" -ForegroundColor White
    Write-Host "  6. AUD - Australian Dollar (A$)" -ForegroundColor White
    Write-Host ""

    $currencyChoice = Read-PromptInput -Prompt "Enter choice (1-6):" -Default "1"

    $currencyMap = @{
        "1" = "USD"
        "2" = "EUR"
        "3" = "GBP"
        "4" = "BRL"
        "5" = "CAD"
        "6" = "AUD"
    }

    $displayCurrency = $currencyMap[$currencyChoice]
    if (-not $displayCurrency) { $displayCurrency = "USD" }

    Write-Host "  Selected: $displayCurrency" -ForegroundColor Green

    # STEP 3: Directory Structure
    Write-Step -StepNum 3 -StepTitle "Directory Structure"

    New-DirectoryStructure -ProjectRoot $projectRoot

    # STEP 4: Copy Scripts
    Write-Step -StepNum 4 -StepTitle "Core Scripts"

    Copy-CoreScripts -ProjectRoot $projectRoot -SourceDir $script:ScriptDir

    # STEP 5: Configuration
    Write-Step -StepNum 5 -StepTitle "Configuration Files"

    New-ConfigFile -ProjectRoot $projectRoot -ProjectName $projectName -ProjectType $projectType -ModelDev $modelDev -ModelPlanning $modelPlanning -DisplayCurrency $displayCurrency
    New-AgentPersonas -ProjectRoot $projectRoot
    New-SprintStatus -ProjectRoot $projectRoot -ProjectName $projectName

    # STEP 6: Checkpoint Service
    Write-Step -StepNum 6 -StepTitle "Checkpoint Service (Optional)"

    Write-Host "The checkpoint service monitors Claude sessions and auto-saves context." -ForegroundColor Blue
    Write-Host "This prevents losing progress when context windows fill up." -ForegroundColor Blue
    Write-Host ""

    if (Read-YesNo "Install checkpoint service as Windows Scheduled Task?") {
        $setupScript = Join-Path $projectRoot "tooling\scripts\setup-checkpoint-service.ps1"
        if (Test-Path $setupScript) {
            & $setupScript -Action install
        }
        Write-Host "  [OK] Checkpoint service installed" -ForegroundColor Green
    }
    else {
        Write-Host "  [i] Skipped checkpoint service installation" -ForegroundColor Yellow
        Write-Host "  You can install later with: .\tooling\scripts\setup-checkpoint-service.ps1 -Action install" -ForegroundColor Blue
    }

    # STEP 7: Documentation
    Write-Step -StepNum 7 -StepTitle "Documentation"

    New-WorkflowReadme -ProjectRoot $projectRoot -ProjectName $projectName

    # STEP 8: Finalize
    Write-Step -StepNum 8 -StepTitle "Setup Complete!"

    Write-Host "[OK] Workflow initialization complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host ("{0}" -f ("=" * 65)) -ForegroundColor Cyan
    Write-Host "  NEXT STEPS" -ForegroundColor Cyan
    Write-Host ("{0}" -f ("=" * 65)) -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Review configuration:" -ForegroundColor Yellow
    Write-Host "   $projectRoot\tooling\.automation\config.ps1" -ForegroundColor Blue
    Write-Host ""
    Write-Host "2. Add your first story:" -ForegroundColor Yellow
    Write-Host "   Edit: $projectRoot\tooling\docs\sprint-status.yaml" -ForegroundColor Blue
    Write-Host "   Create: $projectRoot\tooling\docs\1-1-your-story.md" -ForegroundColor Blue
    Write-Host ""
    Write-Host "3. Run your first story:" -ForegroundColor Yellow
    Write-Host "   cd $projectRoot\tooling\scripts" -ForegroundColor Blue
    Write-Host "   .\run-story.ps1 -StoryKey '1-1'" -ForegroundColor Blue
    Write-Host ""
    Write-Host "4. Read the workflow guide:" -ForegroundColor Yellow
    Write-Host "   $projectRoot\tooling\README.md" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Happy coding!" -ForegroundColor Green
    Write-Host ""
}

#endregion

# Run main
Main
