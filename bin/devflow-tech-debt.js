#!/usr/bin/env node

const path = require('path');
const { execPythonScript, getScriptsDir } = require('../lib/exec-python');

const scriptPath = path.join(getScriptsDir(), 'tech-debt-tracker.py');
const args = process.argv.slice(2);

const exitCode = execPythonScript(scriptPath, args);
process.exit(exitCode);
