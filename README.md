
# disk_usage_metrics_oci

## Prerequisites
Following utilities needs to be preinstalled on OCI instance
 1. Python 3, pip3
 2. python packages namely oci, json, time, psutil and os
 3. Linux commands lsblk, jq, crontab 
 4. make sure crontab service is enabled. Refer [Crontab Reboot](https://phoenixnap.com/kb/crontab-reboot)
 
## Steps
 1. Create dynamic group(say named DG_X) for nodes for which you want to capture disk usage, similar to one below
   ``
   All {instance.compartment.id = 'ocid1.compartment.oc1..XXX'}
   ``

 2. Create policy for above dynamic group to allow it to post metrics in the same compartment, similar to one below
   ``
   Allow dynamic-group DG_X to use metrics in compartment [Your Compartmentname where Nodes reside]
   ``
 3. Use crontab to schedule the code from the file `disk_usage_metrics_export.py` even after crashes or reboot as follows

  ``

  ``





 
 
 
