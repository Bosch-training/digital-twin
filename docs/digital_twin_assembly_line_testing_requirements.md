# MVP Requirements: Digital Twin Assembly-Line Simulation

## GitHub Copilot Training --- Testing Team Edition

**Document type:** MVP product and test requirements\
**Audience:** Automotive / industrial software testing team\
**Training duration:** 16 hours, including concepts and hands-on labs\
**Target delivery:** A small Python application with automated tests,
CI/CD, and deployment to AWS\
**Primary training goal:** Use GitHub Copilot throughout a realistic
testing workflow: requirement analysis, test design, test automation,
test execution, defect analysis, refactoring, code review, CI/CD, and
deployment verification.

------------------------------------------------------------------------

## 1. Problem Statement

An assembly-line simulation contains a sequence of stations that process
a product. A product moves from one station to the next only when the
station is available and the required processing time has elapsed.

The testing team needs a small, deterministic Digital Twin simulator to
validate normal and abnormal assembly-line behavior. The MVP must
provide predictable inputs and outputs so testers can derive
requirements, create test scenarios, automate tests, and validate a
deployed build.

This is a **software simulation for training**. It does not connect to
real factory equipment, production PLCs, sensors, or vehicles.

## 2. MVP Objective

Build and validate a lightweight web API that simulates one assembly
line with three stations:

1.  **Assembly** --- attaches components.
2.  **Inspection** --- checks the assembled product.
3.  **Packaging** --- marks the product as ready for dispatch.

The API accepts a simulation request and returns a deterministic result
containing the product status, station outcomes, and any validation
errors.

The MVP is successful when the team can demonstrate: - Requirements
converted into test conditions and acceptance criteria. - Positive,
negative, boundary, and error-handling tests. - Automated unit and API
tests. - Test execution in a GitHub Actions pipeline. - A reviewable
code change with evidence from tests and static checks. - Deployment to
AWS and post-deployment smoke testing.

## 3. Scope

### 3.1 In scope

-   Python-based simulation logic.
-   REST API with request validation and JSON responses.
-   Fixed three-station assembly line.
-   Deterministic simulation; no real-time clock or random outcomes.
-   Configurable processing time and inspection result through request
    fields.
-   Unit tests and API-level tests.
-   Test reports and basic code-quality checks in CI.
-   Container image build.
-   Deployment of the API to an AWS-hosted environment.
-   Deployment smoke test and basic operational logging.

### 3.2 Out of scope

-   Real factory, PLC, robot, sensor, or vehicle integration.
-   3D visualization, CAD models, physics simulation, or digital-twin
    synchronization.
-   Authentication, user accounts, roles, or multi-tenancy.
-   Database persistence and historical dashboards.
-   Multiple concurrent production lines or complex scheduling.
-   Machine learning, predictive maintenance, or anomaly detection.
-   High availability, autoscaling, disaster recovery, and
    production-grade security hardening.
-   Performance benchmarking beyond a basic response-time sanity check.

## 4. Intended Users

  User                       Need
  -------------------------- --------------------------------------------------------
  Test engineer              Submit scenarios and verify expected behavior
  Test automation engineer   Implement and maintain automated checks
  Developer                  Implement the API and simulation rules
  Reviewer                   Assess test coverage, maintainability, and change risk
  CI/CD pipeline             Run checks and publish a deployable container
  Trainer                    Demonstrate GitHub Copilot across the SDLC

## 5. Functional Requirements

### FR-01: Health Check

The service shall expose `GET /health`.

**Expected behavior** - Return HTTP `200`. - Return JSON containing
`status: "healthy"`. - The endpoint shall not start a simulation or
modify simulation state.

### FR-02: Simulation Request

The service shall expose `POST /simulate`.

The request shall accept the following JSON fields:

  ----------------------------------------------------------------------------------
  Field                      Type                          Required Rules
  -------------------------- ---------------- --------------------- ----------------
  `product_id`               String                             Yes Non-empty after
                                                                    trimming;
                                                                    maximum 50
                                                                    characters

  `assembly_time_seconds`    Integer                            Yes 1--300 inclusive

  `inspection_result`        String                             Yes One of `PASS` or
                                                                    `FAIL`

  `packaging_time_seconds`   Integer                            Yes 1--120 inclusive
  ----------------------------------------------------------------------------------

