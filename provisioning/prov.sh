#!/bin/bash

ID=1

umount /dev/sda1
umount /dev/sda2
umount /dev/sda3

read -p "Are you sure? Y/N " -n 1 -r REPLY
if [[ $REPLY =~ ^[Yy]$ ]]
then
  # create the partition table
  sfdisk /dev/sda < sfdisk.table

  # copy filesystems
  dd if=sda1.img of=/dev/sda1 bs=4M status=progress
  dd if=sda2.img of=/dev/sda2 bs=4M status=progress

  # make the data filesystem
  mkfs.ext4 -L "data" /dev/sda3

  # create a directory where the data can be logged
  mkdir data
  mount /dev/sda3 data
  mkdir data/bmnode
  chown 1000:1000 data/bmnode

  umount /dev/sda3

  # change the hostname on root  fs
  mount /dev/sda2 root

  sed --in-place "s/bmnode-1/bmnode-${ID}/" root/etc/hostname
  sed --in-place "s/bmnode-1/bmnode-${ID}/" root/etc/hosts

  umount /dev/sda2

  # eject the disk now that we're done
  eject /dev/sda
fi

echo "all done!"
