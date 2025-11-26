# GRUB + Secure Boot Setup Script

This repository provides a Bash script to simplify installing GRUB on UEFI systems with Secure Boot enabled, managing Secure Boot keys with [sbctl](https://github.com/Foxboron/sbctl), and signing EFI binaries.

## Features

* Automatically create and enroll Secure Boot keys (plus the Microsoft keys).
* Install GRUB with embedded modules to the EFI System Partition (ESP).
* Detect and sign all unsigned EFI binaries with sbctl.
* Can run all steps at once, or selected steps individually.

## Requirements

* A UEFI motherboard **with Secure Boot enabled and set to *Setup Mode***.
* Linux system with `grub-install`, `grub-mkconfig`, and `sbctl` available.
* Root privileges (script uses `sudo`).

## Usage

```bash
./setup.sh [--enroll] [--install --esp <ESP_PATH> --id <BOOTLOADER_ID>] [--sign]
```

### Options

* `--enroll`  → Create and enroll Secure Boot keys (if not already enrolled).
* `--install` → Install GRUB with embedded modules and generate configuration.

  * Requires `--esp` (EFI System Partition mountpoint, e.g. `/boot`) and `--id` (bootloader ID, e.g. `GRUB`).
* `--sign`    → Sign all unsigned EFI binaries detected by `sbctl verify`.
* No arguments → Run all steps (asks interactively for ESP path and bootloader ID).

### Example

```bash
# Enroll Secure Boot keys
./setup.sh --enroll

# Install GRUB to /boot with bootloader ID GRUB
./setup.sh --install --esp /boot --id GRUB

# Sign all unsigned EFI binaries
./setup.sh --sign

# Run all steps interactively
./setup.sh
```

## Notes

* The script runs `sbctl create-keys` automatically if keys are not present.
* If keys already exist, `sbctl create-keys` may print a warning, which is harmless.
* After running all steps successfully, you should be able to reboot with Secure Boot enabled.

