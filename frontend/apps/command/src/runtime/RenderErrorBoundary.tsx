import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  domain: string;
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  message: string;
}

export class RenderErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, message: '' };

  static getDerivedStateFromError(err: Error): State {
    return { hasError: true, message: err.message };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.warn(`[${this.props.domain}] render recovery`, error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div className="flex h-full flex-col items-center justify-center bg-slate-950 p-4 text-center">
            <p className="font-mono text-xs uppercase tracking-widest text-amber-400">
              {this.props.domain} · degraded mode
            </p>
            <p className="mt-2 max-w-sm text-[10px] text-slate-500">{this.state.message}</p>
            <button
              type="button"
              className="mt-4 rounded border border-slate-700 px-3 py-1 text-[10px] text-cyan-400"
              onClick={() => this.setState({ hasError: false, message: '' })}
            >
              Recover render
            </button>
          </div>
        )
      );
    }
    return this.props.children;
  }
}
