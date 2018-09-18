bits 32
  call getend
  mov cl, 0x41
  mov ebx, 0x00b8000
  mov edx, 0x60
loop:
  mov byte [ebx], cl
  add ebx, 1
  mov byte [ebx], 0x1f
  add ebx, 1
  mov byte cl, [eax]
  add eax, 1
  add edx, -1
  cmp edx, 0
  je loop2
  jmp loop
loop2:
  jmp loop2
getend:
  call end
end:
  pop eax
  ret

;.flag: db "flag{xxx}", 0, 0, 0
