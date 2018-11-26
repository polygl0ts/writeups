TUCTF 2018: Colonel Mustard's Simple Signin
=============================

## Description

We know Col Mustard is up to something--can you find a way in to tell us what?

http://13.59.239.132/

## Solution

The website is just a login page. When trying inputs we notices that it is weak to SQL injection.

So we input `' or '1' = '1` in both the user and password textfield. (this SQL injection works in the password textfiled)

We are redirected to the page with the flag:

`TUCTF{1_4ccu53_c0l0n3l_mu574rd_w17h_7h3_r0p3_1n_7h3_l061n}`