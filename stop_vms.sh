#!/bin/bash

for vm in storage cache; do
    VBoxManage controlvm $vm savestate
done;
