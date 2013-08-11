# Initial Planning

 1. First create an installer for Nginx (it uses make only as far as I can
    tell).
     a) The source code should be hashed and compared to a hash stored in the
        installer.
     b) The installer should note all versions it is capable of installing.
     c) This type of thing should be handled by some core logic exposed by the
        installer core code.
