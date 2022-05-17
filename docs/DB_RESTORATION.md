## Restoration Guide
### (when restoring from snapshot is not possible)

1. Obtain GotDataArticleNeedTopics CSV from Google Drive

2. Run [to-ubd.py](../util/to-ubd.py)

3. Deploy an ubuntu ec2 instance.

4. Attach security groups: one for SSH from your IP, the default VPC sg, and the neptune sg.

5. `chmod 400 ubd-kp.cer`

6. Copy relevant files (util folder, requirements-common.txt, csv that you want to load, using -r for directories): 

```
scp -i ubd-kp.cer requirements-common.txt ubuntu@ec2-xxx.region-id.compute.amazonaws.com:~/.
```

7. `ssh -i "ubd-kp.cer" ubuntu@ec2-xxx.region-id.compute.amazonaws.com`

8. Install Python3.8

```
$ sudo apt-get install software-properties-common
$ sudo add-apt-repository ppa:deadsnakes/ppa
$ sudo apt-get update
$ sudo apt-get install python3.8
```

9. `sudo apt-get install python3.8-venv`

10. `python3.8 -m venv ./venv`

11. `source venv/bin/activate`

12. `pip install --upgrade pip`

13. `pip install -r requirements-common.txt`

14. `EXPORT NEPTUNEDBRO=wss://instance-id.abc123.region-id.neptune.amazonaws.com:8182/gremlin`

15. run [load_graph.py](../util/load_graph.py)
