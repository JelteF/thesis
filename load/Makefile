# vim:noexpandtab:sw=2 ts=2

SERVER=apache
PLATFORM=linux
ifeq ($(SERVER), apache)
PORT=80
else ifeq ($(SERVER), nginx)
PORT=82
endif

export URL_PREFIX?=basic
export URL=http://$(URL_PREFIX).edge.usp.local/video/tears-of-steel

export WRK=wrk/wrk
export SCRIPT=files/report.lua

# expansion works in bash, not in sh
SHELL=bash
export CONNECTIONS=1
export CONNECTION_STEPS:=$(shell eval echo {1..1})
export THREADS=1
export THREAD_STEPS:=$(shell eval echo {1..1})
export DURATION=30s
export RUNS=5

OBJECTS=
#OBJECTS+=mp4
#OBJECTS+=smil
#OBJECTS+=fmp4
OBJECTS+=fmp4-iss-log
OBJECTS+=fmp4-hls-log
OBJECTS+=fmp4-hds-log
OBJECTS+=fmp4-dash-log
OBJECTS+=mp4-iss-log
OBJECTS+=mp4-hls-log
OBJECTS+=mp4-hds-log
OBJECTS+=mp4-dash-log
OBJECTS+=drm-iss-log
OBJECTS+=drm-hls-log
OBJECTS+=drm-hds-log
OBJECTS+=drm-dash-log
OBJECTS+=s3-fmp4-iss-log

.PHONY: clean all link

TIMESTAMP:=$(shell date -u +"%Y-%m-%dT%T.%3N")
DATA=data/$(URL_PREFIX)

#	$(foreach i, $(THREAD_STEPS), \
#		$(foreach n, $(CONNECTION_STEPS), \
#			$i $n \
#		) \
#	)

# wrk -d1 -c1 -t1 -s files/report.lua --latency http://usp-pack:80/video.ref -- mp4
define run-wrk
	bash do_tests.sh $(1) $(2)
endef

all: $(OBJECTS) \
	link

#mp4:
#	$(call run-wrk, $@, $(DATA)/test-$@.log)

#smil:
#	$(call run-wrk, $@, $(DATA)/test-$@.log)

#fmp4:
#	$(call run-wrk, $@, $(DATA)/test-$@.log)

fmp4-hls-log:
	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).log)

fmp4-iss-log:
	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).log)

fmp4-hds-log:
	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).log)

fmp4-dash-log:
	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).log)

# mp4-iss-log:
# 	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).log)
#
# mp4-hds-log:
# 	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).log)
#
# mp4-hls-log:
# 	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).log)
#
# mp4-dash-log:
# 	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).log)
#
# drm-iss-log:
# 	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).log)
#
# drm-hds-log:
# 	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).log)
#
# drm-hls-log:
# 	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).log)
#
# drm-dash-log:
# 	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).log)
#
# s3-fmp4-iss-log:
# 	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).log)

link:
	mkdir -p $(DATA)
	cd $(DATA) && ln -sf ../../files/index.html && ln -sf ../../files/render.html
	#cp -r data data-$(SERVER)-$(TIMESTAMP)

clean:
	rm -rf $(DATA)/*

