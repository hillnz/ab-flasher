# ab-flasher

Simple tool to implement an A/B partition image update strategy for a device.
Currently supports Raspberry Pi.

## What it does

ab-flasher updates a device in place, using what is sometimes known as a double copy, dual copy, or A/B strategy. This is where the device has two OS partitions but only one is active. Updates are done by flashing the inactive partition, then the bootloader is updated to switch to the new version.

When you run ab-flasher:, it:
1. Reads `.ab_version`.
2. Checks if active (booted) partition's version is less than desired (else stop).
3. Downloads the new image, extracting/writing it to the inactive partition.
4. Checksums the inactive partition to confirm successful write.
5. Configures the bootloader to use the new (currently inactive) partition.

## Usage

### Dependencies

Install using `poetry install` or `pip install -f requirements.txt`.

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
