"""
Specialized autonomous agents for different SDLC phases
Each agent acts as a domain expert with connector integration
"""

import uuid
import json
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent, AgentRole, AgentDecision, AgentAction
from ..connectors.base_connector import ConnectorType
from ..state.sdlc_state import SDLCState, UserStories, UserStoryList


class ProjectManagerAgent(BaseAgent):
    """Autonomous project manager agent that handles project initialization and coordination"""
    
    def __init__(self, llm, connector_manager):
        super().__init__(AgentRole.PROJECT_MANAGER, llm, connector_manager)
        self.capabilities = [
            "project_planning", "resource_allocation", "stakeholder_communication",
            "risk_assessment", "timeline_management", "connector_orchestration"
        ]
    
    async def analyze(self, state: SDLCState, context: Dict[str, Any]) -> AgentDecision:
        """Analyze project state and make management decisions"""
        
        # Get insights from connected systems
        insights = await self.get_connector_insights([
            ConnectorType.PROJECT_MANAGEMENT, 
            ConnectorType.VERSION_CONTROL,
            ConnectorType.COMMUNICATION
        ])
        
        project_name = state.get("project_name", "")
        requirements = state.get("requirements", [])
        
        prompt = f"""
        As an autonomous project manager agent analyzing project: "{project_name}"
        
        Current state:
        - Requirements: {requirements}
        - Phase: Project initialization
        
        External system insights:
        {json.dumps(insights, indent=2)}
        
        Your memory context:
        {json.dumps(self.get_memory_context(), indent=2)}
        
        Analyze the situation and decide on the best course of action for:
        1. Setting up project infrastructure
        2. Coordinating with external systems
        3. Managing stakeholder communication
        4. Risk mitigation strategies
        
        Provide reasoning for your decisions and assign confidence levels.
        """
        
        response = await self.llm.ainvoke(prompt)
        
        # Generate autonomous actions
        actions = [
            AgentAction(
                action_type="setup_project_repository",
                target="github",
                parameters={"project_name": project_name, "private": False},
                connector_involved="github",
                priority=1,
                estimated_duration=10
            ),
            AgentAction(
                action_type="create_project_channel",
                target="slack",
                parameters={"project_name": project_name},
                connector_involved="slack",
                priority=2,
                estimated_duration=5
            ),
            AgentAction(
                action_type="initialize_jira_project",
                target="jira",
                parameters={"project_name": project_name, "project_key": project_name[:10].upper()},
                connector_involved="jira",
                priority=3,
                estimated_duration=15
            )
        ]
        
        return AgentDecision(
            decision_id=f"pm_{uuid.uuid4().hex[:8]}",
            agent_role=self.role,
            context={"insights": insights, "analysis_context": context},
            reasoning=f"Project setup requires coordinated initialization across GitHub, Slack, and Jira. {response.content[:500]}",
            confidence=0.85,
            actions=actions
        )
    
    async def execute_action(self, action: AgentAction, state: SDLCState) -> Dict[str, Any]:
        """Execute project management actions"""
        try:
            if action.action_type == "setup_project_repository":
                result = await self.connector_manager.execute_connector_action(
                    "github",
                    "send_data",
                    {
                        "action": "create_repository",
                        "repository_data": {
                            "name": action.parameters["project_name"].replace(" ", "-").lower(),
                            "description": f"Autonomous SDLC project: {action.parameters['project_name']}",
                            "private": action.parameters.get("private", False)
                        }
                    }
                )
                
                if result.success:
                    repo_name = result.data.get("created_repository")
                    await self.notify_progress(f"✅ Project repository created: {repo_name}")
                    return {"success": True, "repository": repo_name}
                
            elif action.action_type == "create_project_channel":
                result = await self.connector_manager.execute_connector_action(
                    "slack",
                    "send_data",
                    {
                        "action": "create_channel",
                        "channel_name": f"devpilot-{action.parameters['project_name'].lower().replace(' ', '-')}",
                        "is_private": False
                    }
                )
                
                if result.success:
                    channel_id = result.data.get("created_channel", {}).get("id")
                    await self.notify_progress(f"✅ Project communication channel created")
                    return {"success": True, "channel_id": channel_id}
                    
            elif action.action_type == "initialize_jira_project":
                # This would require more complex Jira project creation
                await self.notify_progress(f"📋 Jira project initialization planned for: {action.parameters['project_name']}")
                return {"success": True, "message": "Jira project initialization planned"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Unknown action"}


class BusinessAnalystAgent(BaseAgent):
    """Autonomous business analyst that generates and refines user stories"""
    
    def __init__(self, llm, connector_manager):
        super().__init__(AgentRole.BUSINESS_ANALYST, llm, connector_manager)
        self.capabilities = [
            "requirements_analysis", "user_story_generation", "acceptance_criteria_definition",
            "stakeholder_needs_assessment", "business_process_modeling"
        ]
    
    async def analyze(self, state: SDLCState, context: Dict[str, Any]) -> AgentDecision:
        """Analyze requirements and decide on user story approach"""
        
        requirements = state.get("requirements", [])
        project_name = state.get("project_name", "")
        feedback = state.get("user_stories_feedback")
        
        # Get insights from project management tools
        insights = await self.get_connector_insights([ConnectorType.PROJECT_MANAGEMENT])
        
        prompt = f"""
        As an autonomous business analyst, analyze these requirements for "{project_name}":
        
        Requirements: {requirements}
        Previous feedback: {feedback if feedback else "None"}
        External insights: {json.dumps(insights, indent=2)}
        
        Determine the optimal approach for user story generation considering:
        1. Complexity of requirements
        2. User personas that need to be considered
        3. Business value priorities
        4. Acceptance criteria complexity
        
        Provide strategic recommendations for user story creation.
        """
        
        response = await self.llm.ainvoke(prompt)
        
        actions = [
            AgentAction(
                action_type="generate_enhanced_user_stories",
                target="internal",
                parameters={
                    "requirements": requirements,
                    "project_name": project_name,
                    "enhancement_strategy": "persona_driven"
                },
                priority=1,
                estimated_duration=20
            ),
            AgentAction(
                action_type="sync_user_stories_to_jira",
                target="jira",
                parameters={"project_key": project_name[:10].upper()},
                connector_involved="jira",
                priority=2,
                estimated_duration=10
            )
        ]
        
        return AgentDecision(
            decision_id=f"ba_{uuid.uuid4().hex[:8]}",
            agent_role=self.role,
            context={"requirements_analysis": response.content, "insights": insights},
            reasoning="Enhanced user story generation with persona-driven approach and external system integration",
            confidence=0.90,
            actions=actions
        )
    
    async def execute_action(self, action: AgentAction, state: SDLCState) -> Dict[str, Any]:
        """Execute business analysis actions"""
        
        if action.action_type == "generate_enhanced_user_stories":
            # Enhanced user story generation with AI
            requirements = action.parameters["requirements"]
            project_name = action.parameters["project_name"]
            
            prompt = f"""
            You are a senior business analyst with 10+ years of experience in Agile methodologies.
            Generate comprehensive user stories for project "{project_name}" based on these requirements:
            
            Requirements: {requirements}
            
            For each requirement, create detailed user stories that include:
            1. Multiple user personas (end-user, admin, system, etc.)
            2. Detailed acceptance criteria with Given-When-Then format
            3. Business value estimation
            4. Dependencies and risks
            5. Definition of done
            
            Ensure stories are INVEST compliant (Independent, Negotiable, Valuable, Estimable, Small, Testable).
            """
            
            llm_with_structured = self.llm.with_structured_output(UserStoryList)
            user_stories = llm_with_structured.invoke(prompt)
            
            # Update state with generated stories
            updated_state = {"user_stories": user_stories}
            
            await self.notify_progress(f"📝 Generated {len(user_stories.user_stories)} enhanced user stories")
            
            return {
                "success": True, 
                "updated_state": updated_state,
                "stories_count": len(user_stories.user_stories)
            }
        
        elif action.action_type == "sync_user_stories_to_jira":
            user_stories = state.get("user_stories")
            if user_stories and hasattr(user_stories, 'user_stories'):
                stories_data = []
                for story in user_stories.user_stories:
                    stories_data.append({
                        "title": story.title,
                        "description": story.description,
                        "priority": story.priority,
                        "acceptance_criteria": story.acceptance_criteria
                    })
                
                result = await self.connector_manager.execute_connector_action(
                    "jira",
                    "send_data",
                    {
                        "action": "sync_user_stories",
                        "project_key": action.parameters["project_key"],
                        "user_stories": stories_data
                    }
                )
                
                if result.success:
                    await self.notify_progress(f"📋 Synced {len(stories_data)} user stories to Jira")
                    return {"success": True, "synced_count": len(stories_data)}
        
        return {"success": False, "error": "Action not implemented"}


class SoftwareArchitectAgent(BaseAgent):
    """Autonomous software architect for system design"""
    
    def __init__(self, llm, connector_manager):
        super().__init__(AgentRole.SOFTWARE_ARCHITECT, llm, connector_manager)
        self.capabilities = [
            "system_architecture", "technology_selection", "design_patterns",
            "scalability_planning", "security_architecture", "integration_design"
        ]
    
    async def analyze(self, state: SDLCState, context: Dict[str, Any]) -> AgentDecision:
        """Analyze system requirements and create architectural decisions"""
        
        user_stories = state.get("user_stories")
        project_name = state.get("project_name", "")
        
        # Analyze user stories to determine architectural requirements
        stories_text = ""
        if user_stories and hasattr(user_stories, 'user_stories'):
            stories_text = "\n".join([f"- {story.title}: {story.description}" for story in user_stories.user_stories])
        
        prompt = f"""
        As an autonomous software architect, analyze the system requirements for "{project_name}":
        
        User Stories Summary:
        {stories_text}
        
        Determine the optimal system architecture considering:
        1. Scalability requirements
        2. Technology stack selection
        3. Integration patterns
        4. Security considerations
        5. Performance requirements
        6. Deployment strategy
        
        Provide architectural recommendations and design decisions.
        """
        
        response = await self.llm.ainvoke(prompt)
        
        actions = [
            AgentAction(
                action_type="create_technical_design",
                target="internal",
                parameters={
                    "project_name": project_name,
                    "architecture_style": "microservices",  # Could be determined dynamically
                    "tech_stack": "python_fastapi"
                },
                priority=1,
                estimated_duration=45
            ),
            AgentAction(
                action_type="create_architecture_diagrams",
                target="internal",
                parameters={"diagram_types": ["system", "component", "deployment"]},
                priority=2,
                estimated_duration=30
            )
        ]
        
        return AgentDecision(
            decision_id=f"arch_{uuid.uuid4().hex[:8]}",
            agent_role=self.role,
            context={"architectural_analysis": response.content},
            reasoning="System architecture design based on user story analysis and scalability requirements",
            confidence=0.85,
            actions=actions
        )
    
    async def execute_action(self, action: AgentAction, state: SDLCState) -> Dict[str, Any]:
        """Execute architectural design actions"""
        
        if action.action_type == "create_technical_design":
            # Generate comprehensive technical design document
            user_stories = state.get("user_stories")
            stories_context = ""
            
            if user_stories and hasattr(user_stories, 'user_stories'):
                stories_context = "\n".join([
                    f"Story: {story.title}\nDescription: {story.description}\nCriteria: {story.acceptance_criteria}\n"
                    for story in user_stories.user_stories[:5]  # Limit for context
                ])
            
            prompt = f"""
            Create a comprehensive technical design document for the project based on these user stories:
            
            {stories_context}
            
            Architecture Style: {action.parameters['architecture_style']}
            Technology Stack: {action.parameters['tech_stack']}
            
            Include:
            1. System Architecture Overview
            2. Component Design
            3. Data Architecture
            4. API Design
            5. Security Architecture
            6. Deployment Architecture
            7. Technology Justifications
            8. Performance Considerations
            9. Scalability Plan
            10. Integration Points
            """
            
            technical_design = await self.llm.ainvoke(prompt)
            
            # Create functional design as well
            functional_prompt = f"""
            Create a functional design document that complements the technical design:
            
            User Stories Context:
            {stories_context}
            
            Include:
            1. Business Process Flows
            2. User Journey Mapping
            3. Functional Requirements Detail
            4. Business Rules
            5. Data Flow Diagrams
            6. User Interface Design Principles
            7. Integration Requirements
            8. Acceptance Testing Strategy
            """
            
            functional_design = await self.llm.ainvoke(functional_prompt)
            
            design_documents = {
                "technical": technical_design.content,
                "functional": functional_design.content
            }
            
            updated_state = {"design_documents": design_documents}
            
            await self.notify_progress("📋 Created comprehensive design documents")
            
            return {
                "success": True,
                "updated_state": updated_state,
                "documents_created": 2
            }
        
        return {"success": False, "error": "Action not implemented"}


class DeveloperAgent(BaseAgent):
    """Autonomous developer agent for code generation and implementation"""
    
    def __init__(self, llm, connector_manager):
        super().__init__(AgentRole.DEVELOPER, llm, connector_manager)
        self.capabilities = [
            "code_generation", "refactoring", "debugging", "version_control",
            "code_review", "testing", "documentation"
        ]
    
    async def analyze(self, state: SDLCState, context: Dict[str, Any]) -> AgentDecision:
        """Analyze design documents and plan code generation"""
        
        design_docs = state.get("design_documents", {})
        user_stories = state.get("user_stories")
        
        # Get insights from version control
        insights = await self.get_connector_insights([ConnectorType.VERSION_CONTROL])
        
        prompt = f"""
        As an autonomous developer agent, analyze the design documents and plan code implementation:
        
        Technical Design Available: {"Yes" if design_docs.get("technical") else "No"}
        Functional Design Available: {"Yes" if design_docs.get("functional") else "No"}
        User Stories Count: {len(user_stories.user_stories) if user_stories and hasattr(user_stories, 'user_stories') else 0}
        
        Repository insights: {json.dumps(insights, indent=2)}
        
        Plan the development approach considering:
        1. Code architecture implementation
        2. Development patterns to follow
        3. Testing strategy
        4. Version control workflow
        5. Code quality standards
        """
        
        response = await self.llm.ainvoke(prompt)
        
        actions = [
            AgentAction(
                action_type="generate_project_structure",
                target="internal",
                parameters={"framework": "fastapi", "database": "postgresql"},
                priority=1,
                estimated_duration=20
            ),
            AgentAction(
                action_type="implement_core_features",
                target="internal",
                parameters={"implementation_strategy": "mvp_first"},
                priority=2,
                estimated_duration=60
            ),
            AgentAction(
                action_type="create_pull_request",
                target="github",
                parameters={"branch": "feature/initial-implementation"},
                connector_involved="github",
                priority=3,
                estimated_duration=10
            )
        ]
        
        return AgentDecision(
            decision_id=f"dev_{uuid.uuid4().hex[:8]}",
            agent_role=self.role,
            context={"development_plan": response.content, "insights": insights},
            reasoning="Systematic code implementation with automated testing and version control integration",
            confidence=0.88,
            actions=actions
        )
    
    async def execute_action(self, action: AgentAction, state: SDLCState) -> Dict[str, Any]:
        """Execute development actions"""
        
        if action.action_type == "generate_project_structure":
            # Generate comprehensive code based on design documents
            design_docs = state.get("design_documents", {})
            user_stories = state.get("user_stories")
            
            technical_design = design_docs.get("technical", "")
            
            stories_context = ""
            if user_stories and hasattr(user_stories, 'user_stories'):
                stories_context = "\n".join([
                    f"Feature: {story.title}\nRequirements: {story.description}\nAcceptance: {story.acceptance_criteria}"
                    for story in user_stories.user_stories
                ])
            
            prompt = f"""
            Generate a complete, production-ready codebase based on the technical design and user stories:
            
            Technical Design:
            {technical_design[:2000]}  # Limit for context
            
            User Stories to Implement:
            {stories_context[:3000]}  # Limit for context
            
            Framework: {action.parameters['framework']}
            Database: {action.parameters['database']}
            
            Generate:
            1. Project structure with proper directories
            2. Main application files
            3. API endpoints based on user stories
            4. Database models
            5. Configuration files
            6. Requirements/dependencies
            7. Basic tests
            8. Documentation
            9. Docker configuration
            10. CI/CD pipeline configuration
            
            Ensure code follows best practices, includes error handling, logging, and is production-ready.
            """
            
            generated_code = await self.llm.ainvoke(prompt)
            
            updated_state = {"code_generated": generated_code.content}
            
            await self.notify_progress("💻 Generated complete project codebase with best practices")
            
            return {
                "success": True,
                "updated_state": updated_state,
                "code_generated": True
            }
        
        elif action.action_type == "create_pull_request":
            # Create PR in GitHub
            project_name = state.get("project_name", "")
            repo_name = project_name.replace(" ", "-").lower()
            
            pr_data = {
                "title": "Initial autonomous implementation",
                "body": """
## Autonomous Implementation by DevPilot

This PR contains the initial implementation generated by the autonomous developer agent.

### Features Implemented:
- Complete project structure
- API endpoints based on user stories
- Database models
- Configuration and deployment files
- Basic tests

### Generated by:
🤖 DevPilot Autonomous Developer Agent

### Review Notes:
- Code follows established patterns and best practices
- All user stories have been considered in implementation
- Security recommendations have been incorporated
                """,
                "head": action.parameters["branch"],
                "base": "main"
            }
            
            result = await self.connector_manager.execute_connector_action(
                "github",
                "send_data",
                {
                    "action": "create_pull_request",
                    "repository": f"owner/{repo_name}",  # Should be configurable
                    "pull_request_data": pr_data
                }
            )
            
            if result.success:
                pr_url = result.data.get("created_pull_request", {}).get("url")
                await self.notify_progress(f"🔄 Created pull request for review: {pr_url}")
                return {"success": True, "pr_created": True}
        
        return {"success": False, "error": "Action not implemented"}


class SecurityExpertAgent(BaseAgent):
    """Autonomous security expert for security analysis and recommendations"""
    
    def __init__(self, llm, connector_manager):
        super().__init__(AgentRole.SECURITY_EXPERT, llm, connector_manager)
        self.capabilities = [
            "security_analysis", "vulnerability_assessment", "threat_modeling",
            "security_architecture_review", "compliance_checking", "penetration_testing"
        ]
    
    async def analyze(self, state: SDLCState, context: Dict[str, Any]) -> AgentDecision:
        """Analyze code and architecture for security vulnerabilities"""
        
        code_generated = state.get("code_generated", "")
        design_docs = state.get("design_documents", {})
        
        prompt = f"""
        As an autonomous security expert, perform comprehensive security analysis:
        
        Code Available: {"Yes" if code_generated else "No"}
        Design Documents Available: {"Yes" if design_docs else "No"}
        
        Analyze for:
        1. Common security vulnerabilities (OWASP Top 10)
        2. Authentication and authorization flaws
        3. Data protection issues
        4. API security concerns
        5. Infrastructure security
        6. Compliance requirements
        
        Provide specific, actionable security recommendations.
        """
        
        response = await self.llm.ainvoke(prompt)
        
        actions = [
            AgentAction(
                action_type="perform_security_scan",
                target="internal",
                parameters={"scan_type": "comprehensive"},
                priority=1,
                estimated_duration=25
            ),
            AgentAction(
                action_type="generate_security_recommendations",
                target="internal",
                parameters={"focus_areas": ["authentication", "api_security", "data_protection"]},
                priority=2,
                estimated_duration=20
            )
        ]
        
        return AgentDecision(
            decision_id=f"sec_{uuid.uuid4().hex[:8]}",
            agent_role=self.role,
            context={"security_analysis": response.content},
            reasoning="Comprehensive security analysis with focus on OWASP guidelines and best practices",
            confidence=0.92,
            actions=actions
        )
    
    async def execute_action(self, action: AgentAction, state: SDLCState) -> Dict[str, Any]:
        """Execute security analysis actions"""
        
        if action.action_type == "generate_security_recommendations":
            code_generated = state.get("code_generated", "")
            design_docs = state.get("design_documents", {})
            
            prompt = f"""
            Perform detailed security analysis and generate comprehensive recommendations:
            
            Code to analyze:
            {code_generated[:4000] if code_generated else "No code available"}
            
            Technical design context:
            {design_docs.get('technical', '')[:2000] if design_docs.get('technical') else 'No design available'}
            
            Focus areas: {action.parameters['focus_areas']}
            
            Provide:
            1. Identified security vulnerabilities
            2. Risk assessment for each vulnerability
            3. Specific remediation steps
            4. Code examples for fixes
            5. Security best practices to implement
            6. Compliance considerations
            7. Security testing recommendations
            8. Monitoring and alerting suggestions
            
            Format as actionable security recommendations with priority levels.
            """
            
            security_analysis = await self.llm.ainvoke(prompt)
            
            updated_state = {"security_recommendations": security_analysis.content}
            
            await self.notify_progress("🔒 Completed comprehensive security analysis")
            
            return {
                "success": True,
                "updated_state": updated_state,
                "vulnerabilities_identified": True
            }
        
        return {"success": False, "error": "Action not implemented"}


class QAEngineerAgent(BaseAgent):
    """Autonomous QA engineer for testing and quality assurance"""
    
    def __init__(self, llm, connector_manager):
        super().__init__(AgentRole.QA_ENGINEER, llm, connector_manager)
        self.capabilities = [
            "test_planning", "test_automation", "quality_assurance",
            "bug_detection", "performance_testing", "regression_testing"
        ]
    
    async def analyze(self, state: SDLCState, context: Dict[str, Any]) -> AgentDecision:
        """Analyze system for testing requirements"""
        
        user_stories = state.get("user_stories")
        code_generated = state.get("code_generated", "")
        
        stories_count = len(user_stories.user_stories) if user_stories and hasattr(user_stories, 'user_stories') else 0
        
        prompt = f"""
        As an autonomous QA engineer, plan comprehensive testing strategy:
        
        User Stories: {stories_count}
        Code Available: {"Yes" if code_generated else "No"}
        
        Plan testing approach for:
        1. Unit testing coverage
        2. Integration testing
        3. API testing
        4. Performance testing
        5. Security testing
        6. User acceptance testing
        
        Determine testing priorities and automation opportunities.
        """
        
        response = await self.llm.ainvoke(prompt)
        
        actions = [
            AgentAction(
                action_type="generate_test_cases",
                target="internal",
                parameters={"test_types": ["unit", "integration", "api", "e2e"]},
                priority=1,
                estimated_duration=40
            ),
            AgentAction(
                action_type="create_test_automation",
                target="internal",
                parameters={"framework": "pytest"},
                priority=2,
                estimated_duration=30
            ),
            AgentAction(
                action_type="execute_qa_testing",
                target="internal",
                parameters={"test_suite": "comprehensive"},
                priority=3,
                estimated_duration=25
            )
        ]
        
        return AgentDecision(
            decision_id=f"qa_{uuid.uuid4().hex[:8]}",
            agent_role=self.role,
            context={"testing_strategy": response.content},
            reasoning="Comprehensive testing strategy with automation focus and multi-level coverage",
            confidence=0.90,
            actions=actions
        )
    
    async def execute_action(self, action: AgentAction, state: SDLCState) -> Dict[str, Any]:
        """Execute QA testing actions"""
        
        if action.action_type == "generate_test_cases":
            user_stories = state.get("user_stories")
            code_generated = state.get("code_generated", "")
            
            stories_context = ""
            if user_stories and hasattr(user_stories, 'user_stories'):
                stories_context = "\n".join([
                    f"Story: {story.title}\nCriteria: {story.acceptance_criteria}"
                    for story in user_stories.user_stories
                ])
            
            prompt = f"""
            Generate comprehensive test cases based on user stories and code:
            
            User Stories:
            {stories_context}
            
            Code Context:
            {code_generated[:3000] if code_generated else "Code analysis pending"}
            
            Test Types: {action.parameters['test_types']}
            
            Generate:
            1. Unit test cases for all functions/methods
            2. Integration test cases for API endpoints
            3. End-to-end test scenarios
            4. Performance test cases
            5. Security test cases
            6. Negative test cases
            7. Boundary condition tests
            8. Test data requirements
            9. Automated test scripts
            10. Test execution plan
            
            Ensure tests cover all acceptance criteria and edge cases.
            """
            
            test_cases = await self.llm.ainvoke(prompt)
            
            updated_state = {"test_cases": test_cases.content}
            
            await self.notify_progress("🧪 Generated comprehensive test suite")
            
            return {
                "success": True,
                "updated_state": updated_state,
                "test_cases_generated": True
            }
        
        elif action.action_type == "execute_qa_testing":
            test_cases = state.get("test_cases", "")
            code_generated = state.get("code_generated", "")
            
            prompt = f"""
            Execute comprehensive QA testing and provide detailed results:
            
            Test Cases:
            {test_cases[:2000]}
            
            Code Under Test:
            {code_generated[:2000] if code_generated else "Code not available"}
            
            Simulate test execution and provide:
            1. Test results summary
            2. Pass/fail status for each test category
            3. Identified bugs and issues
            4. Performance analysis
            5. Security testing results
            6. Code coverage analysis
            7. Recommendations for fixes
            8. Quality assessment score
            9. Release readiness evaluation
            10. Regression testing notes
            
            Provide realistic testing outcomes based on best practices.
            """
            
            qa_results = await self.llm.ainvoke(prompt)
            
            updated_state = {"qa_testing_comments": qa_results.content}
            
            await self.notify_progress("✅ Completed comprehensive QA testing")
            
            return {
                "success": True,
                "updated_state": updated_state,
                "testing_completed": True
            }
        
        return {"success": False, "error": "Action not implemented"}


class DevOpsEngineerAgent(BaseAgent):
    """Autonomous DevOps engineer for deployment and infrastructure"""
    
    def __init__(self, llm, connector_manager):
        super().__init__(AgentRole.DEVOPS_ENGINEER, llm, connector_manager)
        self.capabilities = [
            "infrastructure_automation", "deployment_pipeline", "monitoring_setup",
            "container_orchestration", "cloud_architecture", "ci_cd_management"
        ]
    
    async def analyze(self, state: SDLCState, context: Dict[str, Any]) -> AgentDecision:
        """Analyze system for deployment requirements"""
        
        code_generated = state.get("code_generated", "")
        qa_results = state.get("qa_testing_comments", "")
        
        prompt = f"""
        As an autonomous DevOps engineer, plan deployment strategy:
        
        Code Ready: {"Yes" if code_generated else "No"}
        QA Completed: {"Yes" if qa_results else "No"}
        
        Plan for:
        1. Deployment architecture
        2. Infrastructure as Code
        3. Container strategy
        4. CI/CD pipeline
        5. Monitoring and logging
        6. Scaling strategy
        
        Determine optimal deployment approach.
        """
        
        response = await self.llm.ainvoke(prompt)
        
        actions = [
            AgentAction(
                action_type="create_deployment_config",
                target="internal",
                parameters={"platform": "docker", "orchestrator": "kubernetes"},
                priority=1,
                estimated_duration=30
            ),
            AgentAction(
                action_type="setup_monitoring",
                target="internal",
                parameters={"monitoring_stack": "prometheus_grafana"},
                priority=2,
                estimated_duration=20
            )
        ]
        
        return AgentDecision(
            decision_id=f"devops_{uuid.uuid4().hex[:8]}",
            agent_role=self.role,
            context={"deployment_strategy": response.content},
            reasoning="Container-based deployment with comprehensive monitoring and scalability",
            confidence=0.87,
            actions=actions
        )
    
    async def execute_action(self, action: AgentAction, state: SDLCState) -> Dict[str, Any]:
        """Execute deployment actions"""
        
        if action.action_type == "create_deployment_config":
            project_name = state.get("project_name", "")
            code_generated = state.get("code_generated", "")
            
            prompt = f"""
            Create comprehensive deployment configuration for "{project_name}":
            
            Code Context:
            {code_generated[:2000] if code_generated else "Code analysis pending"}
            
            Platform: {action.parameters['platform']}
            Orchestrator: {action.parameters['orchestrator']}
            
            Generate:
            1. Dockerfile for containerization
            2. Kubernetes deployment manifests
            3. Service and ingress configurations
            4. Environment configuration files
            5. CI/CD pipeline configuration
            6. Health check endpoints
            7. Scaling policies
            8. Security configurations
            9. Backup and recovery procedures
            10. Rollback strategies
            
            Ensure production-ready, scalable deployment setup.
            """
            
            deployment_config = await self.llm.ainvoke(prompt)
            
            updated_state = {"deployment_feedback": deployment_config.content}
            
            await self.notify_progress("🚀 Created production-ready deployment configuration")
            
            return {
                "success": True,
                "updated_state": updated_state,
                "deployment_ready": True
            }
        
        return {"success": False, "error": "Action not implemented"}
