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

console.log('Project created successfully!');
console.log('\nNext steps:');
console.log('  1. cd Devflow');
console.log('  2. Open Claude Code');
console.log('  3. Run /init for AI-guided project setup');
console.log('  4. Use /story <key> to start development');
console.log('\nDocumentation: https://github.com/Pedro-Jose-da-Rocha-Mendonca/Devflow\n');
