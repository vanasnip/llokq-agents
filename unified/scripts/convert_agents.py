#!/usr/bin/env python3
"""
Convert existing D3P agents to unified format
"""
import yaml
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from unified.agents.schema import Agent, AgentCategory, RiskProfile


def normalize_risk_profile(risk_str: str) -> str:
    """Normalize risk profile string to match RiskProfile enum values"""
    risk_str = risk_str.lower()
    
    # Handle special cases and mappings
    if 'zero tolerance' in risk_str:
        return 'zero_tolerance'
    elif 'conservative' in risk_str:
        return 'conservative'
    elif 'aggressive' in risk_str:
        return 'aggressive'
    elif 'balanced' in risk_str or 'pragmatic' in risk_str:
        return 'balanced'
    else:
        # Default to balanced for unknown values
        return 'balanced'


def convert_design_agents(design_agents_path: Path) -> dict:
    """Convert design agents to unified format"""
    with open(design_agents_path, 'r') as f:
        content = f.read()
    
    # Parse the non-standard YAML format
    design_data = yaml.safe_load(content)
    
    converted = {}
    
    # Skip the comment line and process all top-level keys as agents
    for agent_name, agent_data in design_data.items():
        if agent_name == 'Design_Agents' or isinstance(agent_data, str):
            continue
        
        # Skip entries that are clearly not agents (commands, workflows, etc.)
        skip_patterns = ['_Commands', '_Workflows', '_Operations', '_Standards', '_Platform', 
                        '_Architecture', '_Application', '_Processes', '_Management', 
                        '_System', '_servers', '_layout']
        if any(pattern in agent_name for pattern in skip_patterns):
            continue
        
        # Skip entries with empty identity (not real agents)
        if not agent_data.get('Identity'):
            continue
        # Map to unified schema (handle capitalized keys)
        unified_agent = {
            'name': agent_name,
            'command': f'--{agent_name}',
            'category': AgentCategory.DESIGN.value,
            'identity': agent_data.get('Identity', ''),
            'core_belief': agent_data.get('Core_Belief', ''),
            'primary_question': agent_data.get('Primary_Question', ''),
            'decision_framework': agent_data.get('Decision_Framework', ''),
            'risk_profile': normalize_risk_profile(agent_data.get('Risk_Profile', 'balanced')),
            'success_metrics': agent_data.get('Success_Metrics', ''),
            'communication_style': agent_data.get('Communication_Style', ''),
            'problem_solving': agent_data.get('Problem_Solving', ''),
            'mcp_preferences': agent_data.get('MCP_Preferences', '').replace(' + ', ',').split(','),
            'focus_areas': agent_data.get('Focus', '').split(' | ') if agent_data.get('Focus') else [],
            'values': agent_data.get('Values', ''),
            'limitations': agent_data.get('Limitations', ''),
            'compatible_agents': [],  # To be populated based on workflow analysis
            'handoff_protocols': {},  # To be populated based on workflow analysis
            'primary_phases': [],  # To be populated based on phase mapping
            'support_phases': []   # To be populated based on phase mapping
        }
        
        # Clean up MCP preferences
        unified_agent['mcp_preferences'] = [
            pref.strip().lower().replace('(primary)', '').replace('(secondary)', '').strip()
            for pref in unified_agent['mcp_preferences']
        ]
        
        converted[agent_name] = unified_agent
    
    return converted


