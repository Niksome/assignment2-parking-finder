 Fortune Meya

What I implemented:
I built the Parking client stub and server skeleton for Part B. This includes the 4 Parking methods, length-prefixed JSON framing, and timeout handling.

A bug I fixed:
My try block was outside the with socket block so the socket was closing before anything got sent. Moved it inside and it worked.

One design change:
I used mocked return values in dispatch first so I could test without waiting on the rest of the team, then swapped in the real parking logic once it was ready.