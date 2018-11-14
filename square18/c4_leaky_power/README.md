Square CTF 2018: C4 - leaky power
=================================

## Description

C4 is a very advanced AES based defensive system. You are able to monitor the
power lines. Is that enough?

You’re given three files:

* powertraces.npy: Measurements (over time) of power consumption of a chip while
performing AES encryption

* plaintexts.npy: Corresponding plaintext inputs that were encrypted

* instructions.jwe: File encrypted using the same key as plaintexts.npy.

note: The first two files are NumPy arrays.

note: there's a mistake in the way instructions.jwe was created (the algorithm
is A128GCM, not A256GCM).

## Solution

`instructions_corrected.jwe` is a JSON file containing an encrypted message,
along with an IV, an authentication tag and a `protected` field, all
base64-encoded. The `protected` field decodes to `{"alg":"dir","enc":"A128GCM"}`
which suggests that the message is encrypted with AES-128 in GCM mode. When the
challenge was released, the files only contained `instructions.jwe` whose
`protected` field instead decodes to `{"alg":"dir","enc":"A256GCM"}`,
incorrectly suggesting that a 256-bit key was being used instead.

In order to solve this task we must perform a correlation power analysis (CPA)
attack, which can recover an AES key from the plaintexts and power traces. The
attack is explained [here](https://wiki.newae.com/Tutorial_B6_Breaking_AES_(Manual_CPA_Attack))
and the authors provide some example code which we adapted to solve this task.

`flag-e2f27bac480a7857de45`
