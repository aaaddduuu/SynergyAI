---
name: "bug-fixer"
description: "Fixes bugs by confirming details, collecting logs, analyzing issues, and executing fixes. Invoke when user reports a bug or needs help debugging issues."
---

# Bug Fixer

## Purpose
This skill helps identify, analyze, and fix bugs in the codebase by following a structured debugging process.

## When to Invoke
Invoke this skill when:
- User reports a bug or issue
- User needs help debugging an error
- User asks to fix a specific problem in the codebase
- Code is not working as expected

## Process Flow

### 1. Confirm Bug Details
- Ask user for:
  - **Affected page/feature** (e.g., "login page", "dashboard search")
  - **Reproduction steps** (exact actions to trigger the bug)
  - **Expected vs actual behavior**
  - **Error messages** (if any)
  - **Browser/device information** (for frontend issues)
  - **Frequency** (how often the bug occurs)
  - **Recent changes** (any code changes before the bug appeared)

### 2. Collect Comprehensive Logs
- **Frontend logs**:
  - Browser console logs (including warnings and errors)
  - Network requests (status codes, response times, payloads)
  - React dev tools component state and props
  - Local storage/cookie information
  - Console timeline and performance data
- **Backend logs**:
  - Server error logs (detailed stack traces)
  - API request/response logs
  - Database query logs
  - Authentication/authorization events
  - Server performance metrics
- **Environment details**:
  - Development/staging/production environment
  - Node.js version
  - Browser versions
  - Network conditions

### 3. Initial Analysis
- **Code analysis**: Search for relevant code files and identify potential root causes
- **Error pattern recognition**: Look for common error patterns in logs
- **Dependency checks**: Verify if dependencies are up-to-date and compatible
- **Reproduce the issue**: Attempt to replicate the bug locally

### 4. Locate the Problem
- **File identification**: Determine which files need modification
- **Line number pinpointing**: Identify specific code sections causing the issue
- **Root cause analysis**: Understand why the bug occurs

### 5. Create Fix Plan
- **Proposed solution**: Detailed steps to fix the bug
- **Impact assessment**:
  - Files to modify
  - Functions/features affected
  - Potential side effects
- **Risk analysis**:
  - Breaking changes
  - Performance impacts
  - Compatibility issues
- **Testing plan**: How to verify the fix works

### 6. Execute Fix
- **Implement changes**: Make the necessary code modifications
- **Run tests**: Execute existing tests and add new test cases if needed
- **Verify fix**: Confirm the bug is resolved
- **Document changes**: Record what was fixed and why

### 7. Deep Dive Investigation (When Bug Persists)

#### 7.1 Extended Data Collection
- **Frontend**:
  - Enable verbose logging
  - Capture network waterfall charts
  - Record browser console with timestamps
  - Take screenshots/video of the issue
  - Check browser extensions that might interfere
- **Backend**:
  - Enable debug logging
  - Capture full request/response payloads
  - Check database transaction logs
  - Monitor server resource usage
  - Review authentication session details

#### 7.2 Systematic Root Cause Analysis
- **Hypothesis Testing**:
  1. Create multiple hypotheses about the root cause
  2. Design experiments to test each hypothesis
  3. Eliminate hypotheses based on test results
  4. Focus on the most likely cause

- **Code Tracing**:
  - Step through code execution line by line
  - Use debug breakpoints to inspect variables
  - Trace data flow through the entire system
  - Identify where the expected behavior diverges

- **Dependency Analysis**:
  - Check for version conflicts
  - Test with different dependency versions
  - Verify API compatibility
  - Check for breaking changes in dependencies

- **Environment Analysis**:
  - Test in different browsers/OS
  - Check network latency and connectivity
  - Verify environment variables
  - Test with different data sets

#### 7.3 Cross-Component Investigation
- **Frontend-Backend Integration**:
  - Verify API contract compliance
  - Check data format transformations
  - Test edge cases and boundary conditions
  - Verify error handling across layers

