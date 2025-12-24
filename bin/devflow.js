#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const commands = {
  'init': 'Initialize Devflow in your project',
  'story': 'Run full story pipeline (context + dev + review)',
  'collab': 'Run collaborative story with mode selection',
  'checkpoint': 'Create or restore context checkpoints',
  'memory': 'View or query shared agent memory',
  'cost': 'View cost dashboard and spending analytics',
  'validate': 'Validate project configuration',
  'create-persona': 'Create a new agent persona',
  'personalize': 'Personalize agent behavior with guided wizard',
  'validate-overrides': 'Validate override configurations',
  'new-doc': 'Create new documentation',
  'tech-debt': 'Analyze and track technical debt',
  'setup-checkpoint': 'Setup checkpoint system',
  'version': 'Show version information'
};

/**
 * Check if we're in a Devflow project
 */
function isInDevflowProject() {
  const indicators = [
    'tooling/.automation',
    'tooling/scripts',
    '.claude'
  ];

  return indicators.some(indicator => fs.existsSync(path.join(process.cwd(), indicator)));
}

/**
 * Show help message
 */
function showHelp() {
  console.log('Devflow - Development workflow automation with Claude Code\n');
  console.log('Usage: devflow <command> [options]\n');
  console.log('Available commands:\n');

  Object.entries(commands).forEach(([cmd, desc]) => {
    console.log(`  ${cmd.padEnd(20)} ${desc}`);
  });

  console.log('\nRun "devflow <command> --help" for more information on a command.');
  console.log('\nGet started: devflow init');
}

const args = process.argv.slice(2);

// If no arguments or --help, check if we're in a project
if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
  if (!isInDevflowProject()) {
    // Not in a project - run scaffolder
    console.log('No Devflow project detected. Running project scaffolder...\n');
    const createScript = require.resolve('./create-devflow.js');
    const child = spawn('node', [createScript], { stdio: 'inherit' });
    child.on('exit', (code) => process.exit(code || 0));
  } else {
    // In a project - show help
    showHelp();
    process.exit(0);
  }
} else {
  // Command provided
  const command = args[0];

  if (commands[command]) {
    const binPath = require.resolve(`./devflow-${command}.js`);
    const child = spawn('node', [binPath, ...args.slice(1)], { stdio: 'inherit' });
    child.on('exit', (code) => process.exit(code || 0));
  } else {
    console.error(`Unknown command: ${command}`);
    console.error('Run "devflow --help" to see available commands.');
    process.exit(1);
  }
}
