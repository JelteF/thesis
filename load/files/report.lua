
local json = require 'dkjson'
--[[ 
--Needs content from 'pack'
--backend_f4m -> ../../pack/video.ref/backend_f4m
--baseline -> ../../pack/video.ref/baseline
--pseudo_streaming -> ../../pack/video.ref/pseudo_streaming/
--smil_mp4 -> ../../pack/video.ref/smil_mp4/
--srt -> ../../pack/video.ref/srt
--srt_vod -> ../../pack/video.ref/srt_vod/

local mp4 = "/srt/w2g-band_a.mp4"
local mp4_urls = {}
mp4_urls[1] = mp4.."/Manifest"
mp4_urls[2] = mp4.."/QualityLevels(510000)/Fragments(video=32000000000)"

local smil = "/smil_mp4/bigbuckbunny.smil"
local smil_urls = {}
smil_urls[1] = smil.."/Manifest"
smil_urls[2] = smil.."/QualityLevels(1500000)/Fragments(video=5940000000)"

local ism = "/srt_vod/srt_vod.ism"
local fmp4_urls = {}
fmp4_urls[1] = ism.."/srt_vod.mpd"
fmp4_urls[2] = ism.."/srt_vod-audio=63000-video=255000-168000.dash"
fmp4_urls[3] = ism.."/srt_vod.f4m"
fmp4_urls[4] = ism.."/srt_vod-audio=63000-video=255000-Seg1-Frag50"
fmp4_urls[5] = ism.."/srt_vod-audio=63000-video=255000.m3u8"
fmp4_urls[6] = ism.."/srt_vod-audio=63000-video=255000-1.ts"
fmp4_urls[7] = ism.."/Manifest"
fmp4_urls[8] = ism.."/QualityLevels(63000)/Fragments(audio=1680000000)"
fmp4_urls[9] = ism.."/QualityLevels(510000)/Fragments(video=1680000000)"

local urls = {}
urls['mp4'] = mp4_urls
urls['smil'] = smil_urls
urls['fmp4'] = fmp4_urls
]]-- 

function create_urls(requests, base_url, paths)
  for k,v in ipairs(paths) do
    table.insert(requests, wrk.format(nil, base_url..v))
  end
end

function replay(requests, base_url, file)
  for path in io.lines(file) do 
    table.insert(requests, wrk.format(nil, base_url..path))
  end
end

init = function(args)
  wrk.init(args)
--  h = json.encode(args)
--  io.write(h)

  base_url = wrk.scheme.."://"..wrk.host..wrk.path
  target = args[1]
--  io.write(target)
  local requests = {}
  if string.find(target, "log") then
    replay(requests, base_url, target)
  else
    create_urls(requests, base_url, urls[target])
  end

--  io.write(json.encode(r))
  req = table.concat(requests)
end

request = function()
--  io.write(req)
  return req
end

function round(val, decimal)
  local exp = decimal and 10^decimal or 1
  return math.ceil(val * exp - 0.5) / exp
end

done = function(summary, latency, requests)
  summary["total_errors"] = 
    summary.errors.write
      + summary.errors.read
      + summary.errors.status
      + summary.errors.timeout
      + summary.errors.connect

--[[
  summary["latency"] =
    {min=latency.min,
     max=latency.max,
     mean=latency.mean,
     stdev=latency.stdev}

  distribution = {} 
  for _, p in pairs({ 50, 90, 99, 99.999 }) do
      n = latency:percentile(p)
      distribution[string.format("%g%%", p)]= n
  end
  summary["distribution"] = distribution
]]--
  
  sec = summary.duration * 0.000001

  summary["requests_sec"] = 
   round(summary.requests / sec, 2)

  summary["bytes_sec"] = 
    round(summary.bytes / sec, 2)

  summary["kbytes_sec"] = 
    round(summary.bytes_sec / 1000, 2)
 
  summary["mbytes_sec"] = 
    round(summary.kbytes_sec / 1000, 2)

  s = json.encode(summary)
  io.write(s .. "\n")
end
