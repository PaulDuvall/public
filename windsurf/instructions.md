> **Technology Stack:**  
The solution is built with **Python 3.11** and leverages a suite of **AWS services** for robust infrastructure management. GitHub Actions powers the CI/CD pipeline to ensure streamlined builds, tests, and deployments.

> **Tooling:**  
The project employs **Windsurf** for incremental code implementation, efficient memory management, and seamless integration of user stories with testing.

## 1. Project Workflow & Development Process

- **User Story Creation & Incremental Development:**
  - **User Story Generation:**  
    Use ChatGPT (current version o3-mini) to draft detailed user stories (ID format: `US-XXX`) with clear acceptance criteria. Iterate until the stories fully capture the intended functionality.
  - **Incremental Code Implementation:**  
    Instruct Windsurf to implement code in the smallest increments possible using the user story acceptance criteria.
  - **Test-Driven Development (TDD):**  
    Adopt a Test-Driven Development (TDD) approach by writing comprehensive automated tests with pytest before any implementation, ensuring they capture the desired behavior and initially fail to confirm missing functionality. Then, implement the minimal code required to make these tests pass, and iteratively refactor while maintaining green test results. This process not only validates functionality but also serves as living documentation of the code's intended behavior.

- **Memory & Traceability:**
  - **Memory Utilization:**  
    Leverage global (`global_rules.md`) and project memories (` .windsurfrules.md`) in Windsurf. Always verify that Windsurf cross-checks against these memories.

  - **Traceability:**  
    Maintain a traceability matrix (e.g., in `docs/traceability_matrix.md`) linking each user story (e.g., `US-300`) to its implementation and test files.

- **Documentation & Updates:**
  - **README & Supplementary Docs:**  
    Regularly update the centralized `README.md` to capture new functionalities, user stories, and traceability links. Maintain additional documentation (e.g., `docs/prompts.md`, `SECURITY.md`) with comprehensive details.
  - **Architectural Guidance:**  
    Continuously provide Windsurf with guidance on the overall architecture, services, and tooling. When suboptimal results occur, switch between available LLMs to improve outcomes.

- **Automation & Analysis:**
  - **GitHub Actions for Refactoring:**  
    Use GitHub Actions (leveraging GPT-4) to analyze the entire repository and generate refactoring reports based on Martin Fowler’s Refactoring Catalog.
  - **Security Analysis:**  
    Regularly analyze the code for security, privacy, and compliance issues (using tools like Bandit, Prowler, or AWS CodeGuru Reviewer) and document findings in a markdown file.
  - **Build, Test, Deploy & Cleanup:**  
    Create a bash script to:
    - Set up a virtual environment (`venv`)
    - Install/configure Python 3.11, pip, and dependencies
    - Execute build, test, and deploy commands  
    Also, include code that deletes all application resources (e.g., AWS services) when required.

---



