#!/usr/bin/env python3
"""
AI Workflow - Requirements Analysis & System Design

Leverage BA Agent and Architect Agent from aiteam to:
1. Analyze requirements
2. Design system architecture
"""

import os
import sys

# Add aiteam to Python path
aiteam_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'aiteam')
sys.path.insert(0, aiteam_path)

from agents.ba_agent import BAAgent
from agents.architect_agent import ArchitectAgent
from dotenv import load_dotenv

def main(requirements_file='requirements/user_requirement.md', codebase_path='src'):
    """Simple workflow: Requirements Analysis → System Design → Outputs"""
    
    # Load config from aiteam
    load_dotenv(os.path.join(aiteam_path, '.env'), override=True)
    
    # Simple config
    llm_config = {
        'provider': os.getenv('LLM_PROVIDER', 'github_copilot_cli'),
        'model': os.getenv('GITHUB_MODEL', 'gpt-4o')
    }
    
    jira_config = {
        'server': os.getenv('JIRA_SERVER', 'https://example.atlassian.net'),
        'user': os.getenv('JIRA_USER', 'user@example.com'),
        'token': os.getenv('JIRA_API_TOKEN', 'token')
    }
    
    print("🚀 AI Workflow: Requirements → Architecture Design\n")
    
    # Step 1: Requirements Analysis with BA Agent
    print("=" * 60)
    print("STEP 1: Requirements Analysis")
    print("=" * 60)
    ba = BAAgent(llm_config, jira_config)
    requirement_data = ba.read_requirement_file(requirements_file)
    
    if 'error' in requirement_data:
        print(f"❌ Error: {requirement_data['error']}")
        return 1
    
    ba_result = ba.analyze_requirements(requirement_data, output_dir='requirements/analysis')
    
    print(f"\n✅ Requirements analyzed!")
    print(f"   • User stories: {len(ba_result.get('user_stories', []))}")
    print(f"   • Assumptions: {len(ba_result.get('assumptions', []))}")
    
    # Step 2: System Design with Architect Agent
    print(f"\n{'=' * 60}")
    print("STEP 2: System Architecture Design")
    print("=" * 60)
    architect = ArchitectAgent(llm_config)
    
    # Analyze codebase structure (or create initial structure)
    if os.path.exists(codebase_path):
        codebase_analysis = architect.analyze_codebase(codebase_path)
    else:
        print(f"ℹ️  Codebase path '{codebase_path}' not found - designing new system")
        codebase_analysis = {
            'total_files': 0,
            'languages': {},
            'complexity': 'new',
            'requirements_summary': requirement_data.get('content', '')[:500]
        }
    
    # Get architecture recommendations
    patterns = architect.recommend_patterns(codebase_analysis)
    
    # Summary
    print(f"\n{'=' * 60}")
    print("📊 WORKFLOW COMPLETE")
    print("=" * 60)
    print(f"\n✅ Requirements Analysis:")
    print(f"   📁 requirements/analysis/requirements_analysis.md")
    print(f"   📁 requirements/analysis/test_scenarios.feature")
    print(f"\n✅ Architecture Recommendations:")
    print(f"   💡 {len(patterns)} design patterns suggested")
    print(f"\n🎯 Next Steps:")
    print(f"   1. Review requirements analysis")
    print(f"   2. Validate architecture patterns")
    print(f"   3. Begin implementation based on design")
    
    return 0

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='AI-powered requirements analysis & system design')
    parser.add_argument('requirements_file', nargs='?', 
                       default='requirements/user_requirement.md',
                       help='Requirements file to analyze')
    parser.add_argument('--codebase', default='src',
                       help='Codebase path to analyze (default: src)')
    
    args = parser.parse_args()
    
    try:
        sys.exit(main(args.requirements_file, args.codebase))
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
