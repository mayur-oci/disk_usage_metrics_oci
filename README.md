
# disk_usage_metrics_oci

## Prerequisites
Following utilities needs to be preinstalled on OCI instance
 1. Python 3, pip3
 2. python packages namely oci, json, time, psutil and os
 3. Linux commands lsblk, jq, crontab 

 4. Create dynamic group(say named DG_X) for nodes for which you want to capture disk usage, similar to one below
``
        All {instance.compartment.id = 'ocid1.compartment.oc1..XXX'}
``
 5.  Create policy for above dynamic group to allow it to post metrics in the same compartment, similar to one below
``
Allow dynamic-group DG_X to use metrics in compartment [Your Compartmentname where Nodes reside]
``
6. 



 
 
 
