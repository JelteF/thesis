# vim:noexpandtab:sw=2 ts=2

SERVER=apache
PLATFORM=linux
ifeq ($(SERVER), apache)
PORT=80
else ifeq ($(SERVER), nginx)
PORT=82
endif
URL=http://single.edge.usp.local:$(PORT)/video/tears-of-steel

WRK=wrk
SCRIPT=files/report.lua

# expansion works in bash, not in sh
SHELL=bash
CONNECTIONS=1
CONNECTION_STEPS:=$(shell eval echo {1..1})
THREADS=1
THREAD_STEPS:=$(shell eval echo {1..1})
DURATION=20s

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
DATA=data

#	$(foreach i, $(THREAD_STEPS), \
#		$(foreach n, $(CONNECTION_STEPS), \
#			$i $n \
#		) \
#	)

# wrk -d1 -c1 -t1 -s files/report.lua --latency http://usp-pack:80/video.ref -- mp4
define run-wrk
	for n in $(THREAD_STEPS); do \
		for i in $(CONNECTION_STEPS) $(CONNECTION_STEPS); do \
			date -u +"%Y-%m-%dT%T.%3N" | tr -d '\n' >> $(2); \
			echo -n " $(SERVER)-$(PLATFORM)" $(notdir $(2)) "$$n $$i " >> $(2); \
			echo running $$n $$i; \
			echo $(WRK) -t $(THREADS) -d $(DURATION) -s $(SCRIPT) -c $$(($(CONNECTIONS) * $$i * $$n)) $(URL) -- $(1) ; \
			$(WRK) -t $(THREADS) -d $(DURATION) -s $(SCRIPT) -c $$(($(CONNECTIONS) * $$i * $$n)) $(URL) -- $(1) \
			| grep {.*} >> $(2); \
		done; \
	done;
endef

all: $(OBJECTS) \
	link

#mp4:
#	$(call run-wrk, $@, $(DATA)/test-$@.wsv)

#smil:
#	$(call run-wrk, $@, $(DATA)/test-$@.wsv)

#fmp4:
#	$(call run-wrk, $@, $(DATA)/test-$@.wsv)

fmp4-hls-log:
	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).wsv)

fmp4-iss-log:
	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).wsv)

fmp4-hds-log:
	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).wsv)

fmp4-dash-log:
	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).wsv)

# mp4-iss-log:
# 	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).wsv)
#
# mp4-hds-log:
# 	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).wsv)
#
# mp4-hls-log:
# 	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).wsv)
#
# mp4-dash-log:
# 	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).wsv)
#
# drm-iss-log:
# 	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).wsv)
#
# drm-hds-log:
# 	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).wsv)
#
# drm-hls-log:
# 	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).wsv)
#
# drm-dash-log:
# 	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).wsv)
#
# s3-fmp4-iss-log:
# 	$(call run-wrk, files/$@, $(DATA)/test-$(notdir $@).wsv)

link:
	cd data && ln -sf ../files/index.html && ln -sf ../files/render.html
	#cp -r data data-$(SERVER)-$(TIMESTAMP)

clean:
	rm -rf data/*

