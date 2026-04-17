import { useState, useEffect, useCallback, useRef } from 'react';

interface WebRTCStreamConfig {
  serverUrl: string;
  streamId: string;
}

interface WebRTCStreamState {
  isConnected: boolean;
  isStreaming: boolean;
  error: string | null;
  latencyMs: number;
}

export const useWebRTCStream = (config: WebRTCStreamConfig) => {
  const [state, setState] = useState<WebRTCStreamState>({
    isConnected: false,
    isStreaming: false,
    error: null,
    latencyMs: 0,
  });

  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  const connect = useCallback(async () => {
    try {
      const pc = new RTCPeerConnection({
        iceServers: [{ urls: 'stun:stun.l.google.com:19302' }],
      });

      pc.oniceconnectionstatechange = () => {
        setState(prev => ({
          ...prev,
          isConnected: pc.iceConnectionState === 'connected',
        }));
      };

      pc.ontrack = (event) => {
        if (videoRef.current && event.streams[0]) {
          videoRef.current.srcObject = event.streams[0];
          setState(prev => ({ ...prev, isStreaming: true }));
        }
      };

      // Add transceiver for receiving video
      pc.addTransceiver('video', { direction: 'recvonly' });

      // Create and set offer
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      peerConnectionRef.current = pc;
      setState(prev => ({ ...prev, isConnected: true, error: null }));
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: err instanceof Error ? err.message : 'Connection failed',
      }));
    }
  }, []);

  const disconnect = useCallback(() => {
    if (peerConnectionRef.current) {
      peerConnectionRef.current.close();
      peerConnectionRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setState({
      isConnected: false,
      isStreaming: false,
      error: null,
      latencyMs: 0,
    });
  }, []);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    ...state,
    videoRef,
    connect,
    disconnect,
  };
};

export default useWebRTCStream;
