# CLIENT CODE
import asyncio
import websockets
import threading
import queue
import json
# Message queue for communication between threads
message_queue = queue.Queue()
name = input("Enter your name: ")
# Function to get user input in a separate thread
def get_user_input():
    while True:
        message = input("Enter message: ")
        message_queue.put(message)

# Function to handle the chat client
async def chat_client():
    uri = "ws://localhost:12345"
    
    # Ask for the user's name
    
    
    print(f"Connecting to server as {name}...")
    
    async with websockets.connect(uri) as websocket:
        print("Connected to server!")
        message={"text":f"{name} has joined the chat","type":"notification"}

        # First send the name to the server
        await websocket.send(json.dumps(message))
        
        # Start input thread
        input_thread = threading.Thread(target=get_user_input, daemon=True)
        input_thread.start()
        
        # Task for receiving messages
        receive_task = asyncio.create_task(receive_messages(websocket))
        
        # Task for sending messages from the queue
        send_task = asyncio.create_task(send_messages(websocket))
        
        # Wait for either task to complete
        await asyncio.gather(receive_task, send_task)

# Function to receive messages continuously
async def receive_messages(websocket):
    try:
        while True:
            
            message = await websocket.recv()
            message=json.loads(message)
            if message["type"]=="message":
                name=message["name"]
                text=message["text"]
                print(f"\n{name}: {text}")
            else:

                print(f"\n{message["text"]}")
            print("Enter message: ", end="", flush=True)  # Re-prompt
    except websockets.exceptions.ConnectionClosed:
        print("\nConnection to server closed")

# Function to send messages from the queue
async def send_messages(websocket):
    try:
        while True:
            # Check the queue for new messages without blocking
            if not message_queue.empty():
                text = message_queue.get()
                message={"text":text,"type":"message","name":name}
                await websocket.send(json.dumps(message))
            
            # Yield control to allow other tasks to run
            await asyncio.sleep(0.1)
    except websockets.exceptions.ConnectionClosed:
        print("\nConnection to server closed")

# Run the client
if __name__ == "__main__":
    try:
        asyncio.run(chat_client())
    except KeyboardInterrupt:
        print("\nClient terminated by user")
    except Exception as e:
        print(f"\nError: {e}")