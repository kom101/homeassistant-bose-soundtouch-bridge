#!/usr/bin/env python3
"""Debug WebSocket messages from a real Bose SoundTouch speaker."""

import sys
import argparse
from datetime import datetime

try:
    import websocket
except ImportError:
    print("ERROR: websocket-client not installed. Install it with: pip install websocket-client")
    sys.exit(1)

from bose_bridge.helpers import _parse_ws_preset_id, _parse_ws_button_event

def debug_websocket(host: str, duration_seconds: int = 60):
    """Connect to a real speaker and log all WebSocket messages."""
    ws_url = f"ws://{host}:8080"
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Connecting to {ws_url}...")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Listening for {duration_seconds} seconds")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Press buttons on your remote...\n")
    
    message_count = 0
    preset_count = 0
    button_count = 0
    
    def on_message(ws, message):
        nonlocal message_count, preset_count, button_count
        message_count += 1
        
        # Try to extract preset and button
        preset_id = _parse_ws_preset_id(message)
        button_event = _parse_ws_button_event(message)
        
        # Abbreviated output (show first 150 chars)
        msg_abbr = message[:150].replace('\n', ' ')
        if len(message) > 150:
            msg_abbr += "..."
        
        print(f"[MSG #{message_count}] {msg_abbr}")
        
        if preset_id:
            preset_count += 1
            print(f"  → PRESET DETECTED: {preset_id}\n")
        elif button_event:
            button_count += 1
            print(f"  → BUTTON DETECTED: {button_event}\n")
        else:
            print()  # newline for spacing
    
    def on_error(ws, error):
        print(f"[ERROR] {error}")
    
    def on_close(ws, close_status_code, close_msg):
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] WebSocket closed")
    
    def on_open(ws):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] WebSocket connected ✓\n")
    
    try:
        ws = websocket.WebSocketApp(
            ws_url,
            subprotocols=["gabbo"],
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        
        # Run with timeout
        ws.run_forever(ping_interval=10, ping_timeout=5)
        
    except KeyboardInterrupt:
        print("\n[INTERRUPTED]")
    except Exception as e:
        print(f"[FATAL] {e}")
        sys.exit(1)
    finally:
        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  Messages received: {message_count}")
        print(f"  Presets detected: {preset_count}")
        print(f"  Buttons detected: {button_count}")
        print(f"{'='*60}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Debug WebSocket messages from a Bose SoundTouch speaker"
    )
    parser.add_argument(
        "host",
        help="IP address of your Bose SoundTouch speaker (e.g., 192.168.1.100)"
    )
    parser.add_argument(
        "-d", "--duration",
        type=int,
        default=60,
        help="Listen for N seconds (default: 60)"
    )
    
    args = parser.parse_args()
    
    try:
        debug_websocket(args.host, args.duration)
    except KeyboardInterrupt:
        print("\n[Stopped by user]")
        sys.exit(0)
