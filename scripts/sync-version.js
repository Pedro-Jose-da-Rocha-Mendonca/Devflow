#!/usr/bin/env node

/**
 * Version Synchronization Script
 *
 * Syncs version from CHANGELOG.md to package.json
 * Runs automatically before npm publish via prepublishOnly hook
 */

const fs = require('fs');
const path = require('path');

// Paths
const rootDir = path.join(__dirname, '..');
const changelogPath = path.join(rootDir, 'CHANGELOG.md');
const packageJsonPath = path.join(rootDir, 'package.json');

/**
 * Extract version from CHANGELOG.md
 * @returns {string|null} Version string or null if not found
 */
function extractVersionFromChangelog() {
  try {
    const changelog = fs.readFileSync(changelogPath, 'utf-8');

    // Match first version entry: ## [X.Y.Z]
    const match = changelog.match(/^##\s+\[(\d+\.\d+\.\d+)\]/m);

    if (match) {
      return match[1];
    }

    console.error('Could not find version in CHANGELOG.md');
    console.error('Expected format: ## [X.Y.Z] - YYYY-MM-DD');
    return null;
  } catch (error) {
    console.error(`Error reading CHANGELOG.md: ${error.message}`);
    return null;
  }
}

/**
 * Update version in package.json
 * @param {string} version - New version to set
 * @returns {boolean} Success
 */
function updatePackageJson(version) {
  try {
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));
    const oldVersion = packageJson.version;

    if (oldVersion === version) {
      console.log(`package.json already at version ${version}`);
      return true;
    }

    packageJson.version = version;

    // Write with proper formatting (2 spaces, newline at end)
    fs.writeFileSync(
      packageJsonPath,
      JSON.stringify(packageJson, null, 2) + '\n',
      'utf-8'
    );

    console.log(`[OK] Updated package.json from ${oldVersion} to ${version}`);
    return true;
  } catch (error) {
    console.error(`Error updating package.json: ${error.message}`);
    return false;
  }
}

/**
 * Main sync function
 */
function syncVersion() {
  console.log('Syncing version from CHANGELOG.md to package.json...\n');

  const version = extractVersionFromChangelog();

  if (!version) {
    process.exit(1);
  }

  console.log(`CHANGELOG version: ${version}`);

  const success = updatePackageJson(version);

  if (!success) {
    process.exit(1);
  }

  console.log('\n[OK] Version sync complete!');
  process.exit(0);
}

// Run sync
syncVersion();
