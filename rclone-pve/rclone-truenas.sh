#!/bin/bash

# Create snapshot of pyspy dir
mkdir /mnt/pve/cephfs/pyspy/.snap/backup1

# sync snapshot over to truenas
rclone sync -P --transfers=15 /mnt/pve/cephfs/pyspy/.snap/backup1/ /mnt/truenas/pyspy

# Remove snapshot
rmdir /mnt/pve/cephfs/pyspy/.snap/backup1


# Create snapshot of nextcloud dir
mkdir /mnt/pve/cephfs/nextcloud-data/.snap/backup1

# sync snapshot over to truenas
rclone sync -P --transfers=15 /mnt/pve/cephfs/nextcloud-data/.snap/backup1/ /mnt/truenas/nextcloud

# Remove snapshot
rmdir /mnt/pve/cephfs/nextcloud-data/.snap/backup1
