import streamlit as st
from src.dev_pilot.LLMS.groqllm import GroqLLM
from src.dev_pilot.LLMS.geminillm import GeminiLLM
from src.dev_pilot.LLMS.openai_llm import OpenAILLM
from src.dev_pilot.graph.enhanced_graph_builder import EnhancedGraphBuilder
from src.dev_pilot.ui.uiconfigfile import Config
import src.dev_pilot.utils.constants as const
from src.dev_pilot.graph.graph_executor import GraphExecutor
from src.dev_pilot.state.sdlc_state import UserStoryList
import os

def initialize_session():
    st.session_state.stage = const.PROJECT_INITILIZATION
    st.session_state.project_name = ""
    st.session_state.requirements = ""
    st.session_state.task_id = ""
    st.session_state.state = {}


def load_sidebar_ui(config):
    user_controls = {}
    
    with st.sidebar:
        # Get options from config
        llm_options = config.get_llm_options()

        # LLM selection
        user_controls["selected_llm"] = st.selectbox("Select LLM", llm_options)

        if user_controls["selected_llm"] == 'Groq':
            # Model selection
            model_options = config.get_groq_model_options()
            user_controls["selected_groq_model"] = st.selectbox("Select Model", model_options)
            # API key input
            os.environ["GROQ_API_KEY"] = user_controls["GROQ_API_KEY"] = st.session_state["GROQ_API_KEY"] = st.text_input("API Key",
                                                                                                    type="password",
                                                                                                    value=os.getenv("GROQ_API_KEY", ""))
            # Validate API key
            if not user_controls["GROQ_API_KEY"]:
                st.warning("⚠️ Please enter your GROQ API key to proceed. Don't have? refer : https://console.groq.com/keys ")
                
        if user_controls["selected_llm"] == 'Gemini':
            # Model selection
            model_options = config.get_gemini_model_options()
            user_controls["selected_gemini_model"] = st.selectbox("Select Model", model_options)
            # API key input
            os.environ["GEMINI_API_KEY"] = user_controls["GEMINI_API_KEY"] = st.session_state["GEMINI_API_KEY"] = st.text_input("API Key",
                                                                                                    type="password",
                                                                                                    value=os.getenv("GEMINI_API_KEY", "")) 
            # Validate API key
            if not user_controls["GEMINI_API_KEY"]:
                st.warning("⚠️ Please enter your GEMINI API key to proceed. Don't have? refer : https://ai.google.dev/gemini-api/docs/api-key ")
                
                
        if user_controls["selected_llm"] == 'OpenAI':
            # Model selection
            model_options = config.get_openai_model_options()
            user_controls["selected_openai_model"] = st.selectbox("Select Model", model_options)
            # API key input
            os.environ["OPENAI_API_KEY"] = user_controls["OPENAI_API_KEY"] = st.session_state["OPENAI_API_KEY"] = st.text_input("API Key",
                                                                                                    type="password",
                                                                                                    value=os.getenv("OPENAI_API_KEY", "")) 
            # Validate API key
            if not user_controls["OPENAI_API_KEY"]:
                st.warning("⚠️ Please enter your OPENAI API key to proceed. Don't have? refer : https://platform.openai.com/api-keys ")
    
        if st.button("Reset Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            initialize_session()
            st.rerun()
            
        st.subheader("Workflow Overview")
        st.image("workflow_graph.png")
            
    return user_controls


def load_streamlit_ui(config):
    st.set_page_config(page_title=config.get_page_title(), layout="wide")
    st.header(config.get_page_title())
    st.subheader("Let AI agents plan your SDLC journey", divider="rainbow", anchor=False)
    user_controls = load_sidebar_ui(config)
    return user_controls


def render_deployment_feedback(deployment_feedback, deployment_checklist=None):
    """
    Render deployment feedback with structured UI components instead of markdown
    """
    # Add deployment analysis header with metadata
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.subheader("🚀 Deployment Analysis")
    
    with col2:
        if st.session_state.state.get('deployment_complexity') == 'high':
            st.info("📊 Complex Codebase")
        else:
            st.success("📊 Standard Analysis")
    
    with col3:
        if st.session_state.state.get('deployment_analysis_complete'):
            st.success("✅ Complete")
        else:
            st.warning("⏳ In Progress")
    
    # Parse the deployment feedback to extract structured information
    lines = deployment_feedback.split('\n')
    
    # Look for deployment status
    status_line = None
    sections = {}
    current_section = None
    section_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for deployment status
        if 'deployment status:' in line.lower() or 'status:' in line.lower():
            status_line = line
            continue
        
        # Check if this is a section header
        if (line.endswith(':') and len(line) < 50) or line.startswith('##'):
            # Save previous section
            if current_section and section_content:
                sections[current_section] = section_content
            
            # Start new section
            current_section = line.replace('##', '').replace(':', '').strip()
            section_content = []
        else:
            if current_section:
                section_content.append(line)
    
    # Add the last section
    if current_section and section_content:
        sections[current_section] = section_content
    
    # Display deployment status with appropriate styling and metrics
    if status_line:
        status_text = status_line.lower()
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if 'ready' in status_text and 'not_ready' not in status_text:
                st.success("✅ Deployment Status: Ready for Production")
                deployment_score = 90
            elif 'not_ready' in status_text:
                st.error("❌ Deployment Status: Not Ready for Production")
                deployment_score = 30
            elif 'needs_improvement' in status_text:
                st.warning("⚠️ Deployment Status: Needs Improvement")
                deployment_score = 65
            else:
                st.info(f"📋 {status_line}")
                deployment_score = 50
        
        with col2:
            st.metric("Readiness Score", f"{deployment_score}%")
    
    # Create tabs for different sections
    if sections:
        tab_names = list(sections.keys())
        if len(tab_names) > 1:
            tabs = st.tabs(tab_names)
            for i, (section_name, content) in enumerate(sections.items()):
                with tabs[i]:
                    display_deployment_section(section_name, content)
        else:
            # If only one section, display directly
            section_name, content = list(sections.items())[0]
            display_deployment_section(section_name, content)
    
    # Display deployment checklist if available
    if deployment_checklist:
        st.subheader("📋 Production Readiness Checklist")
        display_deployment_checklist(deployment_checklist)
    
    # Add quick actions section
    st.subheader("🔧 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Download Analysis", key="download_analysis"):
            st.download_button(
                label="Download Deployment Report",
                data=deployment_feedback,
                file_name="deployment_analysis.md",
                mime="text/markdown"
            )
    
    with col2:
        if st.button("🔄 Regenerate Analysis", key="regen_analysis"):
            st.info("Analysis regeneration would clear cache and re-run deployment assessment")
    
    with col3:
        if st.button("📋 Export Checklist", key="export_checklist"):
            if deployment_checklist:
                st.download_button(
                    label="Download Checklist",
                    data=deployment_checklist,
                    file_name="deployment_checklist.md",
                    mime="text/markdown"
                )
    
    # If no structured content was found, display as simple text
    if not sections and not status_line:
        st.info("📋 Deployment Feedback:")
        st.text_area("Details", deployment_feedback, height=300, disabled=True)


def display_deployment_section(title, content):
    """
    Display a deployment feedback section with appropriate styling
    """
    # Determine section type and apply styling
    title_lower = title.lower()
    
    if any(keyword in title_lower for keyword in ['critical', 'error', 'issue', 'problem']):
        st.error(f"🔴 {title}")
    elif any(keyword in title_lower for keyword in ['security', 'authentication', 'authorization']):
        st.warning(f"🔒 {title}")
    elif any(keyword in title_lower for keyword in ['configuration', 'infrastructure', 'deployment']):
        st.info(f"⚙️ {title}")
    elif any(keyword in title_lower for keyword in ['monitoring', 'observability', 'logging']):
        st.info(f"📊 {title}")
    elif any(keyword in title_lower for keyword in ['performance', 'optimization', 'scalability']):
        st.success(f"⚡ {title}")
    else:
        st.write(f"**{title}**")
    
    # Display content with proper formatting
    for item in content:
        if item.strip():
            # Format list items
            if item.startswith('-') or item.startswith('*'):
                st.write(f"• {item[1:].strip()}")
            else:
                st.write(item.strip())


def display_deployment_checklist(checklist):
    """
    Display the deployment checklist with priority-based styling
    """
    lines = checklist.split('\n')
    current_priority = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check for priority headers
        if any(priority in line.upper() for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']):
            if 'CRITICAL' in line.upper():
                st.error(f"🚨 {line}")
                current_priority = 'critical'
            elif 'HIGH' in line.upper():
                st.warning(f"⚠️ {line}")
                current_priority = 'high'
            elif 'MEDIUM' in line.upper():
                st.info(f"📋 {line}")
                current_priority = 'medium'
            elif 'LOW' in line.upper():
                st.success(f"💡 {line}")
                current_priority = 'low'
        else:
            # Display checklist items with checkboxes
            if line.startswith('-') or line.startswith('*'):
                item_text = line[1:].strip()
                if current_priority == 'critical':
                    st.checkbox(item_text, key=f"critical_{hash(item_text)}", disabled=True)
                else:
                    st.write(f"• {item_text}")


def render_connector_management(graph_builder):
    """Render connector management interface"""
    
    # Get connector status
    status = graph_builder.get_connector_status()
    
    # Display status overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Connectors", status["summary"]["total"])
    
    with col2:
        st.metric("Connected", status["summary"]["connected"], 
                 delta=status["summary"]["connected"] - status["summary"]["total"])
    
    with col3:
        st.metric("Enabled", status["summary"]["enabled"])
    
    with col4:
        st.metric("Disabled", status["summary"]["disabled"])
    
    # Connection status
    if status["summary"]["connected"] > 0:
        st.success(f"✅ {status['summary']['connected']} connectors active")
    elif status["summary"]["enabled"] > 0:
        st.warning("⚠️ Connectors enabled but not connected")
    else:
        st.info("ℹ️ No connectors currently active")
    
    # Connector details
    st.subheader("📋 Connector Status")
    
    for name, connector_info in status["connectors"].items():
        with st.expander(f"{name.title()} - {connector_info['status'].title()}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Type:** {connector_info['type'].replace('_', ' ').title()}")
                st.write(f"**Status:** {connector_info['status'].title()}")
                st.write(f"**Enabled:** {'Yes' if connector_info['enabled'] else 'No'}")
            
            with col2:
                if connector_info['connection_time']:
                    st.write(f"**Connected:** {connector_info['connection_time']}")
                if connector_info['last_error']:
                    st.error(f"**Error:** {connector_info['last_error']}")
            
            # Action buttons
            button_col1, button_col2, button_col3 = st.columns(3)
            
            with button_col1:
                if st.button(f"Test {name}", key=f"test_{name}"):
                    st.info(f"Testing {name} connection...")
            
            with button_col2:
                if connector_info['status'] == 'connected':
                    if st.button(f"Disconnect {name}", key=f"disconnect_{name}"):
                        st.info(f"Disconnecting {name}...")
                else:
                    if st.button(f"Connect {name}", key=f"connect_{name}"):
                        st.info(f"Connecting to {name}...")
            
            with button_col3:
                if st.button(f"Configure {name}", key=f"config_{name}"):
                    st.info(f"Configuration for {name} would open here")
    
    # Integration recommendations
    st.subheader("💡 Integration Recommendations")
    
    recommendations = graph_builder.get_integration_recommendations()
    
    for connector_name, rec in recommendations["recommendations"].items():
        priority_color = {
            "high": "🔴",
            "medium": "🟡", 
            "low": "🟢"
        }
        
        with st.expander(f"{priority_color[rec['priority']]} {connector_name.title()} - {rec['priority'].title()} Priority"):
            st.write("**Benefits:**")
            for benefit in rec["benefits"]:
                st.write(f"• {benefit}")
            
            st.write("**Requirements:**")
            for requirement in rec["requirements"]:
                st.write(f"• {requirement}")
    
    # Quick setup
    st.subheader("⚡ Quick Setup")
    
    setup_option = st.selectbox(
        "Choose setup option:",
        ["Select an option", "Development Setup", "Production Setup", "Testing Setup"]
    )
    
    if setup_option == "Development Setup":
        st.info("Development setup would enable GitHub and Slack connectors with basic configuration.")
        if st.button("🚀 Setup Development Environment"):
            st.success("Development environment setup initiated!")
    
    elif setup_option == "Production Setup":
        st.info("Production setup would enable all connectors with security best practices.")
        if st.button("🏭 Setup Production Environment"):
            st.success("Production environment setup initiated!")
    
    elif setup_option == "Testing Setup":
        st.info("Testing setup would enable mock connectors for demonstration.")
        if st.button("🧪 Setup Testing Environment"):
            st.success("Testing environment setup initiated!")


## Main Entry Point    
def load_app():
    """
    Main entry point for the Streamlit app using tab-based UI.
    """
    config = Config()
    if 'stage' not in st.session_state:
        initialize_session()

    user_input = load_streamlit_ui(config)
    if not user_input:
        st.error("Error: Failed to load user input from the UI.")
        return

    try:
        # Configure LLM 
        selectedLLM = user_input.get("selected_llm")
        model = None
        if selectedLLM == "Gemini":
            obj_llm_config = GeminiLLM(user_controls_input=user_input)
            model = obj_llm_config.get_llm_model()
        elif selectedLLM == "Groq":
            obj_llm_config = GroqLLM(user_controls_input=user_input)
            model = obj_llm_config.get_llm_model()
        elif selectedLLM == "OpenAI":
            obj_llm_config = OpenAILLM(user_controls_input=user_input)
            model = obj_llm_config.get_llm_model()
        if not model:
            st.error("Error: LLM model could not be initialized.")
            return

        ## Graph Builder
        graph_builder = EnhancedGraphBuilder(model)
        try:
            graph = graph_builder.setup_graph()
            graph_executor = GraphExecutor(graph)
        except Exception as e:
            st.error(f"Error: Graph setup failed - {e}")
            return

        # Create tabs for different stages
        tabs = st.tabs(["Project Requirement", "User Stories", "Design Documents", "Code Generation", "Test Cases", "QA Testing", "Deployment", "Connectors", "Download Artifacts"])

        # ---------------- Tab 1: Project Requirement ----------------
        with tabs[0]:
            st.header("Project Requirement")
            project_name = st.text_input("Enter the project name:", value=st.session_state.get("project_name", ""))
            st.session_state.project_name = project_name

            if st.session_state.stage == const.PROJECT_INITILIZATION:
                if st.button("🚀 Let's Start"):
                    if not project_name:
                        st.error("Please enter a project name.")
                        st.stop()
                    graph_response = graph_executor.start_workflow(project_name)
                    st.session_state.task_id = graph_response["task_id"]
                    st.session_state.state = graph_response["state"]
                    st.session_state.project_name = project_name
                    st.session_state.stage = const.REQUIREMENT_COLLECTION
                    st.rerun()

            # If stage has progressed beyond initialization, show requirements input and details.
            if st.session_state.stage in [const.REQUIREMENT_COLLECTION, const.GENERATE_USER_STORIES]:
                requirements_input = st.text_area(
                    "Enter the requirements. Write each requirement on a new line:",
                    value="\n".join(st.session_state.get("requirements", []))
                )
                if st.button("Submit Requirements"):
                    requirements = [req.strip() for req in requirements_input.split("\n") if req.strip()]
                    st.session_state.requirements = requirements
                    if not requirements:
                        st.error("Please enter at least one requirement.")
                    else:
                        st.success("Project details saved successfully!")
                        st.subheader("Project Details:")
                        st.write(f"**Project Name:** {st.session_state.project_name}")
                        st.subheader("Requirements:")
                        for req in requirements:
                            st.write(req)
                        graph_response = graph_executor.generate_stories(st.session_state.task_id, requirements)
                        st.session_state.state = graph_response["state"]
                        st.session_state.stage = const.GENERATE_USER_STORIES
                        st.rerun()

        # ---------------- Tab 2: User Stories ----------------
        with tabs[1]:
            st.header("User Stories")
            if "user_stories" in st.session_state.state:
                user_story_list = st.session_state.state["user_stories"]
                st.divider()
                st.subheader("Generated User Stories")
                if isinstance(user_story_list, UserStoryList):
                    for story in user_story_list.user_stories:
                        unique_id = f"US-{story.id:03}"
                        with st.container():
                            st.markdown(f"#### {story.title} ({unique_id})")
                            st.write(f"**Priority:** {story.priority}")
                            st.write(f"**Description:** {story.description}")
                            st.write(f"**Acceptance Criteria:**")
                            st.markdown(story.acceptance_criteria.replace("\n", "<br>"), unsafe_allow_html=True)
                            st.divider()

            # User Story Review Stage.
            if st.session_state.stage == const.GENERATE_USER_STORIES:
                st.subheader("Review User Stories")
                feedback_text = st.text_area("Provide feedback for improving the user stories (optional):")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Approve User Stories"):
                        st.success("✅ User stories approved.")
                        graph_response = graph_executor.graph_review_flow(
                            st.session_state.task_id, status="approved", feedback=None,  review_type=const.REVIEW_USER_STORIES
                        )
                        st.session_state.state = graph_response["state"]
                        st.session_state.stage = const.CREATE_DESIGN_DOC
                        st.rerun()
                        
                        ## For Testing
                        # st.session_state.stage = const.CODE_GENERATION
                        
                        
                with col2:
                    if st.button("✍️ Give User Stories Feedback"):
                        if not feedback_text.strip():
                            st.warning("⚠️ Please enter feedback before submitting.")
                        else:
                            st.info("🔄 Sending feedback to revise user stories.")
                            graph_response = graph_executor.graph_review_flow(
                                st.session_state.task_id, status="feedback", feedback=feedback_text.strip(),review_type=const.REVIEW_USER_STORIES
                            )
                            st.session_state.state = graph_response["state"]
                            st.session_state.stage = const.GENERATE_USER_STORIES
                            st.rerun()
            else:
                st.info("User stories generation pending or not reached yet.")

        # ---------------- Tab 3: Design Documents ----------------
        with tabs[2]:
            st.header("Design Documents")
            if st.session_state.stage == const.CREATE_DESIGN_DOC:
                
                # Check if design documents are already available in the current state
                if "design_documents" not in st.session_state.state:
                    st.info("🔄 Design documents are being generated. Please wait...")
                    # Try to get updated state
                    try:
                        graph_response = graph_executor.get_updated_state(st.session_state.task_id)
                        st.session_state.state = graph_response["state"]
                    except Exception as e:
                        st.warning(f"Unable to fetch updated state: {e}")
                
                if "design_documents" in st.session_state.state:
                    design_doc = st.session_state.state["design_documents"]        
                    st.subheader("Functional Design Document")
                    st.markdown(design_doc.functional)
                    st.subheader("Technical Design Document")
                    st.markdown(design_doc.technical)
                
                    # Design Document Review Stage.
                    st.divider()
                    st.subheader("Review Design Documents")
                    feedback_text = st.text_area("Provide feedback for improving the design documents (optional):")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Approve Design Documents"):
                            st.success("✅ Design documents approved.")
                            graph_response = graph_executor.graph_review_flow(
                                st.session_state.task_id, status="approved", feedback=None,  review_type=const.REVIEW_DESIGN_DOCUMENTS
                            )
                            st.session_state.state = graph_response["state"]
                            st.session_state.stage = const.CODE_GENERATION
                            st.rerun()
                        
                    with col2:
                        if st.button("✍️ Give Design Documents Feedback"):
                            if not feedback_text.strip():
                                st.warning("⚠️ Please enter feedback before submitting.")
                            else:
                                st.info("🔄 Sending feedback to revise design documents.")
                                graph_response = graph_executor.graph_review_flow(
                                    st.session_state.task_id, status="feedback", feedback=feedback_text.strip(),review_type=const.REVIEW_DESIGN_DOCUMENTS
                                )
                                st.session_state.state = graph_response["state"]
                                st.session_state.stage = const.CREATE_DESIGN_DOC
                                st.rerun()
                else:
                    # Add a refresh button when documents are not ready
                    if st.button("🔄 Check for Design Documents"):
                        st.rerun()
                    
            else:
                st.info("Design document generation pending or not reached yet.")

        # ---------------- Tab 4: Coding ----------------
        with tabs[3]:
            st.header("Code Genearation")
            if st.session_state.stage in [const.CODE_GENERATION, const.SECURITY_REVIEW]:
                
                graph_response = graph_executor.get_updated_state(st.session_state.task_id)
                st.session_state.state = graph_response["state"]
                        
                if "code_generated" in st.session_state.state:
                    code_generated = st.session_state.state["code_generated"]        
                    st.subheader("Code Files")
                    st.markdown(code_generated)
                    st.divider()
                    
                if st.session_state.stage == const.CODE_GENERATION:  
                        review_type = const.REVIEW_CODE
                elif st.session_state.stage == const.SECURITY_REVIEW:
                      if "security_recommendations" in st.session_state.state:
                        security_recommendations = st.session_state.state["security_recommendations"]        
                        st.subheader("Security Recommendations")
                        st.markdown(security_recommendations)
                        review_type = const.REVIEW_SECURITY_RECOMMENDATIONS
                
                # Code Review Stage.
                st.divider()
                st.subheader("Review Details")
                
                if st.session_state.stage == const.CODE_GENERATION:
                    feedback_text = st.text_area("Provide feedback (optional):")
                    
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Approve Code"):
                        graph_response = graph_executor.graph_review_flow(
                            st.session_state.task_id, status="approved", feedback=None, review_type=review_type
                        )
                        st.session_state.state = graph_response["state"]
                        if st.session_state.stage == const.CODE_GENERATION:
                            st.session_state.stage = const.SECURITY_REVIEW
                            st.rerun()
                        elif st.session_state.stage == const.SECURITY_REVIEW:
                            st.session_state.stage = const.WRITE_TEST_CASES
                            st.rerun()
                            
                with col2:
                    if st.session_state.stage == const.SECURITY_REVIEW:
                        if st.button("✍️ Implment Security Recommendations"):
                            st.info("🔄 Sending feedback to revise code generation.")
                            graph_response = graph_executor.graph_review_flow(
                                st.session_state.task_id, status="feedback", feedback=None, review_type=review_type
                            )
                            st.session_state.state = graph_response["state"]
                            st.session_state.stage = const.CODE_GENERATION
                            st.rerun()
                    else:
                        if st.button("✍️ Give Feedback"):
                            if not feedback_text.strip():
                                st.warning("⚠️ Please enter feedback before submitting.")
                            else:
                                st.info("🔄 Sending feedback to revise code generation.")
                                graph_response = graph_executor.graph_review_flow(
                                    st.session_state.task_id, status="feedback", feedback=feedback_text.strip(),review_type=review_type
                                )
                                st.session_state.state = graph_response["state"]
                                st.session_state.stage = const.CODE_GENERATION
                                st.rerun()
                    
            else:
                st.info("Code generation pending or not reached yet.")
                
        # ---------------- Tab 5: Test Cases ----------------
        with tabs[4]:
            st.header("Test Cases")
            if st.session_state.stage == const.WRITE_TEST_CASES:
                
                # Check if test cases are already available in the current state
                if "test_cases" not in st.session_state.state:
                    st.info("🔄 Test cases are being generated. Please wait...")
                    # Try to get updated state
                    try:
                        graph_response = graph_executor.get_updated_state(st.session_state.task_id)
                        st.session_state.state = graph_response["state"]
                    except Exception as e:
                        st.warning(f"Unable to fetch updated state: {e}")
                
                if "test_cases" in st.session_state.state:
                    test_cases = st.session_state.state["test_cases"]        
                    st.markdown(test_cases)
                
                    # Test Cases Review Stage.
                    st.divider()
                    st.subheader("Review Test Cases")
                    feedback_text = st.text_area("Provide feedback for improving the test cases (optional):")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Approve Test Cases"):
                            st.success("✅ Test cases approved.")
                            graph_response = graph_executor.graph_review_flow(
                                st.session_state.task_id, status="approved", feedback=None,  review_type=const.REVIEW_TEST_CASES
                            )
                            st.session_state.state = graph_response["state"]
                            st.session_state.stage = const.QA_TESTING
                            st.rerun()
                            
                    with col2:
                        if st.button("✍️ Give Test Cases Feedback"):
                            if not feedback_text.strip():
                                st.warning("⚠️ Please enter feedback before submitting.")
                            else:
                                st.info("🔄 Sending feedback to revise test cases.")
                                graph_response = graph_executor.graph_review_flow(
                                    st.session_state.task_id, status="feedback", feedback=feedback_text.strip(),review_type=const.REVIEW_TEST_CASES
                                )
                                st.session_state.state = graph_response["state"]
                                st.session_state.stage = const.WRITE_TEST_CASES
                                st.rerun()
                else:
                    # Add a refresh button when test cases are not ready
                    if st.button("🔄 Check for Test Cases"):
                        st.rerun()
                    
            else:
                st.info("Test Cases generation pending or not reached yet.")
                
        # ---------------- Tab 6: QA Testing ----------------
        with tabs[5]:
            st.header("QA Testing")
            if st.session_state.stage == const.QA_TESTING:
                
                # Check if QA testing comments are already available in the current state
                if "qa_testing_comments" not in st.session_state.state:
                    st.info("🔄 QA testing is being performed. Please wait...")
                    # Try to get updated state
                    try:
                        graph_response = graph_executor.get_updated_state(st.session_state.task_id)
                        st.session_state.state = graph_response["state"]
                    except Exception as e:
                        st.warning(f"Unable to fetch updated state: {e}")
                
                if "qa_testing_comments" in st.session_state.state:
                    qa_testing = st.session_state.state["qa_testing_comments"]        
                    st.markdown(qa_testing)
                
                    # QA Testing Review Stage.
                    st.divider()
                    st.subheader("Review QA Testing Comments")
                    col1, col2 = st.columns(2)
                    with col1:
                        if  st.button("✅ Approve Testing"):
                            st.success("✅ QA Testing approved.")
                            graph_response = graph_executor.graph_review_flow(
                                st.session_state.task_id, status="approved", feedback=None,  review_type=const.REVIEW_QA_TESTING
                            )
                            st.session_state.state = graph_response["state"]
                            st.session_state.stage = const.DEPLOYMENT
                            st.rerun()
                            
                    with col2:
                        if  st.button("✍️ Fix testing issues"):
                            st.info("🔄 Sending feedback to revise code.")
                            graph_response = graph_executor.graph_review_flow(
                                st.session_state.task_id, status="feedback", feedback=None, review_type=const.REVIEW_QA_TESTING
                            )
                            st.session_state.state = graph_response["state"]
                            st.session_state.stage = const.CODE_GENERATION
                            st.rerun()
                else:
                    # Add a refresh button when QA testing is not ready
                    if st.button("🔄 Check for QA Testing"):
                        st.rerun()
                    
            else:
                st.info("QA Testing Report generation pending or not reached yet.")
                
        # ---------------- Tab 7: Deployment ----------------
        with tabs[6]:
            st.header("Deployment")
            if st.session_state.stage == const.DEPLOYMENT:
                
                # Check if deployment feedback is already available in the current state
                if "deployment_feedback" not in st.session_state.state:
                    st.info("🔄 Deployment verification is in progress. Please wait...")
                    # Try to get updated state
                    try:
                        graph_response = graph_executor.get_updated_state(st.session_state.task_id)
                        st.session_state.state = graph_response["state"]
                    except Exception as e:
                        st.warning(f"Unable to fetch updated state: {e}")
                
                if "deployment_feedback" in st.session_state.state:
                    deployment_feedback = st.session_state.state["deployment_feedback"]        
                    deployment_checklist = st.session_state.state.get("deployment_checklist", None)
                    render_deployment_feedback(deployment_feedback, deployment_checklist)
                    st.session_state.stage = const.ARTIFACTS
                    st.rerun()
                else:
                    # Add a refresh button when deployment is not ready
                    if st.button("🔄 Check Deployment Status"):
                        st.rerun()
                                
            else:
                st.info("Deployment verification pending or not reached yet.")
                
        # ---------------- Tab 8: Connectors ----------------
        with tabs[7]:
            st.header("🔗 Connector Management")
            
            # Check if enhanced graph builder is available
            if hasattr(graph_builder, 'connector_manager') and graph_builder.connector_manager:
                render_connector_management(graph_builder)
            else:
                st.info("ℹ️ Connector system not initialized. Connectors provide advanced integrations with external services.")
                
                with st.expander("🚀 Available Integrations"):
                    st.markdown("""
                    ### 🔧 Development Tools
                    - **GitHub**: Automatic repository creation, code commits, issue tracking
                    - **GitLab**: Version control and CI/CD integration
                    - **Bitbucket**: Code hosting and collaboration
                    
                    ### 💬 Communication
                    - **Slack**: Real-time notifications and team updates
                    - **Microsoft Teams**: Workflow notifications
                    - **Discord**: Development team communication
                    
                    ### 📋 Project Management
                    - **Jira**: User story tracking and sprint management
                    - **Azure DevOps**: End-to-end project management
                    - **Trello**: Simple task management
                    
                    ### ☁️ Cloud Services
                    - **AWS S3**: Artifact storage and backup
                    - **Google Drive**: Document sharing
                    - **Azure Blob**: Cloud storage integration
                    
                    ### 📊 Monitoring & Analytics
                    - **Datadog**: Performance monitoring
                    - **Prometheus**: Metrics collection
                    - **Grafana**: Visualization dashboards
                    """)
                
                if st.button("🔧 Initialize Connector System"):
                    st.info("Connector system initialization would be implemented here.")
                
        # ---------------- Tab 9: Artifacts ----------------
        with tabs[8]:
            st.header("Artifacts")
            if "artifacts" in st.session_state.state and st.session_state.state["artifacts"]:
                st.subheader("Download Artifacts")
                for artifact_name, artifact_path in st.session_state.state["artifacts"].items():
                    if artifact_path:
                        try:
                            with open(artifact_path, "rb") as f:
                                file_bytes = f.read()
                            st.download_button(
                                label=f"Download {artifact_name}",
                                data=file_bytes,
                                file_name=os.path.basename(artifact_path),
                                mime="application/octet-stream"
                            )
                        except Exception as e:
                            st.error(f"Error reading {artifact_name}: {e}")
                    else:
                        st.info(f"{artifact_name} not available.")
            else:
                st.info("No artifacts generated yet.")

    except Exception as e:
        raise ValueError(f"Error occured with Exception : {e}")
    