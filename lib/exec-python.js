/**
 * Python Script Execution Wrapper for Devflow
 *
 * Provides cross-platform Python script execution with proper
 * path resolution and stdio handling.
 */

const { spawnSync } = require('child_process');
const path = require('path');

/**
 * Detect available Python command
 * @returns {string} Python command (python3, python, or py)
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

  // Fallback to python3 (will error with helpful message)
  return 'python3';
}

/**
 * Get the scripts directory path
 * @returns {string} Absolute path to tooling/scripts directory
 */
function getScriptsDir() {
  // __dirname is lib/, so go up one level to package root
  return path.join(__dirname, '..', 'tooling', 'scripts');
}

/**
 * Execute a Python script with arguments
 * @param {string} scriptPath - Path to Python script (relative to scripts dir or absolute)
 * @param {string[]} args - Arguments to pass to the script
 * @returns {number} Exit code from the Python script
 */
function execPythonScript(scriptPath, args = []) {
  const pythonCmd = getPythonCommand();

  // If scriptPath is not absolute, resolve it relative to scripts dir
  const fullPath = path.isAbsolute(scriptPath)
    ? scriptPath
    : path.join(getScriptsDir(), scriptPath);

  const spawnOptions = {
    stdio: 'inherit', // Pass through stdin, stdout, stderr
    shell: process.platform === 'win32', // Windows needs shell for proper execution
    windowsHide: true // Prevent console window flash on Windows
  };

  const result = spawnSync(pythonCmd, [fullPath, ...args], spawnOptions);

  // Handle errors
  if (result.error) {
    console.error(`Error executing Python script: ${result.error.message}`);
    return 1;
  }

  return result.status || 0;
}

module.exports = {
  execPythonScript,
  getPythonCommand,
  getScriptsDir
};
