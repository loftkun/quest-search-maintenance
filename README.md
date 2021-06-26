quest-search-maintenance
==================================================

# What it is?
maintenance tools for quest-search

## Usage

### remove old Kif files ( on Sakura VPN )

```sh
$ cd /dev/clean/quest-search-maintenance
$ python3 clean.py /home/loftkun/dev/nginx/html/quest/ > test.log &
$ tail -f test.log | grep -w moved
```

## Memo

### deal with disk space increase (on Ubuntu on ec2)

```sh
# check
$ cd /
$ sudo du -m | sort -rn | head -100 > dir-size-sort.txt
$ less dir-size-sort.txt

# remove docker related files
$ sudo docker system df
$ sudo docker system prune -a
$ sudo docker volume ls
$ sudo docker volume rm XXXXXXXXXX

# remove unused kernel images and headers
$ uname -a
$ sudo apt-get autoremove --purge linux-aws-headers-XXXXXXXXXX
```

example :

```log
# before
ubuntu@ip-172-31-30-183:/$ df -h
Filesystem      Size  Used Avail Use% Mounted on
udev            488M     0  488M   0% /dev
tmpfs           100M   12M   88M  12% /run
/dev/xvda1      7.7G  6.4G  1.4G  83% /
tmpfs           496M     0  496M   0% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
tmpfs           496M     0  496M   0% /sys/fs/cgroup
tmpfs           100M     0  100M   0% /run/user/1000
ubuntu@ip-172-31-30-183:/$ 

ubuntu@ip-172-31-30-183:/$ uname -a
Linux ip-172-31-30-183 4.4.0-1119-aws #133-Ubuntu SMP Tue Dec 1 19:04:22 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
ubuntu@ip-172-31-30-183:/$ sudo apt-get autoremove --purge linux-aws-headers-4.4.0-1121
Reading package lists... Done
Building dependency tree
Reading state information... Done
The following packages will be REMOVED:
  linux-aws-headers-4.4.0-1111* linux-aws-headers-4.4.0-1112* linux-aws-headers-4.4.0-1113* linux-aws-headers-4.4.0-1114* linux-aws-headers-4.4.0-1117* linux-aws-headers-4.4.0-1118* linux-aws-headers-4.4.0-1121*
  linux-aws-headers-4.4.0-1122* linux-aws-headers-4.4.0-1123* linux-aws-headers-4.4.0-1124* linux-aws-headers-4.4.0-1126* linux-headers-4.4.0-1111-aws* linux-headers-4.4.0-1112-aws* linux-headers-4.4.0-1113-aws*
  linux-headers-4.4.0-1114-aws* linux-headers-4.4.0-1117-aws* linux-headers-4.4.0-1118-aws* linux-headers-4.4.0-1121-aws* linux-headers-4.4.0-1122-aws* linux-headers-4.4.0-1123-aws* linux-headers-4.4.0-1124-aws*
  linux-headers-4.4.0-1126-aws* linux-image-4.4.0-1111-aws* linux-image-4.4.0-1112-aws* linux-image-4.4.0-1113-aws* linux-image-4.4.0-1114-aws* linux-image-4.4.0-1117-aws* linux-image-4.4.0-1118-aws*
  linux-image-4.4.0-1121-aws* linux-image-4.4.0-1122-aws* linux-image-4.4.0-1123-aws* linux-image-4.4.0-1124-aws* linux-image-4.4.0-1126-aws* linux-modules-4.4.0-1111-aws* linux-modules-4.4.0-1112-aws*
  linux-modules-4.4.0-1113-aws* linux-modules-4.4.0-1114-aws* linux-modules-4.4.0-1117-aws* linux-modules-4.4.0-1118-aws* linux-modules-4.4.0-1121-aws* linux-modules-4.4.0-1122-aws* linux-modules-4.4.0-1123-aws*
  linux-modules-4.4.0-1124-aws* linux-modules-4.4.0-1126-aws*
0 upgraded, 0 newly installed, 44 to remove and 126 not upgraded.
After this operation, 1,485 MB disk space will be freed.
Do you want to continue? [Y/n] y


# after
ubuntu@ip-172-31-30-183:/$ df -h
Filesystem      Size  Used Avail Use% Mounted on
udev            488M     0  488M   0% /dev
tmpfs           100M   12M   88M  12% /run
/dev/xvda1      7.7G  4.4G  3.4G  57% /
tmpfs           496M     0  496M   0% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
tmpfs           496M     0  496M   0% /sys/fs/cgroup
tmpfs           100M     0  100M   0% /run/user/1000
ubuntu@ip-172-31-30-183:/$
```
