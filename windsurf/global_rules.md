# Global Development Standards & Best Practices
**Location:** `~/.codeium/windsurf/memories/global_rules.md`

---

## 1. Python Execution & Naming Conventions
- **Shell Script Execution:**  
  Execute shell scripts using bash. Instead of running Python scripts directly, invoke them via bash with a command like:
  ```bash
  python3 script.py
  ```
- **Naming Conventions:**  
  Use underscores for file, directory, and script names.

---

## 2. Infrastructure as Code (IaC)
- **Primary Tool:**  
  Use AWS CloudFormation to declare and manage all infrastructure.
- **Deployment:**  
  Drive builds and deployments using Bash scripts that invoke CloudFormation, with fallback to AWS CLI when necessary.
- **S3 Bucket Naming:**  
  Ensure S3 bucket names are globally unique, DNS-compliant (3–63 characters, lowercase letters, numbers, hyphens, periods), and follow a standardized convention including project and environment identifiers.
- **Methodology:**  
  Follow the [Twelve-Factor App](https://twelvefactorapp.com/) principles for SaaS development.
- **String Manipulation:**  
  Avoid using `sed` or `awk` to simplify maintenance.

---

## 3. Python Development Standards
- Develop using Python 3.11 within a virtual environment.
- Follow [PEP8](https://peps.python.org/pep-0008/) guidelines with detailed inline comments and comprehensive documentation.
- Manage dependencies through `requirements.txt` and, where appropriate, use AWS Lambda layers.

---

## 4. Cross-Platform & CI/CD
- Ensure compatibility on macOS and Linux.
- Use GitHub Actions for cross-platform testing and continuous integration/deployment (CI/CD), including AWS SAM with `samconfig.toml` for headless deployments.

---

## 5. Performance Optimization
- Optimize Lambda functions to complete within 10 seconds.
- Allocate at least 128MB memory per function.

---

## 6. Security & Compliance
- Apply the principle of least privilege for all IAM roles and policies.
- Secure sensitive data using AWS KMS, encrypted Parameter Store values, or AWS Secrets Manager.
- Enable AWS CloudTrail for auditing and schedule regular vulnerability scans and security audits.

---

## 7. Code Quality & Version Control
- **Continuous Refactoring:**  
  Regularly refactor code to boost performance, readability, and maintainability using Martin Fowler’s [Refactoring Catalog](https://refactoring.com/catalog/).
- **Code Reviews:**  
  Document code changes in the README and ensure thorough reviews.
- **Git Commit Standards:**  
  Use only alphanumeric characters, spaces, underscores, and dashes in commit messages. For example:
  ```bash
  git commit -am "fix update for deployment script" && git push
  ```
- **Semantic Versioning & Tagging:**  
  Create tags using the format `v0.0.0-description` where:
  - **Major:** Indicates backward-incompatible changes.
  - **Minor:** Adds backward-compatible functionality.
  - **Patch:** Fixes bugs in a backward-compatible manner.

---

## 8. Versioning, Documentation, & Git Operations
- **Tag Creation Using Semantic Versioning:**
  - Create new tags using the format `v0.0.0-description` to indicate major, minor, or patch changes.
  - Clearly document the tag creation process along with the changes made.
- **README Updates:**
  - Review the repository to capture all recent changes and new functionalities.
  - Update the `README.md` with detailed setup, usage, and contribution instructions. Include links to user stories, traceability documents, and versioning information.

---

## 9. Security, Codebase Analysis & Refactoring
- **Security, Privacy, & Compliance Analysis:**
  - Conduct regular code reviews to detect vulnerabilities and privacy or compliance issues.
  - Use automated tools (e.g., Bandit, Prowler, AWS CodeGuru Reviewer) and document findings in a `SECURITY.md` file or equivalent documentation.
- **Analyzing Unused Files & Consolidation:**
  - Use static analysis tools and custom scripts to identify orphaned modules, outdated libraries, and redundant configurations.
  - Evaluate the dependency graph and test coverage to target files for consolidation or removal.
  - Develop and document a refactoring plan, ensuring team collaboration and traceability.
- **Documentation Standards:**
  - **User Stories:**  
    Document each with a unique ID (e.g., `US-XXX`), acceptance criteria, and links to the implementation and tests.
  - **Code Comments & Version Control:**  
    Include references to user story IDs, configuration details, and complex logic in code comments. Use semantic versioning for all documentation changes.
  - **Testing Documentation:**  
    Store test files in `./tests/` and provide execution instructions in a script (e.g., `./tests/run_tests.sh`).

---

## 10. Project Change Log
Maintain a comprehensive, up-to-date change log that documents all project modifications, decision rationales, and contextual details. This log will be automatically referenced in every new chat session to ensure continuity, informed decision-making, and complete historical traceability.

---

## 11. Generating Diagrams
- **Architecture Diagrams:**
  - Create a file named `docs/architecture_diagrams.md` containing instructions for generating diagrams that illustrate:
    1. **Data Processing Architecture:**  
       Flow from data acquisition to HTML generation and the AWS services used (e.g., S3, CloudFront).
    2. **AWS Infrastructure for Static Site:**  
       Configuration of ACM, Route 53, CloudFront, and S3, including security and access flows.
    3. **Scheduled Lambda for HTML Upload:**  
       An overview of the execution cycle (using CloudWatch Events/EventBridge) and the data pipeline.

---

## 12. Fully Automated AWS OIDC Authentication for GitHub Actions
- **One-Step OIDC Setup:**
  - Provide a solution that automates the configuration of OpenID Connect (OIDC) between GitHub Actions and AWS. This involves:
    - Deploying a CloudFormation stack that creates an IAM OIDC Identity Provider, an IAM Role with a trust policy (scoped to your GitHub organization, repository, and branch), and a managed IAM policy with minimal permissions.
    - Waiting for the CloudFormation deployment to complete.
    - Retrieving the IAM Role ARN and automatically setting the GitHub repository variable (`AWS_ROLE_TO_ASSUME`) using the GitHub API.
- **GitHub Actions Workflow Example:**
  ```yaml
  jobs:
    deploy:
      permissions:
        id-token: write   # Required for OIDC
        contents: read
      steps:
        - name: Checkout code
          uses: actions/checkout@v3
        
        - name: Configure AWS credentials
          uses: aws-actions/configure-aws-credentials@v2
          with:
            role-to-assume: ${{ vars.AWS_ROLE_TO_ASSUME }}
            aws-region: us-east-1
        
        # Additional deployment steps...
  ```
- For further details, refer to:  
  - [AWS OIDC Documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)  
  - [GitHub Actions OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)