# SimpleAuth

The challenge server is running the following PHP script:

```php
<?php

require_once 'flag.php';

if (!empty($_SERVER['QUERY_STRING'])) {
    $query = $_SERVER['QUERY_STRING'];
    $res = parse_str($query);
    if (!empty($res['action'])){
        $action = $res['action'];
    }
}

if ($action === 'auth') {
    if (!empty($res['user'])) {
        $user = $res['user'];
    }
    if (!empty($res['pass'])) {
        $pass = $res['pass'];
    }

    if (!empty($user) && !empty($pass)) {
        $hashed_password = hash('md5', $user.$pass);
    }
    if (!empty($hashed_password) && $hashed_password === 'c019f6e5cd8aa0bbbcc6e994a54c757e') {
        echo $flag;
    }
    else {
        echo 'fail :(';
    }
}
else {
    highlight_file(__FILE__);
}
```

The only input to the script that we control is the query string. We can see
that `parse_str` is used to parse it, so the next step is to read the
documentation for `parse_str` and see if it can be exploited.

From the PHP documentation:

> Parses encoded_string as if it were the query string passed via a URL and
sets variables in the current scope (or in the array if result is provided).  
> **Warning** Using this function without the result parameter is highly
DISCOURAGED and DEPRECATED as of PHP 7.2.  
> Read section on security of Using Register Globals explaining why it is
dangerous.

What this means is that, unless a second argument is passed to `parse_str`,
all variables in the query string will become PHP variables in the current
scope. So for example if we invoked the script with `?action=myaction`,
`$action` will be set to `myaction` in php code. We can set any global variable
we want in this way.

The script checks if `$action == 'auth'`, then uses `$user` and `$pass` to
compute a md5 hash and compares the hash against a constant. Since we can set
any global variable, rather than attempting to crack the hash, we can just use
`?action=auth&hashed_password=c019f6e5cd8aa0bbbcc6e994a54c757e`.

`TWCTF{d0_n0t_use_parse_str_without_result_param}`