CSAW CTF 2018: Ldab
====================

## Description

> dab
> http://web.chal.csaw.io:8080

The website seems to be a list of employees. There's a search bar, which we probably want to exploit.

## Solution

The first hint was in the title ("Ldab" → LDAP). The second hint came from noticing that the results table was empty when typing random queries ("asdf", quotes, etc), but empty _and truncated_ when typing `(` or `)`. A third hint could be found by noticing that `*` returned all results (which made me think of globbing, but wasn't).

A quick search for LDAP vulnerabilities wields [this page](https://www.owasp.org/index.php/Testing_for_LDAP_Injection_(OTG-INPVAL-006)) from the OWASP Wiki, which conveniently lists the syntax for LDAP search queries, common operators, and the way it could be exploited.

We have to guess the format of the query in the PHP code, assuming our input is concatenated somewhere in the middle without any escaping.
The column names are not very user-friendly, so we can assume these are directly the field names on which the query is written.

Finally, we use `*` and a boolean OR to bypass the original query's restrictions:

```
*))(|(GivenName=*
```

This search returns one more "employee", which has the flag!

```
http://web.chal.csaw.io:8080/index.php?search=*%29%29%28%7C%28GivenName%3D*

Employees   flag{ld4p_inj3ction_i5_a_th1ng} Man Flag    fman
```
