#!/usr/bin/env node

/**
 * create-devflow - NPM initializer for Devflow
 *
 * Creates a new "Devflow" directory with all necessary files
 * Usage: npm create @pjmendonca/devflow
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Get the current working directory where the user ran the command
const targetDir = path.join(process.cwd(), 'Devflow');

// Get the source directory (where this package is installed)
const sourceDir = path.join(__dirname, '..');

console.log('\n========================================');
console.log('  Devflow Project Initializer');
console.log('========================================\n');

// Check if Devflow directory already exists
if (fs.existsSync(targetDir)) {
  console.error(`Error: Directory "Devflow" already exists in ${process.cwd()}`);
  console.error('Please remove it or run this command from a different location.\n');
  process.exit(1);
}

console.log(`Creating Devflow directory at: ${targetDir}`);
fs.mkdirSync(targetDir, { recursive: true });

/**
 * Recursively copy directory
 */
function copyDir(src, dest) {
  // Create destination directory
  fs.mkdirSync(dest, { recursive: true });

  // Read source directory
  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

/**
 * Copy file
 */
function copyFile(src, dest) {
  const destDir = path.dirname(dest);
  fs.mkdirSync(destDir, { recursive: true });
  fs.copyFileSync(src, dest);
}

// Files and directories to copy
const itemsToCopy = [
  { type: 'dir', name: 'tooling' },
  { type: 'dir', name: 'bin' },
  { type: 'dir', name: 'lib' },
  { type: 'dir', name: '.claude' },
  { type: 'file', name: 'LICENSE' },
  { type: 'file', name: 'README.md' },
  { type: 'file', name: 'CHANGELOG.md' },
  { type: 'file', name: 'package.json' },
  { type: 'file', name: '.gitignore' }
];

console.log('\nCopying project files...');
for (const item of itemsToCopy) {
  const src = path.join(sourceDir, item.name);
  const dest = path.join(targetDir, item.name);

  if (!fs.existsSync(src)) {
    console.log(`  Skipping ${item.name} (not found)`);
    continue;
  }

  try {
    if (item.type === 'dir') {
      console.log(`  Copying ${item.name}/ ...`);
      copyDir(src, dest);
    } else {
      console.log(`  Copying ${item.name} ...`);
      copyFile(src, dest);
    }
  } catch (error) {
    console.error(`  Error copying ${item.name}: ${error.message}`);
  }
}

console.log('\n[OK] Files copied successfully!\n');

// Initialize git repo if not already in one
console.log('Initializing git repository...');
try {
  process.chdir(targetDir);
  execSync('git init', { stdio: 'ignore' });
  console.log('[OK] Git repository initialized\n');
} catch (error) {
  console.log('[INFO] Git not available or already initialized\n');
}

// Run the setup wizard
console.log('========================================');
console.log('  Running Setup Wizard');
console.log('========================================\n');

try {
  const initScript = path.join(targetDir, 'bin', 'devflow-init.js');

  if (fs.existsSync(initScript)) {
    console.log('Starting interactive setup wizard...\n');
    execSync(`node "${initScript}"`, { stdio: 'inherit' });
  } else {
    console.log('[WARNING] Setup wizard not found. You may need to run it manually:');
    console.log('  cd Devflow');
    console.log('  npx devflow-init\n');
  }
} catch (error) {
  console.log('[WARNING] Setup wizard encountered an issue.');
  console.log('You can run it manually later with: npx devflow-init\n');
}

console.log('\n========================================');
console.log('  Setup Complete!');
console.log('========================================\n');
console.log('Next steps:');
console.log('  1. cd Devflow');
console.log('  2. Review the README.md for usage instructions');
console.log('  3. Start using Devflow with: /story <key>\n');
console.log('Documentation: https://github.com/Pedro-Jose-da-Rocha-Mendonca/Devflow\n');
