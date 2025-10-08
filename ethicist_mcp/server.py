#!/usr/bin/env python3
"""
Ethicist MCP Server - A full-featured MCP server with Streamable HTTP support.

This server provides tools, resources, and prompts for ethical AI analysis and guidance.
"""

import asyncio
import json
import logging
import os
from typing import Any, Sequence

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
from openai import AsyncOpenAI
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
        "description": "Focuses on maximising overall happiness and well-being",
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
    "social_contract": {
        "name": "Social Contract Theory",
        "description": "Centers on fairness and mutual justification grounded in Rawlsian contractualism and Scanlonian contractarianism",
        "key_principles": [
            "Select principles that would be chosen under fair conditions, such as Rawls's veil of ignorance",
            "Ensure decisions can be justified to every affected party, following Scanlon's notion of reasonable rejection",
            "Promote equitable institutions and uphold agreed-upon obligations"
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


RESPONSIBLE_AI_FRAMEWORKS = {
    "oecd_ai_principles": {
        "name": "OECD AI Principles",
        "origin": (
            "Adopted in 2019 and revised in 2024 by OECD member and partner countries as a "
            "non-binding intergovernmental standard."
        ),
        "structure": (
            "Five value-based principles for AI actors plus complementary "
            "recommendations for public policy."
        ),
        "core_principles": [
            {
                "name": "Inclusive growth, sustainable development and well-being",
                "description": (
                    "AI should advance human and planetary well-being, reduce inequities, "
                    "and promote sustainable development."
                )
            },
            {
                "name": "Respect for human rights and democratic values",
                "description": (
                    "Align AI with rule of law, fundamental rights, privacy, and the 2024 "
                    "focus on countering mis/disinformation."
                )
            },
            {
                "name": "Transparency and explainability",
                "description": (
                    "Enable stakeholders to understand AI logic, data sources, "
                    "limitations, and uncertainty."
                )
            },
            {
                "name": "Robustness, security and safety",
                "description": (
                    "Deliver resilient, secure systems with graceful degradation, "
                    "override options, and lifecycle maintenance."
                )
            },
            {
                "name": "Accountability",
                "description": (
                    "Clarify responsibility for AI outcomes with risk management, "
                    "auditability, traceability, and redress."
                )
            }
        ],
        "policy_recommendations": [
            "Invest in AI research and development",
            "Foster trustworthy AI ecosystems and interoperable governance",
            "Strengthen human capacity and institutional readiness",
            "Align with international cooperation and standards",
            "Create enabling policy environments and infrastructure"
        ],
        "strengths": [
            "Broad international consensus while remaining flexible",
            "2024 update addresses generative AI, info integrity, and lifecycle controls"
        ],
        "challenges": [
            "High-level principles require national implementation to operationalise",
            "Tension points (privacy vs explainability, accountability vs autonomy) remain"
        ]
    },
    "eu_trustworthy_ai_guidelines": {
        "name": "EU Ethics Guidelines for Trustworthy AI",
        "origin": (
            "Developed by the European Commission's High-Level Expert Group on AI and "
            "published in April 2019 as influential but non-binding guidance."
        ),
        "three_pillars": [
            "Lawfulness: comply with applicable EU and member-state laws",
            "Ethical alignment: respect fundamental rights and societal values",
            "Robustness: maintain technical and social resilience across the lifecycle"
        ],
        "ethical_principles": [
            {
                "name": "Respect for human autonomy",
                "description": (
                    "Keep humans in control, avoid manipulation, and ensure oversight."
                )
            },
            {
                "name": "Prevention of harm",
                "description": "Avoid and mitigate foreseeable physical, psychological, or social harm."
            },
            {
                "name": "Fairness",
                "description": "Promote justice, non-discrimination, equal opportunity, and redress."
            },
            {
                "name": "Explicability",
                "description": "Provide transparency, explainability, and contestability for stakeholders."
            }
        ],
        "requirements": [
            "Human agency and oversight",
            "Technical robustness and safety",
            "Privacy and data governance",
            "Transparency",
            "Diversity, non-discrimination, and fairness",
            "Societal and environmental well-being",
            "Accountability"
        ],
        "strengths": [
            "Practical self-assessment checklists (e.g., ALTAI) enable adoption",
            "Deep grounding in EU fundamental rights and emerging regulation"
        ],
        "challenges": [
            "Implementation depends on organisations translating guidance into metrics",
            "Trade-offs between requirements can be under-specified"
        ]
    },
    "australia_ai_ethics_principles": {
        "name": "Australia's AI Ethics Principles",
        "origin": (
            "Voluntary guidance published by the Australian Government for public and "
            "private AI development, aligned with OECD norms."
        ),
        "principles": [
            "Beneficial purpose",
            "Safe and reliable",
            "Transparency and explainability",
            "Fairness",
            "Privacy protection",
            "Contestability",
            "Accountability",
            "Human, social, and environmental well-being"
        ],
        "notes": [
            "Supported by a 2024 Voluntary AI Safety Standard with 10 guardrails",
            "Government assurance frameworks map practices to these principles"
        ],
        "strengths": [
            "Flexible, interoperable with global norms",
            "Encourages translation into sector-specific assurance"
        ],
        "challenges": [
            "Voluntary status can limit compliance",
            "Requires additional tooling to measure and audit adherence"
        ]
    },
    "nist_ai_rmf": {
        "name": "NIST AI Risk Management Framework",
        "origin": (
            "Developed by the U.S. National Institute of Standards and Technology; AI RMF "
            "1.0 released in 2023 with ongoing generative AI updates."
        ),
        "core_functions": [
            {
                "name": "Govern",
                "description": "Establish roles, oversight, and accountability for AI risk."
            },
            {
                "name": "Map",
                "description": "Identify AI contexts, stakeholders, and potential harms."
            },
            {
                "name": "Measure",
                "description": "Assess risk likelihood and impact with appropriate metrics."
            },
            {
                "name": "Manage",
                "description": "Implement mitigations, monitor outcomes, and respond to incidents."
            }
        ],
        "considerations": [
            "Risk is context-dependent and evolves over the lifecycle",
            "Transparency, fairness, robustness, and accountability underpin trustworthy AI",
            "The NIST Playbook offers concrete actions and references"
        ],
        "strengths": [
            "Process-oriented and adaptable to diverse domains",
            "Widely referenced by industry (e.g., Microsoft Responsible AI)"
        ],
        "challenges": [
            "Voluntary adoption can leave gaps, especially for smaller organisations",
            "Quantifying social or ethical harms remains difficult"
        ]
    },
    "microsoft_responsible_ai_principles": {
        "name": "Microsoft Responsible AI Principles",
        "origin": (
            "Microsoft's internal and public commitments that guide AI product "
            "development, supported by governance standards and tooling."
        ),
        "principles": [
            "Fairness",
            "Reliability and safety",
            "Privacy and security",
            "Inclusiveness",
            "Transparency",
            "Accountability"
        ],
        "operational_approach": [
            "Align governance with the NIST AI RMF",
            "Publish Transparency Notes documenting system limitations",
            "Use internal tooling and policy gates to enforce standards"
        ],
        "strengths": [
            "Concrete tooling and processes translate principles into practice",
            "Demonstrates how a large organisation operationalises responsible AI"
        ],
        "challenges": [
            "Organisation-specific perspective may miss domain nuances",
            "Implementation gaps between stated principles and deployed systems"
        ]
    },
    "responsible_ai_additional_references": {
        "name": "Other Notable Responsible AI Frameworks",
        "highlights": [
            "IEEE Ethically Aligned Design and IEEE 7000 value-based engineering standards",
            "Responsible AI Pattern Catalogue (CSIRO and research community) mapping principles to patterns",
            "UN human-rights-centred AI proposals",
            "Toronto Declaration emphasising equality and non-discrimination",
            "Asilomar AI Principles articulating safety and long-term AI governance"
        ]
    }
}


OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
SYSTEM_PROMPT = (
    "You are the Ethicist MCP Server, an expert in responsible and ethical AI. "
    "Respond in Australian English, provide well-structured Markdown output, and ground your guidance "
    "in recognised ethical frameworks, responsible AI standards, and practical governance steps. "
    "Always highlight stakeholder impacts, risk mitigation, and actionable recommendations."
)
_openai_client: AsyncOpenAI | None = None


def _get_openai_client() -> AsyncOpenAI | None:
    """Initialise and cache the OpenAI client if an API key is configured."""
    global _openai_client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=api_key)
    return _openai_client


async def _generate_openai_response(subject: str, user_prompt: str, *, temperature: float = 0.7) -> str:
    """
    Generate a response from OpenAI with consistent formatting and graceful fallbacks.
    
    Args:
        subject: Short description of the request for logging and fallback messaging.
        user_prompt: The prompt delivered to the model.
        temperature: Sampling temperature for creativity vs determinism.
    """
    client = _get_openai_client()
    if client is None:
        logger.warning("OpenAI API key not configured; returning fallback content for '%s'.", subject)
        return (
            "Warning: OpenAI API key not configured (set `OPENAI_API_KEY`).\n\n"
            f"Requested content could not be generated automatically:\n{subject}\n\n"
            "Provide a valid API key to enable AI-generated analyses."
        )
    
    try:
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=temperature,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
    except Exception as exc:  # pragma: no cover - network failures are runtime concerns
        logger.error("Error calling OpenAI for '%s': %s", subject, exc, exc_info=True)
        return (
            "Warning: Encountered an error while contacting OpenAI.\n\n"
            f"Subject: {subject}\nError: {exc}\n\n"
            "Please retry later or review API credentials."
        )
    
    message = response.choices[0].message if response.choices else None
    content = getattr(message, "content", "") if message else ""
    cleaned = content.strip() if content else ""
    if not cleaned:
        logger.warning("OpenAI returned an empty response for '%s'.", subject)
        return (
            "Warning: OpenAI returned an empty response.\n\n"
            f"Subject: {subject}\n\n"
            "Consider reissuing the request or adjusting the input context."
        )
    return cleaned


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available ethical analysis tools."""
    return [
        Tool(
            name="analyze_ethical_scenario",
            description="Analyse an ethical scenario using multiple ethical frameworks and provide comprehensive guidance",
            inputSchema={
                "type": "object",
                "properties": {
                    "scenario": {
                        "type": "string",
                        "description": "The ethical scenario or dilemma to analyse"
                    },
                    "frameworks": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["utilitarian", "deontological", "virtue", "social_contract"]
                        },
                        "description": "Ethical frameworks to apply (default: all)",
                        "default": ["utilitarian", "deontological", "virtue", "social_contract"]
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
            description="Generate customised ethical guidelines for a specific AI project or use case",
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
        if not scenario:
            return [TextContent(type="text", text="Warning: The 'scenario' argument is required.")]
        
        frameworks = arguments.get("frameworks", ["utilitarian", "deontological", "virtue", "social_contract"])
        framework_blocks: list[str] = []
        for key in frameworks:
            framework = ETHICAL_FRAMEWORKS.get(key)
            if framework:
                principles = "\n".join(f"- {item}" for item in framework["key_principles"])
                framework_blocks.append(
                    f"### {framework['name']}\nDescription: {framework['description']}\nKey principles:\n{principles}"
                )
        frameworks_context = "\n\n".join(framework_blocks) if framework_blocks else "No recognised frameworks provided."
        
        user_prompt = (
            f"Scenario:\n{scenario}\n\n"
            f"Framework context:\n{frameworks_context}\n\n"
            "Analyse the scenario using each framework. For every framework include:\n"
            "- Core ethical focus and obligations\n"
            "- Scenario-specific assessment referencing the listed principles\n"
            "- Key risks, impacted stakeholders, and tension points\n"
            "- Practical mitigation or decision guidance\n\n"
            "Conclude with:\n"
            "- Cross-framework synthesis highlighting convergences/divergences\n"
            "- Actionable recommendations and governance checkpoints\n"
            "- Risk register (high/medium/low) with monitoring cues."
        )
        
        analysis = await _generate_openai_response("Ethical scenario analysis", user_prompt)
        return [TextContent(type="text", text=analysis)]
    
    elif name == "evaluate_ai_system":
        system_desc = arguments.get("system_description")
        use_case = arguments.get("use_case")
        stakeholders = arguments.get("stakeholders", [])
        
        if not system_desc or not use_case:
            return [TextContent(type="text", text="Warning: 'system_description' and 'use_case' are required.")]
        
        guideline_summary = "\n".join(
            f"- {key.replace('_', ' ').title()}: {value}"
            for key, value in AI_ETHICS_GUIDELINES.items()
        )
        stakeholder_line = ", ".join(stakeholders) if stakeholders else "Not specified"
        
        user_prompt = (
            f"Evaluate the ethical posture of an AI system.\n\n"
            f"System description: {system_desc}\n"
            f"Use case: {use_case}\n"
            f"Stakeholders: {stakeholder_line}\n\n"
            "Reference guidelines and principles:\n"
            f"{guideline_summary}\n\n"
            "Produce a Markdown report with sections for each guideline. For every section include:\n"
            "- Strengths currently observed or targeted\n"
            "- Gaps or risks with severity ratings\n"
            "- Mitigation actions, owners, and timelines\n"
            "- Metrics or signals to monitor\n\n"
            "After the per-guideline analysis provide:\n"
            "- A consolidated risk heatmap\n"
            "- Immediate, short-term, and long-term recommendations\n"
            "- Governance artefacts needed (policies, audits, documentation)\n"
            "- Stakeholder engagement plan."
        )
        
        evaluation = await _generate_openai_response("AI system ethical evaluation", user_prompt)
        return [TextContent(type="text", text=evaluation)]
    
    elif name == "check_bias":
        context = arguments.get("context")
        bias_types = arguments.get("bias_types", ["selection", "confirmation", "algorithmic", "representation", "measurement"])
        
        bias_descriptions = {
            "selection": "Occurs when the data sample is not representative of the population",
            "confirmation": "Tendency to interpret information confirming existing beliefs",
            "algorithmic": "Systematic errors introduced by algorithm design choices",
            "representation": "Underrepresentation or misrepresentation of certain groups",
            "measurement": "Errors in how variables are defined and measured"
        }
        
        if not context:
            return [TextContent(type="text", text="Warning: The 'context' argument is required.")]
        
        bias_blocks = "\n".join(
            f"- {bias_type.title()} bias: {bias_descriptions.get(bias_type, 'No definition available')}"
            for bias_type in bias_types
        )
        
        user_prompt = (
            f"Context for bias assessment:\n{context}\n\n"
            f"Bias types to evaluate:\n{bias_blocks}\n\n"
            "Deliver a structured bias risk assessment that includes:\n"
            "- Diagnostic questions and tests for each bias type\n"
            "- Evidence to collect or metrics to review\n"
            "- Likely impacts on stakeholders and compliance obligations\n"
            "- Concrete mitigation strategies (data, model, process, governance)\n"
            "- Residual risk and monitoring plans\n"
            "- Checklist for ongoing assurance."
        )
        
        report = await _generate_openai_response("Bias assessment", user_prompt)
        return [TextContent(type="text", text=report)]
    
    elif name == "generate_ethical_guidelines":
        project_type = arguments.get("project_type")
        risk_level = arguments.get("risk_level", "medium")
        regulations = arguments.get("regulations", [])
        
        if not project_type:
            return [TextContent(type="text", text="Warning: The 'project_type' argument is required.")]
        
        regulations_line = ", ".join(regulations) if regulations else "None specified"
        guideline_summary = "\n".join(
            f"- {key.replace('_', ' ').title()}: {value}"
            for key, value in AI_ETHICS_GUIDELINES.items()
        )
        
        user_prompt = (
            f"Create ethical guidelines.\n\n"
            f"Project type: {project_type}\n"
            f"Risk level: {risk_level}\n"
            f"Regulations or standards: {regulations_line}\n\n"
            "Relevant ethical principles:\n"
            f"{guideline_summary}\n\n"
            "Output a Markdown guide containing:\n"
            "- Executive summary with risk posture\n"
            "- Principle-by-principle requirements with acceptance criteria\n"
            "- Domain-specific considerations (reference regulations if provided)\n"
            "- Roles and responsibilities matrix\n"
            "- Implementation roadmap (immediate, near-term, long-term)\n"
            "- Assurance activities (audits, evaluations, reporting)\n"
            "- Stakeholder engagement and communication plan\n"
            "- KPIs/metrics for ongoing monitoring."
        )
        
        guidelines_text = await _generate_openai_response("Project ethical guidelines", user_prompt)
        return [TextContent(type="text", text=guidelines_text)]
    
    elif name == "assess_transparency":
        system_type = arguments.get("system_type")
        explanation_method = arguments.get("explanation_method")
        stakeholder_needs = arguments.get("stakeholder_needs", [])
        
        if not system_type:
            return [TextContent(type="text", text="Warning: The 'system_type' argument is required.")]
        
        explanation_line = explanation_method or "Not specified"
        stakeholders_line = ", ".join(stakeholder_needs) if stakeholder_needs else "Not specified"
        
        user_prompt = (
            "Prepare a transparency and explainability assessment.\n\n"
            f"System type: {system_type}\n"
            f"Explanation method: {explanation_line}\n"
            f"Stakeholder needs: {stakeholders_line}\n\n"
            "Address the following:\n"
            "- Transparency objectives for each stakeholder group\n"
            "- Current explanation techniques and their adequacy\n"
            "- Gaps in comprehensibility, documentation, or tooling\n"
            "- Risks related to opacity, misinterpretation, or misuse\n"
            "- Recommendations for improving transparency (technical, process, communication)\n"
            "- Evidence required for regulatory or assurance purposes\n"
            "- Plan for monitoring transparency effectiveness over time."
        )
        
        assessment = await _generate_openai_response("Transparency assessment", user_prompt)
        return [TextContent(type="text", text=assessment)]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available ethical resources."""
    resources: list[Resource] = [
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
            uri=AnyUrl("ethicist://frameworks/social_contract"),
            name="Social Contract Theory",
            mimeType="application/json",
            description="Social contract theory framework details rooted in Rawlsian and Scanlonian perspectives"
        ),
        Resource(
            uri=AnyUrl("ethicist://frameworks/responsible_ai"),
            name="Responsible AI Frameworks Overview",
            mimeType="application/json",
            description="Aggregated view of OECD, EU, Australia, NIST, Microsoft, and related responsible AI frameworks"
        )
    ]

    for key, data in RESPONSIBLE_AI_FRAMEWORKS.items():
        resources.append(
            Resource(
                uri=AnyUrl(f"ethicist://frameworks/{key}"),
                name=data.get("name", key.replace("_", " ").title()),
                mimeType="application/json",
                description=data.get(
                    "origin",
                    "Detailed reference material for responsible AI frameworks"
                )
            )
        )

    return resources


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
        if framework_key == "responsible_ai":
            return json.dumps(RESPONSIBLE_AI_FRAMEWORKS, indent=2)
        if framework_key in ETHICAL_FRAMEWORKS:
            return json.dumps(ETHICAL_FRAMEWORKS[framework_key], indent=2)
        if framework_key in RESPONSIBLE_AI_FRAMEWORKS:
            return json.dumps(RESPONSIBLE_AI_FRAMEWORKS[framework_key], indent=2)
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
            description="Help analyse and consider all stakeholders affected by a decision",
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

Please help me analyse this using a structured approach:

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
   - Social Contract: Would this decision be acceptable under fair terms to all affected parties?

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
                        text=f"""I need to analyse stakeholders for: {decision}

Help me identify and analyse all stakeholders:

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
