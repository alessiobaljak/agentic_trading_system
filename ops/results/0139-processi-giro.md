# 0139-processi-giro.req

_eseguito: 2026-09-22 05:46 UTC_

**richiesta:** `processi`
**eseguito:** `ps -eo pid,pcpu,pmem,etime,args --sort=-pcpu`
**esito:** codice 0 in 0.0s

```
    PID %CPU %MEM     ELAPSED COMMAND
1544260 99.2 10.6    02:52:30 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1544302 99.2  8.4    02:52:30 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1544281 99.2 11.0    02:52:30 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1544344 99.2  9.4    02:52:30 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1544323 99.2 10.4    02:52:30 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1544218 99.2  7.0    02:52:30 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1544365 99.1 11.2    02:52:30 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1544239 99.1  8.6    02:52:30 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1547734  6.4  0.0       00:00 /root/agentic_trading_system/.venv/bin/python -m scripts.ops_agent
1547730  2.3  0.0       00:18 sshd: root [priv]
1535908  0.5  0.8    09:59:07 /root/agentic_trading_system/.venv/bin/python -m bot.main
1544150  0.1  0.9    02:54:05 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1186867  0.0  0.0  8-23:18:03 /usr/sbin/qemu-ga
      1  0.0  0.0 40-00:53:53 /usr/lib/systemd/systemd --system --deserialize=78
     91  0.0  0.0 40-00:53:52 [kswapd0]
1186897  0.0  0.3  8-23:18:03 /usr/lib/systemd/systemd-journald
1547562  0.0  0.0       07:02 [kworker/2:0-events]
     17  0.0  0.0 40-00:53:53 [rcu_preempt]
     71  0.0  0.0 40-00:53:53 [kcompactd0]
1543981  0.0  0.0    03:02:00 [kworker/5:3-events]
1186899  0.0  0.0  8-23:18:03 /usr/lib/systemd/systemd-resolved
1542751  0.0  0.0    03:48:31 [kworker/u16:0-events_power_efficient]
1186864  0.0  0.1  8-23:18:03 /sbin/multipathd -d -s
1547333  0.0  0.0       20:57 [kworker/u16:1-ext4-rsv-conversion]
1542632  0.0  0.0    03:57:17 [kworker/0:0-mm_percpu_wq]
1545591  0.0  0.0    01:53:36 [kworker/u16:2-events_power_efficient]
1546902  0.0  0.0       44:44 [kworker/u16:3-events_power_efficient]
1186885  0.0  0.0  8-23:18:03 sshd: /usr/sbin/sshd -D [listener] 1 of 10-100 startups
     73  0.0  0.0 40-00:53:53 [khugepaged]
1186905  0.0  0.0  8-23:18:03 /usr/sbin/rsyslogd -n -iNONE
1540039  0.0  0.0    06:29:03 [kworker/7:0-events]
1547141  0.0  0.0       32:09 [kworker/3:3-mm_percpu_wq]
1533373  0.0  0.0    11:13:30 [kworker/1:0-cgroup_free]
1545694  0.0  0.0    01:46:43 [kworker/4:3-events]
    914  0.0  0.0 40-00:53:32 @dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation --syslog-only
1547243  0.0  0.0       26:44 [kworker/6:0-mm_percpu_wq]
1356672  0.0  0.0  4-22:59:12 /usr/lib/polkit-1/polkitd --no-debug
    324  0.0  0.0 40-00:53:49 [jbd2/sda1-8]
    926  0.0  0.0 40-00:53:32 /usr/lib/systemd/systemd-logind
    200  0.0  0.0 40-00:53:51 [kworker/2:1H-kblockd]
1186900  0.0  0.0  8-23:18:03 /usr/lib/systemd/systemd-timesyncd
     18  0.0  0.0 40-00:53:53 [migration/0]
     23  0.0  0.0 40-00:53:53 [migration/1]
     29  0.0  0.0 40-00:53:53 [migration/2]
     35  0.0  0.0 40-00:53:53 [migration/3]
     47  0.0  0.0 40-00:53:53 [migration/5]
     41  0.0  0.0 40-00:53:53 [migration/4]
     59  0.0  0.0 40-00:53:53 [migration/7]
     53  0.0  0.0 40-00:53:53 [migration/6]
    177  0.0  0.0 40-00:53:51 [kworker/3:1H-kblockd]
     36  0.0  0.0 40-00:53:53 [ksoftirqd/3]
     30  0.0  0.0 40-00:53:53 [ksoftirqd/2]
    165  0.0  0.0 40-00:53:51 [kworker/5:1H-kblockd]
    197  0.0  0.0 40-00:53:51 [kworker/4:1H-kblockd]
    162  0.0  0.0 40-00:53:51 [kworker/6:1H-kblockd]
    178  0.0  0.0 40-00:53:51 [kworker/7:1H-kblockd]
    109  0.0  0.0 40-00:53:52 [kworker/1:1H-kblockd]
1186858  0.0  0.0  8-23:18:03 /usr/sbin/cron -f -P
     89  0.0  0.0 40-00:53:53 [kworker/0:1H-kblockd]
1186915  0.0  0.0  8-23:18:03 /usr/lib/systemd/systemd-networkd
1186904  0.0  0.0  8-23:18:03 /usr/lib/systemd/systemd-udevd
     42  0.0  0.0 40-00:53:53 [ksoftirqd/4]
     48  0.0  0.0 40-00:53:53 [ksoftirqd/5]
     54  0.0  0.0 40-00:53:53 [ksoftirqd/6]
     16  0.0  0.0 40-00:53:53 [ksoftirqd/0]
     60  0.0  0.0 40-00:53:53 [ksoftirqd/7]
     24  0.0  0.0 40-00:53:53 [ksoftirqd/1]
     66  0.0  0.0 40-00:53:53 [khungtaskd]
      2  0.0  0.0 40-00:53:53 [kthreadd]
    211  0.0  0.0 40-00:53:51 [hwrng]
1527151  0.0  0.0    15:00:21 [psimon]
1186850  0.0  0.0  8-23:18:03 /usr/sbin/atd -f
    962  0.0  0.0 40-00:53:32 /usr/bin/python3 /usr/share/unattended-upgrades/unattended-upgrade-shutdown --wait-for-signal
    226  0.0  0.0 40-00:53:51 [scsi_eh_1]
    237  0.0  0.0 40-00:53:51 [scsi_eh_6]
 274616  0.0  0.0 32-00:37:49 /sbin/agetty -o -p -- \u --noclear - linux
    977  0.0  0.0 40-00:53:32 /sbin/agetty -o -p -- \u --keep-baud 115200,57600,38400,9600 - vt220
    228  0.0  0.0 40-00:53:51 [scsi_eh_2]
    230  0.0  0.0 40-00:53:51 [scsi_eh_3]
    232  0.0  0.0 40-00:53:51 [scsi_eh_4]
      3  0.0  0.0 40-00:53:53 [pool_workqueue_release]
      4  0.0  0.0 40-00:53:53 [kworker/R-rcu_g]
      5  0.0  0.0 40-00:53:53 [kworker/R-rcu_p]
      6  0.0  0.0 40-00:53:53 [kworker/R-slub_]
      7  0.0  0.0 40-00:53:53 [kworker/R-netns]
     10  0.0  0.0 40-00:53:53 [kworker/0:0H-events_highpri]
     12  0.0  0.0 40-00:53:53 [kworker/R-mm_pe]
     13  0.0  0.0 40-00:53:53 [rcu_tasks_kthread]
     14  0.0  0.0 40-00:53:53 [rcu_tasks_rude_kthread]
     15  0.0  0.0 40-00:53:53 [rcu_tasks_trace_kthread]
     19  0.0  0.0 40-00:53:53 [idle_inject/0]
     20  0.0  0.0 40-00:53:53 [cpuhp/0]
     21  0.0  0.0 40-00:53:53 [cpuhp/1]
     22  0.0  0.0 40-00:53:53 [idle_inject/1]
     26  0.0  0.0 40-00:53:53 [kworker/1:0H-events_highpri]
     27  0.0  0.0 40-00:53:53 [cpuhp/2]
     28  0.0  0.0 40-00:53:53 [idle_inject/2]
     32  0.0  0.0 40-00:53:53 [kworker/2:0H-events_highpri]
     33  0.0  0.0 40-00:53:53 [cpuhp/3]
     34  0.0  0.0 40-00:53:53 [idle_inject/3]
     38  0.0  0.0 40-00:53:53 [kworker/3:0H-events_highpri]
     39  0.0  0.0 40-00:53:53 [cpuhp/4]
     40  0.0  0.0 40-00:53:53 [idle_inject/4]
     44  0.0  0.0 40-00:53:53 [kworker/4:0H-events_highpri]
     45  0.0  0.0 40-00:53:53 [cpuhp/5]
     46  0.0  0.0 40-00:53:53 [idle_inject/5]
     50  0.0  0.0 40-00:53:53 [kworker/5:0H-events_highpri]
     51  0.0  0.0 40-00:53:53 [cpuhp/6]
     52  0.0  0.0 40-00:53:53 [idle_inject/6]
     56  0.0  0.0 40-00:53:53 [kworker/6:0H-events_highpri]
     57  0.0  0.0 40-00:53:53 [cpuhp/7]
     58  0.0  0.0 40-00:53:53 [idle_inject/7]
     62  0.0  0.0 40-00:53:53 [kworker/7:0H-events_highpri]
     63  0.0  0.0 40-00:53:53 [kdevtmpfs]
     64  0.0  0.0 40-00:53:53 [kworker/R-inet_]
     65  0.0  0.0 40-00:53:53 [kauditd]
     67  0.0  0.0 40-00:53:53 [oom_reaper]
     69  0.0  0.0 40-00:53:53 [kworker/R-write]
     72  0.0  0.0 40-00:53:53 [ksmd]
     74  0.0  0.0 40-00:53:53 [kworker/R-kinte]
     75  0.0  0.0 40-00:53:53 [kworker/R-kbloc]
     76  0.0  0.0 40-00:53:53 [kworker/R-blkcg]
     77  0.0  0.0 40-00:53:53 [irq/9-acpi]
     80  0.0  0.0 40-00:53:53 [kworker/R-tpm_d]
     81  0.0  0.0 40-00:53:53 [kworker/R-ata_s]
     82  0.0  0.0 40-00:53:53 [kworker/R-md]
     83  0.0  0.0 40-00:53:53 [kworker/R-md_bi]
     84  0.0  0.0 40-00:53:53 [kworker/R-edac-]
     85  0.0  0.0 40-00:53:53 [kworker/R-devfr]
     86  0.0  0.0 40-00:53:53 [watchdogd]
     88  0.0  0.0 40-00:53:53 [kworker/R-quota]
     92  0.0  0.0 40-00:53:52 [ecryptfs-kthread]
     93  0.0  0.0 40-00:53:52 [kworker/R-kthro]
     94  0.0  0.0 40-00:53:52 [irq/24-aerdrv]
     95  0.0  0.0 40-00:53:52 [irq/25-aerdrv]
     96  0.0  0.0 40-00:53:52 [irq/26-aerdrv]
     97  0.0  0.0 40-00:53:52 [irq/27-aerdrv]
     98  0.0  0.0 40-00:53:52 [irq/28-aerdrv]
     99  0.0  0.0 40-00:53:52 [irq/29-aerdrv]
    100  0.0  0.0 40-00:53:52 [irq/30-aerdrv]
    101  0.0  0.0 40-00:53:52 [irq/31-aerdrv]
    102  0.0  0.0 40-00:53:52 [irq/32-aerdrv]
    103  0.0  0.0 40-00:53:52 [kworker/R-acpi_]
    105  0.0  0.0 40-00:53:52 [scsi_eh_0]
    106  0.0  0.0 40-00:53:52 [kworker/R-scsi_]
    108  0.0  0.0 40-00:53:52 [kworker/R-mld]
    110  0.0  0.0 40-00:53:52 [kworker/R-ipv6_]
    117  0.0  0.0 40-00:53:52 [kworker/R-kstrp]
    121  0.0  0.0 40-00:53:52 [kworker/u17:0]
    126  0.0  0.0 40-00:53:52 [kworker/R-crypt]
    137  0.0  0.0 40-00:53:52 [kworker/R-charg]
    227  0.0  0.0 40-00:53:51 [kworker/R-scsi_]
    229  0.0  0.0 40-00:53:51 [kworker/R-scsi_]
    231  0.0  0.0 40-00:53:51 [kworker/R-scsi_]
    233  0.0  0.0 40-00:53:51 [kworker/R-scsi_]
    235  0.0  0.0 40-00:53:51 [scsi_eh_5]
    236  0.0  0.0 40-00:53:51 [kworker/R-scsi_]
    238  0.0  0.0 40-00:53:51 [kworker/R-scsi_]
    284  0.0  0.0 40-00:53:49 [kworker/R-raid5]
    325  0.0  0.0 40-00:53:49 [kworker/R-ext4-]
    412  0.0  0.0 40-00:53:47 [kworker/R-kmpat]
    413  0.0  0.0 40-00:53:47 [kworker/R-kmpat]
   1098  0.0  0.0 40-00:53:30 [kworker/R-tls-s]
1186914  0.0  0.0  8-23:18:03 [psimon]
1546318  0.0  0.0    01:17:24 [kworker/7:2]
1547125  0.0  0.0       33:10 [kworker/5:1-cgroup_free]
1547301  0.0  0.0       23:07 [kworker/1:2]
1547330  0.0  0.0       21:06 [kworker/4:1-cgwb_release]
1547390  0.0  0.0       17:05 [kworker/0:1-cgroup_free]
1547408  0.0  0.0       16:05 [kworker/3:2-cgwb_release]
1547499  0.0  0.0       11:03 [kworker/6:3-cgroup_free]
1547588  0.0  0.0       06:02 [kworker/2:2]
1547605  0.0  0.0       05:01 [kworker/5:0-cgroup_free]
1547649  0.0  0.0       03:01 [kworker/5:2-cgroup_free]
1547731  0.0  0.0       00:18 sshd: root [net]
1547746  0.0  0.0       00:00 ps -eo pid,pcpu,pmem,etime,args --sort=-pcpu
```
