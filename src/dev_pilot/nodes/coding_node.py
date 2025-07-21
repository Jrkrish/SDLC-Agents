from src.dev_pilot.state.sdlc_state import SDLCState, UserStoryList
from src.dev_pilot.utils.Utility import Utility
from loguru import logger

class CodingNode:
    """
    Graph Node for the Coding
    
    """
    
    def __init__(self, model):
        self.llm = model
        self.utility = Utility()
    
    ## ---- Code Generation ----- ##
    def generate_code(self, state: SDLCState):
        """
            Generates the code for the given SDLC state as multiple Python files.
        """
        logger.info("----- Generating the code ----")
        
        requirements = state.get('requirements', '')
        user_stories = state.get('user_stories', '')
        code_feedback = state.get('code_review_feedback', '') if 'code_generated' in state else ""
        security_feedback = state.get('security_recommendations', '') if 'security_recommendations' in state else ""
        
        prompt = f"""
        Generate a complete Python project organized as multiple code files. 
        Based on the following SDLC state, generate only the Python code files with their complete implementations. 
        Do NOT include any explanations, requirements text, or design document details in the output—only code files with proper names and code content.

        SDLC State:
        ---------------
        Project Name: {state['project_name']}

        Requirements:
        {self.utility.format_list(requirements)}

        User Stories:
        {self.utility.format_user_stories(user_stories)}

        Functional Design Document:
        {state['design_documents']['functional']}

        Technical Design Document:
        {state['design_documents']['technical']}

        {"Note: Incorporate the following code review feedback: " + code_feedback if code_feedback else ""}
        {"Note: Apply the following security recommendations: " + security_feedback if security_feedback else ""}

        Instructions:
        - Structure the output as multiple code files (for example, "main.py", "module1.py", etc.), each separated clearly.
        - Each file should contain only the code necessary for a modular, fully-functional project based on the input state.
        - Do not output any additional text, explanations, or commentary outside the code files.
        - Ensure the code follows Python best practices, is syntactically correct, and is ready for development.
        """
        response = self.llm.invoke(prompt)
        code_review_comments = self.get_code_review_comments(code=response.content)
        return {
                'code_generated': response.content, 
                'code_review_comments': code_review_comments
            }
    
    ## This code review comments will be used while generating test cases
    def get_code_review_comments(self, code: str):
        """
        Generate code review comments for the provided code
        """
        logger.info("----- Generating code review comments ----")
        
        # Create a prompt for the LLM to review the code
        prompt = f"""
            You are a coding expert. Please review the following code and provide detailed feedback:
            ```
            {code}
            ```
            Focus on:
            1. Code quality and best practices
            2. Potential bugs or edge cases
            3. Performance considerations
            4. Security concerns
            
            End your review with an explicit APPROVED or NEEDS_FEEDBACK status.
        """
        
        # Get the review from the LLM
        response = self.llm.invoke(prompt)
        review_comments = response.content
        return review_comments
    
    def code_review(self, state: SDLCState):
        return state
    
    def fix_code(self, state: SDLCState):
        pass
    
    def code_review_router(self, state: SDLCState):
        """
            Evaluates Code review is required or not.
        """
        return state.get("code_review_status", "approved")  # default to "approved" if not present
    
    ## ---- Security Review ----- ##
    def security_review_recommendations(self, state: SDLCState):
        """
            Performs security review of the code generated
        """
        logger.info("----- Generating security recommendations ----")
          
         # Get the generated code from the state
        code_generated = state.get('code_generated', '')

         # Create a prompt for the LLM to review the code for security concerns
        prompt = f"""
            You are a security expert. Please review the following Python code for potential security vulnerabilities:
            ```
            {code_generated}
            ```
            Focus on:
            1. Identifying potential security risks (e.g., SQL injection, XSS, insecure data handling).
            2. Providing recommendations to mitigate these risks.
            3. Highlighting any best practices that are missing.

            End your review with an explicit APPROVED or NEEDS_FEEDBACK status.
        """

         # Invoke the LLM to perform the security review
        response = self.llm.invoke(prompt)
        state["security_recommendations"] =  response.content
        return state
    
    def security_review(self, state: SDLCState):
        return state
    
    def fix_code_after_security_review(self, state: SDLCState):
        pass
    
    def security_review_router(self, state: SDLCState):
        """
            Security Code review is required or not.
        """
        return state.get("security_review_status", "approved")  # default to "approved" if not present
    
    ## ---- Test Cases ----- ##
    def write_test_cases(self, state: SDLCState):
        """
            Generates the test cases based on the generated code and code review comments
        """
        logger.info("----- Generating Test Cases ----")
    
        # Get the generated code and code review comments from the state
        code_generated = state.get('code_generated', '')
        code_review_comments = state.get('code_review_comments', '')

         # Create a prompt for the LLM to generate test cases
        prompt = f"""
            You are a software testing expert. Based on the following Python code and its review comments, generate comprehensive test cases:
            
            ### Code:
            ```
                {code_generated}
                ```

                ### Code Review Comments:
                {code_review_comments}

                Focus on:
                1. Covering all edge cases and boundary conditions.
                2. Ensuring functional correctness of the code.
                3. Including both positive and negative test cases.
                4. Writing test cases in Python's `unittest` framework format.

                Provide the test cases in Python code format, ready to be executed.
        """

        response = self.llm.invoke(prompt)
        state["test_cases"] = response.content

        return state
    
    def review_test_cases(self, state: SDLCState):
        return state
    
    def revise_test_cases(self, state: SDLCState):
        pass
    
    def review_test_cases_router(self, state: SDLCState):
        """
            Evaluates Test Cases review is required or not.
        """
        return state.get("test_case_review_status", "approved")  # default to "approved" if not present
    
    ## ---- QA Testing ----- ##
    def qa_testing(self, state: SDLCState):
        """
            Performs QA testing based on the generated code and test cases
        """
        logger.info("----- Performing QA Testing ----")
        # Get the generated code and test cases from the state
        code_generated = state.get('code_generated', '')
        test_cases = state.get('test_cases', '')

        # Create a prompt for the LLM to simulate running the test cases
        prompt = f"""
            You are a QA testing expert. Based on the following Python code and test cases, simulate running the test cases and provide feedback:
            
            ### Code:
            ```
            {code_generated}
            ```

            ### Test Cases:
            ```
            {test_cases}
            ```

            Focus on:
            1. Identifying which test cases pass and which fail.
            2. Providing detailed feedback for any failed test cases, including the reason for failure.
            3. Suggesting improvements to the code or test cases if necessary.

            Provide the results in the following format:
            - Test Case ID: [ID]
            Status: [Pass/Fail]
            Feedback: [Detailed feedback if failed]
        """

        # Invoke the LLM to simulate QA testing
        response = self.llm.invoke(prompt)
        qa_testing_comments = response.content

        state["qa_testing_comments"]= qa_testing_comments
        return state
    
    def qa_review(self, state: SDLCState):
        pass
    
    def deployment(self, state: SDLCState):
        """
            Performs advanced deployment analysis and simulation with optimization
        """
        logger.info("----- Generating Advanced Deployment Analysis ----")

        code_generated = state.get('code_generated', '')
        security_recommendations = state.get('security_recommendations', '')
        test_cases = state.get('test_cases', '')
        qa_testing_comments = state.get('qa_testing_comments', '')
        
        # Check if we've already done deployment analysis to avoid recomputation
        if state.get('deployment_analysis_complete'):
            logger.info("Deployment analysis already complete, returning cached results")
            return state

        # Analyze code complexity to optimize prompt length
        code_lines = len(code_generated.split('\n')) if code_generated else 0
        use_summarized_analysis = code_lines > 500  # Use summarized analysis for large codebases

        if use_summarized_analysis:
            # For large codebases, focus on key architectural decisions
            prompt = f"""
                You are a Senior DevOps Engineer. Perform a focused deployment readiness assessment for this large Python application ({code_lines} lines).

                ### Application Code Summary:
                {code_generated[:2000]}... [Code truncated for analysis efficiency]

                ### Previous Analysis Context:
                Security: {"Available" if security_recommendations else "Not performed"}
                Testing: {"Available" if test_cases else "Not performed"}
                QA: {"Available" if qa_testing_comments else "Not performed"}

                **FOCUSED DEPLOYMENT ANALYSIS:**

                1. **Architecture Assessment**: Overall application structure and deployment complexity
                2. **Critical Dependencies**: Key external dependencies and services required
                3. **Environment Configuration**: Essential environment variables and configuration
                4. **Security Baseline**: Production security requirements
                5. **Scalability Design**: Resource requirements and scaling considerations
                6. **Deployment Strategy**: Recommended deployment approach

                **OUTPUT FORMAT:**
                Deployment Status: [READY/NEEDS_IMPROVEMENT/NOT_READY]
                
                Architecture Assessment: [Brief architectural analysis]
                Critical Dependencies: [Key dependencies to manage]
                Configuration Requirements: [Essential configurations]
                Security Baseline: [Core security requirements]
                Deployment Strategy: [Recommended approach]
                Next Steps: [Priority actions for deployment readiness]
            """
        else:
            # For smaller codebases, use comprehensive analysis
            prompt = f"""
                You are a Senior DevOps Engineer with expertise in production deployments, containerization, and cloud infrastructure. 
                Perform a comprehensive deployment readiness assessment for the following Python application.

                ### Application Code:
                ```
                {code_generated}
                ```

                ### Security Analysis:
                {security_recommendations if security_recommendations else "No security analysis provided"}

                ### Test Coverage:
                {test_cases if test_cases else "No test cases provided"}

                ### QA Results:
                {qa_testing_comments if qa_testing_comments else "No QA testing performed"}

                **COMPREHENSIVE DEPLOYMENT ANALYSIS:**

                1. **Dependency Analysis**: Required dependencies, versions, and potential conflicts
                2. **Configuration Management**: Environment variables, configuration files, and secrets
                3. **Infrastructure Requirements**: Deployment architecture and resource needs
                4. **Security Readiness**: Production security checklist and requirements
                5. **Monitoring Setup**: Logging, health checks, and observability
                6. **Deployment Strategy**: CI/CD pipeline and deployment approach
                7. **Production Checklist**: Critical and recommended items

                **OUTPUT FORMAT:**
                Deployment Status: [READY/NEEDS_IMPROVEMENT/NOT_READY]
                
                Critical Issues: [Any blocking issues]
                Configuration Requirements: [Configuration needs]
                Infrastructure Recommendations: [Infrastructure setup]
                Security Considerations: [Security requirements]
                Performance Optimization: [Performance recommendations]
                Deployment Steps: [Step-by-step process]
                Monitoring Setup: [Observability requirements]
                Post-Deployment Checklist: [Verification items]
            """

        # Invoke the LLM for deployment analysis
        response = self.llm.invoke(prompt)
        deployment_feedback = response.content

        # Enhanced status determination
        deployment_status = "needs_improvement"
        feedback_upper = deployment_feedback.upper()
        
        if "DEPLOYMENT STATUS: READY" in feedback_upper or "STATUS: READY" in feedback_upper:
            deployment_status = "ready"
        elif "DEPLOYMENT STATUS: NOT_READY" in feedback_upper or "STATUS: NOT_READY" in feedback_upper:
            deployment_status = "not_ready"
        elif "DEPLOYMENT STATUS: NEEDS_IMPROVEMENT" in feedback_upper or "STATUS: NEEDS_IMPROVEMENT" in feedback_upper:
            deployment_status = "needs_improvement"

        # Generate optimized deployment checklist
        checklist_prompt = f"""
            Create a prioritized action checklist for production deployment based on the analysis.

            Analysis Summary: {deployment_feedback[:1000]}...

            Generate a concise checklist with priorities:
            **CRITICAL** (Must fix before deployment)
            **HIGH** (Should fix for production stability)  
            **MEDIUM** (Recommended improvements)

            Format: - Priority: [Action item with specific guidance]
            
            Focus on actionable items with clear implementation guidance.
        """

        checklist_response = self.llm.invoke(checklist_prompt)
        deployment_checklist = checklist_response.content

        # Update state with comprehensive results
        return {
            **state,
            "deployment_status": deployment_status,
            "deployment_feedback": deployment_feedback,
            "deployment_checklist": deployment_checklist,
            "deployment_analysis_complete": True,
            "deployment_complexity": "high" if use_summarized_analysis else "standard"
        }