# CSAW CTF 2018: Algebra



## Description

This was a challenge in the Misc category with the following description:

**Are you a real math wiz?**

`nc misc.chal.csaw.io 9002`



On connecting to the server, we receive an equation:

`4 - X = 55`

`What does X equal?:`

If we solve the equation, we get a new one. The idea is to solve for X till we (hopefully) get the flag.



## Solution

My initial thought was to write my own solver in python. However, a quick Google search revealed a nice library, **SymPy**, that eases the process of calculation.

The script, **algebra.py**, has the code to solve the challenge using SymPy. I also used the **pwn** library for handling the netcat connection with the server.

The challenge was relatively straightforward; I only had to spend a little bit of time reading the SymPy documentation to ensure that my inputs were in the correct format for the module. Code flow is as follows:

- Use pwn to connect to the server and receive the input
- Perform some pre-processing to get the equation (in string format) from the input
- Split the string to the left hand side (L.H.S) and right hand side (R.H.S) of the equation
- Convert the L.H.S and R.H.S from string to a SymPy expression using Sympy's parse_expr()
- Solve the equation using SymPy's Eq and solve functions
- Send the result back to the server. Note: When the solution is 0 or 1, SymPy converts it into Boolean True/False so you have to change it before sending.
- Repeat



## Flag

flag{y0u_s0_60od_aT_tH3_qU1cK_M4tH5}
