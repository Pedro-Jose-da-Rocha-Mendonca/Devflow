#!/usr/bin/env node

/**
 * Python Version Checker for Devflow npm Package
 *
 * Verifies that Python 3.9+ is installed and accessible.
 * Runs during npm postinstall to ensure requirements are met.
 */

const { spawnSync } = require('child_process');
const REQUIRED_VERSION = '3.9.0';

// ANSI color codes
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  bold: '\x1b[1m'
};

function colorize(text, color) {
  return `${colors[color]}${text}${colors.reset}`;
}

/**
 * Detect available Python command
 * @returns {string|null} Python command or null if not found
 */
function getPythonCommand() {
  const commands = ['python3', 'python', 'py'];

  for (const cmd of commands) {
    const result = spawnSync(cmd, ['--version'], {
      shell: true,
      stdio: 'pipe',
      windowsHide: true
    });

    if (result.status === 0) {
      return cmd;
    }
  }

  return null;
}

/**
 * Parse version string to array of numbers
 * @param {string} versionString - e.g., "Python 3.11.5"
 * @returns {number[]|null} - e.g., [3, 11, 5] or null
 */
function parseVersion(versionString) {
  const match = versionString.match(/(\d+)\.(\d+)\.(\d+)/);
  if (!match) return null;
  return [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])];
}

/**
 * Compare two version arrays
 * @param {number[]} version - Current version
 * @param {number[]} required - Required version
 * @returns {boolean} - true if version >= required
 */
function isVersionSufficient(version, required) {
  for (let i = 0; i < 3; i++) {
    if (version[i] > required[i]) return true;
    if (version[i] < required[i]) return false;
  }
  return true;
}

/**
 * Get platform-specific installation instructions
 * @returns {string} Installation instructions
 */
function getInstallInstructions() {
  const platform = process.platform;

  if (platform === 'win32') {
    return `
${colorize('Windows Installation:', 'bold')}
  1. Download Python from https://www.python.org/downloads/
  2. Run the installer and check "Add Python to PATH"
  3. Verify: open Command Prompt and run: ${colorize('python --version', 'blue')}

  Or use Chocolatey:
    ${colorize('choco install python', 'blue')}
`;
  } else if (platform === 'darwin') {
    return `
${colorize('macOS Installation:', 'bold')}
  Using Homebrew (recommended):
    ${colorize('brew install python@3.11', 'blue')}

  Or download from:
    https://www.python.org/downloads/macos/
`;
  } else {
    return `
${colorize('Linux Installation:', 'bold')}
  Ubuntu/Debian:
    ${colorize('sudo apt update && sudo apt install python3', 'blue')}

  Fedora:
    ${colorize('sudo dnf install python3', 'blue')}

  Arch:
    ${colorize('sudo pacman -S python', 'blue')}
`;
  }
}

/**
 * Main check function
 */
function checkPython() {
  const silent = process.argv.includes('--silent');

  // Find Python command
  const pythonCmd = getPythonCommand();

  if (!pythonCmd) {
    if (!silent) {
      console.error(colorize('\n✗ Python not found', 'red'));
      console.error('\nDevflow requires Python 3.9 or higher.');
      console.error(getInstallInstructions());
      console.error(colorize('After installation, run:', 'yellow'));
      console.error(colorize('  npm install -g devflow', 'blue'));
      console.error('');
    }
    process.exit(1);
  }

  // Get Python version
  const result = spawnSync(pythonCmd, ['--version'], {
    shell: true,
    stdio: 'pipe',
    encoding: 'utf-8',
    windowsHide: true
  });

  const versionOutput = (result.stdout || result.stderr || '').trim();
  const currentVersion = parseVersion(versionOutput);
  const requiredVersion = parseVersion(REQUIRED_VERSION);

  if (!currentVersion) {
    if (!silent) {
      console.error(colorize('\n✗ Could not parse Python version', 'red'));
      console.error(`Version output: ${versionOutput}`);
      console.error('');
    }
    process.exit(1);
  }

  // Check if version is sufficient
  if (!isVersionSufficient(currentVersion, requiredVersion)) {
    if (!silent) {
      console.error(colorize(`\n✗ Python ${currentVersion.join('.')} found, but ${REQUIRED_VERSION}+ required`, 'red'));
      console.error(getInstallInstructions());
      console.error('');
    }
    process.exit(1);
  }

  // Success!
  if (!silent) {
    console.log(colorize(`\n✓ Python ${currentVersion.join('.')} found (${pythonCmd})`, 'green'));
    console.log(colorize('✓ Devflow is ready to use!\n', 'green'));
    console.log(`Try: ${colorize('devflow-validate', 'blue')}\n`);
  }

  process.exit(0);
}

// Run check
checkPython();
