# (The WOD : (.....) class is open for reservation)

import re

message = "The WOD : 04h00 class is open for reservation"

subject = re.search("(?P<msg>The WOD : (.....) class is open for reservation)", message)

if subject:
    subject = subject.group("msg")

print subject
