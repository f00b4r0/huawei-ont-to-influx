# How to run it

```bash
# cat /opt/huawei-onu-to-graphite/run.sh
#!/usr/bin/env bash
while sleep 8; do
  #timeout 8 /opt/huawei-onu-to-graphite/huawei-onu-to-graphite-http.py &
  #timeout 8 /opt/huawei-onu-to-graphite/huawei-onu-to-graphite-telnet.py &
done
exit 0

# cat /etc/systemd/system/huawei-ont-stats.service 
[Unit]
  Description=huawei-ont-stats
  After=time-sync.target
[Service]
  ExecStart=/opt/huawei-onu-to-graphite/run.sh
  WorkingDirectory=/opt/huawei-onu-to-graphite
  Restart=on-failure
  RestartSec=10
[Install]
  WantedBy=multi-user.target
```
