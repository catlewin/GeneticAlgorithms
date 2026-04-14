# file for all fitness functions, with an additional function to call all fitness functions
# import Class from classes
import string

'''Fitness function:
• For each activity, fitness starts at 0.
• Activity is scheduled at the same time in the same room as another of the activities: -0.5
• Room size:
◦ Activities is in a room too small for its expected enrollment: -0.5
◦ Activities is in a room with capacity > 1.5 times expected enrollment: -0.2
◦ Activities is in a room with capacity > 3 times expected enrollment: -0.4
◦ Otherwise + 0.3
• Activities is overseen by a preferred facilitator: + 0.5
• Activities is overseen by another facilitator listed for that activity: +0.2
• Activities is overseen by some other facilitator: -0.1
• Facilitator load:
◦ Activity facilitator is scheduled for only 1 activity in this time slot: + 0.2
◦ Activity facilitator is scheduled for more than one activity at the same time: - 0.2
◦ Facilitator is scheduled to oversee more than 4 activities total: -0.5
◦ Facilitator is scheduled to oversee only <3 activities*: -0.4
▪ Exception: Dr. Tyler is committee chair and has other demands on his time.
*No penalty if he’s only required to oversee < 2 activities.
◦ If any facilitator scheduled for consecutive time slots: Same rules as for SLA 191 and SLA
101 in consecutive time slots—see below.'''

# For each activity, fitness starts at 0.

# treating a schedule as a list of gene classes

# Activity is scheduled at the same time in the same room as another of the activities: -0.5
# def check_room_overlap(schedule):
#
#     for gene in schedule:
#         if gene.room == s