# 0413-1ott-processi-col-gate.req

_eseguito: 2026-10-01 15:29 UTC_

**richiesta:** `processi`
**eseguito:** `ps -eo pid,pcpu,pmem,etime,args --sort=-pcpu`
**esito:** codice 0 in 0.0s

```
    PID %CPU %MEM     ELAPSED COMMAND
1975170 99.9 11.1       11:51 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1975128 99.9 11.8       11:51 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1975086 99.9  9.6       11:51 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1975107 99.9  9.8       11:51 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1975065 99.8 11.7       11:51 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1975149 99.8 11.9       11:51 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1975892 10.9  0.0       00:00 /root/agentic_trading_system/.venv/bin/python -m scripts.ops_agent
1975598  8.4  1.0       05:01 /root/agentic_trading_system/.venv/bin/python -m bot.main
1974986  0.6  0.9       12:56 /root/agentic_trading_system/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
1625202  0.1  0.0  7-08:32:06 /usr/sbin/qemu-ga
1975234  0.0  0.0       11:15 [kworker/5:0-events]
1975228  0.0  0.0       11:21 sshd: root@pts/0
      1  0.0  0.0 49-10:36:53 /usr/lib/systemd/systemd --system --deserialize=78
1186897  0.0  0.9 18-09:01:03 /usr/lib/systemd/systemd-journald
     91  0.0  0.0 49-10:36:52 [kswapd0]
1975233  0.0  0.0       11:15 /usr/lib/systemd/systemd --user
1968315  0.0  0.6    03:40:11 /root/agentic_trading_system/.venv/bin/python -m scripts.replay_gate --su-file
     17  0.0  0.0 49-10:36:53 [rcu_preempt]
1973627  0.0  0.0       54:39 [kworker/6:0-mm_percpu_wq]
1974831  0.0  0.0       18:27 [kworker/u16:3-events_power_efficient]
     71  0.0  0.0 49-10:36:53 [kcompactd0]
1975695  0.0  0.0       04:56 [kworker/u16:4-ext4-rsv-conversion]
1974382  0.0  0.0       27:31 [kworker/u16:0-flush-8:0]
1973408  0.0  0.0    01:04:14 [kworker/u16:2-writeback]
1974851  0.0  0.0       18:05 [kworker/2:2-events]
1974219  0.0  0.0       33:32 [kworker/u16:1-flush-8:0]
1969841  0.0  0.0    02:57:59 [kworker/7:1-events]
1186864  0.0  0.1 18-09:01:03 /sbin/multipathd -d -s
1186899  0.0  0.0 18-09:01:03 /usr/lib/systemd/systemd-resolved
1186885  0.0  0.0 18-09:01:03 sshd: /usr/sbin/sshd -D [listener] 0 of 10-100 startups
1629822  0.0  0.0  7-06:43:48 /usr/sbin/rsyslogd -n -iNONE
1971177  0.0  0.0    01:57:58 [kworker/4:0-mm_percpu_wq]
1921399  0.0  0.0    23:20:19 [kworker/1:2-mm_percpu_wq]
     73  0.0  0.0 49-10:36:53 [khugepaged]
1961352  0.0  0.0    06:28:26 [kworker/3:1-mm_percpu_wq]
1974551  0.0  0.0       21:07 [kworker/0:2-mm_percpu_wq]
1975325  0.0  0.0       11:14 -bash
    914  0.0  0.0 49-10:36:33 @dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation --syslog-only
1755413  0.0  0.0  4-08:42:19 /usr/lib/polkit-1/polkitd --no-debug
    324  0.0  0.0 49-10:36:49 [jbd2/sda1-8]
    926  0.0  0.0 49-10:36:33 /usr/lib/systemd/systemd-logind
    200  0.0  0.0 49-10:36:51 [kworker/2:1H-kblockd]
1186900  0.0  0.0 18-09:01:03 /usr/lib/systemd/systemd-timesyncd
     18  0.0  0.0 49-10:36:53 [migration/0]
     23  0.0  0.0 49-10:36:53 [migration/1]
     29  0.0  0.0 49-10:36:53 [migration/2]
     30  0.0  0.0 49-10:36:53 [ksoftirqd/2]
     35  0.0  0.0 49-10:36:53 [migration/3]
     41  0.0  0.0 49-10:36:53 [migration/4]
     47  0.0  0.0 49-10:36:53 [migration/5]
    177  0.0  0.0 49-10:36:52 [kworker/3:1H-kblockd]
     59  0.0  0.0 49-10:36:53 [migration/7]
     53  0.0  0.0 49-10:36:53 [migration/6]
     36  0.0  0.0 49-10:36:53 [ksoftirqd/3]
    165  0.0  0.0 49-10:36:52 [kworker/5:1H-kblockd]
    197  0.0  0.0 49-10:36:51 [kworker/4:1H-kblockd]
    162  0.0  0.0 49-10:36:52 [kworker/6:1H-kblockd]
    178  0.0  0.0 49-10:36:51 [kworker/7:1H-kblockd]
     89  0.0  0.0 49-10:36:53 [kworker/0:1H-kblockd]
    109  0.0  0.0 49-10:36:52 [kworker/1:1H-kblockd]
1186858  0.0  0.0 18-09:01:03 /usr/sbin/cron -f -P
1186915  0.0  0.0 18-09:01:03 /usr/lib/systemd/systemd-networkd
1186904  0.0  0.0 18-09:01:03 /usr/lib/systemd/systemd-udevd
     42  0.0  0.0 49-10:36:53 [ksoftirqd/4]
     48  0.0  0.0 49-10:36:53 [ksoftirqd/5]
     54  0.0  0.0 49-10:36:53 [ksoftirqd/6]
     16  0.0  0.0 49-10:36:53 [ksoftirqd/0]
     60  0.0  0.0 49-10:36:53 [ksoftirqd/7]
     66  0.0  0.0 49-10:36:53 [khungtaskd]
     24  0.0  0.0 49-10:36:53 [ksoftirqd/1]
      2  0.0  0.0 49-10:36:53 [kthreadd]
    211  0.0  0.0 49-10:36:51 [hwrng]
1186850  0.0  0.0 18-09:01:03 /usr/sbin/atd -f
    962  0.0  0.0 49-10:36:32 /usr/bin/python3 /usr/share/unattended-upgrades/unattended-upgrade-shutdown --wait-for-signal
    226  0.0  0.0 49-10:36:51 [scsi_eh_1]
    237  0.0  0.0 49-10:36:51 [scsi_eh_6]
1186914  0.0  0.0 18-09:01:03 [psimon]
 274616  0.0  0.0 41-10:20:49 /sbin/agetty -o -p -- \u --noclear - linux
    977  0.0  0.0 49-10:36:32 /sbin/agetty -o -p -- \u --keep-baud 115200,57600,38400,9600 - vt220
    228  0.0  0.0 49-10:36:51 [scsi_eh_2]
    230  0.0  0.0 49-10:36:51 [scsi_eh_3]
    232  0.0  0.0 49-10:36:51 [scsi_eh_4]
      3  0.0  0.0 49-10:36:53 [pool_workqueue_release]
      4  0.0  0.0 49-10:36:53 [kworker/R-rcu_g]
      5  0.0  0.0 49-10:36:53 [kworker/R-rcu_p]
      6  0.0  0.0 49-10:36:53 [kworker/R-slub_]
      7  0.0  0.0 49-10:36:53 [kworker/R-netns]
     10  0.0  0.0 49-10:36:53 [kworker/0:0H-events_highpri]
     12  0.0  0.0 49-10:36:53 [kworker/R-mm_pe]
     13  0.0  0.0 49-10:36:53 [rcu_tasks_kthread]
     14  0.0  0.0 49-10:36:53 [rcu_tasks_rude_kthread]
     15  0.0  0.0 49-10:36:53 [rcu_tasks_trace_kthread]
     19  0.0  0.0 49-10:36:53 [idle_inject/0]
     20  0.0  0.0 49-10:36:53 [cpuhp/0]
     21  0.0  0.0 49-10:36:53 [cpuhp/1]
     22  0.0  0.0 49-10:36:53 [idle_inject/1]
     26  0.0  0.0 49-10:36:53 [kworker/1:0H-events_highpri]
     27  0.0  0.0 49-10:36:53 [cpuhp/2]
     28  0.0  0.0 49-10:36:53 [idle_inject/2]
     32  0.0  0.0 49-10:36:53 [kworker/2:0H-events_highpri]
     33  0.0  0.0 49-10:36:53 [cpuhp/3]
     34  0.0  0.0 49-10:36:53 [idle_inject/3]
     38  0.0  0.0 49-10:36:53 [kworker/3:0H-events_highpri]
     39  0.0  0.0 49-10:36:53 [cpuhp/4]
     40  0.0  0.0 49-10:36:53 [idle_inject/4]
     44  0.0  0.0 49-10:36:53 [kworker/4:0H-events_highpri]
     45  0.0  0.0 49-10:36:53 [cpuhp/5]
     46  0.0  0.0 49-10:36:53 [idle_inject/5]
     50  0.0  0.0 49-10:36:53 [kworker/5:0H-events_highpri]
     51  0.0  0.0 49-10:36:53 [cpuhp/6]
     52  0.0  0.0 49-10:36:53 [idle_inject/6]
     56  0.0  0.0 49-10:36:53 [kworker/6:0H-events_highpri]
     57  0.0  0.0 49-10:36:53 [cpuhp/7]
     58  0.0  0.0 49-10:36:53 [idle_inject/7]
     62  0.0  0.0 49-10:36:53 [kworker/7:0H-events_highpri]
     63  0.0  0.0 49-10:36:53 [kdevtmpfs]
     64  0.0  0.0 49-10:36:53 [kworker/R-inet_]
     65  0.0  0.0 49-10:36:53 [kauditd]
     67  0.0  0.0 49-10:36:53 [oom_reaper]
     69  0.0  0.0 49-10:36:53 [kworker/R-write]
     72  0.0  0.0 49-10:36:53 [ksmd]
     74  0.0  0.0 49-10:36:53 [kworker/R-kinte]
     75  0.0  0.0 49-10:36:53 [kworker/R-kbloc]
     76  0.0  0.0 49-10:36:53 [kworker/R-blkcg]
     77  0.0  0.0 49-10:36:53 [irq/9-acpi]
     80  0.0  0.0 49-10:36:53 [kworker/R-tpm_d]
     81  0.0  0.0 49-10:36:53 [kworker/R-ata_s]
     82  0.0  0.0 49-10:36:53 [kworker/R-md]
     83  0.0  0.0 49-10:36:53 [kworker/R-md_bi]
     84  0.0  0.0 49-10:36:53 [kworker/R-edac-]
     85  0.0  0.0 49-10:36:53 [kworker/R-devfr]
     86  0.0  0.0 49-10:36:53 [watchdogd]
     88  0.0  0.0 49-10:36:53 [kworker/R-quota]
     92  0.0  0.0 49-10:36:52 [ecryptfs-kthread]
     93  0.0  0.0 49-10:36:52 [kworker/R-kthro]
     94  0.0  0.0 49-10:36:52 [irq/24-aerdrv]
     95  0.0  0.0 49-10:36:52 [irq/25-aerdrv]
     96  0.0  0.0 49-10:36:52 [irq/26-aerdrv]
     97  0.0  0.0 49-10:36:52 [irq/27-aerdrv]
     98  0.0  0.0 49-10:36:52 [irq/28-aerdrv]
     99  0.0  0.0 49-10:36:52 [irq/29-aerdrv]
    100  0.0  0.0 49-10:36:52 [irq/30-aerdrv]
    101  0.0  0.0 49-10:36:52 [irq/31-aerdrv]
    102  0.0  0.0 49-10:36:52 [irq/32-aerdrv]
    103  0.0  0.0 49-10:36:52 [kworker/R-acpi_]
    105  0.0  0.0 49-10:36:52 [scsi_eh_0]
    106  0.0  0.0 49-10:36:52 [kworker/R-scsi_]
    108  0.0  0.0 49-10:36:52 [kworker/R-mld]
    110  0.0  0.0 49-10:36:52 [kworker/R-ipv6_]
    117  0.0  0.0 49-10:36:52 [kworker/R-kstrp]
    121  0.0  0.0 49-10:36:52 [kworker/u17:0]
    126  0.0  0.0 49-10:36:52 [kworker/R-crypt]
    137  0.0  0.0 49-10:36:52 [kworker/R-charg]
    227  0.0  0.0 49-10:36:51 [kworker/R-scsi_]
    229  0.0  0.0 49-10:36:51 [kworker/R-scsi_]
    231  0.0  0.0 49-10:36:51 [kworker/R-scsi_]
    233  0.0  0.0 49-10:36:51 [kworker/R-scsi_]
    235  0.0  0.0 49-10:36:51 [scsi_eh_5]
    236  0.0  0.0 49-10:36:51 [kworker/R-scsi_]
    238  0.0  0.0 49-10:36:51 [kworker/R-scsi_]
    284  0.0  0.0 49-10:36:49 [kworker/R-raid5]
    325  0.0  0.0 49-10:36:49 [kworker/R-ext4-]
    412  0.0  0.0 49-10:36:47 [kworker/R-kmpat]
    413  0.0  0.0 49-10:36:47 [kworker/R-kmpat]
   1098  0.0  0.0 49-10:36:30 [kworker/R-tls-s]
1969764  0.0  0.0    03:02:00 [kworker/1:1-cgwb_release]
1973764  0.0  0.0       50:32 [kworker/4:3-cgwb_release]
1974381  0.0  0.0       28:06 [kworker/0:1-cgroup_free]
1974552  0.0  0.0       21:07 [kworker/6:1]
1974921  0.0  0.0       14:04 [kworker/2:3]
1975046  0.0  0.0       12:03 [kworker/7:2-cgroup_free]
1975231  0.0  0.0       11:15 [psimon]
1975236  0.0  0.0       11:15 (sd-pam)
1975241  0.0  0.0       11:15 [psimon]
1975520  0.0  0.0       07:02 [kworker/3:0]
1975539  0.0  0.0       06:01 [kworker/5:2-cgroup_free]
1975873  0.0  0.0       02:00 [kworker/7:0]
1975907  0.0  0.0       00:00 ps -eo pid,pcpu,pmem,etime,args --sort=-pcpu
```
