# class for rooms
# Each room has a hall name, room #, and capacity

class Room:
    def __init__(self, name: str, room: int, capacity: int) -> None:
        self.name = name
        self.room = room
        self.capacity = capacity
    def __eq__(self, other):
        return self.name == other.name and self.room == other.room

if __name__ == "__main__":
    room1 = Room(name='Beach', room = 201, capacity=10)
    room2 = Room(name='Beach', room = 301, capacity=10)
    print(room1 == room2) # should be false
    room2 = Room(name='Beach', room=201, capacity=10)
    print(room1 == room2) # should be true