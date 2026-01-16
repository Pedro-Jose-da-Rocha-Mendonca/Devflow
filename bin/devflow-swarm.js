#!/usr/bin/env node

const path = require('path');
const { execPythonScript, getScriptsDir } = require('../lib/exec-python');

const scriptPath = path.join(getScriptsDir(), 'run-collab.py');
const args = process.argv.slice(2);

// Prepend --swarm flag to run in swarm mode
const exitCode = execPythonScript(scriptPath, ['--swarm', ...args]);
process.exit(exitCode);
