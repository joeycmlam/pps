#!/usr/bin/env python3
"""
AI Workflow - Orchestrated Requirements Analysis & System Design

Uses Lead Orchestrator to manage flexible workflow execution.
"""

import os
import sys

# Add aiteam to Python path
aiteam_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'aiteam')
sys.path.insert(0, aiteam_path)

from agents.lead_orchestrator import LeadOrchestrator
from agents.ba_agent import BAAgent
from agents.architect_agent import ArchitectAgent
from dotenv import load_dotenv

def create_ba_handler(llm_config, jira_config, requirements_file):
    """Handler for BA Agent step"""
    def handler(context):
        print("📋 Running BA Agent...")
        ba = BAAgent(llm_config, jira_config)
        req_data = ba.read_requirement_file(requirements_file)
        
        if 'error' in req_data:
            return {'status': 'error', 'message': req_data['error']}
        
        result = ba.analyze_requirements(req_data, output_dir='requirements/analysis')
        return {
            'status': 'success',
            'user_stories': len(result.get('user_stories', [])),
            'assumptions': len(result.get('assumptions', []))
        }
    return handler

def create_architect_handler(llm_config, codebase_path):
    """Handler for Architect Agent step"""
    def handler(context):
        print("🏗️  Running Architect Agent...")
        architect = ArchitectAgent(llm_config)
        
        if os.path.exists(codebase_path):
            analysis = architect.analyze_codebase(codebase_path)
        else:
            print(f"   ℹ️  Codebase '{codebase_path}' not found - designing new system")
            analysis = {'total_files': 0, 'languages': {}, 'complexity': 'new'}
        
        patterns = architect.recommend_patterns(analysis)
        return {
            'status': 'success',
            'patterns_count': len(patterns),
            'patterns': patterns
        }
    return handler

def main(requirements_file='requirements/user_requirement.md', 
         codebase_path='src',
         steps=None,
         step_by_step=False):
    """Orchestrated workflow with flexible step selection
    
    Args:
        requirements_file: Path to requirements file
        codebase_path: Path to codebase for analysis
        steps: List of steps to run (e.g., ['ba'] or ['ba', 'architect'])
               If None, runs ['ba', 'architect']
        step_by_step: If True, pauses between steps for review
    """
    
    # Load config from aiteam
    load_dotenv(os.path.join(aiteam_path, '.env'), override=True)
    
    llm_config = {
        'provider': os.getenv('LLM_PROVIDER', 'github_copilot_cli'),
        'model': os.getenv('GITHUB_MODEL', 'gpt-4o')
    }
    
    jira_config = {
        'server': os.getenv('JIRA_SERVER', 'https://example.atlassian.net'),
        'user': os.getenv('JIRA_USER', 'user@example.com'),
        'token': os.getenv('JIRA_API_TOKEN', 'token')
    }
    
    # Default to BA + Architect if no steps specified
    if steps is None:
        steps = ['ba', 'architect']
    
    print(f"🚀 AI Workflow: {' → '.join([s.upper() for s in steps])}\n")
    
    # Initialize orchestrator
    orchestrator = LeadOrchestrator(llm_config, jira_config)
    
    # Register step handlers
    if 'ba' in steps:
        orchestrator.register_step_handler('ba', create_ba_handler(llm_config, jira_config, requirements_file))
    
    if 'architect' in steps:
        orchestrator.register_step_handler('architect', create_architect_handler(llm_config, codebase_path))
    
    # Create and execute workflow
    workflow = orchestrator.create_workflow(
        steps=steps,
        context={
            'requirements_file': requirements_file,
            'codebase_path': codebase_path
        }
    )
    
    result = orchestrator.execute_workflow(workflow, pause_between_steps=step_by_step)
    
    # Display summary
    print(f"\n{'=' * 60}")
    print("📊 WORKFLOW SUMMARY")
    print("=" * 60)
    print(f"Status: {result['status']}")
    print(f"\nSteps Executed:")
    
    for stage in result['stages']:
        status_emoji = {
            'completed': '✅',
            'failed': '❌',
            'skipped': '⚠️'
        }.get(stage['status'], '❓')
        
        print(f"  {status_emoji} {stage['name']}: {stage['status']}")
        
        if stage.get('result'):
            for key, value in stage['result'].items():
                if key != 'status' and key != 'patterns':
                    print(f"     • {key}: {value}")
    
    if 'ba' in steps:
        print(f"\n📁 Requirements Analysis: requirements/analysis/")
    
    if 'architect' in steps:
        print(f"📁 Architecture Design: requirements/analysis/architecture_design.md")
    
    return 0 if result['status'] == 'completed' else 1

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='AI-powered workflow with flexible step execution',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run both BA and Architect (default)
  python3 ai_workflow_orchestrated.py requirements/user_requirement.md
  
  # Run only BA Agent for review
  python3 ai_workflow_orchestrated.py requirements/user_requirement.md --steps ba
  
  # Run full pipeline with pauses
  python3 ai_workflow_orchestrated.py requirements/user_requirement.md --steps ba architect --step-by-step
  
  # Custom codebase path
  python3 ai_workflow_orchestrated.py requirements/user_requirement.md --codebase backend/
        """
    )
    
    parser.add_argument('requirements_file', nargs='?',
                       default='requirements/user_requirement.md',
                       help='Requirements file to analyze')
    parser.add_argument('--codebase', default='src',
                       help='Codebase path to analyze (default: src)')
    parser.add_argument('--steps', nargs='+', 
                       choices=['ba', 'architect', 'qa', 'developer', 'senior_dev'],
                       help='Workflow steps to execute (default: ba architect)')
    parser.add_argument('--step-by-step', action='store_true',
                       help='Pause between steps for review')
    
    args = parser.parse_args()
    
    try:
        sys.exit(main(
            requirements_file=args.requirements_file,
            codebase_path=args.codebase,
            steps=args.steps,
            step_by_step=args.step_by_step
        ))
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