- **State Management**:
  - Inspect global state consistency
  - Check for race conditions
  - Verify state persistence
  - Test concurrent operations

- **Security Analysis**:
  - Check authentication/authorization flows
  - Verify CSRF/CSRF protections
  - Test for input validation issues
  - Check for session management problems

#### 7.4 Advanced Debugging Techniques
- **Logging Enhancements**:
  - Add strategic debug logs
  - Implement structured logging
  - Add performance metrics
  - Capture execution context

- **Profiling**:
  - Use performance profilers
  - Identify bottlenecks
  - Analyze memory usage
  - Check for memory leaks

- **Staging Environment Testing**:
  - Replicate production environment
  - Test with production-like data
  - Simulate production traffic
  - Monitor system behavior

#### 7.5 Root Cause Confirmation
- **Isolation Testing**:
  - Create minimal reproduction cases
  - Test components in isolation
  - Verify fix in controlled environment
  - Confirm root cause before implementing fix

- **Regression Testing**:
  - Test existing functionality
  - Verify no new issues introduced
  - Test edge cases and boundary conditions
  - Ensure fix doesn't break other features

## Example Usage

### Example 1: Basic Bug Fix

#### Bug Report
User: "The login page is showing an error when I submit the form."

#### Process
1. **Confirm details**: Ask which browser, exact steps, error message
2. **Collect logs**: Request console logs, network responses
3. **Analyze**: Check login form handling code, API endpoints
4. **Locate**: Identify validation issue in form submission
5. **Plan**: Propose fix for form validation logic
6. **Execute**: Implement fix and verify

### Example 2: Persistent Bug Deep Dive

#### Bug Report
User: "I clicked on the analytics page and it still redirects to login, even after you fixed it."

#### Process
1. **Confirm details**: Ask for exact reproduction steps, browser information, error messages
2. **Collect comprehensive logs**:
   - Frontend: Console logs, network waterfall, localStorage state
   - Backend: Server logs, API responses, database queries
3. **Initial analysis**: Check authentication flow, session management
4. **Deep dive investigation**:
   - **Hypothesis testing**: Test multiple potential causes (session cookie issues, API authentication, frontend state management)
   - **Code tracing**: Step through authentication middleware, session validation, API calls
   - **Cross-component investigation**: Check frontend-backend integration, state persistence
   - **Advanced debugging**: Add debug logs, profile network requests
5. **Root cause confirmation**: Isolate the issue to specific component
6. **Execute comprehensive fix**: Address root cause and related issues
7. **Regression testing**: Verify fix works and doesn't break other features

## Best Practices
- **Minimal changes**: Only modify what's necessary to fix the bug
- **Backward compatibility**: Ensure fixes don't break existing functionality
- **Testing**: Always test the fix thoroughly
- **Documentation**: Record the bug and fix for future reference
- **Follow project guidelines**: Adhere to existing code style and architecture

## Deep Dive Best Practices
- **Systematic approach**: Follow a structured process for root cause analysis
- **Hypothesis-driven**: Test multiple hypotheses before settling on a solution
- **Comprehensive logging**: Add strategic logs to capture execution context
- **Isolation testing**: Create minimal reproduction cases to isolate the issue
- **Cross-component thinking**: Consider how different parts of the system interact
- **Environment awareness**: Test across different environments and configurations
- **Performance consideration**: Check for performance impacts during debugging
- **Security focus**: Always consider security implications of bugs and fixes
- **Incremental testing**: Test changes incrementally to identify breaking points
- **Knowledge sharing**: Document findings and solutions for future reference

## Common Bug Types
- **Frontend**: Form validation, state management, API integration, UI rendering
- **Backend**: API errors, database issues, authentication problems, performance bottlenecks
- **Cross-stack**: Data format mismatches, API versioning, environment configuration

## Success Criteria
- Bug is completely resolved
- No new issues introduced
- Tests pass successfully
- Code follows project standards
- Fix is documented properly