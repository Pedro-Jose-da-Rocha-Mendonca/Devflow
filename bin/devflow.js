#!/usr/bin/env node

const { spawn } = require('child_process');

const commands = {
  'install': 'Install Devflow into your project',
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

function showHelp() {
  console.log('Devflow - Development workflow automation with Claude Code\n');
  console.log('Usage: devflow <command> [options]\n');
  console.log('Available commands:\n');

  Object.entries(commands).forEach(([cmd, desc]) => {
    console.log(`  ${cmd.padEnd(20)} ${desc}`);
  });

  console.log('\nRun "devflow <command> --help" for more information on a command.');
  console.log('\nGet started:');
  console.log('  devflow install    Install into existing project');
  console.log('  /init              Initialize configuration (in Claude Code)');
}

const args = process.argv.slice(2);

if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
  showHelp();
  process.exit(0);
}

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
