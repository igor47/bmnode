#!/bin/bash

umount /dev/sda1
umount /dev/sda2
umount /dev/sda3

# grab the partitions
read -p "Are you sure? Y/N " -n 1 -r REPLY
if [[ $REPLY =~ ^[Yy]$ ]]
then
  # grab partition table
  sfdisk -d /dev/sda > sfdisk.table

  # grab the partitions
  dd of=sda1.img if=/dev/sda1 bs=4M status=progress
  dd of=sda2.img if=/dev/sda2 bs=4M status=progress
fi

echo "all done!"
