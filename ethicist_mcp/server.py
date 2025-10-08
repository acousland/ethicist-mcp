#!/usr/bin/env python3
"""
Ethicist MCP Server - A full-featured MCP server with Streamable HTTP support.

This server provides tools, resources, and prompts for ethical AI analysis and guidance.
"""

import asyncio
import json
import logging
from typing import Any, Sequence
from datetime import datetime

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    Resource,
    Prompt,
    PromptMessage,
    GetPromptResult,
)
from pydantic import AnyUrl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ethicist-mcp")

# Initialize the MCP server
app = Server("ethicist-mcp")

# Ethical frameworks database
ETHICAL_FRAMEWORKS = {
    "utilitarian": {
        "name": "Utilitarian Ethics",
        "description": "Focuses on maximizing overall happiness and well-being",
        "key_principles": [
            "Greatest good for the greatest number",
            "Consequences matter most",
            "Impartial consideration of all affected parties"
        ]
    },
    "deontological": {
        "name": "Deontological Ethics",
        "description": "Emphasizes duties, rules, and moral obligations",
        "key_principles": [
            "Act according to universal moral laws",
            "Respect human dignity and autonomy",
            "Intentions matter more than consequences"
        ]
    },
    "virtue": {
        "name": "Virtue Ethics",
        "description": "Focuses on character development and moral virtues",
        "key_principles": [
            "Cultivate good character traits",
            "Act as a virtuous person would",
            "Balance and moderation in all things"
        ]
    },
    "care": {
        "name": "Ethics of Care",
        "description": "Emphasizes relationships, empathy, and contextual responses",
        "key_principles": [
            "Prioritize caring relationships",
            "Consider emotional and relational impacts",
            "Context-sensitive moral reasoning"
        ]
    }
}