Example request:

``` json
{
  "product_id": "PROD-001",
  "assembly_time_seconds": 30,
  "inspection_result": "PASS",
  "packaging_time_seconds": 10
}
```

### FR-03: Successful Simulation

When the request is valid and `inspection_result` is `PASS`, the service
shall: 1. Process the product through Assembly. 2. Process the product
through Inspection. 3. Process the product through Packaging. 4. Return
overall status `COMPLETED`. 5. Include the product ID, station results,
and total simulated processing time.

Expected total simulated processing time is:

`assembly_time_seconds + packaging_time_seconds`

Inspection contributes zero simulated seconds in this MVP. The simulator
shall not sleep or wait in real time.

Example response:

``` json
{
  "product_id": "PROD-001",
  "status": "COMPLETED",
  "stations": [
    {"station": "Assembly", "status": "COMPLETED", "duration_seconds": 30},
    {"station": "Inspection", "status": "PASS", "duration_seconds": 0},
    {"station": "Packaging", "status": "COMPLETED", "duration_seconds": 10}
  ],
  "total_simulated_time_seconds": 40
}
```

The exact response structure shall be documented and consistently
implemented. Field names and station order must not vary between
requests.

### FR-04: Failed Inspection

When the request is valid and `inspection_result` is `FAIL`, the service
shall: 1. Process the product through Assembly. 2. Mark Inspection as
`FAIL`. 3. Stop the line for that product. 4. Skip Packaging. 5. Return
overall status `REJECTED`. 6. Include a clear reason indicating that
inspection failed.

The total simulated processing time shall equal `assembly_time_seconds`.
Packaging time shall not be included because Packaging was not executed.

### FR-05: Input Validation

The service shall reject invalid requests without running the
simulation.

Invalid inputs include: - Missing required fields. - `product_id` empty
or whitespace-only. - `product_id` longer than 50 characters. -
`assembly_time_seconds` below 1 or above 300. - `packaging_time_seconds`
below 1 or above 120. - Processing-time values supplied as strings,
decimals, booleans, or null. - `inspection_result` other than `PASS` or
`FAIL`. - Malformed JSON or a request body that is not a JSON object.

**Expected behavior** - Return HTTP `400` for invalid request content. -
Return a structured JSON error response with a useful message. - Do not
return a success status for invalid input. - Do not expose stack traces
or internal implementation details in the response.

The implementation may use a validation framework, but the externally
observable behavior must meet these requirements.

### FR-06: Deterministic Results

For identical valid input, the service shall return the same simulation
outcome, station order, statuses, and total simulated processing time.

The API shall not use random outcomes, wall-clock delays, or external
services to determine the result.

### FR-07: Error Response Consistency

All client-input errors shall use a consistent JSON structure, for
example:

``` json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "assembly_time_seconds must be between 1 and 300"
  }
}
```

The exact message may vary by validation failure, but the `error.code`
and `error.message` fields must be present.

### FR-08: API Documentation

The application shall provide concise documentation covering: -
Available endpoints. - Request fields and valid ranges. - Example
success and failure responses. - How to run the application and tests
locally.

Interactive API documentation may be provided by the chosen Python web
framework.

## 6. Non-Functional Requirements

### NFR-01: Maintainability

-   Separate API/request validation from simulation business logic.
-   Use clear names, small functions, and type hints where appropriate.
-   Avoid duplicated validation or simulation rules.
-   Keep the project small enough to understand during a training lab.

### NFR-02: Testability

-   Simulation logic shall be testable without starting an HTTP server.
-   Tests shall not require AWS credentials or access to real
    infrastructure.
-   Automated tests shall not depend on real-time sleeps or random data.

### NFR-03: Reliability

-   Invalid input shall not crash the service.
-   A failed product simulation shall not affect the next independent
    request.
-   The health endpoint shall remain available when a simulation request
    is invalid.

### NFR-04: Observability

-   Log request failures and unexpected application errors without
    logging secrets.
-   Return useful HTTP status codes.
-   Provide a health endpoint suitable for a deployment smoke test.

### NFR-05: Portability

