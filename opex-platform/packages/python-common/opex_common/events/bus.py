class EventBus:
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.connected = False
    
    async def connect_producer(self):
        # Stub implementation
        self.connected = True
        print(f"EventBus connected to {self.bootstrap_servers}")
    
    async def disconnect_producer(self):
        # Stub implementation
        self.connected = False
        print("EventBus disconnected")
