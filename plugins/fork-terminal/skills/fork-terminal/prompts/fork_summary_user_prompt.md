# Fork Summary User Prompt Template

Use this template when the user requests a fork "with summary" or wants to pass conversation context to the forked agent.

## Template Structure

```markdown
## History

<fill_in_conversation_summary_here>

Summarize the prior conversation in YAML format:

- user_prompt: "<summarized user message 1>"
  agent_response: "<summarized agent response 1>"
- user_prompt: "<summarized user message 2>"
  agent_response: "<summarized agent response 2>"
...

## Next User Request

<fill_in_next_user_request_here>

The task or instruction for the forked agent to execute.
```

## Instructions

1. Only use this template for agentic coding tools (Claude Code, Codex, Gemini) that support context handoff
2. Do NOT modify any files to create this prompt - construct it in memory
3. Summarize conversation history concisely, focusing on:
   - Key decisions made
   - Important context established
   - Relevant code or file references
4. Keep the "Next User Request" clear and actionable

## Example

```markdown
## History

- user_prompt: "Set up a new React project"
  agent_response: "Created React app with TypeScript, added ESLint and Prettier"
- user_prompt: "Add authentication"
  agent_response: "Installed NextAuth.js, created auth provider and login page"

## Next User Request

Add user profile page with ability to update name and email
```
