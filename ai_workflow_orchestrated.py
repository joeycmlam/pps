#!/usr/bin/env python3
"""
Orchestrated AI Workflow for PPS Project
Demonstrates BA Agent → Architect Agent integration with context passing

Class-based design for better maintainability and extensibility.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add aiteam directory to path
aiteam_path = '/Users/joeylam/repo/aiteam'
sys.path.insert(0, aiteam_path)

from agents.lead_orchestrator import LeadOrchestrator
from agents.ba_agent import BAAgent
from agents.architect_agent import ArchitectAgent


class PPSWorkflow:
    """Personal Portfolio System AI Workflow orchestrator"""
    
    def __init__(self, 
                 requirements_file: str,
                 analysis_dir: str = 'requirements/analysis',
                 architecture_dir: str = 'architecture',
                 llm_provider: str = 'github_copilot_cli',
                 llm_model: str = 'gpt-4o'):
        """
        Initialize PPS Workflow
        
        Args:
            requirements_file: Path to requirements file
            analysis_dir: Directory for BA Agent outputs
            architecture_dir: Directory for Architect Agent outputs
            llm_provider: LLM provider (github_copilot_cli, ollama)
            llm_model: Model name (gpt-4o, llama3.2, etc.)
        """
        self.requirements_file = requirements_file
        self.analysis_dir = analysis_dir
        self.architecture_dir = architecture_dir
        
        # LLM Configuration
        self.llm_config = {
            'provider': os.getenv('LLM_PROVIDER', llm_provider),
            'model': os.getenv('GITHUB_MODEL', llm_model),
            'temperature': 0.7
        }
        
        # Initialize orchestrator
        self.orchestrator = LeadOrchestrator(self.llm_config)
        
        # Setup directories
        self._setup_directories()
        
        # Register step handlers
        self._register_handlers()
        
    def _setup_directories(self):
        """Create necessary output directories"""
        Path(self.analysis_dir).mkdir(parents=True, exist_ok=True)
        Path(self.architecture_dir).mkdir(parents=True, exist_ok=True)
        
    def _register_handlers(self):
        """Register all workflow step handlers"""
        self.orchestrator.register_step_handler('ba', self._ba_step_handler)
        self.orchestrator.register_step_handler('architect', self._architect_step_handler)
        
    def _ba_step_handler(self, context: Dict) -> Dict:
        """
        Execute BA Agent step
        
        Args:
            context: Workflow context dictionary
            
        Returns:
            Dict with status, analysis results, and file paths
        """
        print("\n🔍 Executing BA Agent...")
        
        # BA Agent requires jira_config (can be empty dict for file-based requirements)
        jira_config = {}
        ba = BAAgent(self.llm_config, jira_config)
        
        # Get requirements file from context (if provided) or use default
        requirements_file = context.get('requirements_file', self.requirements_file)
        print(f"   Reading requirements from: {requirements_file}")
        
        # Read requirements
        requirement_data = ba.read_requirement_file(requirements_file)
        
        # Analyze requirements
        result = ba.analyze_requirements(
            requirement_data=requirement_data,
            output_dir=self.analysis_dir
        )
        
        # Return structured output for next agent
        return {
            'status': 'completed',
            'requirement_data': requirement_data,
            'analysis': result,
            'analysis_file': os.path.join(self.analysis_dir, 'requirements_structured.json')
        }
    
    def _architect_step_handler(self, context: Dict) -> Dict:
        """
        Execute Architect Agent step
        
        Args:
            context: Workflow context dictionary
            
        Returns:
            Dict with status, architecture results, and file paths
        """
        print("\n🏗️  Executing Architect Agent...")
        
        architect = ArchitectAgent(self.llm_config)
        
        # Get BA result from context
        ba_result = context.get('ba_result', {})
        
        if not ba_result:
            print("⚠️  No BA Agent result found in context")
            return {'status': 'skipped', 'reason': 'no_ba_result'}
        
        # Use analysis file path
        analysis_file = ba_result.get('analysis_file')
        
        # Design architecture
        architecture = architect.design_system_architecture(
            ba_analysis=analysis_file,
            output_dir=self.architecture_dir
        )
        
        return {
            'status': 'completed',
            'architecture': architecture,
            'architecture_file': os.path.join(self.architecture_dir, 'system_architecture.md'),
            'structured_file': os.path.join(self.architecture_dir, 'architecture_structured.json')
        }
    
    def run(self, 
            steps: Optional[List[str]] = None,
            pause_between_steps: bool = False,
            project_name: str = 'Personal Portfolio System') -> Dict:
        """
        Run the workflow with specified steps
        
        Args:
            steps: List of step keys to execute (default: ['ba', 'architect'])
            pause_between_steps: If True, wait for user input between steps
            project_name: Project name for context
            
        Returns:
            Workflow result dictionary
        """
        # Default steps
        if steps is None:
            steps = ['ba', 'architect']
        
        # Display workflow info
        self._print_header(steps, project_name)
        
        # Create workflow
        workflow = self.orchestrator.create_workflow(
            steps=steps,
            context={
                'project': project_name,
                'requirements_file': self.requirements_file
            }
        )
        
        # Execute workflow
        print("\n")
        result = self.orchestrator.execute_workflow(
            workflow, 
            pause_between_steps=pause_between_steps
        )
        
        # Display results
        self._print_summary(result)
        
        return result
    
    def _print_header(self, steps: List[str], project_name: str):
        """Print workflow header"""
        print("="*80)
        print(f"🎯 {project_name} - Orchestrated AI Workflow")
        print("="*80)
        print("\nWorkflow Steps:")
        
        step_names = {
            'ba': 'BA Agent: Analyze requirements',
            'architect': 'Architect Agent: Design system architecture',
            'qa': 'QA Agent: Design test strategy',
            'senior_dev': 'Senior Dev Agent: Detailed design',
            'developer': 'Developer Agent: Implementation'
        }
        
        for i, step in enumerate(steps, 1):
            print(f"  {i}. {step_names.get(step, step.upper())}")
        
        print("="*80)
    
    def _print_summary(self, result: Dict):
        """Print workflow execution summary"""
        print("\n" + "="*80)
        print("📊 WORKFLOW SUMMARY")
        print("="*80)
        
        for i, stage in enumerate(result['stages'], 1):
            print(f"\n{i}. {stage['name']} ({stage['agent']})")
            print(f"   Status: {stage['status']}")
            
            if stage['status'] == 'completed' and stage.get('result'):
                if stage['key'] == 'ba':
                    print(f"   Outputs:")
                    print(f"     - {self.analysis_dir}/requirements_analysis.md")
                    print(f"     - {self.analysis_dir}/requirements.feature")
                    print(f"     - {self.analysis_dir}/requirements_structured.json")
                elif stage['key'] == 'architect':
                    print(f"   Outputs:")
                    print(f"     - {self.architecture_dir}/system_architecture.md")
                    print(f"     - {self.architecture_dir}/architecture_structured.json")
        
        print("\n" + "="*80)
        if result['status'] == 'completed':
            print("✅ Workflow completed successfully!")
        else:
            print(f"⚠️  Workflow status: {result['status']}")
        print("="*80)
        
        self._print_next_steps()
    
    def _print_next_steps(self):
        """Print suggested next steps"""
        print("\n📁 Next Steps:")
        print(f"   1. Review architecture: cat {self.architecture_dir}/system_architecture.md")
        print("   2. Run Senior Dev Agent for detailed design")
        print("   3. Run Developer Agent for implementation")
        print()


def main():
    """Main entry point for workflow execution"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Personal Portfolio System AI Workflow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full BA → Architect workflow (default)
  python ai_workflow_orchestrated.py
  
  # Run only BA Agent
  python ai_workflow_orchestrated.py --steps ba
  
  # Run only Architect Agent (requires existing BA analysis)
  python ai_workflow_orchestrated.py --steps architect
  
  # Run with step-by-step confirmation
  python ai_workflow_orchestrated.py --steps ba architect --pause
  
  # Custom requirements file
  python ai_workflow_orchestrated.py --requirements requirements/custom.md
  
  # Custom output directories
  python ai_workflow_orchestrated.py --analysis-dir output/analysis --arch-dir output/architecture
  
  # Use different LLM
  python ai_workflow_orchestrated.py --llm-provider ollama --llm-model llama3.2
        """
    )
    
    parser.add_argument(
        '--requirements',
        default='/Users/joeylam/repo/pps/requirements/user_requirement.md',
        help='Path to requirements file (default: requirements/user_requirement.md)'
    )
    
    parser.add_argument(
        '--analysis-dir',
        default='/Users/joeylam/repo/pps/requirements/analysis',
        help='Output directory for BA Agent analysis (default: requirements/analysis)'
    )
    
    parser.add_argument(
        '--arch-dir',
        default='/Users/joeylam/repo/pps/architecture',
        help='Output directory for architecture design (default: architecture)'
    )
    
    parser.add_argument(
        '--steps',
        nargs='+',
        choices=['ba', 'architect', 'qa', 'senior_dev', 'developer'],
        default=['ba', 'architect'],
        help='Workflow steps to execute (default: ba architect)'
    )
    
    parser.add_argument(
        '--pause',
        action='store_true',
        help='Pause between steps for review'
    )
    
    parser.add_argument(
        '--project-name',
        default='Personal Portfolio System',
        help='Project name for display (default: Personal Portfolio System)'
    )
    
    parser.add_argument(
        '--llm-provider',
        default='github_copilot_cli',
        choices=['github_copilot_cli', 'ollama'],
        help='LLM provider (default: github_copilot_cli)'
    )
    
    parser.add_argument(
        '--llm-model',
        default='gpt-4o',
        help='LLM model name (default: gpt-4o)'
    )
    
    args = parser.parse_args()
    
    # Initialize workflow with parsed arguments
    workflow = PPSWorkflow(
        requirements_file=args.requirements,
        analysis_dir=args.analysis_dir,
        architecture_dir=args.arch_dir,
        llm_provider=args.llm_provider,
        llm_model=args.llm_model
    )
    
    # Run workflow with specified steps
    try:
        workflow.run(
            steps=args.steps,
            pause_between_steps=args.pause,
            project_name=args.project_name
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
