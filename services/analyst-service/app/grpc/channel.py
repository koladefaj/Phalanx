import grpc
from typing import Optional

def create_channel(addr: str, options: Optional[list] = None) -> grpc.aio.Channel:
    """Create a standardized async gRPC channel."""
    if options is None:
        options = [
            ('grpc.max_send_message_length', 10 * 1024 * 1024),
            ('grpc.max_receive_message_length', 10 * 1024 * 1024),
        ]
    
    return grpc.aio.insecure_channel(addr, options=options)
