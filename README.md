# GitHub Dagger Agents

<!--
<style>
    body { font-family: Arial, sans-serif; background-color: #0d1117; color: white; padding: 20px; }
    h1, h3 { border-bottom: 1px solid #30363d; padding-bottom: 0.3em; }
    code { background-color: #161b22; padding: 0.2em 0.4em; border-radius: 4px; }
    pre { background-color: #161b22; padding: 1em; border-radius: 6px; overflow: auto; }
    a { color: #58a6ff; text-decoration: underline; }
    ul { list-style-type: disc; margin-left: 20px; }
    strong { font-weight: bold; }
</style>
-->

Cover.ai Test Bot

<br>

<div>
<h1>Prerequisites</h1>

1. Install Dagger.io (Instructions can be found <a target="_blank" href="https://docs.dagger.io/install"/> here</a>)

</div>

<br>

<div>
    
<h1>Configuration</h1>

1. All repositories should be configured to run tests and generate coverage reports.

2. Configured to create an output file with the test results in JSON format or the format that the reporter plugin supports.

3. A Dockerfile should be present in the repository to run the tests.

4. Create a `config.yaml` file anywhere on desk with the following content:

This is a sample configuration file for our [Github-Dagger-Agent Repo]:
```
$schema: http://json-schema.org/draft-07/schema#

container:
    work_dir: "/app"
    docker_file_path: "./dockerfile"

core_api:
    model: "openai/gpt-4o"
    fallback_models:
        - "openai/gpt-4o"
        - "openai/gpt-3.5-turbo"

git:
    user_email: "AiTestGen@users.noreply.github.com"
    user_name: "Ai-TestGen[bot]"

reporter:
    name: "jest"
    command: "npm run test:coverage"
    output_path: "/app/coverage_reports/testResults.json"
    report_directory: "/app/coverage_reports"

test_generation:
    iterations: 1
    save_next_to_code_under_test: false
    test_directory: "tests"
    test_suffix: "test"
```
</div>

<h1>Usage</h1>

In order to see all functions available with these agents, type in the following command using Dagger: ``` dagger functions ```

If additional context is needed as to how a function may work and what the arguments need to be, type in the following command using Dagger: ``` dagger call [function name] --help ```
```
ARGUMENTS
      --branch string                 Branch to generate tests for [required]
      --github-access-token Secret    GitHub access token [required]
      --repository-url string         Repository URL to generate tests for [required]
      --logfire-access-token Secret   Logfire access token
      --model-name string             LLM model name (e.g., 'openai/gpt-4o', 'anthropic/claude-3.5-sonnet') (default "openai/gpt-4.1-nano")
      --open-router-api-key Secret    OpenRouter API key (required if provider is 'openrouter')
      --openai-api-key Secret         OpenAI API key (required if provider is 'openai')
      --provider string               LLM provider ('openrouter' or 'openai') (default "openrouter")
```
Here, we provide the config file, a GitHub classic token, the target branch, an optional Logfire token, the desired model, an API key (OpenRouter or OpenAI), and specify the provider (Openrouter or Openai).

<p> In order to generate a Github token, please visit <a href="https://github.com/settings/tokens">here</a> (Remember that your token is supposed to be a classic token). </p>
<p> For OpenAI API keys, you must create an OpenAI account and generate a key <a href="https://platform.openai.com/api-keys">here</a>. </p>
<p> For OpenRouter API keys, you must create an OpenRouter account and generate a key <a href="https://openrouter.ai/settings/keys">here</a>. </p>

<br>

An example of what a call to dagger using the REQUIRED arguments is:

``` bash
dagger call --config-file ./demo/agencyservices.yaml generate-unit-tests --github-access-token=env:GITHUB_TOKEN --repository-url https://github.com/Siafu/agencyservices-ai.git --open-router-api-key=env:OPEN_ROUTER_API_KEY --provider openrouter --branch feat/loveable-pairing --model-name x-ai/grok-3-mini-beta
```

<h1>Extensibility</h1>

<span>Reporter Plugin Interface - see dagger/src/main/reporter.py</span>
```
get-code-under-test    Extract code under test from the coverage HTML report
get-coverage-html      Get the coverage HTML file from the report file
get-coverage-reports   Extract coverage data from the HTML input and create a JSON file with the data
parse-test-results     Parse the test results JSON file and return a str with the failed tests
validate-config        Validate the configuration file
```

<h2>Jest implementation</h2> 
```
dagger.json

{
  "name": "Reporter",
  "engineVersion": "v0.18.5",
  "sdk": {
    "source": "python"
  },
  "dependencies": [
    {
      "name": "JestReporterPlugin",
      "source": "jest"
    },
    {
      "name": "PytestReporterPlugin",
      "source": "pytest"
    }
  ]
}
```

<br>

<h1>Workflow</h1>

```mermaid
flowchart TD
    start[Start Test Generation] --> build[Build Test Environment Container]
    build --> getCoverage[Get Coverage Reports]
    getCoverage --> rankReports[Rank Reports by Coverage Percentage]
    rankReports --> loopReports[Loop Through Ranked Reports]
    
    subgraph ProcessLoop["For each report in limit"]
        loopReports --> runCoverAgent[Run Cover Agent to Generate Tests]
        
        runCoverAgent -- Success --> runReviewAgent[Run Review Agent]
        runCoverAgent -- Failure/Error --> setupFailurePR[Setup PR Container]
        
        setupFailurePR --> runPRAgent1[Run PR Agent with Error Context]
        runPRAgent1 --> createFailurePR[Create PR with Error Comments]
        createFailurePR --> nextReport[Move to Next Report]
        
        runReviewAgent -- Coverage Increased --> setupSuccessPR[Setup PR Container]
        runReviewAgent -- No Increase/Error --> setupInsightPR[Setup PR Container]
        
        setupInsightPR --> runPRAgent2[Run PR Agent with Insight Context]
        runPRAgent2 --> createInsightPR[Create PR with Coverage Insights]
        createInsightPR --> nextReport
        
        setupSuccessPR --> runPRAgent3[Run PR Agent with Success Context]
        runPRAgent3 --> createSuccessPR[Create PR with Test Improvements]
        createSuccessPR --> nextReport
    end
    
    ProcessLoop --> finish[Return Final Container]
    
    subgraph CoverAgentProcess["Cover Agent Process"]
        getCT[Get Code Under Test] --> analyzeCR[Analyze Coverage Report]
        analyzeCR --> genTests[Generate Unit Tests]
        genTests --> runTests[Run Tests in Container]
        runTests -- Success --> returnTests[Return CodeModule]
        runTests -- Failure --> fixTests[Fix Tests]
        fixTests --> runTests
    end
    
    subgraph ReviewAgentProcess["Review Agent Process"]
        getInitialCov[Get Initial Coverage] --> getCurrentCov[Get Current Coverage]
        getCurrentCov --> compare[Compare Coverage]
        compare --> returnResult[Return CoverageReview]
    end
    
    subgraph PRAgentProcess["Pull Request Agent Process"]
        gitAdd[Git Add Changes] --> gitCommit[Git Commit]
        gitCommit --> gitPush[Git Push to Remote]
        gitPush --> checkPR[Check if PR Exists]
        checkPR -- PR Exists --> updateExisting[Update Existing PR]
        checkPR -- No PR --> createNewPR[Create New PR]
        createNewPR --> done[Done]
        updateExisting --> done
    end

```
