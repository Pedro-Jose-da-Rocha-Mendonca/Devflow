#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const targetDir = path.join(process.cwd(), 'Devflow');
const sourceDir = path.join(__dirname, '..');

console.log('\nDevflow Project Initializer\n');

if (fs.existsSync(targetDir)) {
  console.error(`Error: "Devflow" directory already exists`);
  console.error('Remove it or run from a different location.\n');
  process.exit(1);
}

console.log(`Creating: ${targetDir}\n`);
fs.mkdirSync(targetDir, { recursive: true });

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
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

const items = [
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

console.log('Copying files...');
for (const item of items) {
  const src = path.join(sourceDir, item.name);
  const dest = path.join(targetDir, item.name);

  if (fs.existsSync(src)) {
    console.log(`  ${item.name}`);
    if (item.type === 'dir') {
      copyDir(src, dest);
    } else {
      fs.mkdirSync(path.dirname(dest), { recursive: true });
      fs.copyFileSync(src, dest);
    }
  }
}

console.log('\nInitializing git...');
try {
  process.chdir(targetDir);
  execSync('git init', { stdio: 'ignore' });
  console.log('Done\n');
} catch (error) {
  console.log('Skipped\n');
}

console.log('Running setup wizard...\n');
try {
  const initScript = path.join(targetDir, 'bin', 'devflow-init.js');
  if (fs.existsSync(initScript)) {
    execSync(`node "${initScript}"`, { stdio: 'inherit' });
  }
} catch (error) {
  console.log('\nSetup wizard failed. Run manually: cd Devflow && npx devflow-init\n');
}

console.log('\nProject created successfully!');
console.log('\nNext steps:');
console.log('  cd Devflow');
console.log('  Use /story <key> in Claude Code\n');
console.log('Documentation: https://github.com/Pedro-Jose-da-Rocha-Mendonca/Devflow\n');
