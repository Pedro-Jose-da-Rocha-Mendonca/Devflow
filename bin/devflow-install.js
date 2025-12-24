#!/usr/bin/env node

/**
 * devflow-install - Install Devflow into the current project
 *
 * Copies .claude/ and tooling/ directories into the user's project
 * This enables Claude Code to automatically detect slash commands
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const targetDir = process.cwd();
const sourceDir = path.join(__dirname, '..');

console.log('\n========================================');
console.log('  Devflow Installer');
console.log('========================================\n');

// Check if we're already in a Devflow directory
const isAlreadyDevflow = fs.existsSync(path.join(targetDir, '.claude', 'commands', 'story.md'));
if (isAlreadyDevflow) {
  console.log('[INFO] Devflow is already installed in this directory.');
  console.log('[INFO] Running validation instead...\n');
  try {
    const validateScript = path.join(__dirname, 'devflow-validate.js');
    execSync(`node "${validateScript}"`, { stdio: 'inherit' });
  } catch (error) {
    process.exit(1);
  }
  process.exit(0);
}

/**
 * Recursively copy directory
 */
function copyDir(src, dest, options = {}) {
  const { exclude = [] } = options;

  // Create destination directory
  fs.mkdirSync(dest, { recursive: true });

  // Read source directory
  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    // Skip excluded files/directories
    if (exclude.some(pattern => entry.name.match(pattern))) {
      continue;
    }

    if (entry.isDirectory()) {
      copyDir(srcPath, destPath, options);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

// Directories to copy
const itemsToCopy = [
  {
    type: 'dir',
    name: '.claude',
    desc: 'Claude Code commands and skills',
    exclude: []
  },
  {
    type: 'dir',
    name: 'tooling',
    desc: 'Automation scripts and agents',
    exclude: [/^\.automation\/logs/, /^\.automation\/costs/, /^\.automation\/checkpoints/]
  }
];

console.log('Installing Devflow into:', targetDir);
console.log('\nCopying essential files...\n');

for (const item of itemsToCopy) {
  const src = path.join(sourceDir, item.name);
  const dest = path.join(targetDir, item.name);

  if (!fs.existsSync(src)) {
    console.log(`  [SKIP] ${item.name}/ (not found in package)`);
    continue;
  }

  try {
    console.log(`  [COPY] ${item.name}/ - ${item.desc}`);
    copyDir(src, dest, { exclude: item.exclude });
  } catch (error) {
    console.error(`  [ERROR] Failed to copy ${item.name}: ${error.message}`);
    process.exit(1);
  }
}

// Copy essential config files if they don't exist
const configFiles = [
  { src: 'CLAUDE.md', desc: 'Project instructions for Claude' },
  { src: '.gitignore', desc: 'Git ignore patterns' }
];

console.log('\nCopying configuration files...\n');
for (const file of configFiles) {
  const src = path.join(sourceDir, file.src);
  const dest = path.join(targetDir, file.src);

  if (!fs.existsSync(src)) {
    console.log(`  [SKIP] ${file.src} (not found)`);
    continue;
  }

  if (fs.existsSync(dest)) {
    console.log(`  [SKIP] ${file.src} (already exists)`);
    continue;
  }

  try {
    console.log(`  [COPY] ${file.src} - ${file.desc}`);
    fs.copyFileSync(src, dest);
  } catch (error) {
    console.error(`  [ERROR] Failed to copy ${file.src}: ${error.message}`);
  }
}

console.log('\n[OK] Installation complete!\n');

// Check if user wants to run the setup wizard
const args = process.argv.slice(2);
const skipSetup = args.includes('--skip-setup') || args.includes('-s');

if (!skipSetup) {
  console.log('========================================');
  console.log('  Running Setup Wizard');
  console.log('========================================\n');

  try {
    const initScript = path.join(__dirname, 'devflow-init.js');
    console.log('Starting interactive setup wizard...\n');
    execSync(`node "${initScript}"`, { stdio: 'inherit', cwd: targetDir });
  } catch (error) {
    console.log('\n[WARNING] Setup wizard encountered an issue.');
    console.log('You can run it manually later with: npx @pjmendonca/devflow init\n');
  }
}

console.log('\n========================================');
console.log('  Installation Complete!');
console.log('========================================\n');
console.log('Devflow is now integrated with your project.\n');
console.log('Next steps:');
console.log('  1. Open Claude Code in this directory');
console.log('  2. Use slash commands like /story <key>');
console.log('  3. Or run directly: npx @pjmendonca/devflow story <key>\n');
console.log('Available commands:');
console.log('  /story <key>     - Full development pipeline');
console.log('  /swarm <key>     - Multi-agent collaboration');
console.log('  /pair <key>      - Pair programming mode');
console.log('  /costs           - View cost dashboard');
console.log('  /memory <key>    - Query shared memory\n');
console.log('Documentation: https://github.com/Pedro-Jose-da-Rocha-Mendonca/Devflow\n');
