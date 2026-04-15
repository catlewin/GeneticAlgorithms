# class for rooms
# Each room has a hall name, room #, and capacity

class Room:
    def __init__(self, name: str, room: int, capacity: int) -> None:
        self.name = name
        self.room = room
        self.capacity = capacity
    def __eq__(self, other):
        return self.name == other.name and self.room == other.room

beach201 = Room("Beach", 201, 18)
beach301 = Room("Beach", 301, 25)
frank119 = Room("Frank", 119, 95)
loft206 = Room("Loft",  206, 55)
loft310 = Room("Loft",  310, 48)
james325 =  Room("James", 325, 110)
roman201 = Room("Roman", 201, 40)
roman216 = Room("Roman", 216, 80)
slater003 = Room("Slater", 3,  32)

rooms = {
    "Beach 201": beach201,
    "Beach 301": beach301,
    "Frank 119": frank119,
    "Loft 206": loft206,
    "Loft 310": loft310,
    "James 325": james325,
    "Roman 201": roman201,
    "Roman 216": roman216,
    "Slater 003": slater003
}

if __name__ == "__main__":
    room1 = Room(name='Beach', room = 201, capacity=10)
    room2 = Room(name='Beach', room = 301, capacity=10)
    print(room1 == room2) # should be false
    room2 = Room(name='Beach', room=201, capacity=10)
    print(room1 == room2) # should be true