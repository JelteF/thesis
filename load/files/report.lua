local json = require 'dkjson'
local socket = require 'socket'

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
--  h = json.encode(args)
--  io.write(h)

  base_url = wrk.path
  target = args[1]
  run_once = args[2] == 'once'
  local requests = {}
  replay(requests, base_url, target)

  req = table.concat(requests)
  req_table = requests
  max_requests = table.getn(req_table)
  -- max_requests = 4
  start_time = socket.gettime()
end

request_count = -1
function request()
  if request_count == max_requests then
      -- Once the last request has been sent stop or start over depending on
      -- the way the command was invoked
      request_count = 0
  end
  request_count = request_count + 1

  if request_count == 0 then
      -- stupid bug in wrk, the first requets is not actually fired
      return req_table[1]
  end

  return req_table[request_count]
end

function round(val, decimal)
  local exp = decimal and 10^decimal or 1
  return math.ceil(val * exp - 0.5) / exp
end

finished_count = 0

function delay()
    return 10000
end

stopped = false

response = function()
    finished_count = finished_count + 1
    if finished_count == max_requests and run_once then
        io.write('elapsed time: ' .. socket.gettime() - start_time .. '\n')
        wrk.thread:stop()
    end
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
  s = json.encode(summary)
  io.write('summary: ')
  io.write(s .. "\n")
end
