# ⚠️ WORK IN PROGRESS ⚠️

# ab-flasher

Simple tool to implement an A/B partition image update strategy for a Raspberry Pi.

## What it does

ab-flasher updates a device in place, using what is sometimes known as a double copy, dual copy, or A/B strategy. This is where the device has two OS partitions but only one is active. Updates are done by flashing the inactive partition, then the bootloader is updated to switch to the new version.

When you run ab-flasher:, it:
1. Reads `.ab_version`.
2. Checks if active (booted) partition's version is less than desired (else stop).
3. Downloads the new image, extracting/writing it to the inactive partition.
4. Checksums the inactive partition to confirm successful write.
5. Configures the bootloader to use the new (currently inactive) partition.

## Usage

usage: ab-flasher [-h] [--dry-run] [--no-reboot] [--hash-url HASH_URL]
                  [--hash-type HASH_TYPE] [--verbose]
                  [--version-file VERSION_FILE] [--force] [--host HOST]
                  new_version boot_files_url boot_partition os_image_url
                  os_partitions

positional arguments:
  new_version           New version number (e.g. 1.2.3).
  boot_files_url        URL to gzipped boot files.
  boot_partition        Partition containing boot files (e.g. sda1)
  os_image_url          URL to new gzipped image.
  os_partitions         Which two partitions to consider (e.g. sda2,sda3)

optional arguments:
  -h, --help            show this help message and exit
  --dry-run             Take no actions.
  --no-reboot           Don't reboot after an update.
  --hash-url HASH_URL   URL to a file containing a hash, used to verify the
                        write.
  --hash-type HASH_TYPE
                        Type of hash contained in the hash file
  --verbose, -v         Verbosity of logging. Specify multiple times for more.
  --version-file VERSION_FILE
                        File to check for volume version (at host)
  --force               Assume upgrade is required
  --host HOST           Path to host's active partition (usually only needed
                        for Docker)

### Dependencies

Install using `poetry install`.

### Example

Check if update to 1.2.3 is required.
Flash it to the inactive partition (either sda2 or sda3) then update the bootloader at sda1.
```
ab-flasher \
    --hash-url https://example.com/os.img.sha256 \
    1.2.3 \
    https://example.com/boot.tar.gz \
    sda1 \
    https://example.com/os.img.gz \
    sda2,sda3
```

Using docker:
```
docker run --privileged -v /:/host jonoh/ab-flasher \
    --host /host \
    --hash-url https://example.com/os.img.sha256 \
    1.2.3 \
    https://example.com/boot.tar.gz \
    sda1 \
    https://example.com/os.img.gz \
    sda2,sda3
```

## Why it exists

Traditionally you might keep a Pi updated by either running in place upgrades (`apt-get update` etc) or reflashing the SD card. These are slow and risky - package mangers usually do a good job but can take a long time and a failure could leave a headless system in a broken state. For these reasons, it's unusual that people have the confidence to run these updates automatically. Reflashing SD cards is labour intensive, for obvious reasons.

The double copy strategy implemented by ab-flasher lets updates be fast and reliable, at the expense of more storage space. 
Updates are fast with minimal downtime because the system can run as normal, then a quick reboot activates the new version.
It's reliable because the new version will be in an exact and known state, without the risk of a failed update causing breakage.
All of this means you can confidently set the process to happen automatically.

I built this to keep a small cluster of Raspberry Pis up to date. I found existing tools too complicated for my needs.

## What it doesn't do

ab-flasher is deliberately simple and makes a lot of assumptions.
Some known limitations:
- Doesn't poll anywhere for updates, you need to tell it the new version when it runs.
- Doesn't integrate with the bootloader for failover. The bootloader won't know to failover if a partition is bad.
- Simplistic in its partiion inspection, so stick to simple partitioning schemes.
- Only supports gz images (gz tends to use the least cpu/memory anyway).
