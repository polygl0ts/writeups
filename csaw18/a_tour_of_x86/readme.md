# Writeup of 'a tour of x86'

I'm a sucker for low level code, especially 16 bit code and DOS challenges. So
even though this was a beginners challenge, I had to take a look at it (also, we
did not have a junior working on it at the time).

The challenge was set in three stages that gradually progressed from reading an
ASM file to reversing a 16 bit code, jumping into protected mode then writing
shellcode for protected mode in a constrained environment.

## Stage 1 (50 points)

Read the stage-1.asm first and follow the simple questions

> xor dh, dh ; 0x00
> mov gs, dx ; 0x0000
> mov si, sp ; 0x0000
> mov al, 't' \n mov ah, 0x0e ; 0x0e74
> mov al, [si] \n mov ah, 0x0e ; 0x0e6c

This stage was very simple, you need to check the last
couple of bytes, translate letters into hex, combine registers, and you're done.

## Stage 2 (100 points)

Check stage 2, there's lots of odd code. A tricky part was to disassemble the 16
bit code and to check where it switches to protected mode. I searched for the
lgdtw instruction and checked where the long jump headed to after that:

> objdump -D -b binary -mi386 -Maddr16,data16 tacOS.bin|less

> lgdtw  0x60e2
> ljmp   $0x8,$0x6158

As the segments are set up so that code is located at 0x6000, we know that the
offset in stage-2 now is 0x158 where the funky protected code stuff starts.

A hexdump of stage-2.bin shows that between 0xe8 and 0x158 there's an
interesting data section. ;)

If we disassemble 0x158 onward, this time no longer in 16-bit mode
> dd if=stage-2.bin of=out.bin bs=1 skip=344
> objdump -D -b binary -mi386 out.bin|less

We see that the code starts with a hlt instruction. hlt instructions stop
execution. We therefore edit stage-1.asm again and replace:

>  jmp LOAD_ADDR
with
>  jmp LOAD_ADDR+1  

And do a make run and get the flag! :)

## Stage 3 (200 points)

We got to write asm code that is executed. From looking at the server we see
that our code is appended at the end in a new block (which is then jumped into)
plus the flag is directly appended to our code.

We therefore whip out some quick asm code to print the flag one by one using the
getrip trip of early shellcode:

> bits 32
>   call getend
>   mov cl, 0x41
>   mov ebx, 0x00b8000
>   mov edx, 0x60
> loop:
>   mov byte [ebx], cl
>   add ebx, 1
>   mov byte [ebx], 0x1f
>   add ebx, 1
>   mov byte cl, [eax]
>   add eax, 1
>   add edx, -1
>   cmp edx, 0
>   je loop2
>   jmp loop
> loop2:
>   jmp loop2
> getend:
>   call end
> end:
>   pop eax
>   ret 

After sending the code to the server and running it, we get the flag.
Interestingly, we could have shortened the code and made it nicer by checking
for the 0x0 byte at the end of the flag instead of decrementing edx.

Also, for the interested reader: why can we use 32-bit code in this environment?
Second question: why would inc fail? The answer is left to the interested
reader. :D
