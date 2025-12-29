/**
 * Shared Constants for Devflow npm Package
 */

module.exports = {
  /**
   * Minimum required Python version
   */
  REQUIRED_PYTHON_VERSION: '3.9.0',

  /**
   * Mapping of CLI command names to Python script filenames
   */
  SCRIPT_MAP: {
    'devflow-cost': 'cost_dashboard.py',
    'devflow-validate': 'validate_setup.py',
    'devflow-story': 'run-story.py',
    'devflow-checkpoint': 'context_checkpoint.py',
    'devflow-memory': 'memory_summarize.py',
    'devflow-collab': 'run-collab.py',
    'devflow-create-persona': 'create-persona.py',
    'devflow-personalize': 'personalize_agent.py',
    'devflow-validate-overrides': 'validate-overrides.py',
    'devflow-new-doc': 'new-doc.py',
    'devflow-tech-debt': 'tech-debt-tracker.py',
    'devflow-setup-checkpoint': 'setup-checkpoint-service.py',
    'devflow-version': 'update_version.py'
  }
};