-   The application shall run locally and inside a Docker container.
-   Configuration shall not require hard-coded AWS account IDs,
    credentials, or environment-specific values.

### NFR-06: Basic Performance

-   For this training MVP, a valid simulation request should complete
    within 1 second in the local test environment under ordinary
    conditions.
-   The application shall calculate simulated duration rather than
    waiting for the simulated duration to pass.
-   This is a sanity check, not a production performance SLA.

## 7. Acceptance Criteria

The MVP is accepted when all the following are true:

1.  `GET /health` returns HTTP `200` and `status: "healthy"`.
2.  A valid request with inspection `PASS` returns `COMPLETED` and
    includes all three stations in the required order.
3.  A valid request with inspection `FAIL` returns `REJECTED` and does
    not execute Packaging.
4.  Total simulated time is calculated correctly for both pass and fail
    scenarios.
5.  Every defined invalid-input category returns HTTP `400` with the
    documented error structure.
6.  Repeating an identical request produces the same outcome.
7.  Automated unit and API tests pass.
8.  Test results are published as a GitHub Actions workflow artifact or
    visible workflow output.
9.  CI fails when an automated test fails.
10. The container image builds successfully.
11. The application can be deployed to the selected AWS target.
12. A post-deployment smoke test verifies the health endpoint and one
    successful simulation.
13. The README contains local setup, test, container, and deployment
    instructions.

## 8. Testing Requirements

### TR-01: Test Levels

  -----------------------------------------------------------------------
  Test level              Objective               Examples
  ----------------------- ----------------------- -----------------------
  Unit                    Verify simulation and   PASS flow, FAIL flow,
                          validation logic        time calculation
                          independently           

  API / integration       Verify HTTP contract    Health endpoint, valid
                          and response codes      and invalid requests

  Regression              Protect previously      Re-run the complete
                          working behavior        suite after changes

  Smoke                   Confirm deployed        Health endpoint and one
                          service is usable       simulation

  Optional performance    Detect obvious delay    Basic response-time
  sanity                  regressions             threshold
  -----------------------------------------------------------------------

### TR-02: Minimum Scenario Coverage

The test suite shall include, at minimum:

  -----------------------------------------------------------------------
  ID                      Scenario                Expected result
  ----------------------- ----------------------- -----------------------
  TC-01                   Health endpoint         HTTP 200; healthy
                                                  status

  TC-02                   Valid product;          HTTP 200; COMPLETED;
                          inspection PASS         all stations run

  TC-03                   Valid product;          HTTP 200; REJECTED;
                          inspection FAIL         Packaging skipped

  TC-04                   Minimum assembly time = Accepted
                          1                       

  TC-05                   Maximum assembly time = Accepted
                          300                     

  TC-06                   Assembly time = 0       HTTP 400

  TC-07                   Assembly time = 301     HTTP 400

  TC-08                   Minimum packaging time  Accepted
                          = 1                     

  TC-09                   Maximum packaging time  Accepted
                          = 120                   

  TC-10                   Packaging time = 0      HTTP 400

  TC-11                   Packaging time = 121    HTTP 400

  TC-12                   Missing `product_id`    HTTP 400

  TC-13                   Empty or                HTTP 400
                          whitespace-only         
                          `product_id`            

  TC-14                   `product_id` exceeds 50 HTTP 400
                          characters              

  TC-15                   Unsupported inspection  HTTP 400
                          value                   

  TC-16                   Required field has      HTTP 400
                          wrong type              

  TC-17                   Malformed JSON          HTTP 400

  TC-18                   Identical request       Equivalent simulation
                          submitted twice         result

  TC-19                   Invalid request         Valid request still
                          followed by valid       succeeds
                          request                 

  TC-20                   Failed inspection       Total time equals
                          duration                assembly time only

  TC-21                   Successful simulation   Total time equals
                          duration                assembly plus packaging

  TC-22                   Non-object JSON body    HTTP 400
  -----------------------------------------------------------------------

The team may add parameterized tests to cover related input combinations
without duplicating test code.

### TR-03: Test Design Techniques

Use the MVP to demonstrate: - Equivalence partitioning. - Boundary-value
analysis. - Positive and negative testing. - Decision-table or
rule-based testing for inspection PASS/FAIL. - API contract
validation. - Regression testing. - Risk-based prioritization.

