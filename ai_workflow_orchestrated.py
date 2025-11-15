#!/usr/bin/env python3
"""
Orchestrated AI Workflow for PPS Project
Demonstrates BA Agent → Architect Agent integration with context passing
"""

import os
import sys
from pathlib import Path

# Add aiteam directory to path
aiteam_path = '/Users/joeylam/repo/aiteam'
sys.path.insert(0, aiteam_path)

from agents.lead_orchestrator import LeadOrchestrator
from agents.ba_agent import BAAgent
from agents.architect_agent import ArchitectAgent

def main():
    """Run orchestrated workflow: BA Analysis → Architecture Design"""
    
    print("="*80)
    print("🎯 Personal Portfolio System - Orchestrated AI Workflow")
    print("="*80)
    print("\nWorkflow Steps:")
    print("  1. BA Agent: Analyze requirements")
    print("  2. Architect Agent: Design system architecture")
    print("="*80)
    
    # Configuration
    llm_config = {
        'provider': os.getenv('LLM_PROVIDER', 'github_copilot_cli'),
        'model': os.getenv('GITHUB_MODEL', 'gpt-4o'),
        'temperature': 0.7
    }
    
    # Initialize orchestrator
    orchestrator = LeadOrchestrator(llm_config)
    
    # Define project paths
    requirements_file = '/Users/joeylam/repo/pps/requirements/user_requirement.md'
    analysis_dir = '/Users/joeylam/repo/pps/requirements/analysis'
    architecture_dir = '/Users/joeylam/repo/pps/architecture'
    
    # Create directories
    Path(analysis_dir).mkdir(parents=True, exist_ok=True)
    Path(architecture_dir).mkdir(parents=True, exist_ok=True)
    
    # Register BA Agent step handler
    def ba_step_handler(context):
        """Execute BA Agent step"""
        print("\n🔍 Executing BA Agent...")
        
        # BA Agent requires jira_config (can be empty dict for file-based requirements)
        jira_config = {}
        ba = BAAgent(llm_config, jira_config)
        
        # Read requirements
        requirement_data = ba.read_requirement_file(requirements_file)
        
        # Analyze requirements (method signature: requirement_data, output_dir)
        result = ba.analyze_requirements(
            requirement_data=requirement_data,
            output_dir=analysis_dir
        )
        
        # Return structured output for next agent
        return {
            'status': 'completed',
            'requirement_data': requirement_data,
            'analysis': result,
            'analysis_file': os.path.join(analysis_dir, 'requirements_structured.json')
        }
    
    # Register Architect Agent step handler
    def architect_step_handler(context):
        """Execute Architect Agent step"""
        print("\n🏗️  Executing Architect Agent...")
        
        architect = ArchitectAgent(llm_config)
        
        # Get BA result from context
        ba_result = context.get('ba_result', {})
        
        if not ba_result:
            print("⚠️  No BA Agent result found in context")
            return {'status': 'skipped', 'reason': 'no_ba_result'}
        
        # Option 1: Use analysis file path
        analysis_file = ba_result.get('analysis_file')
        
        # Option 2: Use analysis dict directly from context (commented out)
        # analysis_dict = ba_result.get('analysis')
        
        # Design architecture
        architecture = architect.design_system_architecture(
            ba_analysis=analysis_file,  # or analysis_dict
            output_dir=architecture_dir
        )
        
        return {
            'status': 'completed',
            'architecture': architecture,
            'architecture_file': os.path.join(architecture_dir, 'system_architecture.md'),
            'structured_file': os.path.join(architecture_dir, 'architecture_structured.json')
        }
    
    # Register handlers
    orchestrator.register_step_handler('ba', ba_step_handler)
    orchestrator.register_step_handler('architect', architect_step_handler)
    
    # Create workflow with BA → Architect steps
    workflow = orchestrator.create_workflow(
        steps=['ba', 'architect'],
        context={
            'project': 'Personal Portfolio System',
            'requirements_file': requirements_file
        }
    )
    
    # Execute workflow
    print("\n")
    result = orchestrator.execute_workflow(
        workflow, 
        pause_between_steps=False  # Set to True for step-by-step execution
    )
    
    # Display results
    print("\n" + "="*80)
    print("📊 WORKFLOW SUMMARY")
    print("="*80)
    
    for i, stage in enumerate(result['stages'], 1):
        print(f"\n{i}. {stage['name']} ({stage['agent']})")
        print(f"   Status: {stage['status']}")
        
        if stage['status'] == 'completed' and stage.get('result'):
            stage_result = stage['result']
            if stage['key'] == 'ba':
                print(f"   Outputs:")
                print(f"     - {analysis_dir}/requirements_analysis.md")
                print(f"     - {analysis_dir}/requirements.feature")
                print(f"     - {analysis_dir}/requirements_structured.json")
            elif stage['key'] == 'architect':
                print(f"   Outputs:")
                print(f"     - {architecture_dir}/system_architecture.md")
                print(f"     - {architecture_dir}/architecture_structured.json")
    
    print("\n" + "="*80)
    print("✅ Workflow completed successfully!")
    print("="*80)
    print("\n📁 Next Steps:")
    print("   1. Review architecture: cat architecture/system_architecture.md")
    print("   2. Run Senior Dev Agent for detailed design")
    print("   3. Run Developer Agent for implementation")
    print()

if __name__ == '__main__':
    main()
