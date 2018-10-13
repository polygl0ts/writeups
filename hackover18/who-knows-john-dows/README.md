Hackover CTF 2018: who knows john dows?
=======================================

## Description

Howdy mate! Just login and hand out the flag, aye! You can find on [h18johndoe](
https://github.com/h18johndoe/user_repository/blob/master/user_repo.rb) has all
you need!

http://yo-know-john-dow.ctf.hackover.de:4567/login

alternative: http://46.101.157.142:4567/login

## Solution

[The first link](https://github.com/h18johndoe/user_repository/blob/master/user_repo.rb)
points to a Ruby script in a GitHub repository that seems to handle logins
for the challenge website. The script is vulnerable to SQL injection.

```rb
def login(identification, password)
    hashed_input_password = hash(password)
    query = "select id, phone, email from users where email = '#{identification}' and password_digest = '#{hashed_input_password}' limit 1"
    puts "SQL executing: '#{query}'"
    @database[query].first if user_exists?(identification)
end

def hash(password)
    password.reverse
end
```

However the challenge website first asks us to provide a valid username or e-mail
and SQL injection doesn't work here. It seems that we need to find a valid
username or email somewhere.

Since the script is stored in a git repository we decided to have a look at the
commit history.

```
$ git shortlog -sne
     1  John Doe <angelo_muh@yahoo.org>
     1  John Doe <jamez@hemail.com>
     1  John Doe <john_doe@gmail.com>
     1  John Doe <john_doe@notes.h18>
```

`john_doe@notes.h18` is a valid e-mail for the challenge site. After entering
that we're directed to a password field which is vulnerable to SQLi.

By using `1' = '1' RO '` as our password (reversed because `hash()` reverses the
password) we can get the flag.

Flag: `hackover18{I_KN0W_H4W_70_STALK_2018}`
