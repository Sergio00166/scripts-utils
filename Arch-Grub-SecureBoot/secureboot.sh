#!/bin/bash
# Code by Sergio00166
set -e

ESP_MOUNTPOINT=""
BOOTLOADER_ID=""
TARGET="x86_64-efi"
GRUB_MODULES="normal search echo linux all_video gfxmenu gfxterm_background gfxterm loadenv configfile tpm fat ext2"

usage() {
  echo "Usage: $0 [--enroll] [--install --esp <ESP_PATH> --id <BOOTLOADER_ID>] [--sign]"
  echo
  echo "Options:"
  echo "  --enroll               Enroll Secure Boot keys (if not already enrolled)"
  echo "  --install              Install GRUB with embedded modules and generate config"
  echo "                         Requires --esp and --id"
  echo "  --sign                 Sign all unsigned EFI binaries detected by sbctl verify"
  echo "  --esp <ESP_PATH>       Mountpoint of EFI System Partition (required for --install)"
  echo "  --id <BOOTLOADER_ID>   Bootloader ID (folder name in EFI partition, required for --install)"
  echo
  echo "If no options are given, all steps run and --esp and --id are mandatory."
  exit 1
}

enroll_keys() {
  echo "==> Checking Secure Boot keys enrollment..."
  if ! sbctl list-keys | grep -q "Platform Key (PK)"; then
    echo "Keys not enrolled. Creating and enrolling now..."
    sudo sbctl create-keys
    if ! sudo sbctl enroll-keys --microsoft; then
      echo "Error: Failed to enroll Secure Boot keys. Aborting."
      exit 1
    fi
    echo "Keys created and enrolled successfully."
  else
    echo "Keys already enrolled."
  fi
}

install_grub() {
  if [[ -z "$ESP_MOUNTPOINT" || -z "$BOOTLOADER_ID" ]]; then
    echo "Error: --esp and --id must be specified for --install"
    usage
  fi

  echo "==> Installing GRUB with embedded modules..."
  sudo grub-install \
    --target=$TARGET \
    --efi-directory="$ESP_MOUNTPOINT" \
    --bootloader-id="$BOOTLOADER_ID" \
    --modules="$GRUB_MODULES" \
    --disable-shim-lock --removable

  echo "==> Generating GRUB config..."
  sudo grub-mkconfig -o /boot/grub/grub.cfg
}

sign_binaries() {
  echo "==> Finding unsigned EFI binaries to sign..."
  mapfile -t unsigned_files < <(sudo sbctl verify 2>&1 | grep "is not" | awk -F" " '{print $2}' | sort -u)

  if [ ${#unsigned_files[@]} -eq 0 ]; then
    echo "All EFI binaries are already signed."
  else
    echo "Found ${#unsigned_files[@]} unsigned binaries. Signing..."
    for f in "${unsigned_files[@]}"; do
      echo "Signing $f"
      sudo sbctl sign "$f"
    done
    echo "Signing complete."
  fi
}


# Parse args
if [ $# -eq 0 ]; then
  echo "No arguments given, running all steps."
  read -p "Enter EFI System Partition mountpoint (e.g. /boot): " ESP_MOUNTPOINT
  read -p "Enter Bootloader ID (e.g. GRUB): " BOOTLOADER_ID
  enroll_keys
  install_grub
  sign_binaries
  echo "==> All done! Reboot with Secure Boot enabled."
  exit 0
fi

DO_ENROLL=0
DO_INSTALL=0
DO_SIGN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --enroll)
      DO_ENROLL=1
      shift
      ;;
    --install)
      DO_INSTALL=1
      shift
      ;;
    --sign)
      DO_SIGN=1
      shift
      ;;
    --esp)
      ESP_MOUNTPOINT="$2"
      shift 2
      ;;
    --id)
      BOOTLOADER_ID="$2"
      shift 2
      ;;
    *)
      usage
      ;;
  esac
done

if [[ $DO_INSTALL -eq 1 ]]; then
  if [[ -z "$ESP_MOUNTPOINT" || -z "$BOOTLOADER_ID" ]]; then
    echo "Error: --install requires --esp and --id to be specified."
    usage
  fi
fi

if [[ $DO_ENROLL -eq 1 ]]; then
  enroll_keys
fi
if [[ $DO_INSTALL -eq 1 ]]; then
  install_grub
fi
if [[ $DO_SIGN -eq 1 ]]; then
  sign_binaries
fi

echo "==> Requested steps completed."

 