def convert_dev_agents(dev_agents_path: Path) -> dict:
    """Convert development agents to unified format"""
    with open(dev_agents_path, 'r') as f:
        content = f.read()
    
    # Parse the non-standard YAML format
    dev_data = yaml.safe_load(content)
    
    converted = {}
    
    # Category mapping based on agent type
    category_map = {
        'system_architect': AgentCategory.ARCHITECTURE,
        'backend_engineer': AgentCategory.DEVELOPMENT,
        'frontend_architect': AgentCategory.DEVELOPMENT,
        'qa_engineer': AgentCategory.QUALITY,
        'devops_engineer': AgentCategory.OPERATIONS,
        'security_engineer': AgentCategory.QUALITY,
        'data_engineer': AgentCategory.DEVELOPMENT,
        'api_architect': AgentCategory.ARCHITECTURE,
        'performance_engineer': AgentCategory.QUALITY,
        'mobile_engineer': AgentCategory.DEVELOPMENT,
        'maintenance_specialist': AgentCategory.OPERATIONS,
        'documentation_specialist': AgentCategory.QUALITY
    }
    
    # Skip comment lines and process all top-level keys as agents
    for agent_name, agent_data in dev_data.items():
        if agent_name == 'Development_Agents' or isinstance(agent_data, str):
            continue
        
        # Skip entries that are clearly not agents (commands, workflows, etc.)
        skip_patterns = ['_Commands', '_Workflows', '_Operations', '_Standards', '_Platform', 
                        '_Architecture', '_Application', '_Processes', '_Management', 
                        '_System', '_servers', '_layout']
        if any(pattern in agent_name for pattern in skip_patterns):
            continue
        
        # Skip entries with empty identity (not real agents)
        if not agent_data.get('Identity'):
            continue
        # Determine category
        category = category_map.get(agent_name, AgentCategory.DEVELOPMENT)
        
        # Map to unified schema (handle capitalized keys)
        unified_agent = {
            'name': agent_name.replace('_engineer', '').replace('_specialist', '').replace('_architect', ''),
            'command': f"--{agent_name.replace('_engineer', '').replace('_specialist', '').replace('_architect', '')}",
            'category': category.value,
            'identity': agent_data.get('Identity', ''),
            'core_belief': agent_data.get('Core_Belief', ''),
            'primary_question': agent_data.get('Primary_Question', ''),
            'decision_framework': agent_data.get('Decision_Framework', ''),
            'risk_profile': normalize_risk_profile(agent_data.get('Risk_Profile', 'balanced')),
            'success_metrics': agent_data.get('Success_Metrics', ''),
            'communication_style': agent_data.get('Communication_Style', ''),
            'problem_solving': agent_data.get('Problem_Solving', ''),
            'mcp_preferences': agent_data.get('MCP_Preferences', '').replace(' + ', ',').split(','),
            'focus_areas': agent_data.get('Focus', '').split(' | ') if agent_data.get('Focus') else [],
            'values': agent_data.get('Values', ''),
            'limitations': agent_data.get('Limitations', ''),
            'compatible_agents': [],
            'handoff_protocols': {},
            'primary_phases': [],
            'support_phases': []
        }
        
        # Clean up MCP preferences
        unified_agent['mcp_preferences'] = [
            pref.strip().lower().replace('(primary)', '').replace('(cache)', '').strip()
            for pref in unified_agent['mcp_preferences']
        ]
        
        # Simplify agent key name
        simple_name = agent_name.replace('_engineer', '').replace('_specialist', '').replace('_architect', '')
        if simple_name == 'system':
            simple_name = 'architect'
        elif simple_name == 'frontend':
            simple_name = 'frontend'
        
        converted[simple_name] = unified_agent
    
    return converted


def update_phase_assignments(agents: dict, phase_mapping_path: Path) -> None:
    """Update agents with their phase assignments"""
    with open(phase_mapping_path, 'r') as f:
        phase_data = yaml.safe_load(f)
    
    # Process each phase
    for phase_num, phase_info in phase_data.get('phases', {}).items():
        primary_agents = phase_info.get('primary_agents', [])
        support_agents = phase_info.get('support_agents', [])
        
        # Update primary agents
        for agent_ref in primary_agents:
            # Extract agent name (handle format like "requirements_agent (Riley)")
            agent_name = agent_ref.split('(')[0].strip()
            agent_name = agent_name.replace('_agent', '').replace('_engineer', '').replace('_architect', '')
            
            if agent_name == 'system':
                agent_name = 'architect'
            elif agent_name == 'aura':
                agent_name = 'aura'
            elif agent_name == 'motion_maestra':
                agent_name = 'motion'
            elif agent_name == 'chromatic':
                agent_name = 'brand'
            elif agent_name == 'layout_loom':
                agent_name = 'layout'
            elif agent_name == 'requirements':
                agent_name = 'requirements'
            
            if agent_name in agents:
                agents[agent_name]['primary_phases'].append(phase_num)
        
        # Update support agents
        for agent_ref in support_agents:
            agent_name = agent_ref.split('(')[0].strip()
            agent_name = agent_name.replace('_agent', '').replace('_engineer', '').replace('_architect', '')
            
            if agent_name == 'system':
                agent_name = 'architect'
            
            if agent_name in agents:
                agents[agent_name]['support_phases'].append(phase_num)


def main():
    """Main conversion process"""
    # Paths
    project_root = Path(__file__).parent.parent.parent
    design_agents_path = project_root / 'design_agents' / 'agents.yaml'
    dev_agents_path = project_root / 'dev_agents' / 'agents.yaml'
    phase_mapping_path = project_root / 'd3p' / 'agent_mapping.yaml'
    output_path = project_root / 'unified' / 'config' / 'agents.yml'
    
    print("Converting D3P agents to unified format...")
    
    # Convert agents
    all_agents = {}
    
    if design_agents_path.exists():
        print("Converting design agents...")
        design_agents = convert_design_agents(design_agents_path)
        all_agents.update(design_agents)
        print(f"  Converted {len(design_agents)} design agents")
    
    if dev_agents_path.exists():
        print("Converting development agents...")
        dev_agents = convert_dev_agents(dev_agents_path)
        all_agents.update(dev_agents)
        print(f"  Converted {len(dev_agents)} development agents")
    
    # Update phase assignments
    if phase_mapping_path.exists():
        print("Updating phase assignments...")
        update_phase_assignments(all_agents, phase_mapping_path)
    
    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write unified configuration
    unified_config = {'agents': all_agents}
    
    with open(output_path, 'w') as f:
        yaml.dump(unified_config, f, default_flow_style=False, sort_keys=False)
    
    print(f"\nSuccessfully converted {len(all_agents)} agents")
    print(f"Output written to: {output_path}")
    
    # Print summary
    print("\nAgent Summary:")
    categories = {}
    for agent in all_agents.values():
        cat = agent['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count} agents")


if __name__ == '__main__':
    main()


# Allow calling as module
def run_conversion():
    """Entry point for module execution"""
    return main()