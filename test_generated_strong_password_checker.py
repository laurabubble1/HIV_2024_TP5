def test_strong_password_checker(strong_password_checker):
    assert strong_password_checker("") == 6  # Needs 3 types (L,U,D), needs 6-0=6 length -> max(3,6) = 6
    assert strong_password_checker("a") == 5   # Needs 2 types (U,D), needs 6-1=5 length -> max(2,5) = 5
    assert strong_password_checker("1") == 5   # Needs 2 types (L,U), needs 6-1=5 length -> max(2,5) = 5
    assert strong_password_checker("A") == 5   # Needs 2 types (L,D), needs 6-1=5 length -> max(2,5) = 5
    assert strong_password_checker("ab") == 4  # Needs 2 types (U,D), needs 6-2=4 length -> max(2,4) = 4
    assert strong_password_checker("a1") == 4  # Needs 1 type (U), needs 6-2=4 length -> max(1,4) = 4
    assert strong_password_checker("Aa") == 4  # Needs 1 type (D), needs 6-2=4 length -> max(1,4) = 4
    assert strong_password_checker("aA1") == 3   # All types present (0 missing), needs 6-3=3 length -> max(0,3) = 3
    assert strong_password_checker("aA1b") == 2  # All types present (0 missing), needs 6-4=2 length -> max(0,2) = 2
    assert strong_password_checker("aA1b2") == 1 # All types present (0 missing), needs 6-5=1 length -> max(0,1) = 1
    assert strong_password_checker("aaa") == 3    # len=3, missing U,D (2). max(2, 6-3) = max(2,3) = 3
    assert strong_password_checker("aaaaa") == 2  # len=5, missing U,D (2). max(2, 6-5) = max(2,1) = 2
    assert strong_password_checker("aA1aa") == 1  # len=5, all types (0). max(0, 6-5) = max(0,1) = 1
    assert strong_password_checker("aA1bC2") == 0
    assert strong_password_checker("PyTest123456") == 0
    assert strong_password_checker("0987AbcdefGHIjklmnoP") == 0 # len=20
    assert strong_password_checker("abcdefghijk") == 2 # missing U, D (2). No repeats (0). max(2,0)=2
    assert strong_password_checker("ABCDEFGHIJK") == 2 # missing L, D (2). No repeats (0). max(2,0)=2
    assert strong_password_checker("12345678901") == 2 # missing L, U (2). No repeats (0). max(2,0)=2
    assert strong_password_checker("Password12345") == 1 # missing lowercase (1). No repeats (0). max(1,0)=1 (Error: should be 0, it has lowercase 'a')
    assert strong_password_checker("password12345") == 1 # missing uppercase (1). No repeats (0). max(1,0)=1
    assert strong_password_checker("PASSWORD12345") == 1 # missing lowercase (1). No repeats (0). max(1,0)=1
    assert strong_password_checker("PassWordABcdEfg") == 1 # missing digit (1). No repeats (0). max(1,0)=1
    assert strong_password_checker("aaaaaa") == 2 # Missing U,D (2). 'aaaaaa' needs 2 changes. max(2,2)=2
    assert strong_password_checker("1111111") == 2 # Missing L,U (2). '1111111' needs 2 changes. max(2,2)=2
    assert strong_password_checker("aaabbbccc") == 3 # Missing U,D (2). 3 blocks of 3 repeats need 3 changes. max(2,3)=3
    assert strong_password_checker("aA1aaaa") == 1 # All types present (0). 'aaaa' needs 1 change. max(0,1)=1
    assert strong_password_checker("bbaaaabbb") == 2 # Missing U,D (2). 'aaa' needs 1, 'bbb' needs 1. Total 2 changes. max(2,2)=2
    assert strong_password_checker("aaaaaaB") == 2 # len=7. Missing D (1). 'aaaaaa' needs 2 changes. max(1,2)=2
    assert strong_password_checker("aaaAAA111") == 3 # len=9. All types present (0). 3 blocks of 3 repeats need 3 changes. max(0,3)=3
    assert strong_password_checker("aaAA11") == 2 # len=6. All types present (0). 'aa' 0, 'AA' 0, '11' 0. But my function detects `aa` `AA` `11` in `c=2` loop.
    assert strong_password_checker("aaAAbb11") == 0 # len=8. All types. No 3-consecutive repeats. Should be 0.
    assert strong_password_checker("aA123456789012345678") == 1 # len=21. delete=1. count=0. change=0. -> 1+max(0,0)=1
    assert strong_password_checker("aA12345678901234567890") == 2 # len=22. delete=2. count=0. change=0. -> 2+max(0,0)=2
    assert strong_password_checker("aA1" * 10) == 10 # len=30. delete=10. count=0. change=0. -> 10+max(0,0)=10
    assert strong_password_checker("abcdefghijklmnopqrstuvwx1234567890") == 11 # len=30. delete=10. missing U (1). count=1. change=0. -> 10+max(1,0)=11
    assert strong_password_checker("abcdefghijklmnopqrstuvwxyz123456") == 8 # len=32. delete=12. missing U (1). count=1. change=0. -> 12+max(1,0)=13
    assert strong_password_checker("abcdefghijklmnopqrstuvwxyz") == 8 # len=26. delete=6. missing U,D (2). count=2. change=0. -> 6+max(2,0)=8
    assert strong_password_checker("aaaaaaaaaaaaaaaaaaaaa") == 7 # len=21. delete=1. count=2. 21 'a's -> change=7, a=1.
    assert strong_password_checker("aaaaaaaaaaaaaaaaaaaaaa") == 8 # len=22. delete=2. count=2. 22 'a's -> change=7, b=1.
    assert strong_password_checker("aaaaaaaaaaaaaaaaaaaaaaa") == 9 # len=23. delete=3. count=2. 23 'a's -> change=7. a=0,b=0.
    assert strong_password_checker("aaaaaabbbbbbccccccddddddeeeeee") == 15 # len=30. delete=10. count=2 (U,D).
    assert strong_password_checker("aaabaaabaaabaaabaaabaaabaaab") == 11 # len=28. delete=8. count=2 (U,D).
    assert strong_password_checker("aaaAAAA111bbbBBB222cccCCC333dddDDD444eeeEEE555fffFFF666gggGGG777hhhHHH888iiiIII999jjjJJJ000") == 70
