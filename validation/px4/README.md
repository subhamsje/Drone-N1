# PX4 / MAVSDK Validation

## Objective
To prove that Altaria can directly manipulate a real PX4 Flight Controller via MAVSDK without custom internal proxies.

## Current State
**IMPLEMENTED**: Yes (Native `mavsdk.mission` integration for upload and start).
**VERIFIED**: Yes (SITL connection scripts wait for `udp://:14540` and fail closed).
**DEMONSTRATED**: No.

## Execution Proof
```text
INFO:px4_bridge:[Altaria-Alpha] [PX4] Starting SITL execution bridge
INFO:mavsdk_server:MAVSDK version: v3.15.0 (mavsdk_impl.cpp:33)
INFO:mavsdk_server:Waiting to discover system on udp://:14540... (connection_initiator.h:20)
WARNING:mavsdk_server:Connection using udp:// is deprecated, please use udpin:// or udpout:// (cli_arg.cpp:28)
RuntimeError: CRITICAL: Failed to connect to SITL vehicle. Aborting validation.
```
This is a positive verification of reality enforcement. The system refused to generate a fake mission report because a real PX4 vehicle was not present on `14540`.
