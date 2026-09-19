# 0092-percorso-app.req

_eseguito: 2026-09-19 14:26 UTC_

**richiesta:** `processi`
**eseguito:** `ps -eo pid,pcpu,pmem,etime,args --sort=-pcpu`
**esito:** codice 0 in 0.0s

```
    PID %CPU %MEM     ELAPSED COMMAND
1449552  100  0.0       00:00 ps -eo pid,pcpu,pmem,etime,args --sort=-pcpu
1447451 99.7  6.0    01:41:56 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1447388 99.6  4.7    01:41:56 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1447409 99.6  5.9    01:41:56 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1447346 99.6  3.7    01:41:56 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1447430 99.5  5.8    01:41:56 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1447472 99.5  4.6    01:41:56 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1447367 99.5  4.0    01:41:56 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1447325 99.3  4.2    01:41:56 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1449540  9.4  0.0       00:00 /root/agentic_trading_system/.venv/bin/python -m scripts.ops_agent
1190071  1.3  0.8  6-05:49:15 /root/agentic_trading_system/.venv/bin/python -m bot.main
1447298  0.1  0.9    01:42:01 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1186867  0.0  0.0  6-07:57:46 /usr/sbin/qemu-ga
1186897  0.0  0.5  6-07:57:46 /usr/lib/systemd/systemd-journald
      1  0.0  0.0 37-09:33:37 /usr/lib/systemd/systemd --system --deserialize=78
     91  0.0  0.0 37-09:33:36 [kswapd0]
     17  0.0  0.0 37-09:33:37 [rcu_preempt]
1449093  0.0  0.0       20:07 [kworker/5:2-events]
     71  0.0  0.0 37-09:33:37 [kcompactd0]
1448791  0.0  0.0       34:11 [kworker/2:1-events]
1447724  0.0  0.0    01:30:28 [kworker/3:1-events]
1449075  0.0  0.0       20:23 [kworker/u16:0-events_power_efficient]
1186864  0.0  0.1  6-07:57:46 /sbin/multipathd -d -s
1449258  0.0  0.0       12:03 [kworker/u16:1-ext4-rsv-conversion]
1186885  0.0  0.0  6-07:57:46 sshd: /usr/sbin/sshd -D [listener] 0 of 10-100 startups
1186899  0.0  0.0  6-07:57:46 /usr/lib/systemd/systemd-resolved
1414761  0.0  0.0    16:46:42 [kworker/7:0-mm_percpu_wq]
1447780  0.0  0.0    01:26:27 [kworker/0:0-mm_percpu_wq]
1448828  0.0  0.0       32:00 [kworker/u16:5-events_power_efficient]
1434295  0.0  0.0    09:02:08 [kworker/4:1-events]
1186905  0.0  0.0  6-07:57:46 /usr/sbin/rsyslogd -n -iNONE
     73  0.0  0.0 37-09:33:37 [khugepaged]
1439483  0.0  0.0    05:43:05 [kworker/1:1-events]
1449463  0.0  0.0       04:06 [kworker/u16:2-events_power_efficient]
1448399  0.0  0.0       55:17 [kworker/6:1-mm_percpu_wq]
    914  0.0  0.0 37-09:33:16 @dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation --syslog-only
1356672  0.0  0.0  2-07:38:55 /usr/lib/polkit-1/polkitd --no-debug
    324  0.0  0.0 37-09:33:32 [jbd2/sda1-8]
    926  0.0  0.0 37-09:33:16 /usr/lib/systemd/systemd-logind
    200  0.0  0.0 37-09:33:35 [kworker/2:1H-kblockd]
     18  0.0  0.0 37-09:33:37 [migration/0]
1186900  0.0  0.0  6-07:57:46 /usr/lib/systemd/systemd-timesyncd
     23  0.0  0.0 37-09:33:37 [migration/1]
     29  0.0  0.0 37-09:33:37 [migration/2]
     35  0.0  0.0 37-09:33:37 [migration/3]
     41  0.0  0.0 37-09:33:37 [migration/4]
     47  0.0  0.0 37-09:33:37 [migration/5]
     59  0.0  0.0 37-09:33:37 [migration/7]
     53  0.0  0.0 37-09:33:37 [migration/6]
    177  0.0  0.0 37-09:33:35 [kworker/3:1H-kblockd]
     36  0.0  0.0 37-09:33:37 [ksoftirqd/3]
     30  0.0  0.0 37-09:33:37 [ksoftirqd/2]
    165  0.0  0.0 37-09:33:35 [kworker/5:1H-kblockd]
    197  0.0  0.0 37-09:33:35 [kworker/4:1H-kblockd]
    162  0.0  0.0 37-09:33:35 [kworker/6:1H-kblockd]
    178  0.0  0.0 37-09:33:35 [kworker/7:1H-kblockd]
    109  0.0  0.0 37-09:33:35 [kworker/1:1H-kblockd]
1186858  0.0  0.0  6-07:57:46 /usr/sbin/cron -f -P
     89  0.0  0.0 37-09:33:36 [kworker/0:1H-kblockd]
1186915  0.0  0.0  6-07:57:46 /usr/lib/systemd/systemd-networkd
1186904  0.0  0.0  6-07:57:46 /usr/lib/systemd/systemd-udevd
     42  0.0  0.0 37-09:33:37 [ksoftirqd/4]
     48  0.0  0.0 37-09:33:37 [ksoftirqd/5]
     54  0.0  0.0 37-09:33:37 [ksoftirqd/6]
     16  0.0  0.0 37-09:33:37 [ksoftirqd/0]
     60  0.0  0.0 37-09:33:37 [ksoftirqd/7]
     24  0.0  0.0 37-09:33:37 [ksoftirqd/1]
     66  0.0  0.0 37-09:33:37 [khungtaskd]
      2  0.0  0.0 37-09:33:37 [kthreadd]
    211  0.0  0.0 37-09:33:35 [hwrng]
1356665  0.0  0.0  2-07:38:55 [psimon]
1186850  0.0  0.0  6-07:57:46 /usr/sbin/atd -f
    962  0.0  0.0 37-09:33:16 /usr/bin/python3 /usr/share/unattended-upgrades/unattended-upgrade-shutdown --wait-for-signal
    226  0.0  0.0 37-09:33:35 [scsi_eh_1]
    237  0.0  0.0 37-09:33:35 [scsi_eh_6]
 274616  0.0  0.0 29-09:17:32 /sbin/agetty -o -p -- \u --noclear - linux
    977  0.0  0.0 37-09:33:16 /sbin/agetty -o -p -- \u --keep-baud 115200,57600,38400,9600 - vt220
    228  0.0  0.0 37-09:33:35 [scsi_eh_2]
    230  0.0  0.0 37-09:33:35 [scsi_eh_3]
    232  0.0  0.0 37-09:33:35 [scsi_eh_4]
      3  0.0  0.0 37-09:33:37 [pool_workqueue_release]
      4  0.0  0.0 37-09:33:37 [kworker/R-rcu_g]
      5  0.0  0.0 37-09:33:37 [kworker/R-rcu_p]
      6  0.0  0.0 37-09:33:37 [kworker/R-slub_]
      7  0.0  0.0 37-09:33:37 [kworker/R-netns]
     10  0.0  0.0 37-09:33:37 [kworker/0:0H-events_highpri]
     12  0.0  0.0 37-09:33:37 [kworker/R-mm_pe]
     13  0.0  0.0 37-09:33:37 [rcu_tasks_kthread]
     14  0.0  0.0 37-09:33:37 [rcu_tasks_rude_kthread]
     15  0.0  0.0 37-09:33:37 [rcu_tasks_trace_kthread]
     19  0.0  0.0 37-09:33:37 [idle_inject/0]
     20  0.0  0.0 37-09:33:37 [cpuhp/0]
     21  0.0  0.0 37-09:33:37 [cpuhp/1]
     22  0.0  0.0 37-09:33:37 [idle_inject/1]
     26  0.0  0.0 37-09:33:37 [kworker/1:0H-events_highpri]
     27  0.0  0.0 37-09:33:37 [cpuhp/2]
     28  0.0  0.0 37-09:33:37 [idle_inject/2]
     32  0.0  0.0 37-09:33:37 [kworker/2:0H-events_highpri]
     33  0.0  0.0 37-09:33:37 [cpuhp/3]
     34  0.0  0.0 37-09:33:37 [idle_inject/3]
     38  0.0  0.0 37-09:33:37 [kworker/3:0H-events_highpri]
     39  0.0  0.0 37-09:33:37 [cpuhp/4]
     40  0.0  0.0 37-09:33:37 [idle_inject/4]
     44  0.0  0.0 37-09:33:37 [kworker/4:0H-events_highpri]
     45  0.0  0.0 37-09:33:37 [cpuhp/5]
     46  0.0  0.0 37-09:33:37 [idle_inject/5]
     50  0.0  0.0 37-09:33:37 [kworker/5:0H-events_highpri]
     51  0.0  0.0 37-09:33:37 [cpuhp/6]
     52  0.0  0.0 37-09:33:37 [idle_inject/6]
     56  0.0  0.0 37-09:33:37 [kworker/6:0H-events_highpri]
     57  0.0  0.0 37-09:33:37 [cpuhp/7]
     58  0.0  0.0 37-09:33:37 [idle_inject/7]
     62  0.0  0.0 37-09:33:37 [kworker/7:0H-events_highpri]
     63  0.0  0.0 37-09:33:37 [kdevtmpfs]
     64  0.0  0.0 37-09:33:37 [kworker/R-inet_]
     65  0.0  0.0 37-09:33:37 [kauditd]
     67  0.0  0.0 37-09:33:37 [oom_reaper]
     69  0.0  0.0 37-09:33:37 [kworker/R-write]
     72  0.0  0.0 37-09:33:37 [ksmd]
     74  0.0  0.0 37-09:33:37 [kworker/R-kinte]
     75  0.0  0.0 37-09:33:37 [kworker/R-kbloc]
     76  0.0  0.0 37-09:33:37 [kworker/R-blkcg]
     77  0.0  0.0 37-09:33:37 [irq/9-acpi]
     80  0.0  0.0 37-09:33:36 [kworker/R-tpm_d]
     81  0.0  0.0 37-09:33:36 [kworker/R-ata_s]
     82  0.0  0.0 37-09:33:36 [kworker/R-md]
     83  0.0  0.0 37-09:33:36 [kworker/R-md_bi]
     84  0.0  0.0 37-09:33:36 [kworker/R-edac-]
     85  0.0  0.0 37-09:33:36 [kworker/R-devfr]
     86  0.0  0.0 37-09:33:36 [watchdogd]
     88  0.0  0.0 37-09:33:36 [kworker/R-quota]
     92  0.0  0.0 37-09:33:36 [ecryptfs-kthread]
     93  0.0  0.0 37-09:33:36 [kworker/R-kthro]
     94  0.0  0.0 37-09:33:36 [irq/24-aerdrv]
     95  0.0  0.0 37-09:33:36 [irq/25-aerdrv]
     96  0.0  0.0 37-09:33:36 [irq/26-aerdrv]
     97  0.0  0.0 37-09:33:36 [irq/27-aerdrv]
     98  0.0  0.0 37-09:33:36 [irq/28-aerdrv]
     99  0.0  0.0 37-09:33:36 [irq/29-aerdrv]
    100  0.0  0.0 37-09:33:36 [irq/30-aerdrv]
    101  0.0  0.0 37-09:33:36 [irq/31-aerdrv]
    102  0.0  0.0 37-09:33:36 [irq/32-aerdrv]
    103  0.0  0.0 37-09:33:36 [kworker/R-acpi_]
    105  0.0  0.0 37-09:33:36 [scsi_eh_0]
    106  0.0  0.0 37-09:33:36 [kworker/R-scsi_]
    108  0.0  0.0 37-09:33:35 [kworker/R-mld]
    110  0.0  0.0 37-09:33:35 [kworker/R-ipv6_]
    117  0.0  0.0 37-09:33:35 [kworker/R-kstrp]
    121  0.0  0.0 37-09:33:35 [kworker/u17:0]
    126  0.0  0.0 37-09:33:35 [kworker/R-crypt]
    137  0.0  0.0 37-09:33:35 [kworker/R-charg]
    227  0.0  0.0 37-09:33:35 [kworker/R-scsi_]
    229  0.0  0.0 37-09:33:35 [kworker/R-scsi_]
    231  0.0  0.0 37-09:33:35 [kworker/R-scsi_]
    233  0.0  0.0 37-09:33:35 [kworker/R-scsi_]
    235  0.0  0.0 37-09:33:35 [scsi_eh_5]
    236  0.0  0.0 37-09:33:35 [kworker/R-scsi_]
    238  0.0  0.0 37-09:33:35 [kworker/R-scsi_]
    284  0.0  0.0 37-09:33:33 [kworker/R-raid5]
    325  0.0  0.0 37-09:33:32 [kworker/R-ext4-]
    412  0.0  0.0 37-09:33:31 [kworker/R-kmpat]
    413  0.0  0.0 37-09:33:31 [kworker/R-kmpat]
   1098  0.0  0.0 37-09:33:13 [kworker/R-tls-s]
1186914  0.0  0.0  6-07:57:46 [psimon]
1448808  0.0  0.0       33:10 [kworker/7:1]
1449092  0.0  0.0       20:07 [kworker/5:0-cgwb_release]
1449213  0.0  0.0       14:04 [kworker/1:2]
1449232  0.0  0.0       13:04 [kworker/3:0-cgroup_free]
1449302  0.0  0.0       10:03 [kworker/4:2]
1449374  0.0  0.0       07:59 [kworker/0:2-cgroup_free]
1449419  0.0  0.0       06:27 [kworker/2:0-cgroup_free]
1449420  0.0  0.0       06:27 [kworker/2:3-cgwb_release]
1449437  0.0  0.0       06:02 [kworker/6:0-cgroup_free]
```
