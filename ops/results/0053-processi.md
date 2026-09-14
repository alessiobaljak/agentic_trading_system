# 0053-processi.req

_eseguito: 2026-09-14 07:51 UTC_

**richiesta:** `processi`
**eseguito:** `ps -eo pid,pcpu,pmem,etime,args --sort=-pcpu`
**esito:** codice 0 in 0.0s

```
    PID %CPU %MEM     ELAPSED COMMAND
1237756  100  0.0       00:00 ps -eo pid,pcpu,pmem,etime,args --sort=-pcpu
1235469 99.6  4.4    01:25:15 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1235595 99.6  4.3    01:25:15 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1235574 99.6  4.1    01:25:15 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1235532 99.5  3.6    01:25:15 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1235490 99.5  4.7    01:25:15 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1235616 99.5  6.1    01:25:15 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1235553 99.3  5.9    01:25:15 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1235511 99.3  4.8    01:25:15 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1237743  8.1  0.0       00:00 /root/agentic_trading_system/.venv/bin/python -m scripts.ops_agent
1190071  1.6  0.7    23:14:23 /root/agentic_trading_system/.venv/bin/python -m bot.main
1235443  0.1  0.9    01:25:18 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1186867  0.0  0.0  1-01:22:54 /usr/sbin/qemu-ga
1186897  0.0  0.4  1-01:22:54 /usr/lib/systemd/systemd-journald
      1  0.0  0.0 32-02:58:45 /usr/lib/systemd/systemd --system --deserialize=78
1228668  0.0  0.0    06:01:49 [kworker/2:3-events]
     17  0.0  0.0 32-02:58:45 [rcu_preempt]
     71  0.0  0.0 32-02:58:45 [kcompactd0]
1233743  0.0  0.0    02:16:53 [kworker/0:2-events]
1236683  0.0  0.0       47:45 [kworker/u16:4-events_power_efficient]
     91  0.0  0.0 32-02:58:44 [kswapd0]
1236908  0.0  0.0       37:13 [kworker/5:2-events]
1186885  0.0  0.0  1-01:22:54 sshd: /usr/sbin/sshd -D [listener] 3 of 10-100 startups
1237673  0.0  0.0       01:14 sshd: [accepted]
1237218  0.0  0.0       22:07 [kworker/3:0-events]
1186864  0.0  0.1  1-01:22:54 /sbin/multipathd -d -s
1186899  0.0  0.0  1-01:22:54 /usr/lib/systemd/systemd-resolved
1186905  0.0  0.0  1-01:22:54 /usr/sbin/rsyslogd -n -iNONE
1236886  0.0  0.0       38:09 [kworker/u16:1-events_power_efficient]
1237497  0.0  0.0       08:20 [kworker/u16:3-ext4-rsv-conversion]
1237301  0.0  0.0       17:48 [kworker/u16:2-flush-8:0]
     73  0.0  0.0 32-02:58:45 [khugepaged]
1232384  0.0  0.0    03:10:06 [kworker/1:3-events]
1229683  0.0  0.0    05:11:34 [kworker/6:2-cgroup_free]
1236328  0.0  0.0    01:00:03 [kworker/u16:0-events_power_efficient]
1235121  0.0  0.0    01:37:33 [kworker/7:0-events]
    914  0.0  0.0 32-02:58:24 @dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation --syslog-only
1235975  0.0  0.0    01:15:25 [kworker/4:3-events]
    324  0.0  0.0 32-02:58:40 [jbd2/sda1-8]
1186860  0.0  0.0  1-01:22:54 /usr/lib/polkit-1/polkitd --no-debug
    926  0.0  0.0 32-02:58:24 /usr/lib/systemd/systemd-logind
    200  0.0  0.0 32-02:58:43 [kworker/2:1H-kblockd]
1186900  0.0  0.0  1-01:22:54 /usr/lib/systemd/systemd-timesyncd
     18  0.0  0.0 32-02:58:45 [migration/0]
     23  0.0  0.0 32-02:58:45 [migration/1]
     29  0.0  0.0 32-02:58:45 [migration/2]
     35  0.0  0.0 32-02:58:45 [migration/3]
     47  0.0  0.0 32-02:58:45 [migration/5]
     41  0.0  0.0 32-02:58:45 [migration/4]
     59  0.0  0.0 32-02:58:45 [migration/7]
     53  0.0  0.0 32-02:58:45 [migration/6]
    177  0.0  0.0 32-02:58:43 [kworker/3:1H-kblockd]
     36  0.0  0.0 32-02:58:45 [ksoftirqd/3]
    165  0.0  0.0 32-02:58:43 [kworker/5:1H-kblockd]
    197  0.0  0.0 32-02:58:43 [kworker/4:1H-kblockd]
     30  0.0  0.0 32-02:58:45 [ksoftirqd/2]
    162  0.0  0.0 32-02:58:43 [kworker/6:1H-kblockd]
    178  0.0  0.0 32-02:58:43 [kworker/7:1H-kblockd]
    109  0.0  0.0 32-02:58:43 [kworker/1:1H-kblockd]
     89  0.0  0.0 32-02:58:44 [kworker/0:1H-kblockd]
1186904  0.0  0.0  1-01:22:54 /usr/lib/systemd/systemd-udevd
1186858  0.0  0.0  1-01:22:54 /usr/sbin/cron -f -P
1186915  0.0  0.0  1-01:22:54 /usr/lib/systemd/systemd-networkd
     42  0.0  0.0 32-02:58:45 [ksoftirqd/4]
     48  0.0  0.0 32-02:58:45 [ksoftirqd/5]
     54  0.0  0.0 32-02:58:45 [ksoftirqd/6]
     16  0.0  0.0 32-02:58:45 [ksoftirqd/0]
     60  0.0  0.0 32-02:58:45 [ksoftirqd/7]
     24  0.0  0.0 32-02:58:45 [ksoftirqd/1]
     66  0.0  0.0 32-02:58:45 [khungtaskd]
      2  0.0  0.0 32-02:58:45 [kthreadd]
    211  0.0  0.0 32-02:58:43 [hwrng]
1186850  0.0  0.0  1-01:22:54 /usr/sbin/atd -f
    962  0.0  0.0 32-02:58:24 /usr/bin/python3 /usr/share/unattended-upgrades/unattended-upgrade-shutdown --wait-for-signal
    226  0.0  0.0 32-02:58:43 [scsi_eh_1]
    237  0.0  0.0 32-02:58:43 [scsi_eh_6]
 274616  0.0  0.0 24-02:42:40 /sbin/agetty -o -p -- \u --noclear - linux
    977  0.0  0.0 32-02:58:24 /sbin/agetty -o -p -- \u --keep-baud 115200,57600,38400,9600 - vt220
    228  0.0  0.0 32-02:58:43 [scsi_eh_2]
    230  0.0  0.0 32-02:58:43 [scsi_eh_3]
    232  0.0  0.0 32-02:58:43 [scsi_eh_4]
      3  0.0  0.0 32-02:58:45 [pool_workqueue_release]
      4  0.0  0.0 32-02:58:45 [kworker/R-rcu_g]
      5  0.0  0.0 32-02:58:45 [kworker/R-rcu_p]
      6  0.0  0.0 32-02:58:45 [kworker/R-slub_]
      7  0.0  0.0 32-02:58:45 [kworker/R-netns]
     10  0.0  0.0 32-02:58:45 [kworker/0:0H-events_highpri]
     12  0.0  0.0 32-02:58:45 [kworker/R-mm_pe]
     13  0.0  0.0 32-02:58:45 [rcu_tasks_kthread]
     14  0.0  0.0 32-02:58:45 [rcu_tasks_rude_kthread]
     15  0.0  0.0 32-02:58:45 [rcu_tasks_trace_kthread]
     19  0.0  0.0 32-02:58:45 [idle_inject/0]
     20  0.0  0.0 32-02:58:45 [cpuhp/0]
     21  0.0  0.0 32-02:58:45 [cpuhp/1]
     22  0.0  0.0 32-02:58:45 [idle_inject/1]
     26  0.0  0.0 32-02:58:45 [kworker/1:0H-events_highpri]
     27  0.0  0.0 32-02:58:45 [cpuhp/2]
     28  0.0  0.0 32-02:58:45 [idle_inject/2]
     32  0.0  0.0 32-02:58:45 [kworker/2:0H-events_highpri]
     33  0.0  0.0 32-02:58:45 [cpuhp/3]
     34  0.0  0.0 32-02:58:45 [idle_inject/3]
     38  0.0  0.0 32-02:58:45 [kworker/3:0H-events_highpri]
     39  0.0  0.0 32-02:58:45 [cpuhp/4]
     40  0.0  0.0 32-02:58:45 [idle_inject/4]
     44  0.0  0.0 32-02:58:45 [kworker/4:0H-events_highpri]
     45  0.0  0.0 32-02:58:45 [cpuhp/5]
     46  0.0  0.0 32-02:58:45 [idle_inject/5]
     50  0.0  0.0 32-02:58:45 [kworker/5:0H-events_highpri]
     51  0.0  0.0 32-02:58:45 [cpuhp/6]
     52  0.0  0.0 32-02:58:45 [idle_inject/6]
     56  0.0  0.0 32-02:58:45 [kworker/6:0H-events_highpri]
     57  0.0  0.0 32-02:58:45 [cpuhp/7]
     58  0.0  0.0 32-02:58:45 [idle_inject/7]
     62  0.0  0.0 32-02:58:45 [kworker/7:0H-events_highpri]
     63  0.0  0.0 32-02:58:45 [kdevtmpfs]
     64  0.0  0.0 32-02:58:45 [kworker/R-inet_]
     65  0.0  0.0 32-02:58:45 [kauditd]
     67  0.0  0.0 32-02:58:45 [oom_reaper]
     69  0.0  0.0 32-02:58:45 [kworker/R-write]
     72  0.0  0.0 32-02:58:45 [ksmd]
     74  0.0  0.0 32-02:58:45 [kworker/R-kinte]
     75  0.0  0.0 32-02:58:45 [kworker/R-kbloc]
     76  0.0  0.0 32-02:58:45 [kworker/R-blkcg]
     77  0.0  0.0 32-02:58:45 [irq/9-acpi]
     80  0.0  0.0 32-02:58:44 [kworker/R-tpm_d]
     81  0.0  0.0 32-02:58:44 [kworker/R-ata_s]
     82  0.0  0.0 32-02:58:44 [kworker/R-md]
     83  0.0  0.0 32-02:58:44 [kworker/R-md_bi]
     84  0.0  0.0 32-02:58:44 [kworker/R-edac-]
     85  0.0  0.0 32-02:58:44 [kworker/R-devfr]
     86  0.0  0.0 32-02:58:44 [watchdogd]
     88  0.0  0.0 32-02:58:44 [kworker/R-quota]
     92  0.0  0.0 32-02:58:44 [ecryptfs-kthread]
     93  0.0  0.0 32-02:58:44 [kworker/R-kthro]
     94  0.0  0.0 32-02:58:44 [irq/24-aerdrv]
     95  0.0  0.0 32-02:58:44 [irq/25-aerdrv]
     96  0.0  0.0 32-02:58:44 [irq/26-aerdrv]
     97  0.0  0.0 32-02:58:44 [irq/27-aerdrv]
     98  0.0  0.0 32-02:58:44 [irq/28-aerdrv]
     99  0.0  0.0 32-02:58:44 [irq/29-aerdrv]
    100  0.0  0.0 32-02:58:44 [irq/30-aerdrv]
    101  0.0  0.0 32-02:58:44 [irq/31-aerdrv]
    102  0.0  0.0 32-02:58:44 [irq/32-aerdrv]
    103  0.0  0.0 32-02:58:44 [kworker/R-acpi_]
    105  0.0  0.0 32-02:58:44 [scsi_eh_0]
    106  0.0  0.0 32-02:58:44 [kworker/R-scsi_]
    108  0.0  0.0 32-02:58:43 [kworker/R-mld]
    110  0.0  0.0 32-02:58:43 [kworker/R-ipv6_]
    117  0.0  0.0 32-02:58:43 [kworker/R-kstrp]
    121  0.0  0.0 32-02:58:43 [kworker/u17:0]
    126  0.0  0.0 32-02:58:43 [kworker/R-crypt]
    137  0.0  0.0 32-02:58:43 [kworker/R-charg]
    227  0.0  0.0 32-02:58:43 [kworker/R-scsi_]
    229  0.0  0.0 32-02:58:43 [kworker/R-scsi_]
    231  0.0  0.0 32-02:58:43 [kworker/R-scsi_]
    233  0.0  0.0 32-02:58:43 [kworker/R-scsi_]
    235  0.0  0.0 32-02:58:43 [scsi_eh_5]
    236  0.0  0.0 32-02:58:43 [kworker/R-scsi_]
    238  0.0  0.0 32-02:58:43 [kworker/R-scsi_]
    284  0.0  0.0 32-02:58:41 [kworker/R-raid5]
    325  0.0  0.0 32-02:58:40 [kworker/R-ext4-]
    412  0.0  0.0 32-02:58:39 [kworker/R-kmpat]
    413  0.0  0.0 32-02:58:39 [kworker/R-kmpat]
   1098  0.0  0.0 32-02:58:21 [kworker/R-tls-s]
1186162  0.0  0.0  1-01:23:04 [psimon]
1186914  0.0  0.0  1-01:22:54 [psimon]
1236805  0.0  0.0       42:15 [kworker/4:1-cgroup_free]
1237075  0.0  0.0       29:09 [kworker/6:3-cgroup_free]
1237362  0.0  0.0       15:05 [kworker/2:2-cgwb_release]
1237402  0.0  0.0       13:04 [kworker/1:2-cgwb_release]
1237449  0.0  0.0       11:03 [kworker/0:0-cgroup_free]
1237492  0.0  0.0       09:02 [kworker/7:2-cgroup_free]
1237510  0.0  0.0       08:02 [kworker/5:0]
1237558  0.0  0.0       06:02 [kworker/3:1-cgroup_free]
1237559  0.0  0.0       06:02 [kworker/3:3-cgwb_release]
1237604  0.0  0.0       04:01 [kworker/6:0-cgroup_free]
1237605  0.0  0.0       04:01 [kworker/6:1-cgwb_release]
1237655  0.0  0.0       01:45 sshd: [accepted]
1237729  0.0  0.0       00:57 [kworker/4:0]
1237732  0.0  0.0       00:44 sshd: [accepted]
```
