import signal
import sys

from tools.common import mcp
from tools import routines 
from tools import workouts
from tools import exercises
from tools import webhooks

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("Received shutdown signal, exiting gracefully...", file=sys.stderr)
    sys.exit(0)

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

from typing import Any  # noqa: F401  (kept for backward-compat import surfaces)

if __name__ == "__main__":
    try:
        # Initialize and run the server
        mcp.run(transport='stdio')
    except BrokenPipeError:
        # Handle broken pipe gracefully when client disconnects
        print("Client disconnected, shutting down gracefully...", file=sys.stderr)
        sys.exit(0)
    except KeyboardInterrupt:
        print("Received interrupt signal, shutting down...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)