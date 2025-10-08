# Ethicist MCP Server - Usage Examples

This document provides practical examples of using the Ethicist MCP Server.

## Table of Contents

- [Tools](#tools)
- [Resources](#resources)
- [Prompts](#prompts)
- [Real-World Scenarios](#real-world-scenarios)

## Tools

### 1. analyze_ethical_scenario

Analyze ethical dilemmas using multiple philosophical frameworks.

**Example 1: Self-Driving Car Dilemma**
```json
{
  "name": "analyze_ethical_scenario",
  "arguments": {
    "scenario": "A self-driving car must choose between hitting a pedestrian crossing illegally or swerving and potentially harming its passengers.",
    "frameworks": ["utilitarian", "deontological", "virtue"]
  }
}
```

**Example 2: AI in Hiring**
```json
{
  "name": "analyze_ethical_scenario",
  "arguments": {
    "scenario": "An AI system screens job applications and must decide whether to prioritize diversity or purely merit-based selection.",
    "frameworks": ["utilitarian", "care"]
  }
}
```

### 2. evaluate_ai_system

Evaluate AI systems against ethical principles.

**Example 1: Healthcare AI**
```json
{
  "name": "evaluate_ai_system",
  "arguments": {
    "system_description": "An AI system that predicts patient readmission risk to help allocate hospital resources",
    "use_case": "Hospital resource planning and patient care prioritization",
    "stakeholders": ["patients", "doctors", "hospital administrators", "insurance companies"]
  }
}
```

**Example 2: Social Media Algorithm**
```json
{
  "name": "evaluate_ai_system",
  "arguments": {
    "system_description": "A content recommendation algorithm for social media that maximizes user engagement",
    "use_case": "Social media content curation and user experience",
    "stakeholders": ["users", "content creators", "advertisers", "platform owners"]
  }
}
```

### 3. check_bias

Identify and assess potential biases in AI systems.

**Example 1: Loan Approval System**
```json
{
  "name": "check_bias",
  "arguments": {
    "context": "A loan approval AI trained on 10 years of historical lending data from a traditional bank",
    "bias_types": ["selection", "representation", "measurement"]
  }
}
```

**Example 2: Facial Recognition**
```json
{
  "name": "check_bias",
  "arguments": {
    "context": "A facial recognition system trained primarily on North American and European faces",
    "bias_types": ["representation", "algorithmic", "measurement"]
  }
}
```

### 4. generate_ethical_guidelines

Create customized ethical guidelines for specific projects.

**Example 1: Healthcare AI Project**
```json
{
  "name": "generate_ethical_guidelines",
  "arguments": {
    "project_type": "healthcare diagnostic AI",
    "risk_level": "high",
    "regulations": ["HIPAA", "FDA", "GDPR"]
  }
}
```

**Example 2: Educational AI**
```json
{
  "name": "generate_ethical_guidelines",
  "arguments": {
    "project_type": "education personalized learning system",
    "risk_level": "medium",
    "regulations": ["FERPA", "COPPA"]
  }
}
```

**Example 3: Financial Services**
```json
{
  "name": "generate_ethical_guidelines",
  "arguments": {
    "project_type": "finance algorithmic trading",
    "risk_level": "critical",
    "regulations": ["SEC", "SOX", "MiFID II"]
  }
}
```

### 5. assess_transparency

Evaluate transparency and explainability of AI systems.

**Example 1: Neural Network System**
```json
{
  "name": "assess_transparency",
  "arguments": {
    "system_type": "deep neural network for medical diagnosis",
    "explanation_method": "GradCAM and attention visualization",
    "stakeholder_needs": ["doctors", "patients", "regulators"]
  }
}
```

**Example 2: LLM System**
```json
{
  "name": "assess_transparency",
  "arguments": {
    "system_type": "Large Language Model for customer service",
    "explanation_method": "chain-of-thought prompting",
    "stakeholder_needs": ["customers", "support staff", "compliance team"]
  }
}
```

## Resources

### Reading Ethical Frameworks

**Get all frameworks:**
```
URI: ethicist://frameworks/all
```

**Get specific framework:**
```
URI: ethicist://frameworks/utilitarian
URI: ethicist://frameworks/deontological
URI: ethicist://frameworks/virtue
URI: ethicist://frameworks/care
```

**Get AI ethics guidelines:**
```
URI: ethicist://guidelines/ai-ethics
```

## Prompts

### 1. ethical_decision_making

Structured guidance for making ethical decisions.

**Example:**
```json
{
  "name": "ethical_decision_making",
  "arguments": {
    "situation": "Our company needs to decide whether to deploy a facial recognition system in our retail stores to prevent theft"
  }
}
```

### 2. stakeholder_analysis

Comprehensive stakeholder analysis for decisions.

**Example:**
```json
{
  "name": "stakeholder_analysis",
  "arguments": {
    "decision": "Implementing an AI system to automate employee performance reviews"
  }
}
```

### 3. ai_risk_assessment

Assess ethical risks of AI systems.

**Example:**
```json
{
  "name": "ai_risk_assessment",
  "arguments": {
    "system_description": "A predictive policing algorithm that suggests areas for increased police patrols based on historical crime data",
    "deployment_context": "Urban police departments across multiple cities"
  }
}
```

## Real-World Scenarios

### Scenario 1: Launching a New AI Product

**Step 1: Generate Guidelines**
```json
{
  "name": "generate_ethical_guidelines",
  "arguments": {
    "project_type": "consumer AI assistant",
    "risk_level": "medium",
    "regulations": ["GDPR", "CCPA"]
  }
}
```

**Step 2: Evaluate the System**
```json
{
  "name": "evaluate_ai_system",
  "arguments": {
    "system_description": "A voice-activated AI assistant that learns from user interactions",
    "use_case": "Personal productivity and home automation",
    "stakeholders": ["users", "family members", "developers", "third-party service providers"]
  }
}
```

**Step 3: Check for Bias**
```json
{
  "name": "check_bias",
  "arguments": {
    "context": "Training data collected from beta testers primarily from tech-savvy urban populations",
    "bias_types": ["selection", "representation"]
  }
}
```

### Scenario 2: Ethical Audit of Existing System

**Step 1: Assess Transparency**
```json
{
  "name": "assess_transparency",
  "arguments": {
    "system_type": "ensemble model for credit scoring",
    "explanation_method": "feature importance scores",
    "stakeholder_needs": ["loan applicants", "loan officers", "regulators"]
  }
}
```

**Step 2: Analyze Ethical Concerns**
```json
{
  "name": "analyze_ethical_scenario",
  "arguments": {
    "scenario": "The credit scoring model shows different approval rates for different demographic groups, even when controlling for creditworthiness indicators",
    "frameworks": ["utilitarian", "deontological", "care"]
  }
}
```

### Scenario 3: Crisis Response

**When an AI system causes harm:**

**Step 1: Stakeholder Analysis**
```json
{
  "name": "stakeholder_analysis",
  "arguments": {
    "decision": "How to respond to reports that our hiring AI has been systematically disadvantaging certain applicant groups"
  }
}
```

**Step 2: Ethical Decision Making**
```json
{
  "name": "ethical_decision_making",
  "arguments": {
    "situation": "We discovered our AI system has been making biased decisions for 6 months. We need to decide whether to disclose this publicly, who to notify, and how to remedy the situation."
  }
}
```

## Tips for Effective Use

1. **Combine Multiple Tools**: Use multiple tools together for comprehensive analysis
2. **Iterate**: Run tools multiple times as you refine your understanding
3. **Document**: Keep records of analyses for accountability
4. **Engage Stakeholders**: Use the insights to facilitate discussions with affected parties
5. **Regular Reviews**: Periodically reassess systems as they evolve
6. **Context Matters**: Provide detailed context for more relevant guidance
7. **Multiple Frameworks**: Consider multiple ethical perspectives for complex decisions

## Integration Examples

### With CI/CD Pipeline

```yaml
# .github/workflows/ethical-review.yml
name: Ethical Review
on: [pull_request]

jobs:
  ethical-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install Ethicist MCP
        run: pip install -r requirements.txt
      - name: Run Ethical Analysis
        run: python scripts/ethical_review.py
```

### With Documentation

Include ethical analysis in your system documentation:

```markdown
## Ethical Considerations

This system was evaluated using the Ethicist MCP Server:

- Bias Assessment: [Link to bias report]
- Transparency Evaluation: [Link to transparency assessment]
- Stakeholder Analysis: [Link to stakeholder analysis]
```

## Getting Help

For more examples and use cases, see:
- [README.md](README.md) - Main documentation
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration options
- GitHub Issues - Report issues or request features