### TR-04: Test Evidence

For the final demonstration, retain: - Test case list or test plan. -
Automated test code. - Test execution results. - CI workflow run showing
pass/fail behavior. - At least one example of a defect or deliberately
failing test and its resolution. - Deployment smoke-test output.

## 9. Suggested Technical Implementation

These are recommended training choices, not mandatory product
requirements.

-   **Language:** Python 3.12 or a compatible supported version.
-   **API framework:** FastAPI.
-   **Test framework:** pytest.
-   **API testing:** FastAPI test client / HTTPX.
-   **Quality checks:** Ruff or an equivalent Python linter.
-   **Containerization:** Docker.
-   **Repository:** GitHub.
-   **CI/CD:** GitHub Actions.
-   **AWS target:** Amazon ECS on AWS Fargate, with an Application Load
    Balancer only if accessible within the training budget and time. A
    simpler AWS-hosted container target may be substituted if required
    by the lab environment.
-   **Test reporting:** JUnit XML from pytest and GitHub Actions
    artifacts.
-   **Infrastructure provisioning:** Optional Terraform; do not make it
    a prerequisite for the testing-team MVP.

Use pinned or otherwise reproducible dependencies. Do not commit AWS
credentials, access keys, tokens, or other secrets to the repository.

## 10. Repository Structure

A suitable starting structure is:

``` text
digital-twin-assembly-line/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── simulator.py
├── tests/
│   ├── unit/
│   │   └── test_simulator.py
│   └── api/
│       └── test_api.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── Dockerfile
├── requirements.txt
├── README.md
└── .gitignore
```

The team may adjust the structure while keeping the simulation logic,
API layer, and tests easy to distinguish.

## 11. Definition of Done

A requirement or change is done only when: - Its acceptance criteria are
clear. - Relevant tests are added or updated. - Tests pass locally. -
Lint or configured static checks pass. - The change is reviewed. - CI
validates the branch or pull request. - Documentation is updated where
needed. - Deployment-impacting changes are verified in the target
environment. - No credentials or unnecessary sensitive data are
committed.

## 12. GitHub Copilot Training Workflow

Use Copilot as an assistant; engineers remain responsible for
requirements, correctness, safety, and approval.

1.  **Requirement analysis:** Ask Copilot to identify ambiguity, missing
    cases, and testable acceptance criteria. Review the results against
    this document.
2.  **Test design:** Generate a test-condition matrix using the
    functional requirements and boundary values. Review completeness and
    expected outcomes.
3.  **Test automation:** Generate unit and API tests incrementally.
    Inspect assertions, fixtures, and edge cases before accepting
    changes.
4.  **Development support:** If the training includes implementation,
    use Copilot to create or modify the simulator and API to satisfy the
    tests.
5.  **Test execution and debugging:** Run tests, inspect failures, and
    ask Copilot to explain likely causes. Verify any proposed fix with a
    regression test.
6.  **Refactoring:** Improve readability and remove duplication without
    changing externally observable behavior. Run the full suite before
    and after.
7.  **Code review:** Ask Copilot to review for missing validation, weak
    assertions, hidden dependencies, error handling, security issues,
    and unintended behavior changes.
8.  **CI/CD:** Use GitHub Actions to run lint and tests on pull
    requests, build the container, and publish test evidence.
9.  **AWS deployment:** Deploy the approved image using the chosen AWS
    environment and run post-deployment smoke tests.

Do not accept generated tests solely because they pass. Confirm that the
assertions reflect the requirement and that tests would fail if the
application violated it.

## 13. Suggested 16-Hour Training Plan

