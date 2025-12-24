#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const targetDir = process.cwd();
const sourceDir = path.join(__dirname, '..');

console.log('\nDevflow Installer\n');

if (fs.existsSync(path.join(targetDir, '.claude', 'commands', 'story.md'))) {
  console.log('Devflow is already installed. Running validation...\n');
  try {
    execSync(`node "${path.join(__dirname, 'devflow-validate.js')}"`, { stdio: 'inherit' });
  } catch (error) {
    process.exit(1);
  }
  process.exit(0);
}

function copyDir(src, dest, exclude = []) {
  fs.mkdirSync(dest, { recursive: true });
  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (exclude.some(pattern => entry.name.match(pattern))) continue;

    if (entry.isDirectory()) {
      copyDir(srcPath, destPath, exclude);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

const items = [
  { name: '.claude', exclude: [] },
  { name: 'tooling', exclude: [/^\.automation\/logs/, /^\.automation\/costs/, /^\.automation\/checkpoints/] }
];

console.log(`Installing into: ${targetDir}\n`);

for (const item of items) {
  const src = path.join(sourceDir, item.name);
  const dest = path.join(targetDir, item.name);

  if (fs.existsSync(src)) {
    console.log(`Copying ${item.name}/`);
    copyDir(src, dest, item.exclude);
  }
}

const configs = ['CLAUDE.md', '.gitignore'];
for (const file of configs) {
  const src = path.join(sourceDir, file);
  const dest = path.join(targetDir, file);
  if (fs.existsSync(src) && !fs.existsSync(dest)) {
    console.log(`Copying ${file}`);
    fs.copyFileSync(src, dest);
  }
}

console.log('\nInstallation complete!\n');

const args = process.argv.slice(2);
if (!args.includes('--skip-setup') && !args.includes('-s')) {
  console.log('Running setup wizard...\n');
  try {
    execSync(`node "${path.join(__dirname, 'devflow-init.js')}"`, { stdio: 'inherit', cwd: targetDir });
  } catch (error) {
    console.log('\nSetup wizard failed. Run manually: npx @pjmendonca/devflow init\n');
  }
}

console.log('\nDevflow installed successfully!');
console.log('\nNext steps:');
console.log('  1. Open Claude Code in this directory');
console.log('  2. Use /story <key> or npx @pjmendonca/devflow story <key>');
console.log('\nDocumentation: https://github.com/Pedro-Jose-da-Rocha-Mendonca/Devflow\n');
