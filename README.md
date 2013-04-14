Pan Scanner
===========
Looking for card numbers in your directory tree which shouldn't be there? PanScanner is the tool for you!

It will look through the directories you point out and find the file, line and character number where the card number is hidden.

Name
----
"Peter Pan what scan?" you probably think.

Here is how it goes: PAN = primary account number = card number.

Usage
-----
It is as simple as knowing the directories you would like to scan (!):

```
$ python pan_scan.py -d /dir1 /dir2 /dir3 ...
Found card number in /dir1/somewhere/deep/down/in/a/forgotten/recess.log:
* Card number found at line 16 in interval: (1, 17)
* Card number found at line 23 in interval: (22, 38) (59, 75)
Found card number in /dir3/another/hidding/place.py:
* Card number found at line 1 in interval: (22, 38)
```
