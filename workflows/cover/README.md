# Cover.Ai

Prerequisites for Local Dev Setup

1. Install Dagger.io (IMPORTANT: For now, our agent works on Dagger version `0.18.5`, instructions on how to install a specific version of Dagger can be found [here](https://docs.dagger.io/install/))

## Configuration

1. All repositories should be configured to run tests and generate coverage reports.

2. Configured to create an output file with the test results in JSON format or the format that the reporter plugin supports.

3. A Dockerfile should be present in the repository to run the tests.

4. Create a `config.yaml` file anywhere on desk with the following content:

This is a sample configuration file for our [Github-Dagger-Agent Repo](../../agents/coverage_agent/demo/agencyservices.yaml):

```yaml
$schema: http://json-schema.org/draft-07/schema#

container:
    work_dir: "/app"
    docker_file_path: "./dockerfile"

git:
    user_email: "AiTestGen@users.noreply.github.com"
    user_name: "Ai-TestGen[bot]"

reporter:
    name: "jest"
    command: "npm run test:coverage"
    output_path: "/app/coverage/testResults.json"
    report_directory: "/app/coverage"

test_generation:
    limit: 1
    save_next_to_code_under_test: true
    test_directory: "n/a"
    test_suffix: "test"
```

### Briefly covering all of the properties within the config:

`work_dir` refers to the working directory, which you define within the Dockerfile.  
`docker_file_path` is where you created your Dockerfile in the repository that you want to generate tests for.

`user_email` refers to the email that the agent will adopt when making changes to your repository.
`user_name` refers to the user name that the agent will adopt whenever changes are made to the repository.

`name` refers to the name of the plugin, in this case it is `Jest` (`Pytest` is also supported!).
`output_file_path` points to the file that your reporter reads for the test results.
`report_directory` is unique to your repository and should be replaced with the directory you want your reports to be stored in.

Note that `save_next_to_code_under_test` and `test_directory` toggle each other.
If you set `save_next_to_code_under_test` to be `true`, set `test_directory` to `n/a`. If you set `save_next_to_code_under_test` to be `false`, then you must set `test_directory` to a directory.

## Usage

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

In order to generate a Github token, please visit [here](https://github.com/settings/tokens) (Remember that your token is supposed to be a classic token).
For OpenAI API keys, you must create an OpenAI account and generate a key [here](https://platform.openai.com/api-keys).
For OpenRouter API keys, you must create an OpenRouter account and generate a key [here](https://openrouter.ai/settings/keys).

An example of what a call to dagger using the REQUIRED arguments is:

``` bash
dagger call --config-file ./demo/agencyservices.yaml
generate-unit-tests
--github-access-token=env:GITHUB_TOKEN
--repository-url https://github.com/Siafu/agencyservices-ai.git
--open-router-api-key=env:OPEN_ROUTER_API_KEY
--provider openrouter
--branch feat/loveable-pairing
--model-name x-ai/grok-3-mini-beta
```

# Extensibility

### Currently supported plugins: Jest and Pytest

### To add your own reporter plugin, you must implement the following interface: 
```
get-code-under-test    Extract code under test from the coverage HTML report
get-coverage-html      Get the coverage HTML file from the report file
get-coverage-reports   Extract coverage data from the HTML input and create a JSON file with the data
parse-test-results     Parse the test results JSON file and return a str with the failed tests
```
Reporter Plugin Interface - see [here](../coverage_agent/plugins/reporter/src/reporter/main.py)

## [Click here for Jest implementation](../coverage_agent/plugins/reporter/jest/src/jest_reporter_plugin/main.py)

## [Click here for Pytest implementation](../coverage_agent/plugins/reporter/pytest/src/pytest_reporter_plugin/main.py)




# Agentic Workflow

``` mermaid
flowchart TD
    start[Start Test Generation] --> build[Build Test Environment Container]
    build --> getCoverage[Get Coverage Reports]
    getCoverage --> rankReports[Rank Reports by Coverage Percentage]
    rankReports --> loopReports[Loop Through Ranked Reports]
    
    subgraph ProcessLoop["For each report in limit"]
        loopReports --> runCoverAgent[Run Cover Agent to Generate Tests]
        
        runCoverAgent -- Success --> setupSuccessPR[Setup PR Container]
        runCoverAgent -- Failure/Error --> setupFailurePR[Setup PR Container]
        
        setupFailurePR --> runPRAgent1[Run PR Agent with Error Context]
        runPRAgent1 --> createFailurePR[Create PR with Error Comments]
        createFailurePR --> nextReport[Move to Next Report]
        
        setupSuccessPR --> runPRAgent3[Run PR Agent with Success Context]
        runPRAgent3 --> createSuccessPR[Create PR with New Tests]
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