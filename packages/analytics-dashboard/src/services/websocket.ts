/**
 * WebSocket Service - Connection lifecycle management
 */
import type { AnalyticsEvent, ConnectionStatus } from '../types';

/**
 * Strip CR/LF and other control characters before a server-sent value is
 * written to the console. Incoming WebSocket events are not trusted input,
 * so logging them raw risks forged/injected log lines (CodeQL
 * js/log-injection).
 */
function sanitizeForLog(value: unknown): string {
  const str = typeof value === 'string' ? value : JSON.stringify(value);
  return str.replace(/[\r\n\x00-\x1f\x7f]/g, '');
}

export type WebSocketEventHandler = (event: AnalyticsEvent) => void;
export type ConnectionStatusHandler = (status: ConnectionStatus) => void;
export type ErrorHandler = (error: Error) => void;

export interface WebSocketServiceConfig {
  url: string;
  reconnectDelay?: number;
  maxReconnectAttempts?: number;
}

/**
 * WebSocket service for real-time analytics events
 */
export class WebSocketService {
  private ws: WebSocket | null = null;
  private config: Required<WebSocketServiceConfig>;
  private reconnectAttempts = 0;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private isManualClose = false;

  // Event handlers
  private eventHandlers: Set<WebSocketEventHandler> = new Set();
  private statusHandlers: Set<ConnectionStatusHandler> = new Set();
  private errorHandlers: Set<ErrorHandler> = new Set();

  constructor(config: WebSocketServiceConfig) {
    this.config = {
      url: config.url,
      reconnectDelay: config.reconnectDelay ?? 3000,
      maxReconnectAttempts: config.maxReconnectAttempts ?? Infinity,
    };
  }

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.warn('WebSocket already connected');
      return;
    }

    this.isManualClose = false;
    this.updateStatus('connecting');

    try {
      this.ws = new WebSocket(this.config.url);
      this.setupEventListeners();
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.handleError(error as Error);
      this.scheduleReconnect();
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.isManualClose = true;
    this.clearReconnectTimer();
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.updateStatus('disconnected');
  }

  /**
   * Setup WebSocket event listeners
   */
  private setupEventListeners(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('WebSocket connected to', this.config.url);
      this.reconnectAttempts = 0;
      this.updateStatus('connected');
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as AnalyticsEvent;
        this.handleEvent(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
        this.handleError(new Error('Invalid JSON received'));
      }
    };

    this.ws.onerror = (event) => {
      console.error('WebSocket error:', event);
      this.handleError(new Error('WebSocket connection error'));
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason);
      this.updateStatus('disconnected');
      
      if (!this.isManualClose) {
        this.scheduleReconnect();
      }
    };
  }

  /**
   * Schedule reconnection attempt
   */
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      console.error('Max reconnect attempts reached');
      this.handleError(new Error('Failed to reconnect after maximum attempts'));
      return;
    }

    this.clearReconnectTimer();
    this.reconnectAttempts++;

    console.log(
      `Reconnecting in ${this.config.reconnectDelay}ms (attempt ${this.reconnectAttempts})`
    );

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, this.config.reconnectDelay);
  }

  /**
   * Clear reconnect timer
   */
  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  /**
   * Handle incoming event
   */
  private handleEvent(event: AnalyticsEvent): void {
    console.log('Received event:', sanitizeForLog(event.type), sanitizeForLog(event));
    this.eventHandlers.forEach((handler) => handler(event));
  }

  /**
   * Update connection status
   */
  private updateStatus(status: ConnectionStatus): void {
    this.statusHandlers.forEach((handler) => handler(status));
  }

  /**
   * Handle error
   */
  private handleError(error: Error): void {
    this.errorHandlers.forEach((handler) => handler(error));
  }

  /**
   * Subscribe to events
   */
  onEvent(handler: WebSocketEventHandler): () => void {
    this.eventHandlers.add(handler);
    return () => this.eventHandlers.delete(handler);
  }

  /**
   * Subscribe to status changes
   */
  onStatusChange(handler: ConnectionStatusHandler): () => void {
    this.statusHandlers.add(handler);
    return () => this.statusHandlers.delete(handler);
  }

  /**
   * Subscribe to errors
   */
  onError(handler: ErrorHandler): () => void {
    this.errorHandlers.add(handler);
    return () => this.errorHandlers.delete(handler);
  }

  /**
   * Get current connection status
   */
  getStatus(): ConnectionStatus {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      default:
        return 'disconnected';
    }
  }
}
