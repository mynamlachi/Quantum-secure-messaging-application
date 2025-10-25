"""
Quantum Secure Messaging Application (BB84 Simulator)

Single-file Python simulator demonstrating a Quantum Key Distribution (BB84)
protocol and using the resulting shared key to encrypt/decrypt a message via
one-time-pad (XOR). This is a classical simulation (no quantum hardware required)
and is suitable to push to GitHub and run locally.

Features:
- Simulate BB84 between Alice and Bob
- Optional Eve (eavesdropper) intercept-resend attack simulation
- Sifting and sample-based error estimation
- If error rate below threshold, accepts key and uses it to encrypt/decrypt
- Simple CLI usage

Requirements: Python 3.7+

Usage examples:
  python Quantum_Secure_Messaging_App.py --generate-key --length 256
  python Quantum_Secure_Messaging_App.py --send "Hello from Alice" --length 128
  python Quantum_Secure_Messaging_App.py --send "Secret" --length 64 --eve

When pushing to GitHub: add this file, create a short README.md referencing
how to run, and optionally add example outputs.

"""

import argparse
import random
import sys
import textwrap
from typing import List, Tuple


def random_bits(n: int) -> List[int]:
    return [random.randint(0, 1) for _ in range(n)]


def random_bases(n: int) -> List[int]:
    # 0 = computational (|0>,|1>), 1 = Hadamard (+/-)
    return [random.randint(0, 1) for _ in range(n)]


def prepare_qubits(bits: List[int], bases: List[int]) -> List[Tuple[int, int]]:
    # Represent each 'qubit' as tuple (bit, basis)
    return list(zip(bits, bases))


def measure_qubit(prep: Tuple[int, int], measure_basis: int, eve: bool = False) -> int:
    """
    Simulate measurement of a prepared qubit.
    - If measured in same basis => get original bit
    - If different basis => random result (50/50)
    If eve=True and Eve has intercepted and resent, we model that by
    assuming she measures in her chosen basis (random) and resends.
    """
    bit, prep_basis = prep
    if measure_basis == prep_basis:
        return bit
    else:
        return random.randint(0, 1)


def bb84_protocol(length: int = 256, sample_size: int = 32, eve: bool = False, verbose: bool = False):
    """
    Simulate a BB84 run between Alice and Bob. Optionally simulate Eve.
    Returns shared_key (list of bits) and error_rate (float).
    """
    # 1) Alice selects random bits and bases
    alice_bits = random_bits(length)
    alice_bases = random_bases(length)
    alice_qubits = prepare_qubits(alice_bits, alice_bases)

    # 2) Eve optionally intercepts and resends
    if eve:
        # Eve chooses bases randomly and measures
        eve_bases = random_bases(length)
        eve_measurements = [measure_qubit(q, b, eve=True) for q, b in zip(alice_qubits, eve_bases)]
        # Eve resends qubits prepared in her measurement result and her basis
        resent_qubits = prepare_qubits(eve_measurements, eve_bases)
        channel_qubits = resent_qubits
        if verbose:
            print("[EVE] Intercept-resend performed.")
    else:
        channel_qubits = alice_qubits

    # 3) Bob chooses random bases and measures
    bob_bases = random_bases(length)
    bob_measurements = [measure_qubit(q, b) for q, b in zip(channel_qubits, bob_bases)]

    # 4) Sifting: Alice and Bob announce bases and keep bits where bases match
    matching_positions = [i for i in range(length) if alice_bases[i] == bob_bases[i]]
    alice_sifted = [alice_bits[i] for i in matching_positions]
    bob_sifted = [bob_measurements[i] for i in matching_positions]

    # 5) Sampling for error estimation: choose sample_size positions randomly from matching set
    if len(matching_positions) == 0:
        return [], 1.0  # catastrophic failure
    sample_size = min(sample_size, len(matching_positions))
    sample_indices = random.sample(range(len(matching_positions)), sample_size)
    sample_alice = [alice_sifted[i] for i in sample_indices]
    sample_bob = [bob_sifted[i] for i in sample_indices]

    # Calculate error rate on sample
    errors = sum(1 for a, b in zip(sample_alice, sample_bob) if a != b)
    error_rate = errors / sample_size

    # 6) Remove sampled positions from key
    keep_positions = [i for i in range(len(matching_positions)) if i not in sample_indices]
    alice_key = [alice_sifted[i] for i in keep_positions]
    bob_key = [bob_sifted[i] for i in keep_positions]

    if verbose:
        print(f"Alice bits:    {alice_bits[:16]}...")
        print(f"Alice bases:   {alice_bases[:16]}...")
        print(f"Bob bases:     {bob_bases[:16]}...")
        print(f"Matching count: {len(matching_positions)} | Sample size: {sample_size}")
        print(f"Sample errors: {errors} | Error rate: {error_rate:.3f}")
        print(f"Raw key length (after removing sample): {len(alice_key)}")

    threshold = 0.15
    if error_rate > threshold:
        if verbose:
            print("Error rate too high -> possible eavesdropping. Aborting key acceptance.")
        return [], error_rate

    key_len = min(len(alice_key), len(bob_key))
    shared_key = alice_key[:key_len]

    return shared_key, error_rate


