import atexit

def cleanup():
    # Code to be executed after script exit
    print("Script cleanup")

# Register the cleanup function
atexit.register(cleanup)

while True:
    # Rest of your script code
    print("Script running")
