# @agent-infra/browser-use

A browser automation and interaction library for AI agents, providing structured DOM access and browser control capabilities. This package is designed to empower AI agents to understand and interact with web pages programmatically.

It appears to be heavily inspired by or based on parts of the [nanobrowser](https://github.com/nanobrowser/nanobrowser) project.

## Core Functionalities

The `@agent-infra/browser-use` package offers several key capabilities for building browser-based AI agents:

1.  **Agent Service (`src/agent/service.ts`)**:
    *   Provides an `Agent` class that orchestrates tasks within a browser context.
    *   Integrates with a Language Model (LLM, specifically `BaseChatModel` from Langchain) to drive agent decisions and actions.
    *   Manages task execution জীবন-ചക്രം (lifecycle) through an `Executor` class, emitting events for each step.
    *   Allows for custom callbacks (`registerNewStepCallback`) to monitor agent progress.

2.  **Browser Page Control (`src/browser/page.ts`)**:
    *   Features a `Page` class that wraps Puppeteer's `Page` object, offering a higher-level API for browser interactions.
    *   Manages page state, including DOM structure, URL, title, screenshots, and scroll information.
    *   Handles Puppeteer page attachment and detachment.
    *   Injects "anti-detection" scripts to mitigate bot-blocking mechanisms.
    *   Provides comprehensive methods for:
        *   Navigation (goto, back, forward, reload).
        *   DOM element interaction (click, type text, select dropdown options).
        *   Content retrieval (HTML, Markdown, Readability-enhanced content).
        *   Taking screenshots.
        *   Sending keyboard inputs.
        *   Scrolling.

3.  **DOM Service (`src/dom/service.ts`)**:
    *   Offers utilities for processing and understanding web page DOM structures.
    *   Builds a structured representation of the DOM, identifying interactive elements (`getClickableElements`). This likely involves injecting and executing the `assets/buildDomTree.js` script on the page.
    *   Parses raw DOM tree data into internal `DOMElementNode` and `DOMTextNode` views.
    *   Provides functions to get page scroll information, convert page content to Markdown, and extract clean content using a Readability-like mechanism.
    *   Manages highlighting of elements on the page for debugging or agent feedback.

4.  **Package Entry Point (`src/index.ts`)**:
    *   Exports the main components of the package, including:
        *   `Agent` class from `agent/service.ts`.
        *   DOM manipulation utilities like `createSelectorMap`, `parseNode`, `removeHighlights` from `dom/service.ts`.
        *   Helper functions like `getBuildDomTreeScript` from `utils.ts`.
        *   Type definitions such as `RawDomTreeNode` and `DOMElementNode`.
        *   Browser utility functions from `browser/utils.ts`.

## Key Abstractions and Concepts

*   **`Agent`**: The central orchestrator that takes a task string and uses an LLM and browser context to execute it.
*   **`BrowserContext` (`src/browser/context.ts`)**: Manages the overall browser environment settings. (Details not fully analyzed in this pass).
*   **`Page` (`src/browser/page.ts`)**: Represents a single browser tab/page, providing methods to interact with it.
*   **`Executor` (`src/agent/executor.ts`)**: Responsible for the step-by-step execution of an agent's plan. (Details not fully analyzed in this pass).
*   **`DOMElementNode` / `DOMTextNode` (`src/dom/views.ts`)**: Internal representations of DOM elements and text nodes, likely enriched with information relevant to agent interaction (e.g., visibility, interactivity, XPath, CSS selectors, highlight index).
*   **`buildDomTree.js` (`assets/`)**: A client-side JavaScript likely injected into the browser page to extract DOM information in a structured way, which is then processed by `dom/service.ts`.

## Usage (Conceptual)

```typescript
// Conceptual example based on analyzed files
import { Agent } from '@agent-infra/browser-use';
import { YourChatModel } from 'your-llm-provider'; // e.g., ChatOpenAI

// Initialize your LLM
const llm = new YourChatModel({ apiKey: 'YOUR_API_KEY' });

// Create an agent instance
const agent = new Agent(llm, {
  registerNewStepCallback: async (event) => {
    console.log('Agent Step:', event.type, event.state, event.data);
    // Handle agent events, update UI, etc.
  },
  // browserContextConfig can be provided if needed
});

// Run a task
async function runAgentTask() {
  try {
    const taskDescription = "Find the current weather in London and tell me.";
    await agent.run(taskDescription);
    console.log('Agent task finished.');
  } catch (error) {
    console.error('Agent task failed:', error);
  }
}

runAgentTask();
```

## Dependencies

*   **Puppeteer-core**: For core browser automation capabilities. The actual browser connection might be handled by a wrapper like `@agent-infra/browser`'s `LocalBrowser`.
*   **Langchain (`@langchain/core`)**: Used for LLM interaction, specifically `BaseChatModel`.
*   **UUID**: For generating unique IDs, likely for tasks or sessions.

## Further Analysis Points

*   Detailed implementation of `BrowserContext` and its configuration.
*   The internal workings of the `Executor` class and how it plans and executes steps.
*   Specific prompt engineering techniques used in `src/agent/prompts/`.
*   The exact structure and functionality of the client-side `assets/buildDomTree.js` script.
*   Error handling and retry mechanisms within the agent and browser interactions.
*   The role of `rslib.config.ts` in the build process.

## Credits

Thanks to:

- The [browser-use](https://github.com/browser-use/browser-use) project which helps us operate the browser better.
- [alexchenzl](https://github.com/alexchenzl) for creating a great [nanobrowser](https://github.com/nanobrowser/nanobrowser) Chrome extension from which we got a lot of technical references when implementing browser in Electron
- The [puppeteer](https://github.com/puppeteer/puppeteer) project which helps us operate the browser better.
```
