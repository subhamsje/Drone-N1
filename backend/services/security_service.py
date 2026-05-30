"""
Cryptographic Security Layer
Enforces zero-trust command execution via ECDSA signatures and payload validation.
"""

import logging
import hashlib
import time
import json
from typing import Dict, Any

try:
    import ecdsa
    from ecdsa import VerifyingKey, SigningKey, NIST256p
    ECDSA_AVAILABLE = True
except ImportError:
    ECDSA_AVAILABLE = False

logger = logging.getLogger("security_guardian")

class SecurityService:
    def __init__(self, uav_id: str):
        self.uav_id = uav_id
        # Load keys from a KMS/Vault. If missing, fail secure.
        self._authorized_public_keys = {} 
        self._signing_key = None
        
        if ECDSA_AVAILABLE:
            # Generate an ephemeral key for this session (simulating Vault loaded key)
            self._signing_key = SigningKey.generate(curve=NIST256p)
            vk = self._signing_key.get_verifying_key()
            self._authorized_public_keys["operator-1"] = vk
            logger.info(f"[{self.uav_id}] Security Guardian initialized. ECDSA Enforced.")
        else:
            logger.warning(f"[{self.uav_id}] Python 'ecdsa' package missing. Zero-trust enforcement degraded.")

    def verify_command_signature(self, command: str, payload: Dict[str, Any], signature: str, timestamp: float) -> bool:
        """
        Validates ECDSA signatures for all MAVLink and autonomous commands.
        Enforces replay protection using timestamp windows.
        """
        now = time.time()
        
        # 1. Replay Protection (Command must be within 5 seconds)
        if abs(now - timestamp) > 5.0:
            logger.error(f"[{self.uav_id}] SECURITY VIOLATION: Command replay attack detected. Timestamp stale.")
            return False

        if not ECDSA_AVAILABLE:
            logger.error(f"[{self.uav_id}] SECURITY FAULT: Cannot verify ECDSA without cryptography package.")
            return False

        # 2. Cryptographic Validation
        payload_bytes = json.dumps(payload, sort_keys=True).encode()
        message = f"{command}:{timestamp}:".encode() + payload_bytes
        message_hash = hashlib.sha256(message).digest()

        for key_id, vk in self._authorized_public_keys.items():
            try:
                if vk.verify(bytes.fromhex(signature), message_hash, hashfunc=hashlib.sha256):
                    return True
            except ecdsa.BadSignatureError:
                continue
            except Exception as e:
                logger.error(f"Signature validation error: {e}")
                
        logger.error(f"[{self.uav_id}] SECURITY VIOLATION: Invalid cryptographic signature for command {command}.")
        return False
        
    def sign_mission_payload(self, mission_plan: Dict[str, Any]) -> str:
        """Signs outgoing mission plans before transmission over RF/MAVLink."""
        if not ECDSA_AVAILABLE or not self._signing_key:
            raise RuntimeError("Cannot sign mission payload: ECDSA unavailable or key not loaded.")
            
        payload_bytes = json.dumps(mission_plan, sort_keys=True).encode()
        message_hash = hashlib.sha256(payload_bytes).digest()
        signature = self._signing_key.sign(message_hash, hashfunc=hashlib.sha256)
        return signature.hex()
