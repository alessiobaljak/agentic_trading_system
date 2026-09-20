# 0118-carico-macchina.req

_eseguito: 2026-09-20 17:30 UTC_

**richiesta:** `processi`
**eseguito:** `ps -eo pid,pcpu,pmem,etime,args --sort=-pcpu`
**esito:** codice 0 in 0.0s

```
    PID %CPU %MEM     ELAPSED COMMAND
1483829 99.7  5.5    01:42:28 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1483808 99.6  3.6    01:42:28 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1483913 99.6  6.1    01:42:28 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1483850 99.5  6.0    01:42:28 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1483955 99.5  4.4    01:42:28 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1483934 99.4  6.3    01:42:28 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1483871 99.4  6.0    01:42:28 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1483892 98.9  6.0    01:42:28 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1486248 12.5  0.0       00:00 sshd: [accepted]
1486242 10.8  0.0       00:00 /root/agentic_trading_system/.venv/bin/python -m scripts.ops_agent
1473997  1.0  0.8    09:50:56 /root/agentic_trading_system/.venv/bin/python -m bot.main
1483747  0.1  0.9    01:43:41 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1186867  0.0  0.0  7-11:01:27 /usr/sbin/qemu-ga
      1  0.0  0.0 38-12:37:17 /usr/lib/systemd/systemd --system --deserialize=78
1186897  0.0  0.3  7-11:01:27 /usr/lib/systemd/systemd-journald
     91  0.0  0.0 38-12:37:16 [kswapd0]
1486165  0.0  0.0       02:56 [kworker/u16:5-events_power_efficient]
     17  0.0  0.0 38-12:37:17 [rcu_preempt]
1484017  0.0  0.0    01:40:08 [kworker/3:3-mm_percpu_wq]
     71  0.0  0.0 38-12:37:17 [kcompactd0]
1482209  0.0  0.0    02:50:23 [kworker/2:1-mm_percpu_wq]
1482675  0.0  0.0    02:29:16 [kworker/5:2-events]
1485098  0.0  0.0       43:10 [kworker/u16:4-events_power_efficient]
1478458  0.0  0.0    06:10:23 [kworker/0:2-events]
1186864  0.0  0.1  7-11:01:27 /sbin/multipathd -d -s
1485670  0.0  0.0       21:44 [kworker/u16:0-flush-8:0]
1485159  0.0  0.0       40:08 [kworker/7:2-events]
1186899  0.0  0.0  7-11:01:27 /usr/lib/systemd/systemd-resolved
1486016  0.0  0.0       07:26 [kworker/u16:1-events_power_efficient]
1186885  0.0  0.0  7-11:01:27 sshd: /usr/sbin/sshd -D [listener] 1 of 10-100 startups
     73  0.0  0.0 38-12:37:17 [khugepaged]
1186905  0.0  0.0  7-11:01:27 /usr/sbin/rsyslogd -n -iNONE
1480053  0.0  0.0    04:40:55 [kworker/6:3-mm_percpu_wq]
1481471  0.0  0.0    03:33:35 [kworker/1:3-mm_percpu_wq]
1485814  0.0  0.0       12:31 [kworker/u16:3-events_unbound]
1483061  0.0  0.0    02:13:42 [kworker/4:3-mm_percpu_wq]
    914  0.0  0.0 38-12:36:56 @dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation --syslog-only
1356672  0.0  0.0  3-10:42:36 /usr/lib/polkit-1/polkitd --no-debug
    324  0.0  0.0 38-12:37:13 [jbd2/sda1-8]
    926  0.0  0.0 38-12:36:56 /usr/lib/systemd/systemd-logind
    200  0.0  0.0 38-12:37:15 [kworker/2:1H-kblockd]
     18  0.0  0.0 38-12:37:17 [migration/0]
1186900  0.0  0.0  7-11:01:27 /usr/lib/systemd/systemd-timesyncd
     23  0.0  0.0 38-12:37:17 [migration/1]
     29  0.0  0.0 38-12:37:17 [migration/2]
     35  0.0  0.0 38-12:37:17 [migration/3]
     41  0.0  0.0 38-12:37:17 [migration/4]
     47  0.0  0.0 38-12:37:17 [migration/5]
     59  0.0  0.0 38-12:37:17 [migration/7]
     53  0.0  0.0 38-12:37:17 [migration/6]
    177  0.0  0.0 38-12:37:15 [kworker/3:1H-kblockd]
     36  0.0  0.0 38-12:37:17 [ksoftirqd/3]
     30  0.0  0.0 38-12:37:17 [ksoftirqd/2]
    165  0.0  0.0 38-12:37:15 [kworker/5:1H-kblockd]
    197  0.0  0.0 38-12:37:15 [kworker/4:1H-kblockd]
    162  0.0  0.0 38-12:37:15 [kworker/6:1H-kblockd]
    178  0.0  0.0 38-12:37:15 [kworker/7:1H-kblockd]
    109  0.0  0.0 38-12:37:16 [kworker/1:1H-kblockd]
1186858  0.0  0.0  7-11:01:27 /usr/sbin/cron -f -P
     89  0.0  0.0 38-12:37:17 [kworker/0:1H-kblockd]
1186915  0.0  0.0  7-11:01:27 /usr/lib/systemd/systemd-networkd
1186904  0.0  0.0  7-11:01:27 /usr/lib/systemd/systemd-udevd
     42  0.0  0.0 38-12:37:17 [ksoftirqd/4]
     48  0.0  0.0 38-12:37:17 [ksoftirqd/5]
     54  0.0  0.0 38-12:37:17 [ksoftirqd/6]
     16  0.0  0.0 38-12:37:17 [ksoftirqd/0]
     60  0.0  0.0 38-12:37:17 [ksoftirqd/7]
     24  0.0  0.0 38-12:37:17 [ksoftirqd/1]
     66  0.0  0.0 38-12:37:17 [khungtaskd]
      2  0.0  0.0 38-12:37:17 [kthreadd]
    211  0.0  0.0 38-12:37:15 [hwrng]
1186850  0.0  0.0  7-11:01:27 /usr/sbin/atd -f
    962  0.0  0.0 38-12:36:56 /usr/bin/python3 /usr/share/unattended-upgrades/unattended-upgrade-shutdown --wait-for-signal
    226  0.0  0.0 38-12:37:15 [scsi_eh_1]
    237  0.0  0.0 38-12:37:15 [scsi_eh_6]
 274616  0.0  0.0 30-12:21:13 /sbin/agetty -o -p -- \u --noclear - linux
    977  0.0  0.0 38-12:36:56 /sbin/agetty -o -p -- \u --keep-baud 115200,57600,38400,9600 - vt220
    228  0.0  0.0 38-12:37:15 [scsi_eh_2]
    230  0.0  0.0 38-12:37:15 [scsi_eh_3]
    232  0.0  0.0 38-12:37:15 [scsi_eh_4]
      3  0.0  0.0 38-12:37:17 [pool_workqueue_release]
      4  0.0  0.0 38-12:37:17 [kworker/R-rcu_g]
      5  0.0  0.0 38-12:37:17 [kworker/R-rcu_p]
      6  0.0  0.0 38-12:37:17 [kworker/R-slub_]
      7  0.0  0.0 38-12:37:17 [kworker/R-netns]
     10  0.0  0.0 38-12:37:17 [kworker/0:0H-events_highpri]
     12  0.0  0.0 38-12:37:17 [kworker/R-mm_pe]
     13  0.0  0.0 38-12:37:17 [rcu_tasks_kthread]
     14  0.0  0.0 38-12:37:17 [rcu_tasks_rude_kthread]
     15  0.0  0.0 38-12:37:17 [rcu_tasks_trace_kthread]
     19  0.0  0.0 38-12:37:17 [idle_inject/0]
     20  0.0  0.0 38-12:37:17 [cpuhp/0]
     21  0.0  0.0 38-12:37:17 [cpuhp/1]
     22  0.0  0.0 38-12:37:17 [idle_inject/1]
     26  0.0  0.0 38-12:37:17 [kworker/1:0H-events_highpri]
     27  0.0  0.0 38-12:37:17 [cpuhp/2]
     28  0.0  0.0 38-12:37:17 [idle_inject/2]
     32  0.0  0.0 38-12:37:17 [kworker/2:0H-events_highpri]
     33  0.0  0.0 38-12:37:17 [cpuhp/3]
     34  0.0  0.0 38-12:37:17 [idle_inject/3]
     38  0.0  0.0 38-12:37:17 [kworker/3:0H-events_highpri]
     39  0.0  0.0 38-12:37:17 [cpuhp/4]
     40  0.0  0.0 38-12:37:17 [idle_inject/4]
     44  0.0  0.0 38-12:37:17 [kworker/4:0H-events_highpri]
     45  0.0  0.0 38-12:37:17 [cpuhp/5]
     46  0.0  0.0 38-12:37:17 [idle_inject/5]
     50  0.0  0.0 38-12:37:17 [kworker/5:0H-events_highpri]
     51  0.0  0.0 38-12:37:17 [cpuhp/6]
     52  0.0  0.0 38-12:37:17 [idle_inject/6]
     56  0.0  0.0 38-12:37:17 [kworker/6:0H-events_highpri]
     57  0.0  0.0 38-12:37:17 [cpuhp/7]
     58  0.0  0.0 38-12:37:17 [idle_inject/7]
     62  0.0  0.0 38-12:37:17 [kworker/7:0H-events_highpri]
     63  0.0  0.0 38-12:37:17 [kdevtmpfs]
     64  0.0  0.0 38-12:37:17 [kworker/R-inet_]
     65  0.0  0.0 38-12:37:17 [kauditd]
     67  0.0  0.0 38-12:37:17 [oom_reaper]
     69  0.0  0.0 38-12:37:17 [kworker/R-write]
     72  0.0  0.0 38-12:37:17 [ksmd]
     74  0.0  0.0 38-12:37:17 [kworker/R-kinte]
     75  0.0  0.0 38-12:37:17 [kworker/R-kbloc]
     76  0.0  0.0 38-12:37:17 [kworker/R-blkcg]
     77  0.0  0.0 38-12:37:17 [irq/9-acpi]
     80  0.0  0.0 38-12:37:17 [kworker/R-tpm_d]
     81  0.0  0.0 38-12:37:17 [kworker/R-ata_s]
     82  0.0  0.0 38-12:37:17 [kworker/R-md]
     83  0.0  0.0 38-12:37:17 [kworker/R-md_bi]
     84  0.0  0.0 38-12:37:17 [kworker/R-edac-]
     85  0.0  0.0 38-12:37:17 [kworker/R-devfr]
     86  0.0  0.0 38-12:37:17 [watchdogd]
     88  0.0  0.0 38-12:37:17 [kworker/R-quota]
     92  0.0  0.0 38-12:37:16 [ecryptfs-kthread]
     93  0.0  0.0 38-12:37:16 [kworker/R-kthro]
     94  0.0  0.0 38-12:37:16 [irq/24-aerdrv]
     95  0.0  0.0 38-12:37:16 [irq/25-aerdrv]
     96  0.0  0.0 38-12:37:16 [irq/26-aerdrv]
     97  0.0  0.0 38-12:37:16 [irq/27-aerdrv]
     98  0.0  0.0 38-12:37:16 [irq/28-aerdrv]
     99  0.0  0.0 38-12:37:16 [irq/29-aerdrv]
    100  0.0  0.0 38-12:37:16 [irq/30-aerdrv]
    101  0.0  0.0 38-12:37:16 [irq/31-aerdrv]
    102  0.0  0.0 38-12:37:16 [irq/32-aerdrv]
    103  0.0  0.0 38-12:37:16 [kworker/R-acpi_]
    105  0.0  0.0 38-12:37:16 [scsi_eh_0]
    106  0.0  0.0 38-12:37:16 [kworker/R-scsi_]
    108  0.0  0.0 38-12:37:16 [kworker/R-mld]
    110  0.0  0.0 38-12:37:16 [kworker/R-ipv6_]
    117  0.0  0.0 38-12:37:16 [kworker/R-kstrp]
    121  0.0  0.0 38-12:37:16 [kworker/u17:0]
    126  0.0  0.0 38-12:37:16 [kworker/R-crypt]
    137  0.0  0.0 38-12:37:16 [kworker/R-charg]
    227  0.0  0.0 38-12:37:15 [kworker/R-scsi_]
    229  0.0  0.0 38-12:37:15 [kworker/R-scsi_]
    231  0.0  0.0 38-12:37:15 [kworker/R-scsi_]
    233  0.0  0.0 38-12:37:15 [kworker/R-scsi_]
    235  0.0  0.0 38-12:37:15 [scsi_eh_5]
    236  0.0  0.0 38-12:37:15 [kworker/R-scsi_]
    238  0.0  0.0 38-12:37:15 [kworker/R-scsi_]
    284  0.0  0.0 38-12:37:13 [kworker/R-raid5]
    325  0.0  0.0 38-12:37:13 [kworker/R-ext4-]
    412  0.0  0.0 38-12:37:11 [kworker/R-kmpat]
    413  0.0  0.0 38-12:37:11 [kworker/R-kmpat]
   1098  0.0  0.0 38-12:36:54 [kworker/R-tls-s]
1186914  0.0  0.0  7-11:01:27 [psimon]
1459242  0.0  0.0    21:02:10 [psimon]
1485310  0.0  0.0       34:12 [kworker/2:2-cgroup_free]
1485686  0.0  0.0       21:07 [kworker/3:1-cgroup_free]
1485729  0.0  0.0       18:05 [kworker/0:0]
1485745  0.0  0.0       17:05 [kworker/6:0-cgwb_release]
1485759  0.0  0.0       16:04 [kworker/1:1-cgroup_free]
1485843  0.0  0.0       11:03 [kworker/7:3-cgroup_free]
1485937  0.0  0.0       10:08 [kworker/5:1-cgwb_release]
1486040  0.0  0.0       07:02 [kworker/3:2-cgwb_release]
1486070  0.0  0.0       06:01 [kworker/4:2]
1486132  0.0  0.0       04:01 [kworker/5:0-events]
1486133  0.0  0.0       04:01 [kworker/5:3]
1486161  0.0  0.0       03:01 [kworker/2:0-cgroup_free]
1486162  0.0  0.0       03:01 [kworker/2:3-cgwb_release]
1486164  0.0  0.0       02:56 [kworker/u16:2-events_power_efficient]
1486221  0.0  0.0       01:00 [kworker/7:0]
1486256  0.0  0.0       00:00 ps -eo pid,pcpu,pmem,etime,args --sort=-pcpu
```
