#!/usr/bin/env node

const path = require('path');
const { execPythonScript, getScriptsDir } = require('../lib/exec-python');

const scriptPath = path.join(getScriptsDir(), 'memory_summarize.py');
const args = process.argv.slice(2);

const exitCode = execPythonScript(scriptPath, args);
process.exit(exitCode);
