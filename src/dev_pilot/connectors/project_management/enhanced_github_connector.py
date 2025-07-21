"""
Enhanced GitHub Connector with AI Agent Integration
Extends the basic GitHub connector with advanced features for SDLC automation
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import base64
import json
import logging

from ..base_connector import BaseConnector, ConnectorConfig, ConnectorResponse, ConnectorType, ConnectorStatus
from .github_connector import GitHubConnector

logger = logging.getLogger(__name__)

class EnhancedGitHubConnector(GitHubConnector):
    """Enhanced GitHub connector with AI agent integration capabilities"""
    
    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.project_repositories: Dict[str, Dict] = {}
        self.workflow_templates = {
            "python": self._get_python_workflow_template(),
            "javascript": self._get_javascript_workflow_template(),
            "general": self._get_general_workflow_template()
        }
    
    async def commit_generated_code(self, repository: str, files: List[Dict[str, str]], commit_message: str) -> ConnectorResponse:
        """Commit AI-generated code files to repository"""
        try:
            if not self.client:
                return ConnectorResponse(success=False, error="GitHub client not connected")
                
            if not repository:
                return ConnectorResponse(success=False, error="Repository name is required")
            
            repo = await asyncio.to_thread(self.client.repository, *repository.split("/"))
            
            # Get the default branch reference
            default_branch = repo.default_branch
            ref = await asyncio.to_thread(repo.ref, f"heads/{default_branch}")
            
            # Create tree elements for all files
            tree_elements = []
            
            for file_info in files:
                try:
                    # Create blob for file content
                    blob = await asyncio.to_thread(
                        repo.create_blob, 
                        file_info["content"], 
                        "utf-8"
                    )
                    
                    tree_elements.append({
                        "path": file_info["path"],
                        "mode": "100644",
                        "type": "blob",
                        "sha": blob.sha
                    })
                except Exception as e:
                    logger.warning(f"Failed to create blob for {file_info['path']}: {str(e)}")
            
            if not tree_elements:
                return ConnectorResponse(success=False, error="No valid files to commit")
            
            # Create new tree
            new_tree = await asyncio.to_thread(
                repo.create_tree,
                tree_elements,
                base_tree=ref.object.sha
            )
            
            # Create commit
            new_commit = await asyncio.to_thread(
                repo.create_commit,
                commit_message,
                new_tree.sha,
                [ref.object.sha]
            )
            
            # Update reference
            await asyncio.to_thread(ref.update, new_commit.sha)
            
            return ConnectorResponse(
                success=True,
                data={
                    "commit": {
                        "sha": new_commit.sha,
                        "message": commit_message,
                        "files_count": len(files),
                        "url": new_commit.html_url,
                        "repository": repository
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Error committing code to {repository}: {str(e)}")
            return ConnectorResponse(success=False, error=str(e))
    
    async def create_project_repository(self, project_name: str, description: str = "", private: bool = True) -> ConnectorResponse:
        """Create a new repository for the SDLC project"""
        try:
            if not self.client:
                return ConnectorResponse(success=False, error="GitHub client not connected")
            
            repo_name = project_name.lower().replace(" ", "-").replace("_", "-")
            
            # Create repository
            repo = await asyncio.to_thread(
                self.client.create_repository,
                repo_name,
                description=description or f"AI-generated project: {project_name}",
                private=private,
                has_issues=True,
                has_projects=True,
                has_wiki=True,
                auto_init=True,
                gitignore_template="Python"
            )
            
            # Store repository info
            repo_info = {
                "name": repo.name,
                "full_name": repo.full_name,
                "clone_url": repo.clone_url,
                "html_url": repo.html_url,
                "created_at": datetime.now().isoformat(),
                "default_branch": repo.default_branch
            }
            
            self.project_repositories[project_name] = repo_info
            
            return ConnectorResponse(
                success=True,
                data={
                    "repository": repo_info,
                    "message": f"Repository '{repo_name}' created successfully"
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating repository for {project_name}: {str(e)}")
            return ConnectorResponse(success=False, error=str(e))
    
    async def sync_user_stories_as_issues(self, user_stories: Any, repository: str) -> ConnectorResponse:
        """Convert user stories to GitHub issues"""
        try:
            if not self.client:
                return ConnectorResponse(success=False, error="GitHub client not connected")
            
            repo = await asyncio.to_thread(self.client.repository, *repository.split("/"))
            created_issues = []
            
            # Handle both UserStoryList objects and regular lists
            stories = user_stories.user_stories if hasattr(user_stories, 'user_stories') else user_stories
            
            for story in stories:
                try:
                    # Get story attributes safely
                    title = getattr(story, 'title', story.get('title', 'Untitled Story'))
                    description = getattr(story, 'description', story.get('description', ''))
                    acceptance_criteria = getattr(story, 'acceptance_criteria', story.get('acceptance_criteria', ''))
                    priority = getattr(story, 'priority', story.get('priority', 3))
                    
                    # Create issue
                    issue_body = f"""## User Story
{description}