# AI Ethics Guidelines
AI_ETHICS_GUIDELINES = {
    "fairness": "Ensure AI systems treat all individuals and groups equitably without bias",
    "transparency": "Make AI decision-making processes understandable and explainable",
    "accountability": "Establish clear responsibility for AI system outcomes",
    "privacy": "Protect individual data and respect privacy rights",
    "safety": "Ensure AI systems are secure, reliable, and do not cause harm",
    "human_autonomy": "Preserve human agency and decision-making authority",
    "beneficence": "Design AI to benefit humanity and individual well-being",
    "sustainability": "Consider long-term environmental and social impacts"
}


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available ethical analysis tools."""
    return [
        Tool(
            name="analyze_ethical_scenario",
            description="Analyze an ethical scenario using multiple ethical frameworks and provide comprehensive guidance",
            inputSchema={
                "type": "object",
                "properties": {
                    "scenario": {
                        "type": "string",
                        "description": "The ethical scenario or dilemma to analyze"
                    },
                    "frameworks": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["utilitarian", "deontological", "virtue", "care"]
                        },
                        "description": "Ethical frameworks to apply (default: all)",
                        "default": ["utilitarian", "deontological", "virtue", "care"]
                    }
                },
                "required": ["scenario"]
            }
        ),
        Tool(
            name="evaluate_ai_system",
            description="Evaluate an AI system against ethical guidelines and principles",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_description": {
                        "type": "string",
                        "description": "Description of the AI system to evaluate"
                    },
                    "use_case": {
                        "type": "string",
                        "description": "The intended use case or application domain"
                    },
                    "stakeholders": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of stakeholder groups affected by the system"
                    }
                },
                "required": ["system_description", "use_case"]
            }
        ),
        Tool(
            name="check_bias",
            description="Check for potential biases in AI system design, data, or decision-making",
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {
                        "type": "string",
                        "description": "Context or description of where bias might occur"
                    },
                    "bias_types": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["selection", "confirmation", "algorithmic", "representation", "measurement"]
                        },
                        "description": "Types of bias to check for"
                    }
                },
                "required": ["context"]
            }
        ),
        Tool(
            name="generate_ethical_guidelines",
            description="Generate customized ethical guidelines for a specific AI project or use case",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_type": {
                        "type": "string",
                        "description": "Type of AI project (e.g., healthcare, finance, education)"
                    },
                    "risk_level": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Risk level of the project"
                    },
                    "regulations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Applicable regulations or standards (e.g., GDPR, HIPAA)"
                    }
                },
                "required": ["project_type"]
            }
        ),
        Tool(
            name="assess_transparency",
            description="Assess the transparency and explainability of an AI system",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_type": {
                        "type": "string",
                        "description": "Type of AI system (e.g., neural network, decision tree, LLM)"
                    },
                    "explanation_method": {
                        "type": "string",
                        "description": "Method used for explaining decisions (if any)"
                    },
                    "stakeholder_needs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Different stakeholder groups needing explanations"
                    }
                },
                "required": ["system_type"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls for ethical analysis."""
    
    if name == "analyze_ethical_scenario":
        scenario = arguments.get("scenario")
        frameworks = arguments.get("frameworks", ["utilitarian", "deontological", "virtue", "care"])
        
        analysis = f"# Ethical Analysis of Scenario\n\n**Scenario:** {scenario}\n\n"
        
        for framework_key in frameworks:
            if framework_key in ETHICAL_FRAMEWORKS:
                framework = ETHICAL_FRAMEWORKS[framework_key]
                analysis += f"\n## {framework['name']}\n\n"
                analysis += f"{framework['description']}\n\n"
                analysis += "**Key Principles:**\n"
                for principle in framework['key_principles']:
                    analysis += f"- {principle}\n"
                analysis += f"\n**Analysis:** This scenario should be evaluated considering whether it aligns with {framework['name'].lower()} principles, particularly focusing on {', '.join(framework['key_principles'][:2]).lower()}.\n"
        
        analysis += "\n## Recommendations\n\n"
        analysis += "1. Consider all stakeholders and their interests\n"
        analysis += "2. Evaluate both short-term and long-term consequences\n"
        analysis += "3. Ensure decisions respect human dignity and autonomy\n"
        analysis += "4. Seek input from diverse perspectives\n"
        analysis += "5. Document the reasoning process for accountability\n"
        
        return [TextContent(type="text", text=analysis)]
    
    elif name == "evaluate_ai_system":
        system_desc = arguments.get("system_description")
        use_case = arguments.get("use_case")
        stakeholders = arguments.get("stakeholders", [])
        
        evaluation = f"# AI System Ethical Evaluation\n\n"
        evaluation += f"**System:** {system_desc}\n\n"
        evaluation += f"**Use Case:** {use_case}\n\n"
        
        if stakeholders:
            evaluation += f"**Stakeholders:** {', '.join(stakeholders)}\n\n"
        
        evaluation += "## Ethical Guidelines Assessment\n\n"
        
        for guideline, description in AI_ETHICS_GUIDELINES.items():
            evaluation += f"### {guideline.replace('_', ' ').title()}\n"
            evaluation += f"{description}\n\n"
            evaluation += "**Assessment Questions:**\n"
            
            if guideline == "fairness":
                evaluation += "- Does the system treat all user groups equitably?\n"
                evaluation += "- Are there mechanisms to detect and mitigate bias?\n"
            elif guideline == "transparency":
                evaluation += "- Can users understand how decisions are made?\n"
                evaluation += "- Is the system's logic documented and accessible?\n"
            elif guideline == "accountability":
                evaluation += "- Who is responsible for system failures?\n"
                evaluation += "- Are there audit trails for decisions?\n"
            elif guideline == "privacy":
                evaluation += "- How is personal data collected and protected?\n"
                evaluation += "- Are privacy-by-design principles followed?\n"
            elif guideline == "safety":
                evaluation += "- What safeguards prevent harmful outcomes?\n"
                evaluation += "- How are edge cases and failures handled?\n"
            
            evaluation += "\n"
        
        evaluation += "## Recommendations\n\n"
        evaluation += "- Conduct regular ethical audits\n"
        evaluation += "- Establish an AI ethics review board\n"
        evaluation += "- Implement continuous monitoring for bias and fairness\n"
        evaluation += "- Provide clear documentation and user education\n"
        
        return [TextContent(type="text", text=evaluation)]
    
    elif name == "check_bias":
        context = arguments.get("context")
        bias_types = arguments.get("bias_types", ["selection", "confirmation", "algorithmic", "representation", "measurement"])
        
        report = f"# Bias Assessment Report\n\n**Context:** {context}\n\n"
        
        bias_descriptions = {
            "selection": "Occurs when the data sample is not representative of the population",
            "confirmation": "Tendency to interpret information confirming existing beliefs",
            "algorithmic": "Systematic errors introduced by algorithm design choices",
            "representation": "Underrepresentation or misrepresentation of certain groups",
            "measurement": "Errors in how variables are defined and measured"
        }
        
        report += "## Bias Types to Check\n\n"
        for bias_type in bias_types:
            if bias_type in bias_descriptions:
                report += f"### {bias_type.title()} Bias\n"
                report += f"{bias_descriptions[bias_type]}\n\n"
                report += "**Mitigation Strategies:**\n"
                
                if bias_type == "selection":
                    report += "- Use stratified sampling to ensure representation\n"
                    report += "- Validate data against known population distributions\n"
                elif bias_type == "algorithmic":
                    report += "- Test algorithm performance across different groups\n"
                    report += "- Use fairness-aware machine learning techniques\n"
                elif bias_type == "representation":
                    report += "- Ensure diverse data collection\n"
                    report += "- Include underrepresented groups in testing\n"
                
                report += "\n"
        
        report += "## Action Items\n\n"
        report += "1. Conduct thorough data audit\n"
        report += "2. Implement bias detection metrics\n"
        report += "3. Establish diverse review teams\n"
        report += "4. Create feedback mechanisms for affected users\n"
        
        return [TextContent(type="text", text=report)]
    
    elif name == "generate_ethical_guidelines":
        project_type = arguments.get("project_type")
        risk_level = arguments.get("risk_level", "medium")
        regulations = arguments.get("regulations", [])
        
        guidelines = f"# Ethical Guidelines for {project_type.title()} AI Project\n\n"
        guidelines += f"**Risk Level:** {risk_level.upper()}\n\n"
        
        if regulations:
            guidelines += f"**Applicable Regulations:** {', '.join(regulations)}\n\n"
        
        guidelines += "## Core Ethical Principles\n\n"
        
        # Add all core guidelines
        for idx, (key, desc) in enumerate(AI_ETHICS_GUIDELINES.items(), 1):
            guidelines += f"{idx}. **{key.replace('_', ' ').title()}:** {desc}\n"
        
        guidelines += "\n## Project-Specific Considerations\n\n"
        
        # Domain-specific guidelines
        domain_specific = {
            "healthcare": [
                "Patient privacy and confidentiality (HIPAA compliance)",
                "Clinical decision support transparency",
                "Doctor-patient relationship preservation",
                "Equitable access to care"
            ],
            "finance": [
                "Fair lending practices",
                "Transparent credit decisions",
                "Financial inclusion",
                "Regulatory compliance (SOX, PCI-DSS)"
            ],
            "education": [
                "Student data protection (FERPA compliance)",
                "Equal learning opportunities",
                "Educator autonomy preservation",
                "Developmental appropriateness"
            ],
            "criminal justice": [
                "Presumption of innocence",
                "Due process rights",
                "Bias prevention in risk assessment",
                "Transparency in sentencing recommendations"
            ]
        }
        
        project_lower = project_type.lower()
        for domain, considerations in domain_specific.items():
            if domain in project_lower:
                for consideration in considerations:
                    guidelines += f"- {consideration}\n"
                break
        else:
            guidelines += "- Identify domain-specific ethical concerns\n"
            guidelines += "- Consult with subject matter experts\n"
            guidelines += "- Review relevant industry standards\n"
        
        guidelines += "\n## Implementation Checklist\n\n"
        guidelines += "- [ ] Establish ethics review board\n"
        guidelines += "- [ ] Create ethical risk assessment process\n"
        guidelines += "- [ ] Develop incident response plan\n"
        guidelines += "- [ ] Implement continuous monitoring\n"
        guidelines += "- [ ] Provide stakeholder training\n"
        guidelines += "- [ ] Document all ethical decisions\n"
        
        if risk_level in ["high", "critical"]:
            guidelines += "- [ ] Conduct third-party ethical audit\n"
            guidelines += "- [ ] Establish public transparency reports\n"
            guidelines += "- [ ] Create external advisory board\n"
        
        return [TextContent(type="text", text=guidelines)]
    
    elif name == "assess_transparency":
        system_type = arguments.get("system_type")
        explanation_method = arguments.get("explanation_method", "None specified")
        stakeholder_needs = arguments.get("stakeholder_needs", [])
        
        assessment = f"# Transparency Assessment\n\n"
        assessment += f"**System Type:** {system_type}\n"
        assessment += f"**Explanation Method:** {explanation_method}\n\n"
        
        if stakeholder_needs:
            assessment += f"**Stakeholder Groups:** {', '.join(stakeholder_needs)}\n\n"
        
        assessment += "## Transparency Dimensions\n\n"
        
        assessment += "### 1. Input Transparency\n"
        assessment += "- What data is collected?\n"
        assessment += "- How is data preprocessed?\n"
        assessment += "- Are data sources disclosed?\n\n"
        
        assessment += "### 2. Process Transparency\n"
        assessment += "- Can the decision-making process be explained?\n"
        assessment += "- Are algorithmic steps documented?\n"
        assessment += "- Is the model architecture understandable?\n\n"
        
        assessment += "### 3. Output Transparency\n"
        assessment += "- Are confidence levels provided?\n"
        assessment += "- Can predictions be justified?\n"
        assessment += "- Are alternative outcomes shown?\n\n"
        
        assessment += "### 4. Performance Transparency\n"
        assessment += "- Are accuracy metrics disclosed?\n"
        assessment += "- Are limitations clearly stated?\n"
        assessment += "- Are failure modes documented?\n\n"
        
        assessment += "## Explainability Techniques\n\n"
        
        techniques = {
            "neural network": ["LIME", "SHAP", "Attention visualization", "Layer-wise relevance propagation"],
            "decision tree": ["Tree visualization", "Feature importance", "Decision paths"],
            "LLM": ["Prompt engineering", "Chain-of-thought", "Attribution methods", "Attention weights"],
            "ensemble": ["Feature importance", "Partial dependence plots", "Individual predictions"]
        }
        
        system_lower = system_type.lower()
        for sys_type, methods in techniques.items():
            if sys_type in system_lower:
                assessment += f"**Recommended for {system_type}:**\n"
                for method in methods:
                    assessment += f"- {method}\n"
                assessment += "\n"
                break
        
        assessment += "## Stakeholder-Specific Recommendations\n\n"
        
        stakeholder_recommendations = {
            "users": "Provide simple, jargon-free explanations of how the system affects them",
            "developers": "Maintain comprehensive technical documentation and model cards",
            "regulators": "Ensure audit trails and compliance documentation",
            "executives": "Create high-level summaries of system capabilities and limitations",
            "affected parties": "Offer clear information about data use and decision appeals"
        }
        
        if stakeholder_needs:
            for stakeholder in stakeholder_needs:
                stakeholder_lower = stakeholder.lower()
                for key, recommendation in stakeholder_recommendations.items():
                    if key in stakeholder_lower:
                        assessment += f"**{stakeholder}:** {recommendation}\n\n"
                        break
        else:
            for stakeholder, recommendation in stakeholder_recommendations.items():
                assessment += f"**{stakeholder.title()}:** {recommendation}\n\n"
        
        assessment += "## Action Items\n\n"
        assessment += "1. Implement appropriate explainability techniques\n"
        assessment += "2. Create documentation for different audiences\n"
        assessment += "3. Establish user feedback mechanisms\n"
        assessment += "4. Conduct transparency audits\n"
        assessment += "5. Provide training on system interpretation\n"
        
        return [TextContent(type="text", text=assessment)]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available ethical resources."""
    return [
        Resource(
            uri=AnyUrl("ethicist://frameworks/all"),
            name="Ethical Frameworks",
            mimeType="application/json",
            description="Complete database of major ethical frameworks and their principles"
        ),
        Resource(
            uri=AnyUrl("ethicist://guidelines/ai-ethics"),
            name="AI Ethics Guidelines",
            mimeType="application/json",
            description="Comprehensive AI ethics guidelines and principles"
        ),
        Resource(
            uri=AnyUrl("ethicist://frameworks/utilitarian"),
            name="Utilitarian Ethics",
            mimeType="application/json",
            description="Utilitarian ethical framework details"
        ),
        Resource(
            uri=AnyUrl("ethicist://frameworks/deontological"),
            name="Deontological Ethics",
            mimeType="application/json",
            description="Deontological ethical framework details"
        ),
        Resource(
            uri=AnyUrl("ethicist://frameworks/virtue"),
            name="Virtue Ethics",
            mimeType="application/json",
            description="Virtue ethics framework details"
        ),
        Resource(
            uri=AnyUrl("ethicist://frameworks/care"),
            name="Ethics of Care",
            mimeType="application/json",
            description="Ethics of care framework details"
        )
    ]


@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read ethical resource content."""
    uri_str = str(uri)
    
    if uri_str == "ethicist://frameworks/all":
        return json.dumps(ETHICAL_FRAMEWORKS, indent=2)
    
    elif uri_str == "ethicist://guidelines/ai-ethics":
        return json.dumps(AI_ETHICS_GUIDELINES, indent=2)
    
    elif uri_str.startswith("ethicist://frameworks/"):
        framework_key = uri_str.split("/")[-1]
        if framework_key in ETHICAL_FRAMEWORKS:
            return json.dumps(ETHICAL_FRAMEWORKS[framework_key], indent=2)
        else:
            raise ValueError(f"Unknown framework: {framework_key}")
    
    else:
        raise ValueError(f"Unknown resource URI: {uri_str}")


