# ⚠️ WORK IN PROGRESS ⚠️

# ab-flasher

Simple tool to implement an A/B partition image update strategy for a Raspberry Pi.

## What it does

ab-flasher updates a Raspberry Pi in place, using what is sometimes known as a double copy, dual copy, or A/B strategy. This is where the device has two OS partitions but only one is active. Updates are done by flashing the inactive partition, then the bootloader is updated to switch to the new version.

When you run ab-flasher:, it:
1. Checks if active (booted) partition's version is less than desired (else stop).
2. Downloads the new image, extracting/writing it to the inactive partition.
3. Checksums the inactive partition to confirm successful write.
4. Configures the bootloader to use the new (currently inactive) partition.
5. Reboots

## How to use it

Your Raspberry Pi should contain the standard boot partition, and two ext4 partitions for the OS.

### Bootstrap

If you need a bootstrap image to get started, you can flash with an image containing ab-flasher from the [Releases](https://github.com/hillnz/ab-flasher/releases/latest).
This image contains the boot partition, two OS partitions, and a data partition. You can flash it with the usual tools (dd, Raspberry Pi Imager, etc).

After flashing, create `ab-flasher.env` in the data partition. This file may contain any of the arguments'/options' environment variable equivalents (see [Usage](#usage)). For example, at a minimum:
```
AB_OS_IMAGE_URL=https://github.com/hillnz/rpi-image-base/releases/latest/download/os.img.gz
AB_FORCE=true
```

On boot, the partitions will be expanded and ab-flasher will run.

### Updates

How you run ab-flasher in your own image is up to you. Beyond the bootstrap image it doesn't take responsibility for how it runs or how you update its configuration.
Any solution which lets you push configuration and run a command will be suitable.

### Dependencies

Install using `poetry install`, or use the [Docker image](https://hub.docker.com/r/jonoh/ab-flasher).

### Usage

```
Usage: ab-flasher [OPTIONS] OS_IMAGE_URL [NEW_VERSION]

Arguments:
  OS_IMAGE_URL   URL to new gzipped image.  [env var:
                 AB_OS_IMAGE_URL;required]

  [NEW_VERSION]  New version number (e.g. 1.2.3).  [env var: AB_NEW_VERSION]

Options:
  --boot-files-url TEXT           URL to gzipped boot files (or skip boot
                                  files update if not set).  [env var:
                                  AB_BOOT_FILES_URL]

  --hash-url TEXT                 URL to a file containing a hash, used to
                                  verify the write.  [env var: AB_HASH_URL;
                                  default: <OS_IMAGE_URL>.<hash-type>]

  --hash-type TEXT                Type of hash contained in the hash file
                                  [env var: AB_HASH_TYPE; default: sha256]

  --host TEXT                     Path to host's active root (usually only
                                  needed for Docker)  [env var: AB_HOST;
                                  default: /]

  --version-file TEXT             File to check for existing version (at host)
                                  [env var: AB_VERSION_FILE; default:
                                  /.ab_version]

  --reboot / --no-reboot          Reboot after an update.  [env var:
                                  AB_REBOOT; default: True]

  --boot-partition TEXT           Partition number containing boot files  [env
                                  var: AB_BOOT_PARTITION; default: 1]

  --os-partitions <INTEGER INTEGER>...
                                  Which two OS partition numbers to consider
                                  for flashing  [env var: AB_OS_PARTITIONS;
                                  default: 2, 3]

  --force / --no-force            Assume upgrade is required.  [env var:
                                  AB_FORCE; default: False]

  --dry-run / --no-dry-run        Take no actions.  [env var: AB_DRY_RUN;
                                  default: False]

  -v                              Verbosity of logging. Specify multiple times
                                  for more.  [env var: AB_VERBOSE; default: 0]

  --help                          Show this message and exit.

```

### Examples

```
ab-flasher \
    --boot-files-url https://example.com/boot.tar.gz \
    https://example.com/os.img.gz
    1.2.3
```

Using docker:
```
docker run --privileged -v /:/host jonoh/ab-flasher \
    --boot-files-url https://example.com/boot.tar.gz \
    https://example.com/os.img.gz
    1.2.3
```
(The entrypoint passes `--host /host` so that the container can see the host filesystem.)

## Why it exists

Traditionally you might keep a Pi updated by either running in place upgrades (`apt-get update` etc) or reflashing the SD card. These options are slow, and risky or difficult to automate.

The double copy strategy implemented by ab-flasher lets updates be fast and reliable, at the expense of more storage space. The system will be down only for the duration of a reboot and will then boot to a known state.

I built this to keep a small cluster of Raspberry Pis up to date. I found existing tools too complicated for my needs.

## Caveats

ab-flasher is deliberately simple and makes a lot of assumptions.

Some known limitations:
- Assumes some basic file system tools are available (fdisk, lsblk, findmnt). Tested only on Raspberry Pi OS.
- Doesn't integrate with the bootloader for failover. The bootloader won't know to failover if a partition is bad.
- Only supports gz images (gz tends to use the least cpu/memory anyway).