## Acceptance Criteria
{acceptance_criteria}

## Priority
{self._map_priority_to_label(priority)}

---
*This issue was automatically generated from user story requirements.*
"""
                    
                    issue = await asyncio.to_thread(
                        repo.create_issue,
                        title=f"User Story: {title}",
                        body=issue_body,
                        labels=[
                            "user-story",
                            f"priority-{self._map_priority_to_label(priority).lower()}",
                            "auto-generated"
                        ]
                    )
                    
                    created_issues.append({
                        "number": issue.number,
                        "title": issue.title,
                        "url": issue.html_url,
                        "labels": [label.name for label in issue.labels()]
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to create issue for story '{title}': {str(e)}")
            
            return ConnectorResponse(
                success=True,
                data={
                    "created_issues": created_issues,
                    "total_created": len(created_issues),
                    "repository": repository
                }
            )
            
        except Exception as e:
            logger.error(f"Error syncing user stories to {repository}: {str(e)}")
            return ConnectorResponse(success=False, error=str(e))
    
    async def setup_ci_cd_workflow(self, repository: str, project_type: str = "python") -> ConnectorResponse:
        """Setup GitHub Actions CI/CD workflow"""
        try:
            workflow_content = self.workflow_templates.get(project_type, self.workflow_templates["general"])
            
            files = [
                {
                    "path": ".github/workflows/ci-cd.yml",
                    "content": workflow_content
                },
                {
                    "path": "requirements.txt",
                    "content": self._get_default_requirements()
                },
                {
                    "path": ".gitignore",
                    "content": self._get_python_gitignore()
                }
            ]
            
            return await self.commit_generated_code(
                repository,
                files,
                "Setup CI/CD workflow and project structure"
            )
            
        except Exception as e:
            return ConnectorResponse(success=False, error=str(e))
    
    async def create_release_from_deployment(self, repository: str, version: str, deployment_notes: str) -> ConnectorResponse:
        """Create a GitHub release after successful deployment"""
        try:
            if not self.client:
                return ConnectorResponse(success=False, error="GitHub client not connected")
            
            repo = await asyncio.to_thread(self.client.repository, *repository.split("/"))
            
            tag_name = f"v{version}"
            release_name = f"Release {version}"
            
            # Create release
            release = await asyncio.to_thread(
                repo.create_release,
                tag_name,
                release_name,
                deployment_notes,
                draft=False,
                prerelease=False
            )
            
            return ConnectorResponse(
                success=True,
                data={
                    "release": {
                        "id": release.id,
                        "tag_name": release.tag_name,
                        "name": release.name,
                        "url": release.html_url,
                        "published_at": release.published_at.isoformat() if release.published_at else None
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating release for {repository}: {str(e)}")
            return ConnectorResponse(success=False, error=str(e))
    
    async def get_project_analytics(self, repository: str) -> ConnectorResponse:
        """Get analytics data for agent decision making"""
        try:
            if not self.client:
                return ConnectorResponse(success=False, error="GitHub client not connected")
            
            repo = await asyncio.to_thread(self.client.repository, *repository.split("/"))
            
            # Get various metrics
            commits_count = await asyncio.to_thread(
                lambda: len(list(repo.commits(number=100)))
            )
            
            issues = await asyncio.to_thread(
                lambda: list(repo.issues(state="all", number=50))
            )
            
            pulls = await asyncio.to_thread(
                lambda: list(repo.pull_requests(state="all", number=30))
            )
            
            analytics = {
                "repository_metrics": {
                    "name": repo.name,
                    "size": repo.size,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "watchers": repo.watchers_count
                },
                "activity_metrics": {
                    "recent_commits": commits_count,
                    "total_issues": len(issues),
                    "open_issues": len([i for i in issues if i.state == "open"]),
                    "closed_issues": len([i for i in issues if i.state == "closed"]),
                    "total_prs": len(pulls),
                    "open_prs": len([p for p in pulls if p.state == "open"]),
                    "merged_prs": len([p for p in pulls if p.state == "closed" and p.merged])
                },
                "health_indicators": {
                    "issue_closure_rate": len([i for i in issues if i.state == "closed"]) / max(len(issues), 1),
                    "pr_merge_rate": len([p for p in pulls if p.state == "closed" and p.merged]) / max(len(pulls), 1),
                    "activity_score": min(commits_count / 10, 1.0)  # Normalized activity score
                }
            }
            
            return ConnectorResponse(
                success=True,
                data=analytics
            )
            
        except Exception as e:
            logger.error(f"Error getting analytics for {repository}: {str(e)}")
            return ConnectorResponse(success=False, error=str(e))
    
    def _map_priority_to_label(self, priority: int) -> str:
        """Map numeric priority to string label"""
        priority_map = {1: "Critical", 2: "High", 3: "Medium", 4: "Low"}
        return priority_map.get(priority, "Medium")
    
    def _get_python_workflow_template(self) -> str:
        """Get Python CI/CD workflow template"""
        return """name: Python CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install flake8 pytest black bandit safety
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

    - name: Format check with black
      run: black --check .

    - name: Security check with bandit
      run: bandit -r . -f json -o bandit-report.json || true

    - name: Safety check
      run: safety check --json --output safety-report.json || true

    - name: Test with pytest
      run: |
        pytest tests/ --junitxml=junit/test-results-${{ matrix.python-version }}.xml --cov=src --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine

    - name: Build package
      run: python -m build

    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment"
        # Add your deployment commands here
"""

    def _get_javascript_workflow_template(self) -> str:
        """Get JavaScript/Node.js CI/CD workflow template"""
        return """name: Node.js CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [14.x, 16.x, 18.x]

    steps:
    - uses: actions/checkout@v3

    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'

    - run: npm ci
    - run: npm run build --if-present
    - run: npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v3
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment"
"""

    def _get_general_workflow_template(self) -> str:
        """Get general CI/CD workflow template"""
        return """name: General CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Run tests
      run: |
        echo "Running tests..."
        # Add your test commands here

    - name: Build application
      run: |
        echo "Building application..."
        # Add your build commands here

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v3

    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment"
        # Add your deployment commands here
"""

    def _get_default_requirements(self) -> str:
        """Get default Python requirements"""
        return """# Core dependencies
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
requests==2.31.0

# Testing
pytest==7.4.3
pytest-cov==4.1.0

# Code quality
black==23.11.0
flake8==6.1.0
bandit==1.7.5
safety==2.3.5

# Additional dependencies will be added based on project needs
"""

    def _get_python_gitignore(self) -> str:
        """Get Python .gitignore template"""
        return """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
logs/
artifacts/
.secrets
"""