@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List available ethical reasoning prompts."""
    return [
        Prompt(
            name="ethical_decision_making",
            description="Guide users through a structured ethical decision-making process",
            arguments=[
                {
                    "name": "situation",
                    "description": "The ethical situation or decision to be made",
                    "required": True
                }
            ]
        ),
        Prompt(
            name="stakeholder_analysis",
            description="Help analyze and consider all stakeholders affected by a decision",
            arguments=[
                {
                    "name": "decision",
                    "description": "The decision or action being considered",
                    "required": True
                }
            ]
        ),
        Prompt(
            name="ai_risk_assessment",
            description="Assess potential ethical risks of an AI system",
            arguments=[
                {
                    "name": "system_description",
                    "description": "Description of the AI system",
                    "required": True
                },
                {
                    "name": "deployment_context",
                    "description": "Where and how the system will be deployed",
                    "required": False
                }
            ]
        )
    ]


@app.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
    """Get a specific ethical reasoning prompt."""
    
    if name == "ethical_decision_making":
        situation = arguments.get("situation", "a difficult choice") if arguments else "a difficult choice"
        
        return GetPromptResult(
            description="Structured ethical decision-making process",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""I need help thinking through an ethical decision: {situation}

Please help me analyze this using a structured approach:

1. **Clarify the Situation**
   - What are the key facts?
   - What is the core ethical question?
   - What is at stake?

2. **Identify Stakeholders**
   - Who will be affected by this decision?
   - What are their interests and concerns?
   - Who has power and who is vulnerable?

3. **Consider Multiple Perspectives**
   - Utilitarian: What produces the greatest good?
   - Deontological: What are my duties and obligations?
   - Virtue Ethics: What would a person of good character do?
   - Care Ethics: How can I maintain relationships and care for those affected?

4. **Evaluate Options**
   - What are the possible courses of action?
   - What are the likely consequences of each?
   - Which aligns best with ethical principles?

5. **Make a Decision**
   - What is the most ethical choice?
   - How will I implement it?
   - How will I monitor the outcome?

Please guide me through this process."""
                    )
                )
            ]
        )
    
    elif name == "stakeholder_analysis":
        decision = arguments.get("decision", "this decision") if arguments else "this decision"
        
        return GetPromptResult(
            description="Comprehensive stakeholder analysis",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""I need to analyze stakeholders for: {decision}

Help me identify and analyze all stakeholders:

1. **Direct Stakeholders** (immediately affected)
   - Who benefits directly from this decision?
   - Who might be harmed directly?
   - What are their rights and interests?

2. **Indirect Stakeholders** (secondarily affected)
   - Who else might be impacted?
   - What are the ripple effects?
   - Are there future generations to consider?

3. **Power Analysis**
   - Who has decision-making power?
   - Who is vulnerable or powerless?
   - How can we ensure fair representation?

4. **Stakeholder Engagement**
   - Who should be consulted?
   - How can we gather their input?
   - How do we balance competing interests?

5. **Equity Considerations**
   - Are any groups disproportionately affected?
   - How can we ensure fairness?
   - What are the implications for social justice?

Please help me work through each of these areas."""
                    )
                )
            ]
        )
    
    elif name == "ai_risk_assessment":
        system_desc = arguments.get("system_description", "an AI system") if arguments else "an AI system"
        context = arguments.get("deployment_context", "various contexts") if arguments else "various contexts"
        
        return GetPromptResult(
            description="AI ethical risk assessment",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""I need to assess ethical risks for: {system_desc}
Deployment context: {context}

Please help me evaluate:

1. **Fairness Risks**
   - Could the system discriminate against protected groups?
   - Is the training data representative?
   - Are there historical biases to consider?
   - How will we measure and ensure fairness?

2. **Transparency Risks**
   - Can users understand how decisions are made?
   - Is the system's logic explainable?
   - Are there "black box" concerns?
   - What documentation is needed?

3. **Privacy Risks**
   - What personal data is collected?
   - How is data protected?
   - Are privacy regulations followed?
   - Could data be misused?

4. **Safety and Security Risks**
   - What could go wrong?
   - How are errors handled?
   - Could the system be manipulated?
   - What are the failure modes?

5. **Autonomy and Control Risks**
   - Does the system preserve human agency?
   - Can decisions be appealed?
   - Is there appropriate human oversight?
   - Could it create dependency?

6. **Social Impact Risks**
   - How might this affect employment?
   - Could it increase inequality?
   - What are the environmental impacts?
   - Are there unintended consequences?

Please help me assess each risk category and recommend mitigations."""
                    )
                )
            ]
        )
    
    else:
        raise ValueError(f"Unknown prompt: {name}")


async def async_main():
    """Main entry point for the MCP server."""
    logger.info("Starting Ethicist MCP Server")
    
    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server running with stdio transport")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main():
    """Synchronous entry point for command-line usage."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
