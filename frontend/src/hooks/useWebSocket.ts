import { useEffect, useRef } from "react";
import { wsUrl } from "../api/client";

type MessageHandler = (type: string, data: any) => void;

/**
 * Verbindet sich mit dem Backend-WebSocket und verbindet sich bei Verbindungsabbruch
 * automatisch neu (Exponential Backoff), damit das Dashboard dauerhaft live bleibt.
 */
export function useWebSocket(onMessage: MessageHandler) {
  const handlerRef = useRef(onMessage);
  handlerRef.current = onMessage;

  useEffect(() => {
    let socket: WebSocket | null = null;
    let retryDelay = 1000;
    let closedByClient = false;
    let retryTimeout: ReturnType<typeof setTimeout>;

    function connect() {
      socket = new WebSocket(wsUrl());

      socket.onopen = () => {
        retryDelay = 1000;
      };

      socket.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          handlerRef.current(parsed.type, parsed.data);
        } catch {
          /* ignorieren */
        }
      };

      socket.onclose = () => {
        if (closedByClient) return;
        retryTimeout = setTimeout(connect, retryDelay);
        retryDelay = Math.min(retryDelay * 2, 30000);
      };
    }

    connect();

    return () => {
      closedByClient = true;
      clearTimeout(retryTimeout);
      socket?.close();
    };
  }, []);
}
