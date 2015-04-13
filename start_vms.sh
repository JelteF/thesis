#!/bin/bash

for vm in storage cache; do
    VBoxManage startvm $vm --type headless
done;
