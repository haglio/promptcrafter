import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './tokens.css';
import './styles.css';
import { schema } from './lib/schema';
// import { testSchema } from './test/fixtures/testSchema';

function reportLauncherEvent(kind: string, detail: string) {
  const payload = JSON.stringify({ kind, detail });

  if (navigator.sendBeacon) {
    navigator.sendBeacon('/__launcher_log__', payload);
    return;
  }

  void fetch('/__launcher_log__', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: payload,
    keepalive: true,
  });
}

class RootErrorBoundary extends React.Component<
  React.PropsWithChildren,
  { error: Error | null }
> {
  constructor(props: React.PropsWithChildren) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    reportLauncherEvent('react.error', `${error.stack ?? error.message}\n${info.componentStack}`);
  }

  render() {
    if (this.state.error) {
      return (
        <main className="app-shell app-error-shell">
          <header>
            <h1>PromptCrafter</h1>
          </header>
          <section className="prompt-area">
            <h2>PromptCrafter hit an error while rendering.</h2>
            <p>Check <code>promptcrafter-launcher.log</code> for details.</p>
          </section>
        </main>
      );
    }

    return this.props.children;
  }
}

window.addEventListener('error', (event) => {
  reportLauncherEvent('window.error', `${event.message} @ ${event.filename}:${event.lineno}:${event.colno}`);
});

window.addEventListener('unhandledrejection', (event) => {
  const reason = event.reason instanceof Error ? event.reason.stack ?? event.reason.message : String(event.reason);
  reportLauncherEvent('unhandledrejection', reason);
});

reportLauncherEvent('boot', 'PromptCrafter frontend bootstrap started.');

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('PromptCrafter root element was not found.');
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <RootErrorBoundary>
      <App schema={schema}/>
    </RootErrorBoundary>
    {/* <App schema={testSchema}/> */}
  </React.StrictMode>,
);

reportLauncherEvent('render', 'PromptCrafter React root render submitted.');

window.setTimeout(() => {
  const computedBodyStyle = window.getComputedStyle(document.body);
  reportLauncherEvent(
    'dom',
    JSON.stringify({
      rootChildCount: rootElement.childElementCount,
      rootTextLength: rootElement.textContent?.length ?? 0,
      bodyBackground: computedBodyStyle.backgroundColor,
      bodyColor: computedBodyStyle.color,
    }),
  );
}, 1000);
