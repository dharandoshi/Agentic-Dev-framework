#!/usr/bin/env python3
"""
Agent Response Validator
Validates agent responses against consistency standards
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

class ResponseValidator:
    """Validates agent responses for consistency and completeness"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.claude_dir = self.project_root / '.claude'
        self.templates_dir = self.claude_dir / 'templates'
        
        # Load response templates
        self.templates = self._load_templates()
        self.standards = self.templates.get('output_standards', {})
        self.validation_rules = self.templates.get('validation_rules', {})
    
    def _load_templates(self) -> Dict:
        """Load response templates"""
        try:
            template_file = self.templates_dir / 'agent_response_templates.json'
            if template_file.exists():
                with open(template_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception:
            return {}
    
    def validate_response(self, agent_name: str, response_type: str, content: Dict) -> Dict:
        """Validate an agent response"""
        validation_result = {
            'valid': True,
            'issues': [],
            'suggestions': [],
            'score': 100
        }
        
        # Basic validation
        basic_issues = self._validate_basic_structure(content)
        validation_result['issues'].extend(basic_issues)
        
        # Template-specific validation
        template_issues = self._validate_against_template(response_type, content)
        validation_result['issues'].extend(template_issues)
        
        # Agent-specific validation
        agent_issues = self._validate_agent_specific_rules(agent_name, content)
        validation_result['issues'].extend(agent_issues)
        
        # Content quality validation
        quality_issues = self._validate_content_quality(content)
        validation_result['issues'].extend(quality_issues)
        
        # Calculate final score and validity
        validation_result['score'] = max(0, 100 - (len(validation_result['issues']) * 10))
        validation_result['valid'] = validation_result['score'] >= 70
        
        # Generate suggestions
        validation_result['suggestions'] = self._generate_suggestions(validation_result['issues'])
        
        return validation_result
    
    def _validate_basic_structure(self, content: Dict) -> List[str]:
        """Validate basic response structure"""
        issues = []
        
        # Check if content is properly structured
        if not isinstance(content, dict):
            issues.append("Response must be structured as a dictionary")
            return issues
        
        # Check minimum content requirements
        general_guidelines = self.standards.get('general_guidelines', {})
        required_elements = self.standards.get('required_elements', {}).get('all_responses_must_include', [])
        
        content_str = json.dumps(content).lower()
        
        for element in required_elements:
            element_key = element.replace(' ', '_')
            if element_key not in content_str and element.replace(' ', '') not in content_str:
                issues.append(f"Missing required element: {element}")
        
        return issues
    
    def _validate_against_template(self, response_type: str, content: Dict) -> List[str]:
        """Validate response against specific template"""
        issues = []
        
        if response_type not in self.templates.get('templates', {}):
            return issues  # No template to validate against
        
        template = self.templates['templates'][response_type]
        required_fields = template.get('required_fields', [])
        
        # Check required fields
        for field in required_fields:
            if field not in content:
                issues.append(f"Missing required field for {response_type}: {field}")
        
        return issues
    
    def _validate_agent_specific_rules(self, agent_name: str, content: Dict) -> List[str]:
        """Validate agent-specific requirements"""
        issues = []
        
        agent_rules = self.validation_rules.get('agent_specific_rules', {}).get(agent_name, {})
        if not agent_rules:
            return issues
        
        must_include = agent_rules.get('must_include', [])
        content_str = json.dumps(content).lower()
        
        for requirement in must_include:
            requirement_check = requirement.replace(' ', '').replace('-', '').lower()
            if requirement_check not in content_str:
                issues.append(f"{agent_name} must include: {requirement}")
        
        return issues
    
    def _validate_content_quality(self, content: Dict) -> List[str]:
        """Validate content quality"""
        issues = []
        
        content_str = json.dumps(content)
        validation_rules = self.validation_rules.get('response_validation', {})
        
        # Check length requirements
        min_length = validation_rules.get('min_length', 0)
        max_length = validation_rules.get('max_length', float('inf'))
        
        if len(content_str) < min_length:
            issues.append(f"Response too short (minimum {min_length} characters)")
        elif len(content_str) > max_length:
            issues.append(f"Response too long (maximum {max_length} characters)")
        
        # Check for forbidden phrases
        forbidden_phrases = validation_rules.get('forbidden_phrases', [])
        content_lower = content_str.lower()
        
        for phrase in forbidden_phrases:
            if phrase.lower() in content_lower:
                issues.append(f"Avoid uncertain language: '{phrase}'")
        
        # Check for required sections
        required_sections = validation_rules.get('required_sections', [])
        for section in required_sections:
            if section not in content_lower:
                issues.append(f"Missing required section: {section}")
        
        return issues
    
    def _generate_suggestions(self, issues: List[str]) -> List[str]:
        """Generate improvement suggestions based on issues"""
        suggestions = []
        
        if any('missing required field' in issue.lower() for issue in issues):
            suggestions.append("Review the response template and ensure all required fields are included")
        
        if any('must include' in issue.lower() for issue in issues):
            suggestions.append("Check agent-specific requirements and include all mandatory elements")
        
        if any('too short' in issue.lower() for issue in issues):
            suggestions.append("Provide more detailed information and context")
        
        if any('uncertain language' in issue.lower() for issue in issues):
            suggestions.append("Use definitive language and provide specific actionable information")
        
        if any('missing required section' in issue.lower() for issue in issues):
            suggestions.append("Structure your response to include context, actions, and timeline")
        
        return suggestions
    
    def format_validation_report(self, validation_result: Dict) -> str:
        """Format validation results into a readable report"""
        report = []
        
        # Header
        status = "✅ VALID" if validation_result['valid'] else "❌ INVALID"
        score = validation_result['score']
        report.append(f"Response Validation: {status} (Score: {score}/100)")
        report.append("=" * 50)
        
        # Issues
        if validation_result['issues']:
            report.append("\n🔍 Issues Found:")
            for i, issue in enumerate(validation_result['issues'], 1):
                report.append(f"  {i}. {issue}")
        
        # Suggestions
        if validation_result['suggestions']:
            report.append("\n💡 Suggestions:")
            for i, suggestion in enumerate(validation_result['suggestions'], 1):
                report.append(f"  {i}. {suggestion}")
        
        if validation_result['valid'] and not validation_result['issues']:
            report.append("\n✨ Response meets all quality standards!")
        
        return "\n".join(report)
    
    def get_template_example(self, response_type: str, agent_name: str = None) -> Optional[Dict]:
        """Get a template example for a specific response type"""
        if response_type not in self.templates.get('templates', {}):
            return None
        
        template = self.templates['templates'][response_type]['template']
        
        # Customize for specific agent if provided
        if agent_name and agent_name in self.validation_rules.get('agent_specific_rules', {}):
            # Add agent-specific customizations
            agent_rules = self.validation_rules['agent_specific_rules'][agent_name]
            template['agent_specific_note'] = f"As {agent_name}, ensure you include: {', '.join(agent_rules.get('must_include', []))}"
        
        return template

def main():
    """CLI interface for the validator"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python response_validator.py <command> [args]")
        print("Commands:")
        print("  validate <agent_name> <response_type> <content_json>")
        print("  template <response_type> [agent_name]")
        sys.exit(1)
    
    validator = ResponseValidator()
    command = sys.argv[1]
    
    if command == 'validate':
        if len(sys.argv) < 5:
            print("Usage: python response_validator.py validate <agent_name> <response_type> <content_json>")
            sys.exit(1)
        
        agent_name = sys.argv[2]
        response_type = sys.argv[3]
        content_json = sys.argv[4]
        
        try:
            content = json.loads(content_json)
            result = validator.validate_response(agent_name, response_type, content)
            print(validator.format_validation_report(result))
        except json.JSONDecodeError:
            print("Error: Invalid JSON content")
            sys.exit(1)
    
    elif command == 'template':
        if len(sys.argv) < 3:
            print("Usage: python response_validator.py template <response_type> [agent_name]")
            sys.exit(1)
        
        response_type = sys.argv[2]
        agent_name = sys.argv[3] if len(sys.argv) > 3 else None
        
        template = validator.get_template_example(response_type, agent_name)
        if template:
            print(json.dumps(template, indent=2))
        else:
            print(f"Template not found: {response_type}")
            print("Available templates:", list(validator.templates.get('templates', {}).keys()))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()