def bits_to_bytes(bits: List[int]) -> bytes:
    extra = (-len(bits)) % 8
    bits_padded = bits + [0] * extra
    out = bytearray()
    for i in range(0, len(bits_padded), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits_padded[i + j]
        out.append(byte)
    return bytes(out)


def xor_bytes(msg: bytes, key: bytes) -> bytes:
    if len(key) == 0:
        raise ValueError("Key must be non-empty")
    out = bytearray()
    for i, b in enumerate(msg):
        out.append(b ^ key[i % len(key)])
    return bytes(out)


def key_from_shared_bits(shared_bits: List[int]) -> bytes:
    return bits_to_bytes(shared_bits)


def demo_run(length: int = 256, message: str = "Hello Quantum World!", eve: bool = False, verbose: bool = False):
    shared_key_bits, error_rate = bb84_protocol(length=length, sample_size=min(32, length//4), eve=eve, verbose=verbose)

    if len(shared_key_bits) == 0:
        print("Failed to establish a secure key (empty key). Error rate:", error_rate)
        return

    key_bytes = key_from_shared_bits(shared_key_bits)
    msg_bytes = message.encode('utf-8')

    cipher = xor_bytes(msg_bytes, key_bytes)
    decrypted = xor_bytes(cipher, key_bytes)

    print("--- Quantum Secure Messaging Demo ---")
    print(f"Requested key length (bits): {length}")
    print(f"Estimated error rate from sample: {error_rate:.4f}")
    print(f"Shared key (hex, first 64 chars): {key_bytes.hex()[:64]}{'...' if len(key_bytes.hex())>64 else ''}")
    print(f"Original message: {message}")
    print(f"Cipher (hex): {cipher.hex()}")
    print(f"Decrypted message: {decrypted.decode('utf-8', errors='replace')}")


def parse_args():
    p = argparse.ArgumentParser(description="BB84 Quantum Secure Messaging Simulator")
    p.add_argument('--generate-key', action='store_true', help='Generate shared key and show key info')
    p.add_argument('--send', type=str, help='Send (encrypt) a message using QKD-generated key')
    p.add_argument('--length', type=int, default=256, help='Number of qubits/bits in BB84 run (default 256)')
    p.add_argument('--eve', action='store_true', help='Simulate eavesdropper (intercept-resend)')
    p.add_argument('--verbose', action='store_true', help='Verbose output')
    return p.parse_args()


def main():
    args = parse_args()
    if args.generate_key:
        key, err = bb84_protocol(length=args.length, sample_size=min(32, args.length//4), eve=args.eve, verbose=args.verbose)
        if key:
            print(f"Key established! Length (bits): {len(key)} | Error rate: {err:.4f}")
            print(f"Key (hex): {key_from_shared_bits(key).hex()}")
        else:
            print(f"No key established. Error rate: {err:.4f}")
        return

    if args.send is not None:
        demo_run(length=args.length, message=args.send, eve=args.eve, verbose=args.verbose)
        return

    print(textwrap.dedent("""
    Quantum Secure Messaging Application - BB84 Simulator

    No arguments provided. Example usages:
      python Quantum_Secure_Messaging_App.py --generate-key --length 256
      python Quantum_Secure_Messaging_App.py --send "Secret message" --length 128
      python Quantum_Secure_Messaging_App.py --send "Test" --length 128 --eve --verbose
    """))


if __name__ == '__main__':
    main()