The schedule is designed for a **testing team**, so test analysis and
automation receive the most time. Development, refactoring, review, and
deployment are included only to the extent needed to validate the
workflow.

  ------------------------------------------------------------------------
  Session               Concept and hands-on                      Duration
                        activity              
  --------------------- --------------------- ----------------------------
  1\. Use case and      Read the                                     1.5 h
  requirement analysis  requirements;         
                        identify ambiguities, 
                        risks, acceptance     
                        criteria, and         
                        testability gaps with 
                        Copilot               

  2\. Test design       Build a                                      2.0 h
                        test-condition        
                        matrix; apply         
                        equivalence           
                        partitioning,         
                        boundary values, and  
                        positive/negative     
                        testing               

  3\. Test automation   Understand the                               1.5 h
  foundations           starter project,      
                        pytest structure,     
                        fixtures, assertions, 
                        and API test client   

  4\. Hands-on test     Implement unit and                           3.0 h
  automation            API tests for PASS,   
                        FAIL, validation,     
                        boundaries, and       
                        determinism           

  5\. Execute, debug,   Run tests, diagnose                          1.5 h
  and regression test   failures, create a    
                        failing test for a    
                        defect, and verify    
                        the fix               

  6\. Refactoring and   Review test quality                          1.5 h
  code review           and implementation    
                        changes; improve      
                        duplication and       
                        maintainability       
                        without behavior      
                        changes               

  7\. CI/CD with GitHub Run lint and tests,                          2.0 h
  Actions               publish test reports, 
                        build the container,  
                        and demonstrate a     
                        failing pipeline      

  8\. AWS deployment    Deploy to the                                2.0 h
  and smoke test        prepared AWS          
                        environment, run      
                        health and simulation 
                        smoke tests, and      
                        inspect logs          

  9\. Wrap-up and       Review evidence,                             1.0 h
  assessment            gaps, and lessons     
                        learned               

  **Total**                                                     **16.0 h**
  ------------------------------------------------------------------------

### Training setup assumptions

-   Participants have basic Python, Git, and GitHub knowledge.
-   A repository or starter branch is available at the beginning of the
    hands-on session.
-   AWS account access, permissions, region, and deployment target are
    prepared before the class.
-   Docker and required Python tooling are installed or available in a
    prepared development environment.
-   Participants do not need to provision a full production AWS
    architecture from scratch during the 16 hours.
-   AWS resources are deleted or stopped after the lab to avoid
    unnecessary charges.

## 14. Trainer Preparation Checklist

-   [ ] Create a GitHub repository with the requirements and starter
    skeleton.
-   [ ] Decide whether participants implement the API or receive a
    working baseline with intentional defects.
-   [ ] Prepare a known-good reference solution for trainer validation.
-   [ ] Prepare one or two seeded defects, such as incorrect time
    calculation or Packaging running after failed inspection.
-   [ ] Confirm local test commands and dependencies.
-   [ ] Configure GitHub Actions permissions and artifact retention.
-   [ ] Prepare AWS target, deployment role/credentials, networking, and
    cleanup instructions.
-   [ ] Test the complete workflow from pull request to deployment
    before the session.
-   [ ] Set a cost limit and teardown procedure for AWS resources.

## 15. Assessment Rubric

  ------------------------------------------------------------------------
  Area                                        Weight Evidence
  --------------------- ---------------------------- ---------------------
  Requirement                                    15% Clear testable
  understanding                                      conditions and
                                                     identified ambiguity

  Test design and                                25% Positive, negative,
  coverage                                           boundary, and
                                                     rule-based scenarios

  Test automation                                25% Useful assertions,
  quality                                            maintainable
                                                     structure, reliable
                                                     execution

  Debugging and                                  10% Defect isolated and
  regression                                         regression test added

  Review and                                     10% Risks identified;
  refactoring                                        behavior preserved

  CI/CD and test                                 10% Pipeline runs checks
  evidence                                           and exposes results

  Deployment smoke test                           5% Deployed health and
                                                     simulation checks
                                                     succeed

  **Total**                                 **100%** 
  ------------------------------------------------------------------------

## 16. Training Completion Criteria

A participant should be able to: - Convert a compact requirement into
testable acceptance criteria. - Identify missing requirements and ask
focused clarification questions. - Derive meaningful boundary and
negative test cases. - Use Copilot to draft tests while independently
validating the assertions. - Diagnose a failing test and verify the fix
with regression coverage. - Review generated code and tests for
correctness, maintainability, and risk. - Interpret CI results and
understand how a failing test blocks delivery. - Execute a basic smoke
test against the deployed AWS service.

**MVP boundary:** The goal is not to build a sophisticated industrial
digital twin. The goal is to give the testing team a small,
deterministic system that supports a realistic, end-to-end testing and
delivery workflow within 16 hours.
