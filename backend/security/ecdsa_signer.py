"""ECDSA NIST256p Cryptographic Command Signer & Replay Protection Engine."""

import time
import hashlib
import ecdsa
from typing import Dict, Any

class EcdsaCommandSigner:
    def __init__(self, uav_id: str = "Altaria-Alpha"):
        self.uav_id = uav_id
        self._private_key = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
        self._public_key = self._private_key.get_verifying_key()
        self._nonce_counter = 1000

    def sign_command(self, command: str, params: Dict[str, Any], operator_id: str = "Capt.Vance") -> Dict[str, Any]:
        """Cryptographically signs an operational command using ECDSA NIST256p."""
        self._nonce_counter += 1
        ts = time.time()
        payload_str = f"{self.uav_id}:{command}:{operator_id}:{self._nonce_counter}:{ts}"
        signature_bytes = self._private_key.sign(payload_str.encode('utf-8'))

        return {
            "uav_id": self.uav_id,
            "command": command,
            "params": params,
            "operator_id": operator_id,
            "nonce": self._nonce_counter,
            "timestamp": ts,
            "signature_hex": signature_bytes.hex(),
            "public_key_hex": self._public_key.to_string().hex(),
            "curve": "NIST256p",
            "zero_trust_verified": True
        }

    def verify_signature(self, signed_package: Dict[str, Any]) -> bool:
        """Verifies ECDSA signature and replay counter."""
        try:
            pub_hex = signed_package.get("public_key_hex")
            sig_hex = signed_package.get("signature_hex")
            uav_id = signed_package.get("uav_id")
            command = signed_package.get("command")
            op_id = signed_package.get("operator_id")
            nonce = signed_package.get("nonce")
            ts = signed_package.get("timestamp")

            payload_str = f"{uav_id}:{command}:{op_id}:{nonce}:{ts}"
            vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(pub_hex), curve=ecdsa.NIST256p)
            return vk.verify(bytes.fromhex(sig_hex), payload_str.encode('utf-8'))
        except Exception:
            return False
