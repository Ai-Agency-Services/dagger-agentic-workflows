# GithubDaggerAgents

```mermaid
flowchart TD
    start[Start Test Generation] --> build[Build Test Environment Container]
    build --> getCoverage[Get Coverage Reports]
    getCoverage --> rankReports[Rank Reports by Coverage Percentage]
    rankReports --> loopReports[Loop Through Ranked Reports]
    
    subgraph ProcessLoop["For each report in limit"]
        loopReports --> runCoverAgent[Run Cover Agent to Generate Tests]
        runCoverAgent -- Success --> setupPR[Setup Pull Request Container]
        runCoverAgent -- Failure/Error --> nextReport[Skip to Next Report]
        
        setupPR --> runPRAgent[Run Pull Request Agent]
        runPRAgent -- Success --> reviewDeps[Create Review Dependencies]
        runPRAgent -- Failure/Error --> nextReport
        
        reviewDeps --> runReviewAgent[Run Review Agent]
        runReviewAgent -- Coverage Increased --> updateContainer[Update Container State]
        runReviewAgent -- No Increase/Error --> nextReport
        
        updateContainer --> createPR[Create New PR or Update Existing]
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
        checkPR -- PR Exists --> done[Done]
        checkPR -- No PR --> createNewPR[Create New PR]
        createNewPR --> done
    end
    
    subgraph ReviewAgentProcess["Review Agent Process"]
        getInitialCov[Get Initial Coverage] --> getCurrentCov[Get Current Coverage]
        getCurrentCov --> compare[Compare Coverage]
        compare --> returnResult[Return CoverageReview]
    end
