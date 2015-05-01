# Logbook
This is a simple logbook to remember when I did what and what issues I
encoutered

## 1st week (Week 14)
### Achievements
- Two running Virtual Machines.
- One storage VM with the Apache that hosts the videos.
- One caching VM with Nginx.
- The caching VM has a Lua capable Nginx installation built from source.

### Issues
- Getting networking to work on the vms was not easy. I tried QEMU as an
    emulator and VirtualBox. Eventually I settled for VritualBox with a NAT
    network interface for internet connectivity and a Host-only Adapter for
    host-guest, guest-host and guest-guest networking.

## 2nd week (Week 15)
### Achievemnts
- Understand how Lua can interact with Nginx by editing and fiddling with the
    prefetch script.
- Automatic backing up of the VMs in case my laptop dies or gets stolen
- Edited the prefetch script to prefetch after the response had been sent to
    the client

### Issues
- The normal `add_header` rule does not work when called from a lua subrequest.
    The `more_set_headers` command should be used from the
    [HttpHeadersModule](http://wiki.nginx.org/HttpHeadersMoreModule).
    The documentation of nginx and the lua extension were very lacking in this
    regard.

## 3rd week (Week 16)
### Achievements
- Get the prefetch script working.
- Get a basic late muxing setup working. Lua wasn't needed for this.
- Set up a proxy from nginx to apache to nginx, all on the same server. Let the
    last nginx request the raw files from the origin.
- Make a couple of aditions to the late muxing setups.

    - Use the prefetching script.
    - Add caching of the local request to Apache.

### Issues
- Nginx would block waiting for itself to return something to ism_proxy_pass,
    since that is a blocking operation. This was fixed by using ismProxyPass on
    Apache on the same server, so nginx would use a non blocking proxy to Apache
    and get a request back from apache that would cause a non blocking proxy to
    the origin server.

## 4th week (Week 17)
### Achievements
- Fix logging of cache status for lua requests

### Issues
- The variable specifying the cache status wasn't accessible from the lua
    request since it was set in the subrequest.


## 5th week (Week 18)
### Achievemnts
- Get Comcast to work.
- Get supplied test script working

## 6t week (Week 19)
### Achievemnts
- Changing the test script so it does tests for something useful for this setup

### Issues
- Getting useful information out of the cache
- Audio is not requested in the same range for all formats
